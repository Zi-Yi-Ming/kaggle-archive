# -*- coding: utf-8 -*-
"""
NLP Getting Started - v4: distilbert + TF-IDF 概率集成(Kaggle Notebook 版)
==========================================================================

思路:预训练 Transformer(语义)与词袋 LR(词汇命中)是两种互补的归纳偏置,
概率加权混合通常比单模型 +0.005~0.01。v3 单模型公开榜 0.83174,目标 0.84+。

关键设计:
- 同一 10% 分层验证集(seed=42,与 v3 一致)上产出两模型的验证概率 →
  权重搜索直接在该验证集上最大化 F1(0.05 步长网格);
- distilbert 输出 sigmoid 概率(不是 v3 的 argmax 标签)——概率混合的前提;
- TF-IDF:word 1-2 + char 2-4 gram + keyword 拼入 text(复用 v2 特征);
- 阈值也随权重一起网格搜索(0.40~0.55,0.01 步长),F1 对阈值敏感。

用法(Kaggle Notebook):
  1. New Notebook → Settings → Accelerator 选 GPU T4
  2. Add Input → 挂载 nlp-getting-started(忘记挂自动 kagglehub 兜底)
  3. 粘贴本文件运行(或上传后 !python nlp_v4_kaggle.py)
  4. 输出 /kaggle/working/submission_nlp_v4.csv → Submit to Competition
本地冒烟(无 GPU,可验证 TF-IDF 与集成逻辑):
  需先安装 transformers 等: pip install transformers torch
"""

import os
import sys

import numpy as np
import pandas as pd
import torch
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          get_linear_schedule_with_warmup)
from torch.optim import AdamW

MODEL_NAME = "distilbert-base-uncased"
MAX_LEN = 96
BATCH_SIZE = 32
EPOCHS = 4
LR = 2e-5
EARLY_STOP_PATIENCE = 2
SEED = 42
VAL_FRAC = 0.1

# ---------------------------------------------------------------------------
# 数据定位(挂载 / kagglehub / 本地)
# ---------------------------------------------------------------------------
def find_data_dir():
    for c in ("/kaggle/input/nlp-getting-started",
              "/kaggle/input/nlp-getting-started/data"):
        if os.path.exists(os.path.join(c, "train.csv")):
            print(f"[数据] 使用挂载目录: {c}")
            return c
    try:
        import kagglehub
        path = kagglehub.competition_download("nlp-getting-started")
        print(f"[数据] kagglehub 下载: {path}")
        return path
    except Exception as e:
        print(f"[数据] kagglehub 不可用({e}), 尝试本地 data/")
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if os.path.exists(os.path.join(local, "train.csv")):
        print(f"[数据] 使用本地目录: {local}")
        return local
    sys.exit("找不到数据: 请 Add Input 挂载 nlp-getting-started, 或把 train.csv 放到本地 data/")


def out_path():
    if os.path.isdir("/kaggle/working"):
        return "/kaggle/working/submission_nlp_v4.csv"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "submissions", "submission_nlp_v4.csv")


# ---------------------------------------------------------------------------
# TF-IDF LR:word 1-2 + char 2-4 + keyword 拼入 text
# ---------------------------------------------------------------------------
def tfidf_predict(train_texts, va_texts, te_texts, y_tr, y_va):
    """在训练集上 fit,返回 验证/测试 正类概率。"""
    word = TfidfVectorizer(ngram_range=(1, 2), analyzer="word",
                           sublinear_tf=True, min_df=3, stop_words="english")
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4),
                           sublinear_tf=True, min_df=3)
    Xw = word.fit_transform(train_texts)
    Xc = char.fit_transform(train_texts)
    X_tr = hstack([Xw, Xc]).tocsr()
    X_va = hstack([word.transform(va_texts), char.transform(va_texts)]).tocsr()
    X_te = hstack([word.transform(te_texts), char.transform(te_texts)]).tocsr()

    lr = LogisticRegression(max_iter=1000, random_state=SEED)
    lr.fit(X_tr, y_tr)
    va_prob = lr.predict_proba(X_va)[:, 1]
    te_prob = lr.predict_proba(X_te)[:, 1]
    va_f1 = f1_score(y_va, (va_prob > 0.5).astype(int))
    print(f"[TF-IDF] 维度 {X_tr.shape[1]}  验证 F1 {va_f1:.4f}", flush=True)
    return va_prob, te_prob


# ---------------------------------------------------------------------------
# distilbert 微调(输出 sigmoid 概率)
# ---------------------------------------------------------------------------
class TweetDataset(Dataset):
    def __init__(self, texts, labels=None):
        self.texts, self.labels = texts, labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        return self.texts[i], (None if self.labels is None else self.labels[i])


def collate_fn(batch):
    texts = [b[0] for b in batch]
    enc = tokenizer(texts, padding=True, truncation=True, max_length=MAX_LEN,
                    return_tensors="pt")
    labels = [b[1] for b in batch]
    if labels[0] is not None:
        enc["labels"] = torch.tensor(labels, dtype=torch.long)
    return enc


