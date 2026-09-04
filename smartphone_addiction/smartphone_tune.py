# -*- coding: utf-8 -*-
"""
S6E8 LGBM 调参脚本
==================
在 20 万行分层子样本上做 3 折 OOF,扫描 num_leaves / learning_rate /
min_child_samples(早停在每折内部 10% 上进行,不外泄)。

两步走:先扫 num_leaves × lr(固定 min_child_samples=200),
再在最优组合上扫 min_child_samples。最终输出最优参数供 smartphone_v3.py 使用。

用法: ../../.venv/Scripts/python smartphone_tune.py
"""

import time
from itertools import product

import numpy as np
import pandas as pd
import lightgbm as lgb

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

RANDOM_STATE = 42
BASE_DIR = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
DATA_DIR = __import__("os").path.join(BASE_DIR, "data")

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]

LGB_BASE = {
    "objective": "binary", "metric": "auc", "subsample": 0.9,
    "subsample_freq": 1, "colsample_bytree": 0.9, "verbosity": -1,
    "random_state": RANDOM_STATE, "num_threads": 0,
}


def add_n_missing(df):
    return df.assign(n_missing=df[NUM_COLS + CAT_COLS].isna().sum(axis=1))


def lgb_oof(X, y, cv, params):
    """3 折 OOF;每折内部切 10% 做早停,外层折只评估。"""
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
    import os
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    y_all = train["addicted_label"].values
    X_all = add_n_missing(train.drop(columns=["id", "addicted_label"]))
    for c in CAT_COLS:
        X_all[c] = X_all[c].astype("category")

    # 15 万行分层子样本
    _, idx = train_test_split(np.arange(len(y_all)), test_size=150000,
                              stratify=y_all, random_state=RANDOM_STATE)
    X, y = X_all.iloc[idx], y_all[idx]
    print(f"子样本: {X.shape}  目标正例占比: {y.mean():.3f}")

    cv = StratifiedKFold(n_splits=2, shuffle=True, random_state=RANDOM_STATE)
    t0 = time.time()

    print("\n===== 第 1 轮:num_leaves × learning_rate(min_child_samples=200)=====")
    best, best_auc = None, 0.0
    for nl, lr in product([63, 127], [0.05, 0.1]):
        p = dict(LGB_BASE, num_leaves=nl, learning_rate=lr, min_child_samples=200)
        auc = lgb_oof(X, y, cv, p)
        print(f"  num_leaves={nl:3d} lr={lr:.2f}  -> OOF AUC {auc:.5f}  ({time.time() - t0:.0f}s)", flush=True)
        if auc > best_auc:
            best, best_auc = (nl, lr), auc

    print(f"\n===== 第 2 轮:min_child_samples(最优 nl/lr = {best})=====")
    best_mcs, best_mcs_auc = 200, best_auc
    for mcs in [100, 400]:
        p = dict(LGB_BASE, num_leaves=best[0], learning_rate=best[1], min_child_samples=mcs)
        auc = lgb_oof(X, y, cv, p)
        print(f"  min_child_samples={mcs:3d} -> OOF AUC {auc:.5f}  ({time.time() - t0:.0f}s)", flush=True)
        if auc > best_mcs_auc:
            best_mcs, best_mcs_auc = mcs, auc

    final = dict(LGB_BASE, num_leaves=best[0], learning_rate=best[1], min_child_samples=best_mcs)
    print(f"\n===== 最优参数 =====")
    print(f"num_leaves={best[0]}, learning_rate={best[1]}, min_child_samples={best_mcs}, "
          f"OOF AUC {best_mcs_auc:.5f}")
    print(f"总耗时 {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
