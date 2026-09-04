# -*- coding: utf-8 -*-
"""
NLP Getting Started - v3: distilbert 微调(Kaggle Notebook 版)
==============================================================

在 v2(词袋特征, 公开榜 0.80784) 基础上换预训练 Transformer:
distilbert-base-uncased 微调 3-4 epoch, 目标公开榜 0.84+。

适配 Kaggle Notebook:
  1. 自动定位数据: /kaggle/input/ 挂载 → kagglehub 兜底 → 本地 data/
  2. GPU 自动启用: 检测到 cuda 用 GPU, 否则 CPU 兜底
  3. 分层 10% 验证集 + 早停(patience=2), 防止过拟合
  4. 跑完输出 /kaggle/working/submission_nlp_v3.csv(或本地 submissions/)

用法:
  1. https://www.kaggle.com/code → New Notebook
  2. Settings → Accelerator 选 GPU T4
  3. Add Input → 搜索 nlp-getting-started 挂载比赛数据(忘记挂会自动 kagglehub 下载)
  4. 粘贴本文件内容运行(或上传后 !python nlp_v3_kaggle.py)
  5. 输出提交文件 → 右侧 Submit to Competition
"""

import os
import sys

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from torch.utils.data import Dataset, DataLoader

# --- transformers 在 Kaggle Notebook 预装; 本地冒烟测试需自行安装 ---
# 注: 用 torch.optim.AdamW 而非 transformers.AdamW——transformers 5.x 移除了
# 顶层 AdamW 导出, torch 版在 4.x/5.x 环境都兼容(Kaggle 上是 4.x)。
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


# ---------------------------------------------------------------------------
# 1. 自动定位数据(挂载 / kagglehub / 本地 三选一)
# ---------------------------------------------------------------------------
def find_data_dir():
    candidates = [
        "/kaggle/input/nlp-getting-started",          # Notebook 挂载
        "/kaggle/input/nlp-getting-started/data",     # 挂载但多包一层
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "train.csv")):
            print(f"[数据] 使用挂载目录: {c}")
            return c
    # kagglehub 兜底(Notebook 未挂载时自动下载)
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


# ---------------------------------------------------------------------------
# 2. Dataset
# ---------------------------------------------------------------------------
class TweetDataset(Dataset):
    def __init__(self, texts, labels=None):
        self.texts = texts
        self.labels = labels

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


# ---------------------------------------------------------------------------
# 3. 训练循环(早停按验证 F1)
# ---------------------------------------------------------------------------
def train_one_epoch(model, loader, optimizer, scheduler, device):
    model.train()
    total_loss = 0.0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        optimizer.zero_grad()
        out = model(**batch)
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += out.loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    preds, trues = [], []
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        logits = model(**batch).logits
        preds.extend(logits.argmax(dim=1).cpu().tolist())
        trues.extend(batch["labels"].cpu().tolist())
    return f1_score(trues, preds)


@torch.no_grad()
def predict_test(model, loader, device):
    model.eval()
    preds = []
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        logits = model(**batch).logits
        preds.extend(logits.argmax(dim=1).cpu().tolist())
    return np.array(preds)


# ---------------------------------------------------------------------------
# 4. 主流程
# ---------------------------------------------------------------------------
def main():
    global tokenizer
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[设备] {device}")

    data_dir = find_data_dir()
    train = pd.read_csv(os.path.join(data_dir, "train.csv"))
    test = pd.read_csv(os.path.join(data_dir, "test.csv"))
    print(f"[数据] train {train.shape}  test {test.shape}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.to(device)

    # keyword 缺失填 unknown, 与 v2 一致(简单小提升)
    train["text"] = train["text"].fillna("") + " " + train["keyword"].fillna("unknown")
    test["text"] = test["text"].fillna("") + " " + test["keyword"].fillna("unknown")

    # 分层 10% 验证集
    tr_texts, va_texts, tr_y, va_y = train_test_split(
        train["text"].tolist(), train["target"].tolist(),
        test_size=0.1, stratify=train["target"], random_state=SEED)
    print(f"[数据] 训练 {len(tr_texts)} 条, 验证 {len(va_texts)} 条")

    tr_loader = DataLoader(TweetDataset(tr_texts, tr_y), batch_size=BATCH_SIZE,
                           shuffle=True, collate_fn=collate_fn)
    va_loader = DataLoader(TweetDataset(va_texts, va_y), batch_size=BATCH_SIZE,
                           shuffle=False, collate_fn=collate_fn)
    te_loader = DataLoader(TweetDataset(test["text"].tolist()), batch_size=BATCH_SIZE,
                           shuffle=False, collate_fn=collate_fn)

    optimizer = AdamW(model.parameters(), lr=LR)
    total_steps = len(tr_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0,
                                                num_training_steps=total_steps)

    print("\n===== 微调 distilbert =====")
    best_f1, best_state, no_improve = 0.0, None, 0
    for epoch in range(1, EPOCHS + 1):
        loss = train_one_epoch(model, tr_loader, optimizer, scheduler, device)
        va_f1 = evaluate(model, va_loader, device)
        print(f"epoch {epoch}/{EPOCHS}: loss {loss:.4f}  val F1 {va_f1:.4f}")
        if va_f1 > best_f1:
            best_f1, no_improve = va_f1, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1
            if no_improve >= EARLY_STOP_PATIENCE:
                print(f"早停: 连续 {EARLY_STOP_PATIENCE} 个 epoch 无提升")
                break
    model.load_state_dict(best_state)
    print(f"最佳验证 F1: {best_f1:.4f}")

    print("\n===== 预测测试集 =====")
    y_pred = predict_test(model, te_loader, device)
    sub = pd.DataFrame({"id": test["id"], "target": y_pred})
    out = os.path.join("/kaggle/working", "submission_nlp_v3.csv")
    if not os.path.isdir("/kaggle/working"):
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "submissions", "submission_v3.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行, 正例占比 {y_pred.mean():.3f})")
    print(sub.head(3).to_string(index=False))
    print("\n完成! 去右侧 Submit to Competition 提交。")


if __name__ == "__main__":
    main()