def train_one_epoch(model, loader, optimizer, scheduler, device):
    model.train()
    total = 0.0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        optimizer.zero_grad()
        out = model(**batch)
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total += out.loss.item()
    return total / len(loader)


@torch.no_grad()
def proba_loader(model, loader, device):
    """返回 sigmoid 正类概率(供混合;验证集另算 F1)。"""
    model.eval()
    probs = []
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        logits = model(**batch).logits
        probs.extend(torch.sigmoid(logits[:, 1]).cpu().tolist())
    return np.array(probs)


def bert_proba(texts_tr, y_tr, texts_va, texts_te, device, y_va):
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.to(device)

    tr_loader = DataLoader(TweetDataset(texts_tr, y_tr), batch_size=BATCH_SIZE,
                           shuffle=True, collate_fn=collate_fn)
    va_loader = DataLoader(TweetDataset(texts_va), batch_size=BATCH_SIZE,
                           shuffle=False, collate_fn=collate_fn)
    te_loader = DataLoader(TweetDataset(texts_te), batch_size=BATCH_SIZE,
                           shuffle=False, collate_fn=collate_fn)

    optimizer = AdamW(model.parameters(), lr=LR)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0,
        num_training_steps=len(tr_loader) * EPOCHS)

    best_f1, best_state, no_improve = 0.0, None, 0
    for epoch in range(1, EPOCHS + 1):
        loss = train_one_epoch(model, tr_loader, optimizer, scheduler, device)
        va_prob = proba_loader(model, va_loader, device)
        va_f1 = f1_score(y_va, (va_prob > 0.5).astype(int))
        print(f"epoch {epoch}/{EPOCHS}: loss {loss:.4f}  val F1 {va_f1:.4f}", flush=True)
        if va_f1 > best_f1:
            best_f1, no_improve = va_f1, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1
            if no_improve >= EARLY_STOP_PATIENCE:
                print("早停")
                break
    model.load_state_dict(best_state)
    print(f"[distilbert] 最佳验证 F1 {best_f1:.4f}", flush=True)
    return proba_loader(model, va_loader, device), proba_loader(model, te_loader, device)


# ---------------------------------------------------------------------------
# 权重 + 阈值网格搜索(在验证集上最大化 F1)
# ---------------------------------------------------------------------------
def search_blend(p_bert, p_tfidf, y):
    """w ∈ [0,1] 步长 0.05,阈值 ∈ [0.40, 0.55] 步长 0.01,最大化验证 F1。"""
    best = (0.0, 0.5, 0.5, 0.0)
    for w in np.arange(0, 1.0001, 0.05):
        blend = w * p_bert + (1 - w) * p_tfidf
        for th in np.arange(0.40, 0.5601, 0.01):
            f1 = f1_score(y, (blend > th).astype(int))
            if f1 > best[0]:
                best = (f1, w, th, 0.0)
    # 对照:单模型在最优阈值下的 F1
    best_bert = max(f1_score(y, (p_bert > th).astype(int))
                    for th in np.arange(0.40, 0.5601, 0.01))
    best_tfidf = max(f1_score(y, (p_tfidf > th).astype(int))
                     for th in np.arange(0.40, 0.5601, 0.01))
    return best, best_bert, best_tfidf


def main():
    global y_va
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[设备] {device}")

    data_dir = find_data_dir()
    train = pd.read_csv(os.path.join(data_dir, "train.csv"))
    test = pd.read_csv(os.path.join(data_dir, "test.csv"))
    print(f"[数据] train {train.shape}  test {test.shape}")

    # keyword 拼入 text(与 v2/v3 一致)
    for df in (train, test):
        df["text"] = df["text"].fillna("") + " " + df["keyword"].fillna("unknown")

    tr_texts, va_texts, tr_y, y_va = train_test_split(
        train["text"].tolist(), train["target"].tolist(),
        test_size=VAL_FRAC, stratify=train["target"], random_state=SEED)
    te_texts = test["text"].tolist()
    print(f"[数据] 训练 {len(tr_texts)} / 验证 {len(va_texts)} / 测试 {len(te_texts)}")

    # 1) TF-IDF LR(快,先跑)
    p_tfidf_va, p_tfidf_te = tfidf_predict(tr_texts, va_texts, te_texts, tr_y, y_va)

    # 2) distilbert 微调
    p_bert_va, p_bert_te = bert_proba(tr_texts, tr_y, va_texts, te_texts, device, y_va)

    # 3) 权重 + 阈值搜索
    (best_f1, w, th, _), f1_bert, f1_tfidf = search_blend(p_bert_va, p_tfidf_va, y_va)
    print(f"\n单模型最佳 F1: distilbert {f1_bert:.4f} | TF-IDF {f1_tfidf:.4f}")
    print(f"混合: w_bert={w:.2f} 阈值={th:.2f}  验证 F1 {best_f1:.4f}")

    # 4) 生成提交
    blend_te = w * p_bert_te + (1 - w) * p_tfidf_te
    y_pred = (blend_te > th).astype(int)
    sub = pd.DataFrame({"id": test["id"], "target": y_pred})
    out = out_path()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行, 正例占比 {y_pred.mean():.3f})")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
