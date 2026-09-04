# -*- coding: utf-8 -*-
"""
Smartphone Addiction (S6E8) v4：LGBM + XGBoost + CatBoost 异构集成
====================================================================
思路:三个不同库的梯度提升模型(不同归纳偏置),5 折 OOF 后做权重搜索混合。

关键设计——可断点续跑:
- 每个模型每折的验证/测试预测都单独存 npy(oof/ 目录),超时后重跑自动跳过已完成部分
- 全部折完成后汇总 OOF 与测试预测,写 .done 标记
- 三个模型都完成后做权重网格搜索(0.1 步长,单纯形),生成最终提交
- 若 CatBoost 未完成,退化为 LGBM+XGB 两模型混合(会在输出里说明)

特征:与 v2 相同的 13 特征(含 n_missing)。
- LGBM/XGB:category dtype(NaN 原生处理)
- CatBoost:类别列 NaN -> "MISSING" 字符串(其要求类别必须可哈希字符串)

用法: conda activate kaggle 后: python smartphone_v4.py
输出: submissions/submission_v4.csv(概率,适配 AUC 评分)
"""

import os
import sys
import time
from itertools import product

import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OOF_DIR = os.path.join(BASE_DIR, "oof")
N_FOLDS = 5

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]

LGB_PARAMS = {
    "objective": "binary", "metric": "auc", "learning_rate": 0.05,
    "num_leaves": 63, "min_child_samples": 100, "subsample": 0.9,
    "subsample_freq": 1, "colsample_bytree": 0.9, "verbosity": -1,
    "random_state": RANDOM_STATE, "num_threads": 0,
}
XGB_PARAMS = {
    "n_estimators": 3000, "max_depth": 6, "learning_rate": 0.05,
    "tree_method": "hist", "n_jobs": -1, "enable_categorical": True,
    "eval_metric": "auc", "random_state": RANDOM_STATE,
}
CAT_PARAMS = {
    "iterations": 1500, "depth": 6, "learning_rate": 0.05,
    "loss_function": "Logloss", "eval_metric": "AUC",
    "bootstrap_type": "Bernoulli", "subsample": 0.7,
    "thread_count": -1, "verbose": 0, "random_seed": RANDOM_STATE,
    "allow_writing_files": False,
}


def prep_lgb_xgb(df, cats):
    """LGBM/XGB 用:category dtype,NaN 保留;测试集类别与训练集对齐(未见类别->NaN)。"""
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    for c in CAT_COLS:
        X[c] = X[c].astype("category")
        if cats is not None:
            X[c] = X[c].cat.set_categories(cats[c])
    return X


def prep_cat(df):
    """CatBoost 用:类别列 NaN -> 'MISSING' 字符串,其余 NaN 保留(原生处理)。"""
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    for c in CAT_COLS:
        X[c] = X[c].fillna("MISSING").astype(str)
    return X


def fold_train(name, Xtr, Xes, ytr, yes, Xva, Xtest):
    """训练单折模型(内层 10% 早停),返回验证/测试概率。"""
    if name == "lgb":
        cat_idx = [Xtr.columns.get_loc(c) for c in CAT_COLS]
        m = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                      num_boost_round=3000,
                      valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        return (m.predict(Xva, num_iteration=m.best_iteration),
                m.predict(Xtest, num_iteration=m.best_iteration))
    if name == "xgb":
        m = xgb.XGBClassifier(**XGB_PARAMS)
        m.fit(Xtr, ytr, eval_set=[(Xes, yes)], verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]
    if name == "cat":
        cat_idx = [Xtr.columns.get_loc(c) for c in CAT_COLS]
        m = cb.CatBoostClassifier(**CAT_PARAMS)
        m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]


