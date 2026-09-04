# -*- coding: utf-8 -*-
"""
Smartphone Addiction (S6E8) v2：LightGBM + RF 对照与集成
==========================================================
v1 基线：RF CV AUC 0.9303 / 公开榜 0.93171。

v2 要点：
1. LightGBM 原生处理缺失值(NaN)与类别特征，不需要 impute / one-hot
2. 新增 n_missing 特征(每行缺失字段数)——公开高分解法提示该特征有信号
3. 早停不漏：每个外层折内部再切 10% 做早停验证，外层折只用于评估
4. RF(impute+OHE 流水线)对照，最后做概率平均集成，按 CV 选最佳

用法: ../../.venv/Scripts/python smartphone_v2.py
输出: submissions/submission_v2.csv
"""

import os
import sys
import time

import numpy as np
import pandas as pd
import lightgbm as lgb

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]

LGB_PARAMS = {
    "objective": "binary", "metric": "auc", "learning_rate": 0.05,
    "num_leaves": 63, "min_child_samples": 200, "subsample": 0.9,
    "subsample_freq": 1, "colsample_bytree": 0.9, "verbosity": -1,
    "random_state": RANDOM_STATE, "num_threads": 0,
}


def add_n_missing(df):
    """每行缺失字段数：合成数据的缺失本身可能携带信号。"""
    return df.assign(n_missing=df[NUM_COLS + CAT_COLS].isna().sum(axis=1))


def rf_pipe():
    """RF 用 impute + OHE 流水线（与 v1 一致）。"""
    return Pipeline([
        ("ct", ColumnTransformer([
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                              ("sc", StandardScaler())]), NUM_COLS + ["n_missing"]),
            ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                              ("ohe", OneHotEncoder(handle_unknown="ignore"))]), CAT_COLS),
        ])),
        ("clf", RandomForestClassifier(
            n_estimators=150, max_depth=8, min_samples_leaf=5,
            random_state=RANDOM_STATE, n_jobs=-1,
        )),
    ])


def lgb_oof(X, y, cv):
    """LightGBM 手工 5 折 OOF：每折内部再切 10% 做早停，外层折只评估。"""
    cat_idx = [X.columns.get_loc(c) for c in CAT_COLS]
    oof = np.zeros(len(y))
    t0 = time.time()
    for i, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
        Xtr, Xes, ytr, yes = train_test_split(
            X.iloc[tr_idx], y[tr_idx], test_size=0.1,
            stratify=y[tr_idx], random_state=RANDOM_STATE)
        dtr = lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx)
        des = lgb.Dataset(Xes, yes, categorical_feature=cat_idx)
        m = lgb.train(LGB_PARAMS, dtr, num_boost_round=3000, valid_sets=[des],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        oof[va_idx] = m.predict(X.iloc[va_idx], num_iteration=m.best_iteration)
        print(f"  折{i + 1}: 树数 {m.best_iteration}, 耗时 {time.time() - t0:.0f}s", flush=True)
    return oof


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    y = train["addicted_label"].values

    X = add_n_missing(train.drop(columns=["id", "addicted_label"]))
    X_test = add_n_missing(test.drop(columns=["id"]))
    for c in CAT_COLS:  # 类别 -> pandas category（NaN 自动编码为 -1，LGBM 视为缺失类别）
        X[c] = X[c].astype("category")
        X_test[c] = X_test[c].astype("category")
    print(f"特征: {list(X.columns)}  ({X.shape[1]} 个)")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    print("\n===== 5 折 CV(AUC)=====")
    # RF 对照（cross_val_predict 拿 OOF 概率）
    t0 = time.time()
    rf_oof = cross_val_predict(rf_pipe(), X, y, cv=cv, method="predict_proba", n_jobs=1)[:, 1]
    rf_auc = roc_auc_score(y, rf_oof)
    print(f"RandomForest   OOF AUC: {rf_auc:.4f}   ({time.time() - t0:.0f}s)")

    # LightGBM（原生缺失 + 类别 + 早停）
    print("LightGBM       OOF 训练中(5 折早停)...")
    lgb_oof_probs = lgb_oof(X, y, cv)
    lgb_auc = roc_auc_score(y, lgb_oof_probs)
    print(f"LightGBM       OOF AUC: {lgb_auc:.4f}")

    # 集成：概率平均
    blend_oof = (rf_oof + lgb_oof_probs) / 2
    blend_auc = roc_auc_score(y, blend_oof)
    print(f"Blend(RF+LGB)  OOF AUC: {blend_auc:.4f}")

    # ---- 选最佳做最终提交 ----
    results = {"RF": rf_auc, "LightGBM": lgb_auc, "Blend": blend_auc}
    best_name = max(results, key=results.get)
    print(f"\n选用: {best_name} (AUC {results[best_name]:.4f})")

    if best_name == "LightGBM":
        cat_idx = [X.columns.get_loc(c) for c in CAT_COLS]
        Xtr, Xes, ytr, yes = train_test_split(
            X, y, test_size=0.02, stratify=y, random_state=RANDOM_STATE)
        final = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                          num_boost_round=3000,
                          valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                          callbacks=[lgb.early_stopping(100, verbose=False)])
        y_prob = final.predict(X_test, num_iteration=final.best_iteration)
    elif best_name == "RF":
        final = rf_pipe().fit(X, y)
        y_prob = final.predict_proba(X_test)[:, 1]
    else:  # Blend：两个模型都重训全量再平均
        final_rf = rf_pipe().fit(X, y)
        cat_idx = [X.columns.get_loc(c) for c in CAT_COLS]
        Xtr, Xes, ytr, yes = train_test_split(
            X, y, test_size=0.02, stratify=y, random_state=RANDOM_STATE)
        final_lgb = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                              num_boost_round=3000,
                              valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                              callbacks=[lgb.early_stopping(100, verbose=False)])
        y_prob = (final_rf.predict_proba(X_test)[:, 1]
                  + final_lgb.predict(X_test, num_iteration=final_lgb.best_iteration)) / 2

    submission = pd.DataFrame({"id": test["id"], "addicted_label": y_prob})
    out = os.path.join(BASE_DIR, "submissions", "submission_v2.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"\n提交文件已生成: {out}")
    print(f"预测概率: 均值 {y_prob.mean():.4f}  分位 [0.25/0.5/0.75] "
          f"{np.percentile(y_prob, [25, 50, 75]).round(4)}")
    align = (submission["id"].values == test["id"].values).all()
    print(f"行数: {len(submission)} (应为 {len(test)})  |  id 顺序与 test.csv 一致: {align}")


if __name__ == "__main__":
    main()
