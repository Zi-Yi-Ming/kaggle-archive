# -*- coding: utf-8 -*-
"""
LLM Classification Finetuning — v1(Chatbot Arena 人类偏好三分类)
================================================================
比赛:https://www.kaggle.com/competitions/llm-classification-finetuning
任务:给定 prompt + 两个匿名 LLM 响应(response_a / response_b),
     预测人类偏好:三分类(winner_model_a / winner_model_b / tie)。
指标:多分类 Log Loss(随机基线 log(3)≈1.0986)。
数据:train.csv 57477 行 × 9 列;test.csv 无标签(亦无 model_a/b 列)。

两条建模路径(--method 选择):
  feat     :特征工程(TF-IDF + 文本质量特征)+ 逻辑回归。无 GPU、无权重依赖,
             秒级可跑,保底提交(目标 logloss < 1.08)。
  finetune :双塔 Siamese Transformer(prompt+resp 分别编码,融合
             [a; b; a-b; a*b] → 3 类头)。需要 transformers 库 + 预训练权重:
             ① 挂载离线权重数据集(如 kozodoi/transformers,含 distilbert-base-uncased
                等全套 config+tokenizer+权重,脚本自动扫描,无需联网);
             ② 或 --pretrained 联网从 HF Hub 下载。
  auto     :(默认)扫到离线模型目录就走 finetune,否则回退 feat。

运行环境:Kaggle Notebook(GPU T4 加速,挂载比赛数据)。
用法:
    !python llm_pref_v1.py --method auto --epochs 3 --batch 16
输出: submission.csv(id + winner_model_a/b/tie 三列概率)
"""
import argparse
import os
import re
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

TARGETS = ["winner_model_a", "winner_model_b", "winner_tie"]
ID_COL = "id"
TEXT_COLS = ["prompt", "response_a", "response_b"]

SEED = 42
MAX_LEN = 384          # finetune 最大 token 数(社区经验 512 以内即可)
FOLDS = 5
EPS = 1e-9

# ---------------- 依赖探测 ----------------
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import log_loss
    HAS_SK = True
except ImportError:
    HAS_SK = False

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from torch.optim import AdamW
    from torch.optim.lr_scheduler import CosineAnnealingLR
    HAS_TF = True
except ImportError:
    HAS_TF = False


