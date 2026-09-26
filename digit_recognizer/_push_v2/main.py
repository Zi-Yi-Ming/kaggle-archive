# -*- coding: utf-8 -*-
"""Digit Recognizer v2 on Kaggle CPU: BN-CNN + aug + multi-seed ensemble.

Target: public > 0.98778 (v1). Writes /kaggle/working/submission.csv
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

SEEDS = [42, 7, 2026]
EPOCHS = 16
BATCH = 128
LR = 1e-3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def resolve_data():
    roots = [Path("/kaggle/input")]
    here = Path(__file__).resolve().parent
    roots += [here.parent / "data", here / "data"]
    for root in roots:
        if not root.exists():
            continue
        print(f"scan {root}:", os.listdir(root)[:40], flush=True)
        for p in root.rglob("train.csv"):
            return p.parent
    raise SystemExit("train.csv not found")


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2), nn.Dropout2d(0.25),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.MaxPool2d(2), nn.Dropout2d(0.25),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 256), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(256, 10),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def augment(x):
    if torch.rand(1).item() < 0.5:
        sx = int(torch.randint(-2, 3, (1,)))
        sy = int(torch.randint(-2, 3, (1,)))
        x = torch.roll(x, shifts=(sx, sy), dims=(2, 3))
    if torch.rand(1).item() < 0.3:
        x = (x + 0.05 * torch.randn_like(x)).clamp(0, 1)
    return x


def predict_proba(model, X):
    model.eval()
    loader = DataLoader(TensorDataset(torch.from_numpy(X)), batch_size=512)
    out = []
    with torch.no_grad():
        for (xb,) in loader:
            out.append(model(xb.to(DEVICE)).softmax(1).cpu().numpy())
    return np.concatenate(out, axis=0)


def train_one(seed, Xtr, ytr, Xva, yva):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = CNN().to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    loss_fn = nn.CrossEntropyLoss()
    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(ytr)),
        batch_size=BATCH, shuffle=True,
    )
    val_loader = DataLoader(
        TensorDataset(torch.from_numpy(Xva), torch.from_numpy(yva)),
        batch_size=512,
    )
    best_acc, best_state = 0.0, None
    for epoch in range(EPOCHS):
        model.train()
        for xb, yb in train_loader:
            xb, yb = augment(xb).to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            loss_fn(model(xb), yb).backward()
            opt.step()
        sched.step()
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                correct += (model(xb).argmax(1) == yb).sum().item()
                total += yb.size(0)
        acc = correct / total
        print(f"  seed{seed} ep{epoch}: val={acc:.5f}", flush=True)
        if acc > best_acc:
            best_acc = acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return best_acc, model


def main():
    data = resolve_data()
    train = pd.read_csv(data / "train.csv")
    test = pd.read_csv(data / "test.csv")
    print(f"train={train.shape} test={test.shape} device={DEVICE}", flush=True)

    y = train["label"].to_numpy().astype(np.int64)
    X = train.drop(columns=["label"]).to_numpy().astype(np.float32).reshape(-1, 1, 28, 28) / 255.0
    X_test = test.to_numpy().astype(np.float32).reshape(-1, 1, 28, 28) / 255.0

    probs = np.zeros((len(X_test), 10), dtype=np.float64)
    accs = []
    for seed in SEEDS:
        Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.1, stratify=y, random_state=seed)
        acc, model = train_one(seed, Xtr, ytr, Xva, yva)
        accs.append(acc)
        # TTA: 5-view average (identity + 1px rolls)
        views = [X_test]
        for shift, dims in ((1, 3), (-1, 3), (1, 2), (-1, 2)):
            views.append(np.roll(X_test, shift, axis=dims))
        p = np.mean([predict_proba(model, v) for v in views], axis=0)
        probs += p
        print(f"seed {seed} best_val={acc:.5f}", flush=True)
        del model

    probs /= len(SEEDS)
    labels = probs.argmax(1)
    sub = pd.DataFrame({"ImageId": np.arange(1, len(labels) + 1), "Label": labels})
    out = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("./_out")
    out.mkdir(parents=True, exist_ok=True)
    sub.to_csv(out / "submission.csv", index=False)
    print(f"saved submission.csv accs={accs} mean={np.mean(accs):.5f}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
