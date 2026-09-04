# -*- coding: utf-8 -*-
"""
Smartphone Addiction (Playground S6E8) 基线脚本
================================================
二分类:预测手机成瘾(addicted_label),评分指标 AUC。

沿用 Titanic 项目的方法论:
1. 对照线:单特征 AUC + 随机 0.5,模型 CV 必须显著高于对照线才有意义
2. 特征工程:数值列中位数填充 + 标准化,类别列众数填充 + one-hot
   (缺失值全部只从训练集学习,测试集套用)
3. 评估:StratifiedKFold 5 折,LR / RF 对比

用法: ../../.venv/Scripts/python smartphone_baseline.py
输出: submissions/submission_baseline.csv (概率,适配 AUC 评分)
"""

import os
import sys

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]


def make_pipe(model):
    """数值/类别统一预处理 + 模型。所有填充值只在训练集上拟合。"""
    return Pipeline([
        ("ct", ColumnTransformer([
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                              ("sc", StandardScaler())]), NUM_COLS),
            ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                              ("ohe", OneHotEncoder(handle_unknown="ignore"))]), CAT_COLS),
        ])),
        ("clf", model),
    ])


def univariate_auc(train, y):
    """对照线:单特征(中位数填充后)与目标的 AUC,不经过任何模型拟合。"""
    best_col, best_auc = None, 0.0
    for col in NUM_COLS:
        s = train[col].fillna(train[col].median())
        auc = roc_auc_score(y, s)
        if auc > best_auc:
            best_col, best_auc = col, auc
    return best_col, best_auc


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
    print("[目标分布]")
    print(train["addicted_label"].value_counts(normalize=True).round(4))
    print("\n[缺失值占比(前 10)]")
    miss = train.isnull().mean().sort_values(ascending=False)
    print(miss.head(10).round(3).to_string())

    y = train["addicted_label"].values
    best_col, best_auc = univariate_auc(train, y)
    print(f"\n[对照线] 单特征 AUC 最高: {best_col} = {best_auc:.4f}  (随机=0.5)")

    # ---- 模型对比:LR vs RF,5 折 StratifiedKFold ----
    print("\n===== 5 折 CV(AUC)=====")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(
            n_estimators=150, max_depth=8, min_samples_leaf=5,
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }
    results = {}
    for name, model in models.items():
        pipe = make_pipe(model)
        scores = cross_val_score(pipe, train.drop(columns=["id", "addicted_label"]), y,
                                 cv=cv, scoring="roc_auc", n_jobs=1)
        results[name] = scores
        lift = scores.mean() - best_auc
        print(f"{name:20s} AUC: {scores.mean():.4f} ± {scores.std():.4f}   相对单特征对照: {lift:+.4f}")

    best_name = max(results, key=lambda k: results[k].mean())
    print(f"\n选用: {best_name}")

    # ---- 最终模型:全量重训 + 预测测试集概率 ----
    final = make_pipe(models[best_name])
    final.fit(train.drop(columns=["id", "addicted_label"]), y)
    y_prob = final.predict_proba(test.drop(columns=["id"]))[:, 1]

    submission = pd.DataFrame({"id": test["id"], "addicted_label": y_prob})
    out = os.path.join(BASE_DIR, "submissions", "submission_baseline.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"\n提交文件已生成: {out}")
    print(f"预测概率分布: 均值 {y_prob.mean():.4f}  分位 [0.25/0.5/0.75] "
          f"{np.percentile(y_prob, [25, 50, 75]).round(4)}")

    # 健康检查:行数、id 顺序与测试集一致
    align = (submission["id"].values == test["id"].values).all()
    print(f"行数: {len(submission)} (应为 {len(test)})  |  id 顺序与 test.csv 一致: {align}")


if __name__ == "__main__":
    main()