def resolve_paths():
    """数据定位:/kaggle/input 挂载 → kagglehub → 本地 llm_classification/ 目录。"""
    if os.path.isdir("/kaggle/input"):
        for sub in sorted(os.listdir("/kaggle/input")):
            d = os.path.join("/kaggle/input", sub)
            for cand in (d, os.path.join(d, sub)):
                if os.path.exists(os.path.join(cand, "train.csv")) and \
                   os.path.exists(os.path.join(cand, "sample_submission.csv")):
                    return cand, "/kaggle/working"
            if os.path.isdir(d):
                for sub2 in sorted(os.listdir(d)):
                    cand = os.path.join(d, sub2)
                    if os.path.exists(os.path.join(cand, "train.csv")) and \
                       os.path.exists(os.path.join(cand, "sample_submission.csv")):
                        return cand, "/kaggle/working"
        print("[诊断] /kaggle/input 存在,但没找到含 train.csv+sample_submission.csv 的目录。"
              "挂载内容:", flush=True)
        for sub in sorted(os.listdir("/kaggle/input")):
            p = os.path.join("/kaggle/input", sub)
            try:
                inner = os.listdir(p)
            except OSError:
                inner = ["(无法读取)"]
            print(f"  /kaggle/input/{sub}/  ->  {inner[:6]}", flush=True)
        print("[诊断] 必须挂比赛数据本体 llm-classification-finetuning"
              "(Add Input -> Competitions 标签页)", flush=True)
    try:
        import kagglehub
        d = kagglehub.competition_download("llm-classification-finetuning")
        if os.path.exists(os.path.join(d, "train.csv")):
            print(f"[路径] 未挂载,已用 kagglehub 获取数据: {d}", flush=True)
            return d, "/kaggle/working"
    except ImportError:
        pass
    except Exception as e:
        print(f"[提示] kagglehub 下载数据失败: {e}", flush=True)
    cands = [os.getcwd(), os.path.join(os.getcwd(), "llm_classification")]
    try:
        cands.insert(0, os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    seen = set()
    for base in cands:
        if base in seen:
            continue
        seen.add(base)
        if os.path.exists(os.path.join(base, "train.csv")):
            return base, base
    sys.exit("找不到数据:请 Add Input 挂载 llm-classification-finetuning;"
             "本地请在 llm_classification/ 下运行。")


# ---------------- 文本质量特征(TF-IDF 路径用) ----------------

def _len_stat(s):
    """一组文本长度统计特征。"""
    n = len(s)
    words = len(s.split())
    sentences = max(s.count(".") + s.count("!") + s.count("?"), 1)
    code = len(re.findall(r"```|`[^`]+`", s))
    caps = sum(1 for ch in s if ch.isupper())
    nums = sum(ch.isdigit() for ch in s)
    return n, words, sentences, code, caps, nums


def build_features(df):
    """从 prompt/response_a/response_b 造出 A-B 对比特征与 TF-IDF 文本。

    返回 (X_meta, tfidf_docs);meta 列全是数值差/比,TF-IDF 文档单独拼接。
    """
    rows = []
    docs = []
    for _, r in df.iterrows():
        prompt = str(r["prompt"]) if pd.notna(r["prompt"]) else ""
        a = str(r["response_a"]) if pd.notna(r["response_a"]) else ""
        b = str(r["response_b"]) if pd.notna(r["response_b"]) else ""
        la, wa, sa, ca, capsa, na = _len_stat(a)
        lb, wb, sb, cb, capsb, nb = _len_stat(b)
        lp = len(prompt)
        rows.append([
            la - lb, wa - wb, sa - sb, ca - cb, capsa - capsb, na - nb,   # A-B 差
            la / max(lb, 1), wa / max(wb, 1), ca / max(cb, 1),            # A/B 比
            lp, la, lb, wa, wb,                                           # 绝对长度
            abs(ca - cb), abs(na - nb),                                   # 结构差异
        ])
        docs.append(f"{prompt} [SEP] {a} [SEP] {b}")
    return np.array(rows, dtype=np.float32), docs


# ---------------- 离线 HF 模型扫描 ----------------

_MODEL_MARKERS = ("config.json",)          # HF 模型目录必须有 config.json
_WEIGHT_FILES = ("model.safetensors", "pytorch_model.bin", "tf_model.h5")
_SKIP_DIRS = {"train_series", "test_series"}


def _scan_hf_models(base="/kaggle/input", depth=0, max_depth=4):
    """递归找挂载目录下的 HF 模型目录(含 config.json + 至少一个权重文件)。

    返回 [(目录, 相对描述)]。按优先级排序:
      distilbert > roberta > deberta > bert-base/large > 其他;
      albert 排除(参数量大,双塔+batch 易 OOM)。
    找不到返回空列表。
    """
    hits = []
    if depth > max_depth or not os.path.isdir(base):
        return hits
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return hits
    for fn in entries:
        p = os.path.join(base, fn)
        if os.path.isdir(p) and fn not in _SKIP_DIRS:
            if os.path.exists(os.path.join(p, "config.json")) and any(
                    os.path.exists(os.path.join(p, w)) for w in _WEIGHT_FILES):
                hits.append((p, os.path.relpath(p, "/kaggle/input")))
            else:
                hits.extend(_scan_hf_models(p, depth + 1, max_depth))

    def pref_rank(item):
        d = item[1].lower()
        if "albert" in d:
            return 99  # albert 含 "bert" 子串但参数量大,排除在优先之外
        for i, k in enumerate(("distilbert", "roberta", "deberta", "bert")):
            if k in d:
                return i
        return 10

    hits.sort(key=pref_rank)
    return hits


def pick_model_dir():
    """返回选定的 HF 模型目录(或 None)。"""
    if not os.path.isdir("/kaggle/input"):
        return None
    hits = _scan_hf_models()
    if not hits:
        return None
    d, desc = hits[0]
    print(f"[模型] 使用离线 HF 模型: {desc}", flush=True)
    return d


# ---------------- 双塔 Siamese Transformer(微调路径) ----------------

class PairDataset(Dataset):
    """每行: (prompt, response_a) 与 (prompt, response_b) 两段文本, 共享编码器。"""

    def __init__(self, df, tokenizer, max_len=MAX_LEN):
        self.texts_a, self.texts_b, self.labels = [], [], []
        for _, r in df.iterrows():
            prompt = str(r["prompt"]) if pd.notna(r["prompt"]) else ""
            a = str(r["response_a"]) if pd.notna(r["response_a"]) else ""
            b = str(r["response_b"]) if pd.notna(r["response_b"]) else ""
            self.texts_a.append(f"{prompt} [SEP] {a}")
            self.texts_b.append(f"{prompt} [SEP] {b}")
            if all(c in r for c in TARGETS):
                self.labels.append([float(r[c]) for c in TARGETS])
            else:
                self.labels.append(None)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts_a)

    def __getitem__(self, i):
        enc_a = self.tokenizer(self.texts_a[i], truncation=True, max_length=self.max_len,
                               padding="max_length", return_tensors="pt")
        enc_b = self.tokenizer(self.texts_b[i], truncation=True, max_length=self.max_len,
                               padding="max_length", return_tensors="pt")
        item = {
            "input_ids_a": enc_a["input_ids"].squeeze(0),
            "attention_mask_a": enc_a["attention_mask"].squeeze(0),
            "input_ids_b": enc_b["input_ids"].squeeze(0),
            "attention_mask_b": enc_b["attention_mask"].squeeze(0),
        }
        if self.labels[i] is not None:
            item["labels"] = torch.tensor(self.labels[i], dtype=torch.float32)
        return item