def run_model(name, X, y, X_test):
    """逐折训练并保存;已完成(有 .done)则跳过。返回是否可用。"""
    done = os.path.join(OOF_DIR, name + ".done")
    if os.path.exists(done):
        print(f"{name}: 已有完成标记,跳过", flush=True)
        return True
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    t0 = time.time()
    for k, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
        fp_va, fp_test = (os.path.join(OOF_DIR, f"{name}_f{k}_va_pred.npy"),
                          os.path.join(OOF_DIR, f"{name}_f{k}_test.npy"))
        if os.path.exists(fp_va):
            print(f"  {name} 折{k}: 已存在,跳过", flush=True)
            continue
        Xtr, Xes, ytr, yes = train_test_split(
            X.iloc[tr_idx], y[tr_idx], test_size=0.1,
            stratify=y[tr_idx], random_state=RANDOM_STATE)
        va_pred, test_pred = fold_train(name, Xtr, Xes, ytr, yes, X.iloc[va_idx], X_test)
        np.save(os.path.join(OOF_DIR, f"{name}_f{k}_va_idx.npy"), va_idx)
        np.save(fp_va, va_pred)
        np.save(fp_test, test_pred)
        print(f"  {name} 折{k}: 完成 ({time.time() - t0:.0f}s)", flush=True)
    # 汇总
    oof = np.zeros(len(y))
    test_sum = np.zeros(len(X_test))
    for k in range(N_FOLDS):
        va_idx = np.load(os.path.join(OOF_DIR, f"{name}_f{k}_va_idx.npy"))
        oof[va_idx] = np.load(os.path.join(OOF_DIR, f"{name}_f{k}_va_pred.npy"))
        test_sum += np.load(os.path.join(OOF_DIR, f"{name}_f{k}_test.npy"))
    np.save(os.path.join(OOF_DIR, f"{name}_oof.npy"), oof)
    np.save(os.path.join(OOF_DIR, f"{name}_test.npy"), test_sum / N_FOLDS)
    with open(done, "w") as f:
        f.write("done")
    print(f"{name} 全部折完成, OOF AUC: {roc_auc_score(y, oof):.5f} ({time.time() - t0:.0f}s)", flush=True)
    return True


def weight_search(names, oofs, y):
    """0.1 步长网格搜索混合权重(权重必须归一),最大化 OOF AUC。"""
    best_w, best_auc = None, -1.0
    n = len(names)
    grid = np.arange(0, 1.0001, 0.1)
    for w1 in grid:
        for w2 in (grid if n >= 3 else [0.0]):
            ws = [w1, w2, 1 - w1 - w2][:n] if n >= 3 else [w1, 1 - w1]
            if any(w < -1e-9 for w in ws):
                continue
            blend = sum(wi * o for wi, o in zip(ws, oofs))
            auc = roc_auc_score(y, blend)
            if auc > best_auc:
                best_auc, best_w = auc, ws
    return best_w, best_auc


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")
    os.makedirs(OOF_DIR, exist_ok=True)

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    y = train["addicted_label"].values

    # 类别编码统一:以训练集为准,测试集对齐
    train_raw = train.drop(columns=["id", "addicted_label"])
    cats = {}
    for c in CAT_COLS:
        cats[c] = pd.Categorical(train_raw[c]).categories

    X_lgb = prep_lgb_xgb(train_raw, None)
    X_test_lgb = prep_lgb_xgb(test.drop(columns=["id"]), cats)
    X_cat = prep_cat(train_raw)
    X_test_cat = prep_cat(test.drop(columns=["id"]))
    print(f"特征 {X_lgb.shape[1]} 个,训练 {len(y)} 行,测试 {len(X_test_lgb)} 行")

    def write_submission(names):
        """把当前可用模型的 OOF 权重混合写盘;CatBoost 未完成时就是临时版。"""
        oofs = [np.load(os.path.join(OOF_DIR, f"{n}_oof.npy")) for n in names]
        tests = [np.load(os.path.join(OOF_DIR, f"{n}_test.npy")) for n in names]
        w, blend_auc = weight_search(names, oofs, y)
        y_prob = sum(wi * t for wi, t in zip(w, tests))
        submission = pd.DataFrame({"id": test["id"], "addicted_label": y_prob})
        out = os.path.join(BASE_DIR, "submissions", "submission_v4.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        submission.to_csv(out, index=False)
        print(f"\n===== 混合({' + '.join(names)}) =====", flush=True)
        for n, o in zip(names, oofs):
            print(f"  {n:4s} OOF AUC: {roc_auc_score(y, o):.5f}")
        print(f"  权重: {dict(zip(names, [round(x, 2) for x in w]))}  混合 OOF AUC: {blend_auc:.5f}", flush=True)
        print(f"提交文件已生成: {out}", flush=True)
        print(f"预测概率: 均值 {y_prob.mean():.4f}  分位 {np.percentile(y_prob, [25, 50, 75]).round(4)}", flush=True)
        align = (submission["id"].values == test["id"].values).all()
        print(f"行数: {len(submission)} (应为 {len(test)})  |  id 顺序一致: {align}", flush=True)

    avail = []
    for name, X, Xt in [("lgb", X_lgb, X_test_lgb),
                        ("xgb", X_lgb, X_test_lgb),
                        ("cat", X_cat, X_test_cat)]:
        if run_model(name, X, y, Xt):
            avail.append(name)
            if len(avail) >= 2:
                write_submission(avail)  # 每完成一个模型就刷新提交文件,防超时丢失
    if len(avail) >= 2:
        write_submission(avail)  # 全部完成后的最终覆盖(与最后一次相同,保险)
    else:
        print(f"\n可用模型不足({avail}),继续重跑本脚本即可续算。")


if __name__ == "__main__":
    main()
