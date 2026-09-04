# -*- coding: utf-8 -*-
"""
Smartphone Addiction (S6E8) v3：调参后 LGBM + 交互特征对比
============================================================
v2: LightGBM OOF AUC 0.9635 / 公开榜 0.96518。

v3 两步：
1. 参数来自 smartphone_tune.py：num_leaves=63, lr=0.05, min_child_samples=100
2. 同一 5 折、同一参数下对比【基础 13 特征】vs【13+3 交互特征】，
   交互特征（NaN 直接透传给 LGBM 原生处理）：
   - screen_notif   = 屏幕时间 × 通知数
   - entertain      = 社交时长 + 游戏时长
   - weekend_excess = 周末屏幕时间 - 平日屏幕时间
按 OOF AUC 选特征集，最终全量重训提交。
进度写入 smartphone_v3_progress.log，超时也能看到中间结果。

用法: ../../.venv/Scripts/python smartphone_v3.py
输出: submissions/submission_v3.csv
"""

import os
import sys
import time

import numpy as np
import pandas as pd
import lightgbm as lgb

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROGRESS_LOG = os.path.join(BASE_DIR, "smartphone_v3_progress.log")

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]
INTERACTIONS = ["screen_notif", "entertain", "weekend_excess"]

# 调参结果(smartphone_tune.py,15 万行子样本 2 折 OOF 最优)
LGB_PARAMS = {
    "objective": "binary", "metric": "auc", "learning_rate": 0.05,
    "num_leaves": 63, "min_child_samples": 100, "subsample": 0.9,
    "subsample_freq": 1, "colsample_bytree": 0.9, "verbosity": -1,
    "random_state": RANDOM_STATE, "num_threads": 0,
}


def make_features(df, interactions):
    """基础 13 特征(含 n_missing)+ 可选 3 个交互特征;类别转 category。"""
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    if interactions:
        X["screen_notif"] = X["daily_screen_time_hours"] * X["notifications_per_day"]
        X["entertain"] = X["social_media_hours"] + X["gaming_hours"]
        X["weekend_excess"] = X["weekend_screen_time"] - X["daily_screen_time_hours"]
    for c in CAT_COLS:
        X[c] = X[c].astype("category")
    return X


def log(msg):
    with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)


def lgb_oof(X, y, cv, params):
    """5 折 OOF;每折内部切 10% 做早停,外层折只评估。"""
    cat_idx = [X.columns.get_loc(c) for c in CAT_COLS]
    oof = np.zeros(len(y))
    for tr_idx, va_idx in cv.split(X, y):
        Xtr, Xes, ytr, yes = train_test_split(
            X.iloc[tr_idx], y[tr_idx], test_size=0.1,
            stratify=y[tr_idx], random_state=RANDOM_STATE)
        dtr = lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx)
        des = lgb.Dataset(Xes, yes, categorical_feature=cat_idx)
        m = lgb.train(params, dtr, num_boost_round=3000, valid_sets=[des],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        oof[va_idx] = m.predict(X.iloc[va_idx], num_iteration=m.best_iteration)
    return roc_auc_score(y, oof)


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    y = train["addicted_label"].values

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    t0 = time.time()
    log(f"v3 参数: {LGB_PARAMS}")

    # ---- 特征集对比(同一折、同一参数)----
    aucs = {}
    for name, use_inter in [("X13(基础)", False), ("X16(+3交互)", True)]:
        X = make_features(train.drop(columns=["id", "addicted_label"]), use_inter)
        auc = lgb_oof(X, y, cv, LGB_PARAMS)
        aucs[name] = auc
        log(f"{name}: OOF AUC {auc:.5f}  ({time.time() - t0:.0f}s)  特征 {X.shape[1]} 个")

    best_name = max(aucs, key=aucs.get)
    use_inter = "X16" in best_name
    log(f"选用特征集: {best_name}")

    # ---- 最终模型:全量重训(2% 早停保留)+ 预测 ----
    X = make_features(train.drop(columns=["id", "addicted_label"]), use_inter)
    X_test = make_features(test.drop(columns=["id"]), use_inter)
    cat_idx = [X.columns.get_loc(c) for c in CAT_COLS]
    Xtr, Xes, ytr, yes = train_test_split(X, y, test_size=0.02,
                                          stratify=y, random_state=RANDOM_STATE)
    final = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                      num_boost_round=3000,
                      valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
    log(f"最终模型树数: {final.best_iteration}  ({time.time() - t0:.0f}s)")
    y_prob = final.predict(X_test, num_iteration=final.best_iteration)

    submission = pd.DataFrame({"id": test["id"], "addicted_label": y_prob})
    out = os.path.join(BASE_DIR, "submissions", "submission_v3.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    log(f"提交文件已生成: {out}")
    log(f"预测概率: 均值 {y_prob.mean():.4f}  分位 [0.25/0.5/0.75] "
        f"{np.percentile(y_prob, [25, 50, 75]).round(4)}")
    align = (submission["id"].values == test["id"].values).all()
    log(f"行数: {len(submission)} (应为 {len(test)})  |  id 顺序与 test.csv 一致: {align}")


if __name__ == "__main__":
    main()
