# -*- coding: utf-8 -*-
"""S6E9 v3 blend on Kaggle: FE + LGB/XGB/Cat multi-seed, writes /kaggle/working/submission.csv.

Run as a competition kernel (playground-series-s6e9). GPU optional for Cat/XGB.
"""
from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

import catboost as cb
import lightgbm as lgb
import xgboost as xgb

warnings.filterwarnings("ignore")

COMP = "playground-series-s6e9"


def resolve_data():
    roots = [Path("/kaggle/input")]
    # local fallback for debugging
    here = Path(__file__).resolve().parent
    roots += [here.parent / "data", here / "data", Path("data")]
    found = []
    for root in roots:
        if not root.exists():
            continue
        try:
            print(f"scan {root}:", os.listdir(root)[:50], flush=True)
        except Exception as e:
            print(f"scan {root} failed: {e}", flush=True)
        for p in root.rglob("train.csv"):
            if p.is_file():
                found.append(p.parent)
    if not found:
        raise SystemExit(f"train.csv not found under {roots}")
    # prefer the competition slug dir if present
    for d in found:
        if COMP in str(d):
            return d
    return found[0]

OUT = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("./_out")
OUT.mkdir(parents=True, exist_ok=True)

CAT_COLS = [
    "Gender", "City_Type", "Current_Car_Type",
    "Home_Charging_Possible", "Subsidy_Available", "Range_Anxiety_Level",
]
TARGET = "Will_Buy_EV"
ID = "id"
N_FOLDS = 5
SEEDS = [42, 7]


def load_xy(data_dir: Path):
    train = pd.read_csv(data_dir / "train.csv")
    test = pd.read_csv(data_dir / "test.csv")
    y = (train[TARGET].astype(str) == "Yes").astype(int).to_numpy()
    return train, test, y


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    X = df.drop(columns=[c for c in (ID, TARGET) if c in df.columns]).copy()
    X["n_missing"] = X.isna().sum(axis=1)
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


def prep_model_frame(X, cats, te_cols):
    X = X.copy()
    cat_names = []
    for c in list(X.columns):
        if c in te_cols:
            X[c] = X[c].astype(float)
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
            verbosity=-1, seed=seed,
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
        use_gpu = False
        try:
            import subprocess
            use_gpu = Path("/dev/nvidia0").exists()
        except Exception:
            pass
        tree_method = "hist"
        device = "cpu"
        # Kaggle GPU: use device=cuda when available
        if os.environ.get("KAGGLE_KERNEL_RUN_TYPE") and Path("/opt/bin/nvidia-smi").exists():
            try:
                m0 = xgb.XGBClassifier(
                    device="cuda", tree_method="hist",
                    objective="binary:logistic", eval_metric="auc",
                    learning_rate=0.03, max_depth=6, n_estimators=50,
                    random_state=seed,
                )
                m0.fit(Xtr.head(200), ytr[:200])
                device = "cuda"
            except Exception:
                device = "cpu"
        m = xgb.XGBClassifier(
            objective="binary:logistic", eval_metric="auc",
            learning_rate=0.03, max_depth=6, n_estimators=2500,
            subsample=0.85, colsample_bytree=0.85, n_jobs=-1,
            random_state=seed, tree_method=tree_method, device=device,
        )
        m.fit(Xtr, ytr, eval_set=[(Xes, yes)], verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xte)[:, 1]

    if model == "cat":
        cat_idx = [Xtr.columns.get_loc(c) for c in cat_names]
        task = "CPU"
        if Path("/opt/bin/nvidia-smi").exists():
            task = "GPU"
        m = cb.CatBoostClassifier(
            loss_function="Logloss", eval_metric="AUC",
            learning_rate=0.03, depth=8, iterations=2500,
            random_seed=seed, verbose=False, task_type=task,
            early_stopping_rounds=80,
        )
        try:
            m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        except Exception as e:
            print(f"cat {task} failed ({e}); fallback CPU", flush=True)
            m = cb.CatBoostClassifier(
                loss_function="Logloss", eval_metric="AUC",
                learning_rate=0.03, depth=8, iterations=2500,
                random_seed=seed, verbose=False, task_type="CPU",
                early_stopping_rounds=80,
            )
            m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xte)[:, 1]
    raise ValueError(model)