class SiameseModel(nn.Module):
    """共享编码器双塔: a=[prompt;resp_a], b=[prompt;resp_b], 融合 [a;b;a-b;a*b] → 3 类。"""

    def __init__(self, model_dir, num_labels=3):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_dir)
        hidden = self.encoder.config.hidden_size
        self.drop = nn.Dropout(0.2)
        self.head = nn.Linear(hidden * 4, num_labels)

    def forward(self, batch):
        enc_a = self.encoder(input_ids=batch["input_ids_a"],
                             attention_mask=batch["attention_mask_a"])
        enc_b = self.encoder(input_ids=batch["input_ids_b"],
                             attention_mask=batch["attention_mask_b"])
        a = enc_a.last_hidden_state[:, 0]   # [CLS]
        b = enc_b.last_hidden_state[:, 0]
        feat = torch.cat([a, b, a - b, a * b], dim=1)
        return self.head(self.drop(feat))   # logits (B, 3)


def train_epoch(model, loader, opt, crit, device):
    model.train()
    tot, cnt = 0.0, 0
    for batch in loader:
        batch = {k: (v.to(device) if isinstance(v, torch.Tensor) else v)
                 for k, v in batch.items()}
        opt.zero_grad()
        logits = model(batch)
        loss = crit(logits, batch["labels"].argmax(dim=1))  # CrossEntropy 需要类别索引
        loss.backward()
        opt.step()
        tot += loss.item() * len(batch["labels"])
        cnt += len(batch["labels"])
    return tot / max(cnt, 1)


@torch.no_grad()
def predict(model, loader, device):
    model.eval()
    outs = []
    for batch in loader:
        batch = {k: (v.to(device) if isinstance(v, torch.Tensor) else v)
                 for k, v in batch.items()}
        logits = model(batch)
        outs.append(torch.softmax(logits, dim=1).cpu().numpy())
    return np.concatenate(outs, axis=0)


def run_finetune(df, test_df, model_dir, args):
    """微调主流程: 5 折交叉验证, 输出 OOF 与 test 平均概率。"""
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[微调] tokenizer 就绪, device={device}, epochs={args.epochs}, "
          f"max_len={MAX_LEN}", flush=True)

    skf = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=args.seed)
    y_main = df[TARGETS].idxmax(axis=1).values  # 分层层用
    oof = np.zeros((len(df), 3))
    test_pred = np.zeros((len(test_df), 3))

    for k, (tr_idx, va_idx) in enumerate(skf.split(df, y_main)):
        print(f"\n[折 {k + 1}/{args.folds}] train {len(tr_idx)} / val {len(va_idx)}", flush=True)
        tr_ds = PairDataset(df.iloc[tr_idx], tokenizer)
        va_ds = PairDataset(df.iloc[va_idx], tokenizer)
        te_ds = PairDataset(test_df, tokenizer)
        tr_ld = DataLoader(tr_ds, batch_size=args.batch, shuffle=True, num_workers=0)
        va_ld = DataLoader(va_ds, batch_size=args.batch, shuffle=False, num_workers=0)
        te_ld = DataLoader(te_ds, batch_size=args.batch, shuffle=False, num_workers=0)

        model = SiameseModel(model_dir).to(device)
        opt = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
        sched = CosineAnnealingLR(opt, T_max=args.epochs)
        crit = nn.CrossEntropyLoss()

        for ep in range(args.epochs):
            loss = train_epoch(model, tr_ld, opt, crit, device)
            va_prob = predict(model, va_ld, device)
            y_va = df.iloc[va_idx][TARGETS].values
            ll = log_loss(y_va, va_prob)  # y_va 是 one-hot(n,3),无需 labels 参数
            print(f"  epoch {ep + 1}/{args.epochs}  train_loss {loss:.4f}  "
                  f"val_logloss {ll:.4f}", flush=True)
            sched.step()

        va_prob = predict(model, va_ld, device)
        oof[va_idx] = va_prob
        test_pred += predict(model, te_ld, device) / args.folds

    y_all = df[TARGETS].values
    print(f"\n[微调] OOF 多分类 LogLoss: {log_loss(y_all, oof):.4f}", flush=True)
    return oof, test_pred


# ---------------- 特征工程 + 逻辑回归路径(保底, 无需 GPU) ----------------

