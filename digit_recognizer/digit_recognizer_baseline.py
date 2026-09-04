# -*- coding: utf-8 -*-
"""
Digit Recognizer (MNIST) 基线脚本
==================================
10 分类(手写数字 0-9),评分指标 Accuracy。
第一次接触图像数据:784 个像素 = 28x28 灰度图(0-255)。

基线对比三种经典做法(3 折 CV,控制运行时间):
1. RandomForest:直接吃原始像素(树模型不需要缩放)
2. PCA(60) + LogisticRegression:归一化 + 降维 + 线性模型(教学点:归一化与 PCA)
3. MLP:归一化 + 单隐藏层神经网络(sklearn 版,为将来上 torch 铺路)

最优模型全量重训 → 提交。
用法: conda activate kaggle 后: python digit_recognizer_baseline.py
输出: submissions/submission_baseline.csv (ImageId, Label)
"""

import os
import sys
import time

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def cv_eval(name, pipe, X, y, cv):
    scores = []
    t0 = time.time()
    for k, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
        pipe.fit(X[tr_idx], y[tr_idx])
        scores.append(accuracy_score(y[va_idx], pipe.predict(X[va_idx])))
        print(f"  {name} 折{k}: {scores[-1]:.4f} ({time.time() - t0:.0f}s)", flush=True)
    return float(np.mean(scores))


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    print(f"训练集: {train.shape}  测试集: {test.shape}")

    print("\n===== EDA =====")
    print(f"标签分布: {train['label'].value_counts().sort_index().to_dict()}")
    y = train["label"].values
    X = train.drop(columns=["label"]).values / 255.0  # 像素归一化到 [0,1]
    X_test = test.values / 255.0
    print(f"像素范围(归一化后): {X.min():.3f} - {X.max():.3f} | 缺失: {np.isnan(X).sum()}")

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "RandomForest": Pipeline([("clf", RandomForestClassifier(
            n_estimators=100, max_depth=16, n_jobs=-1, random_state=RANDOM_STATE))]),
        "PCA+LR": Pipeline([("pca", PCA(n_components=60, svd_solver="randomized",
                                        random_state=RANDOM_STATE)),
                            ("clf", LogisticRegression(max_iter=300, random_state=RANDOM_STATE))]),
        "MLP": Pipeline([("sc", StandardScaler()),
                         ("clf", MLPClassifier(hidden_layer_sizes=(128,), max_iter=25,
                                               early_stopping=True, n_iter_no_change=5,
                                               batch_size=2048, random_state=RANDOM_STATE))]),
    }
    print("\n===== 3 折 CV(Accuracy)=====")
    results = {}
    for name, pipe in models.items():
        results[name] = cv_eval(name, pipe, X, y, cv)
        print(f"{name:15s} CV: {results[name]:.4f}", flush=True)

    best_name = max(results, key=results.get)
    print(f"\n选用: {best_name} ({results[best_name]:.4f})")

    final = models[best_name].fit(X, y)
    y_pred = final.predict(X_test)
    submission = pd.DataFrame({"ImageId": np.arange(1, len(X_test) + 1), "Label": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_baseline.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"\n提交文件已生成: {out}")
    print(f"行数: {len(submission)} (应为 {len(X_test)}) | 预测分布: {np.bincount(y_pred)}")


if __name__ == "__main__":
    main()
