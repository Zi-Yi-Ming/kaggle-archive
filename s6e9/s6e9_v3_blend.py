# -*- coding: utf-8 -*-
"""S6E9 v3：特征工程 + LGB/XGB/Cat 多种子混合（可断点续跑）。

在 s6e9_template.py 骨架上补交互特征、目标编码（折内）与多种子平均。
每模型/种子的 OOF 与 test 预测落盘，中断后可续跑。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

import catboost as cb
import lightgbm as lgb
import xgboost as xgb

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "_out"
SUB_DIR = ROOT / "submissions"

CAT_COLS = [
    "Gender", "City_Type", "Current_Car_Type",
    "Home_Charging_Possible", "Subsidy_Available", "Range_Anxiety_Level",
]
NUM_COLS = [
    "Age", "Annual_Income_USD", "Daily_Commute_km", "Number_of_Cars_Owned",
    "Charging_Stations_Near_Home", "Charging_Stations_Near_Work",
    "Environmental_Concern_Level",
]
TARGET = "Will_Buy_EV"
ID = "id"


def load_xy():
    train = pd.read_csv(DATA / "train.csv")
    test = pd.read_csv(DATA / "test.csv")
    y = (train[TARGET] == "Yes").astype(int).to_numpy()
    return train, test, y


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    X = df.drop(columns=[c for c in (ID, TARGET) if c in df.columns]).copy()
    X["n_missing"] = X.isna().sum(axis=1)

    # 数值交互 / 比值（合成表上常有稳定增益）
    X["income_per_age"] = X["Annual_Income_USD"] / (X["Age"] + 1)
    X["charge_sum"] = (
        X["Charging_Stations_Near_Home"].fillna(0)
        + X["Charging_Stations_Near_Work"].fillna(0)
    )
    X["charge_diff"] = (
        X["Charging_Stations_Near_Work"].fillna(0)
        - X["Charging_Stations_Near_Home"].fillna(0)
    )
    X["commute_per_car"] = X["Daily_Commute_km"] / (X["Number_of_Cars_Owned"] + 1)
    X["income_x_env"] = X["Annual_Income_USD"] * X["Environmental_Concern_Level"]
    X["age_x_env"] = X["Age"] * X["Environmental_Concern_Level"]
    X["cars_x_charge"] = X["Number_of_Cars_Owned"] * (X["charge_sum"] + 1)

    # 低基数组合特征
    X["home_sub"] = (
        X["Home_Charging_Possible"].astype(str) + "_"
        + X["Subsidy_Available"].astype(str)
    )
    X["city_car"] = (
        X["City_Type"].astype(str) + "_" + X["Current_Car_Type"].astype(str)
    )
    X["range_home"] = (
        X["Range_Anxiety_Level"].astype(str) + "_"
        + X["Home_Charging_Possible"].astype(str)
    )
    return X


def target_encode_fold(Xtr, ytr, Xva, cols, smoothing=20.0):
    """折内目标编码，避免泄漏。ytr 为与 Xtr 对齐的 0/1 数组。"""
    ytr = np.asarray(ytr).astype(float)
    global_mean = float(ytr.mean())
    Xtr = Xtr.copy()
    Xva = Xva.copy()
    ys = pd.Series(ytr, index=Xtr.index)
    for c in cols:
        if c not in Xtr.columns:
            continue
        stats = ys.groupby(Xtr[c]).agg(["sum", "count"])
        enc = (stats["sum"] + smoothing * global_mean) / (stats["count"] + smoothing)
        name = f"te_{c}"
        Xtr[name] = Xtr[c].map(enc).astype(float)
        Xva[name] = Xva[c].map(enc).astype(float).fillna(global_mean)
    return Xtr, Xva


def prep_model_frame(X, cats, te_cols, fit_y=None, te_map=None):
    """返回 (数值可用帧, cat 列名列表)。te_map 非空时用已有映射。"""
    X = X.copy()
    cat_names = []
    for c in list(X.columns):
        if c in te_cols:
            continue
        if c in cats or not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype(str).fillna("MISSING")
            cat_names.append(c)
        else:
            X[c] = X[c].astype(float)
    return X, cat_names


def train_one(model, Xtr, ytr, Xes, yes, Xva, Xte, cat_names, seed):
    if model == "lgb":
        params = dict(
            objective="binary", metric="auc", learning_rate=0.03,
            num_leaves=63, min_child_samples=80, feature_fraction=0.85,
            bagging_fraction=0.85, bagging_freq=1, n_jobs=-1,
            verbosity=-1, seed=seed, deterministic=False,
        )
        cat_idx = [Xtr.columns.get_loc(c) for c in cat_names]
        for c in cat_names:
            Xtr[c] = Xtr[c].astype("category")
            Xes[c] = Xes[c].astype("category")
            Xva[c] = Xva[c].astype("category")
            Xte[c] = Xte[c].astype("category")
        m = lgb.train(
            params, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
            num_boost_round=2500,
            valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
            callbacks=[lgb.early_stopping(80, verbose=False)],
        )
        it = m.best_iteration or 2500
        return m.predict(Xva, num_iteration=it), m.predict(Xte, num_iteration=it)

    if model == "xgb":
        # XGB 用整数编码类别，避免 category 索引问题
        frames = []
        cats_int = {}
        for name in cat_names:
            cats_int[name] = {
                v: i for i, v in enumerate(
                    sorted(set(Xtr[name].unique()) | set(Xte[name].unique()))
                )
            }
        def enc(df):
            d = df.copy()
            for name in cat_names:
                d[name] = d[name].map(cats_int[name]).fillna(-1).astype(int)
            return d
        Xtr, Xes, Xva, Xte = enc(Xtr), enc(Xes), enc(Xva), enc(Xte)
        m = xgb.XGBClassifier(
            objective="binary:logistic", eval_metric="auc",
            learning_rate=0.03, max_depth=6, n_estimators=2500,
            subsample=0.85, colsample_bytree=0.85, n_jobs=-1,
            random_state=seed, tree_method="hist",
        )
        m.fit(Xtr, ytr, eval_set=[(Xes, yes)], verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xte)[:, 1]

    if model == "cat":
        cat_idx = [Xtr.columns.get_loc(c) for c in cat_names]
        m = cb.CatBoostClassifier(
            loss_function="Logloss", eval_metric="AUC",
            learning_rate=0.03, depth=8, iterations=2500,
            random_seed=seed, verbose=False, task_type="CPU",
            early_stopping_rounds=80,
        )
        m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xte)[:, 1]

    raise ValueError(model)


def run_model_seed(model, seed, train_raw, y, test_raw, n_folds=5):
    key = f"{model}_s{seed}"
    oof_path = OUT / f"oof_{key}.npy"
    test_path = OUT / f"test_{key}.npy"
    meta_path = OUT / f"meta_{key}.json"
    if oof_path.exists() and test_path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"[skip] {key} 已有 OOF AUC={meta.get('auc')}", flush=True)
        return np.load(oof_path), np.load(test_path), float(meta.get("auc", np.nan))

    oof = np.zeros(len(y), dtype=np.float64)
    test_sum = np.zeros(len(test_raw), dtype=np.float64)
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)

    te_cols = [f"te_{c}" for c in CAT_COLS]
    X_all = add_features(pd.concat([train_raw, test_raw], ignore_index=True))
    n_tr = len(train_raw)
    X_tr_all = X_all.iloc[:n_tr].drop(columns=[ID, TARGET], errors="ignore")
    X_te_all = X_all.iloc[n_tr:].drop(columns=[ID, TARGET], errors="ignore")

    for k, (tr_idx, va_idx) in enumerate(cv.split(X_tr_all, y)):
        _, es_idx = train_test_split(
            tr_idx, test_size=0.1, stratify=y[tr_idx], random_state=seed
        )
        X_tr_raw = X_tr_all.iloc[tr_idx]
        X_va_raw = X_tr_all.iloc[va_idx]
        X_es_raw = X_tr_all.iloc[es_idx]
        X_te_raw = X_te_all

        # 折内目标编码：返回 (训练集, 编码集)，第二份才是要喂模型的
        X_tr_te, X_va_te = target_encode_fold(X_tr_raw, y[tr_idx], X_va_raw, CAT_COLS)
        _, X_es_te = target_encode_fold(X_tr_raw, y[tr_idx], X_es_raw, CAT_COLS)
        _, X_te_te = target_encode_fold(X_tr_raw, y[tr_idx], X_te_raw, CAT_COLS)

        cats = CAT_COLS
        Xtr, cn = prep_model_frame(X_tr_te, cats, te_cols)
        Xva, _ = prep_model_frame(X_va_te, cats, te_cols)
        Xes, _ = prep_model_frame(X_es_te, cats, te_cols)
        Xte, _ = prep_model_frame(X_te_te, cats, te_cols)

        va_p, te_p = train_one(model, Xtr, y[tr_idx], Xes, y[es_idx], Xva, Xte, cn, seed)
        oof[va_idx] = va_p
        test_sum += te_p
        print(f"[{key}] fold{k} done", flush=True)

    test_pred = test_sum / n_folds
    auc = float(roc_auc_score(y, oof))
    np.save(oof_path, oof)
    np.save(test_path, test_pred)
    meta_path.write_text(json.dumps({"model": model, "seed": seed, "auc": auc}), encoding="utf-8")
    print(f"[{key}] OOF AUC={auc:.5f}  saved", flush=True)
    return oof, test_pred, auc


def weight_search(oofs, y):
    names = list(oofs)
    mats = [oofs[n] for n in names]
    best_w, best_v = None, -1.0
    grid = np.arange(0, 1.0001, 0.1)
    n = len(names)
    if n == 1:
        v = roc_auc_score(y, mats[0])
        return {names[0]: 1.0}, v
    if n == 2:
        for w1 in grid:
            ws = [w1, 1 - w1]
            blend = sum(w * m for w, m in zip(ws, mats))
            v = roc_auc_score(y, blend)
            if v > best_v:
                best_v, best_w = v, ws
        return {k: float(w) for k, w in zip(names, best_w)}, best_v
    # 3+ 用坐标下降粗搜（0.1 网格）
    w = np.ones(n) / n
    for _ in range(4):
        for i in range(n):
            local_best, local_w = -1, w[i]
            for t in grid:
                cand = w.copy()
                # 保持其它权重比例
                rest = 1 - w[i]
                if rest < 1e-9:
                    cand[i] = t
                    others = (1 - t) / max(n - 1, 1)
                    for j in range(n):
                        if j != i:
                            cand[j] = others
                else:
                    scale = (1 - t) / rest
                    cand[i] = t
                    for j in range(n):
                        if j != i:
                            cand[j] = w[j] * scale
                blend = sum(c * m for c, m in zip(cand, mats))
                v = roc_auc_score(y, blend)
                if v > local_best:
                    local_best, local_w = v, t
            # apply
            rest = 1 - w[i]
            if rest < 1e-9:
                w[i] = local_w
                others = (1 - local_w) / max(n - 1, 1)
                for j in range(n):
                    if j != i:
                        w[j] = others
            else:
                scale = (1 - local_w) / rest
                w[i] = local_w
                for j in range(n):
                    if j != i:
                        w[j] = w[j] * scale
            best_v = local_best
    best_v = roc_auc_score(y, sum(wi * m for wi, m in zip(w, mats)))
    return {k: float(wi) for k, wi in zip(names, w)}, best_v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="lgb,xgb,cat")
    ap.add_argument("--seeds", default="42,7")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--tag", default="v3")
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    SUB_DIR.mkdir(exist_ok=True)

    train, test, y = load_xy()
    print(f"train={train.shape} test={test.shape} pos={y.mean():.4f}", flush=True)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]

    oofs, tests = {}, {}
    for model in models:
        for seed in seeds:
            oof, te, auc = run_model_seed(model, seed, train, y, test, n_folds=args.folds)
            oofs[f"{model}_s{seed}"] = oof
            tests[f"{model}_s{seed}"] = te

    weights, blend_auc = weight_search(oofs, y)
    print("weights:", {k: round(v, 3) for k, v in weights.items()})
    print(f"blend OOF AUC={blend_auc:.5f}", flush=True)

    y_prob = sum(weights[k] * tests[k] for k in weights)
    sub = pd.DataFrame({ID: test[ID], TARGET: y_prob})
    out_csv = SUB_DIR / f"submission_{args.tag}_blend.csv"
    sub.to_csv(out_csv, index=False)
    (OUT / f"blend_{args.tag}.json").write_text(
        json.dumps({"weights": weights, "oof_auc": blend_auc}, indent=2),
        encoding="utf-8",
    )
    print(f"saved {out_csv}  mean={y_prob.mean():.4f}")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