def run_model_seed(model, seed, train_raw, y, test_raw, n_folds=N_FOLDS):
    key = f"{model}_s{seed}"
    oof_path = OUT / f"oof_{key}.npy"
    test_path = OUT / f"test_{key}.npy"
    meta_path = OUT / f"meta_{key}.json"
    if oof_path.exists() and test_path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        print(f"[skip] {key} OOF={meta.get('auc')}", flush=True)
        return np.load(oof_path), np.load(test_path), float(meta["auc"])

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
        X_tr_te, X_va_te = target_encode_fold(
            X_tr_all.iloc[tr_idx], y[tr_idx], X_tr_all.iloc[va_idx], CAT_COLS
        )
        _, X_es_te = target_encode_fold(
            X_tr_all.iloc[tr_idx], y[tr_idx], X_tr_all.iloc[es_idx], CAT_COLS
        )
        _, X_te_te = target_encode_fold(
            X_tr_all.iloc[tr_idx], y[tr_idx], X_te_all, CAT_COLS
        )
        Xtr, cn = prep_model_frame(X_tr_te, CAT_COLS, te_cols)
        Xva, _ = prep_model_frame(X_va_te, CAT_COLS, te_cols)
        Xes, _ = prep_model_frame(X_es_te, CAT_COLS, te_cols)
        Xte, _ = prep_model_frame(X_te_te, CAT_COLS, te_cols)
        va_p, te_p = train_one(model, Xtr, y[tr_idx], Xes, y[es_idx], Xva, Xte, cn, seed)
        oof[va_idx] = va_p
        test_sum += te_p
        print(f"[{key}] fold{k} done", flush=True)

    test_pred = test_sum / n_folds
    auc = float(roc_auc_score(y, oof))
    np.save(oof_path, oof)
    np.save(test_path, test_pred)
    meta_path.write_text(json.dumps({"model": model, "seed": seed, "auc": auc}))
    print(f"[{key}] OOF AUC={auc:.5f}", flush=True)
    return oof, test_pred, auc


def weight_search(oofs, y):
    names = list(oofs)
    mats = [oofs[n] for n in names]
    n = len(names)
    if n == 1:
        return {names[0]: 1.0}, float(roc_auc_score(y, mats[0]))
    w = np.ones(n) / n
    grid = np.arange(0, 1.0001, 0.1)
    for _ in range(3):
        for i in range(n):
            local_best, local_t = -1.0, w[i]
            for t in grid:
                cand = w.copy()
                rest = 1 - w[i]
                if rest < 1e-9:
                    cand[i] = t
                    for j in range(n):
                        if j != i:
                            cand[j] = (1 - t) / max(n - 1, 1)
                else:
                    cand[i] = t
                    scale = (1 - t) / rest
                    for j in range(n):
                        if j != i:
                            cand[j] = w[j] * scale
                v = roc_auc_score(y, sum(c * m for c, m in zip(cand, mats)))
                if v > local_best:
                    local_best, local_t = v, t
            rest = 1 - w[i]
            if rest < 1e-9:
                w[i] = local_t
                for j in range(n):
                    if j != i:
                        w[j] = (1 - local_t) / max(n - 1, 1)
            else:
                w[i] = local_t
                scale = (1 - local_t) / rest
                for j in range(n):
                    if j != i:
                        w[j] = w[j] * scale
    best_v = float(roc_auc_score(y, sum(wi * m for wi, m in zip(w, mats))))
    return {k: float(wi) for k, wi in zip(names, w)}, best_v


def main():
    data_dir = resolve_data()
    print("data:", data_dir, flush=True)
    train, test, y = load_xy(data_dir)
    print(f"train={train.shape} test={test.shape} pos={y.mean():.4f}", flush=True)

    oofs, tests = {}, {}
    for model in ("lgb", "xgb", "cat"):
        for seed in SEEDS:
            oof, te, auc = run_model_seed(model, seed, train, y, test)
            oofs[f"{model}_s{seed}"] = oof
            tests[f"{model}_s{seed}"] = te

    weights, blend_auc = weight_search(oofs, y)
    print("weights:", {k: round(v, 3) for k, v in weights.items()}, flush=True)
    print(f"blend OOF AUC={blend_auc:.5f}", flush=True)

    y_prob = sum(weights[k] * tests[k] for k in weights)
    sub = pd.DataFrame({ID: test[ID], TARGET: y_prob})
    sub_path = OUT / "submission.csv"
    sub.to_csv(sub_path, index=False)
    (OUT / "blend.json").write_text(json.dumps({"weights": weights, "oof_auc": blend_auc}, indent=2))
    print(f"saved {sub_path} rows={len(sub)} mean={y_prob.mean():.4f}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
