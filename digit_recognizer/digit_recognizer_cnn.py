# -*- coding: utf-8 -*-
"""
Digit Recognizer CNN(第一座 torch 桥)
=======================================
双层卷积网络,在 42k 张 28x28 灰度数字上训练,目标是 0.99+。

流程:CSV → (N,1,28,28) 归一化 → CNN(Conv+Pool ×2 → 全连接)→ Adam + 交叉熵
→ 保留验证集最佳权重 → 预测测试集 → 提交。

结构:Conv(1→32)+ReLU+MaxPool → Conv(32→64)+ReLU+MaxPool → FC(3136→128)+Dropout → FC(128→10)

用法: conda activate kaggle 后: python digit_recognizer_cnn.py
输出: submissions/submission_cnn.csv (ImageId, Label)
"""

import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EPOCHS = 10
BATCH = 256
LR = 1e-3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    print(f"训练集: {train.shape}  测试集: {test.shape} | 设备: {DEVICE}")

    torch.manual_seed(RANDOM_STATE)
    y = train["label"].values.astype(np.int64)
    X = train.drop(columns=["label"]).values.astype(np.float32).reshape(-1, 1, 28, 28) / 255.0
    X_test = test.values.astype(np.float32).reshape(-1, 1, 28, 28) / 255.0

    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.1, stratify=y, random_state=RANDOM_STATE)
    train_loader = DataLoader(TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(ytr)),
                              batch_size=BATCH, shuffle=True)
    val_loader = DataLoader(TensorDataset(torch.from_numpy(Xva), torch.from_numpy(yva)),
                            batch_size=1024)

    model = CNN().to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss()

    best_acc, best_state = 0.0, None
    for epoch in range(EPOCHS):
        model.train()
        tl, tn = 0.0, 0
        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            tl += loss.item() * len(xb)
            tn += len(xb)
        model.eval()
        correct = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                correct += (model(xb).argmax(1) == yb).sum().item()
        acc = correct / len(Xva)
        if acc > best_acc:
            best_acc = acc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        print(f"epoch {epoch + 1}: train_loss {tl / tn:.4f} | val_acc {acc:.4f} (best {best_acc:.4f})", flush=True)
    model.load_state_dict(best_state)
    print(f"最佳验证精度: {best_acc:.4f}")

    # 预测测试集
    test_loader = DataLoader(TensorDataset(torch.from_numpy(X_test)), batch_size=1024)
    preds = []
    model.eval()
    with torch.no_grad():
        for (xb,) in test_loader:
            preds.append(model(xb.to(DEVICE)).argmax(1).cpu().numpy())
    y_pred = np.concatenate(preds)

    submission = pd.DataFrame({"ImageId": np.arange(1, len(y_pred) + 1), "Label": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_cnn.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"提交文件已生成: {out}")
    print(f"行数: {len(submission)} (应为 {len(X_test)}) | 预测分布: {np.bincount(y_pred)}")


if __name__ == "__main__":
    main()