def run_feat(df, test_df, args):
    """TF-IDF + 元特征 + 逻辑回归, 5 折 OOF。"""
    print("[feat] 构造 TF-IDF 与元特征...", flush=True)
    X_meta_tr, docs_tr = build_features(df)
    X_meta_te, docs_te = build_features(test_df)
    tfidf = TfidfVectorizer(max_features=20000, ngram_range=(1, 2),
                            sublinear_tf=True, min_df=3)
    X_tf_tr = tfidf.fit_transform(docs_tr)
    X_tf_te = tfidf.transform(docs_te)
    from scipy.sparse import hstack as sparse_hstack
    X_tr = sparse_hstack([X_tf_tr, X_meta_tr]).tocsr()
    X_te = sparse_hstack([X_tf_te, X_meta_te]).tocsr()

    y = df[TARGETS].idxmax(axis=1).map({c: i for i, c in enumerate(TARGETS)}).values
    skf = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=args.seed)
    oof = np.zeros((len(df), 3))
    test_pred = np.zeros((len(test_df), 3))
    for k, (tr_idx, va_idx) in enumerate(skf.split(df, y)):
        clf = LogisticRegression(C=1.0, max_iter=1000, n_jobs=-1)
        clf.fit(X_tr[tr_idx], y[tr_idx])
        oof[va_idx] = clf.predict_proba(X_tr[va_idx])
        test_pred += clf.predict_proba(X_te) / args.folds
    y_true = np.eye(3)[y]
    print(f"[feat] OOF 多分类 LogLoss: {log_loss(y_true, oof):.4f}", flush=True)
    return oof, test_pred


# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", type=str, default="auto",
                    choices=["auto", "feat", "finetune"],
                    help="auto=扫到离线模型走 finetune,否则 feat;feat=仅特征+LR(无 GPU);"
                         "finetune=双塔微调(需 HF 权重)")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--folds", type=int, default=FOLDS)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--model-dir", type=str, default="",
                    help="显式指定 HF 模型目录(挂载的离线权重);留空自动扫描")
    ap.add_argument("--data", type=str, default="",
                    help="显式指定数据根目录;留空自动定位")
    args, _ = ap.parse_known_args()

    np.random.seed(args.seed)
    if HAS_TF:
        import torch
        torch.manual_seed(args.seed)

    # 数据定位
    if args.data:
        if os.path.exists(os.path.join(args.data, "train.csv")):
            root, out = args.data, args.data
        else:
            sys.exit(f"--data 指定目录 {args.data} 下没有 train.csv")
    else:
        root, out = resolve_paths()
    print(f"[数据] root={root}  out={out}")

    train_df = pd.read_csv(os.path.join(root, "train.csv"))
    test_df = pd.read_csv(os.path.join(root, "test.csv"))
    print(f"[数据] train {len(train_df)} 行 / test {len(test_df)} 行, "
          f"列: {list(train_df.columns)}")
    if not all(c in train_df.columns for c in TARGETS):
        sys.exit(f"train.csv 缺少目标列 {TARGETS},请检查是否挂错数据")
    print(f"[数据] 类别分布: {train_df[TARGETS].sum().to_dict()}")

    # 方法选择
    method = args.method
    model_dir = args.model_dir or ""
    if method == "auto":
        if not model_dir:
            model_dir = pick_model_dir() or ""
        if model_dir and HAS_TF:
            method = "finetune"
            print(f"[方法] auto → finetune(找到离线模型 {model_dir})", flush=True)
        else:
            method = "feat"
            print("[方法] auto → feat(未找到离线 HF 模型,回退特征+LR;"
                  "可挂载 kozodoi/transformers 走微调)", flush=True)
    if method == "finetune":
        if not HAS_TF:
            sys.exit("finetune 需要 transformers+torch,请在 Kaggle Notebook 运行")
        if not model_dir:
            model_dir = pick_model_dir() or ""
        if not model_dir:
            sys.exit("finetune 需要 HF 模型目录:挂载 kozodoi/transformers 等离线权重数据集,"
                     "或用 --model-dir 指定;或加 --pretrained 联网下载(未实现,请用离线挂载)")
        oof, test_pred = run_finetune(train_df, test_df, model_dir, args)
    else:
        if not HAS_SK:
            sys.exit("feat 需要 scikit-learn")
        oof, test_pred = run_feat(train_df, test_df, args)

    # 提交文件
    sub = pd.DataFrame({ID_COL: test_df[ID_COL]})
    for j, c in enumerate(TARGETS):
        sub[c] = test_pred[:, j]
    sub_path = os.path.join(out, "submission.csv")
    sub.to_csv(sub_path, index=False)
    print(f"\n提交文件已生成: {sub_path}  shape={sub.shape}")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
