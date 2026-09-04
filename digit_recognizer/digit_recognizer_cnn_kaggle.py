# -*- coding: utf-8 -*-
"""
Digit Recognizer CNN - Kaggle Notebook 版
===========================================
与本地 digit_recognizer_cnn.py 完全相同的双层 CNN(结果可对比),适配 Kaggle:

1. 自动定位数据:扫描 /kaggle/input/*(Add Input 挂载)→ kagglehub 兜底 → 本地 data/
2. GPU 自动启用:Notebook 有 GPU 就快几十倍;没有也自动用 CPU(1-2 分钟)
3. 输出 /kaggle/working/submission_cnn.csv → 右侧 Submit to Competition 提交

在 Kaggle Notebook 上运行:
1. New Notebook → 可选 Settings → Accelerator 选 GPU
2. Add Input → 搜索 digit-recognizer 挂载比赛数据(或让脚本用 kagglehub 自动下载)
3. 把本文件全部内容粘贴进单元格运行(或上传后 !python digit_recognizer_cnn_kaggle.py)
4. 跑完打印"提交文件已生成"后,右侧 Submit to Competition

预期:验证精度 ~0.989,公开榜 ~0.988(与本地 CNN 一致)。
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


def resolve_paths():
    """优先 /kaggle/input 扫描;其次 kagglehub;最后本地(脚本目录/当前目录/项目目录)。"""
    if os.path.isdir("/kaggle/input"):
        for sub in os.listdir("/kaggle/input"):
            d = os.path.join("/kaggle/input", sub)
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "train.csv")):
                return (os.path.join(d, "train.csv"), os.path.join(d, "test.csv"),
                        "/kaggle/working/submission_cnn.csv")
    try:
        import kagglehub
        d = kagglehub.competition_download("digit-recognizer")
        if os.path.exists(os.path.join(d, "train.csv")):
            print(f"[路径] 使用 kagglehub 数据: {d}", flush=True)
            return (os.path.join(d, "train.csv"), os.path.join(d, "test.csv"),
                    "/kaggle/working/submission_cnn.csv")
    except ImportError:
        pass
    except Exception as e:
        print(f"[提示] kagglehub 获取数据失败: {e}", flush=True)
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.getcwd())
    cands.append(os.path.join(os.getcwd(), "digit_recognizer"))
    for base in cands:
        p = os.path.join(base, "data", "train.csv")
        if os.path.exists(p):
            return (p, os.path.join(base, "data", "test.csv"),
                    os.path.join(base, "submissions", "submission_cnn.csv"))
    sys.exit("找不到数据:Kaggle 上请先 Add Input 挂载 digit-recognizer;本地请确认在项目目录下运行。")


def main():
    train_path, test_path, out_path = resolve_paths()
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

    test_loader = DataLoader(TensorDataset(torch.from_numpy(X_test)), batch_size=1024)
    preds = []
    model.eval()
    with torch.no_grad():
        for (xb,) in test_loader:
            preds.append(model(xb.to(DEVICE)).argmax(1).cpu().numpy())
    y_pred = np.concatenate(preds)

    submission = pd.DataFrame({"ImageId": np.arange(1, len(y_pred) + 1), "Label": y_pred})
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    submission.to_csv(out_path, index=False)
    print(f"提交文件已生成: {out_path}")
    print(f"行数: {len(submission)} (应为 {len(X_test)}) | 预测分布: {np.bincount(y_pred)}")


if __name__ == "__main__":
    main()
