# -*- coding: utf-8 -*-
"""House Prices v5 on Kaggle CPU: FE + equal-blend + OOF stacking.

Target: public < 0.12196 (v4), toward 0.118–0.120.
Writes /kaggle/working/submission.csv (Id, SalePrice)
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import catboost as cb
import lightgbm as lgb
import xgboost as xgb
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

RANDOM_STATE = 42
N_FOLDS = 5


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


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    X = df.copy()
    X["TotalSF"] = X["TotalBsmtSF"].fillna(0) + X["1stFlrSF"] + X["2ndFlrSF"]
    X["QualArea"] = X["OverallQual"] * X["GrLivArea"]
    X["QualSF"] = X["OverallQual"] * X["TotalSF"]
    X["TotalBath"] = (
        X["FullBath"] + 0.5 * X["HalfBath"]
        + X["BsmtFullBath"].fillna(0) + 0.5 * X["BsmtHalfBath"].fillna(0)
    )
    X["HouseAge"] = X["YrSold"] - X["YearBuilt"]
    X["RemodAge"] = X["YrSold"] - X["YearRemodAdd"]
    X["TotalPorch"] = (
        X["OpenPorchSF"] + X["EnclosedPorch"] + X["3SsnPorch"]
        + X["WoodDeckSF"] + X["ScreenPorch"]
    )
    X["TotalBsmtFin"] = X["BsmtFinSF1"].fillna(0) + X["BsmtFinSF2"].fillna(0)
    X["HasPool"] = (X["PoolArea"].fillna(0) > 0).astype(int)
    X["HasGarage"] = (X["GarageArea"].fillna(0) > 0).astype(int)
    X["HasBsmt"] = (X["TotalBsmtSF"].fillna(0) > 0).astype(int)
    X["Has2ndFlr"] = (X["2ndFlrSF"] > 0).astype(int)
    X["HasFireplace"] = (X["Fireplaces"] > 0).astype(int)
    X["MSSubClass"] = X["MSSubClass"].astype(str)
    # quality × size extras
    X["QualGarage"] = X["OverallQual"] * X["GarageArea"].fillna(0)
    X["QualBsmt"] = X["OverallQual"] * X["TotalBsmtSF"].fillna(0)
    X["LivLotRatio"] = X["GrLivArea"] / (X["LotArea"] + 1)
    X["Spaciousness"] = (X["1stFlrSF"] + X["2ndFlrSF"]) / (X["TotRmsAbvGrd"] + 1)
    # neighborhood median quality proxy (computed only on train at fit time)
    return X


def prep_xy(train_raw, test_raw):
    y = np.log1p(train_raw["SalePrice"].to_numpy().astype(float))
    ids = test_raw["Id"].to_numpy()
    tr = add_features(train_raw.drop(columns=["SalePrice"]))
    te = add_features(test_raw)
    cols = [c for c in tr.columns if c != "Id"]
    X = pd.concat([tr[cols], te[cols]], ignore_index=True)
    for c in X.columns:
        if X[c].dtype == object or str(X[c].dtype) == "string":
            X[c] = X[c].astype(str).fillna("None")
        else:
            X[c] = X[c].astype(float)
    Xtr = X.iloc[: len(tr)].reset_index(drop=True)
    Xte = X.iloc[len(tr):].reset_index(drop=True)
    cat_cols = [c for c in cols if Xtr[c].dtype == object or str(Xtr[c].dtype) == "string"]
    return Xtr, Xte, y, ids, cat_cols


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def fit_predict(model_name, Xtr, y, Xte, cat_cols, seed):
    oof = np.zeros(len(y))
    te_pred = np.zeros(len(Xte))
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    for k, (tr_idx, va_idx) in enumerate(kf.split(Xtr, y)):
        Xa, Xb = Xtr.iloc[tr_idx], Xtr.iloc[va_idx]
        ya, yb = y[tr_idx], y[va_idx]
        if model_name == "lgb":
            params = dict(
                objective="regression", metric="rmse", learning_rate=0.03,
                num_leaves=31, min_child_samples=5, feature_fraction=0.85,
                bagging_fraction=0.85, bagging_freq=1, verbosity=-1,
                n_jobs=-1, seed=seed,
            )
            cat_idx = [Xa.columns.get_loc(c) for c in cat_cols]
            Xa2, Xb2, Xt2 = Xa.copy(), Xb.copy(), Xte.copy()
            for c in cat_cols:
                Xa2[c] = Xa2[c].astype("category")
                Xb2[c] = Xb2[c].astype("category")
                Xt2[c] = Xt2[c].astype("category")
            m = lgb.train(
                params, lgb.Dataset(Xa2, ya, categorical_feature=cat_idx),
                num_boost_round=3000,
                valid_sets=[lgb.Dataset(Xb2, yb, categorical_feature=cat_idx)],
                callbacks=[lgb.early_stopping(50, verbose=False)],
            )
            it = m.best_iteration or 3000
            oof[va_idx] = m.predict(Xb2, num_iteration=it)
            te_pred += m.predict(Xt2, num_iteration=it) / N_FOLDS
        elif model_name == "xgb":
            cats_int = {
                c: {v: i for i, v in enumerate(sorted(set(Xtr[c].astype(str)) | set(Xte[c].astype(str))))}
                for c in cat_cols
            }

            def enc(df):
                d = df.copy()
                for c in cat_cols:
                    d[c] = d[c].astype(str).map(cats_int[c]).fillna(-1).astype(int)
                return d

            m = xgb.XGBRegressor(
                objective="reg:squarederror", eval_metric="rmse",
                learning_rate=0.03, max_depth=4, n_estimators=3000,
                subsample=0.85, colsample_bytree=0.85, n_jobs=-1,
                random_state=seed, tree_method="hist",
            )
            m.fit(enc(Xa), ya, eval_set=[(enc(Xb), yb)], verbose=False)
            oof[va_idx] = m.predict(enc(Xb))
            te_pred += m.predict(enc(Xte)) / N_FOLDS
        elif model_name == "cat":
            cat_idx = [Xa.columns.get_loc(c) for c in cat_cols]
            Xa2, Xb2, Xt2 = Xa.copy(), Xb.copy(), Xte.copy()
            for c in cat_cols:
                Xa2[c] = Xa2[c].astype(str)
                Xb2[c] = Xb2[c].astype(str)
                Xt2[c] = Xt2[c].astype(str)
            model = cb.CatBoostRegressor(
                loss_function="RMSE", learning_rate=0.03, depth=6,
                iterations=3000, random_seed=seed, verbose=False,
                allow_writing_files=False, early_stopping_rounds=50,
            )
            model.fit(Xa2, ya, cat_features=cat_idx, eval_set=(Xb2, yb), verbose=False)
            oof[va_idx] = model.predict(Xb2)
            te_pred += model.predict(Xt2) / N_FOLDS
        elif model_name == "ridge":
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            num_cols = [c for c in Xtr.columns if c not in cat_cols]
            pipe = Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("sc", StandardScaler()),
                ("m", Ridge(alpha=10.0)),
            ])
            pipe.fit(Xtr.iloc[tr_idx][num_cols], ya)
            oof[va_idx] = pipe.predict(Xtr.iloc[va_idx][num_cols])
            te_pred += pipe.predict(Xte[num_cols]) / N_FOLDS
        print(f"[{model_name} s{seed}] fold{k} rmse={rmse(yb, oof[va_idx]):.5f}", flush=True)
    print(f"[{model_name} s{seed}] OOF RMSE={rmse(y, oof):.5f}", flush=True)
    return oof, te_pred


def main():
    data = resolve_data()
    train = pd.read_csv(data / "train.csv")
    test = pd.read_csv(data / "test.csv")
    print(f"train={train.shape} test={test.shape}", flush=True)
    Xtr, Xte, y, ids, cat_cols = prep_xy(train, test)
    print(f"features={Xtr.shape[1]} cats={len(cat_cols)}", flush=True)

    oofs, tes = {}, {}
    for name in ("lgb", "xgb", "cat", "ridge"):
        for seed in (RANDOM_STATE, 7):
            oof, te = fit_predict(name, Xtr, y, Xte, cat_cols, seed)
            oofs[f"{name}_s{seed}"] = oof
            tes[f"{name}_s{seed}"] = te

    # equal-weight blend of all
    keys = list(oofs)
    blend_oof = np.mean([oofs[k] for k in keys], axis=0)
    blend_te = np.mean([tes[k] for k in keys], axis=0)
    print(f"equal-blend OOF RMSE={rmse(y, blend_oof):.5f}", flush=True)

    # meta ridge on OOF
    meta = np.column_stack([oofs[k] for k in keys])
    from sklearn.linear_model import RidgeCV
    clf = RidgeCV(alphas=np.logspace(-2, 3, 20))
    clf.fit(meta, y)
    stack_oof = clf.predict(meta)
    stack_te = clf.predict(np.column_stack([tes[k] for k in keys]))
    print(f"stack OOF RMSE={rmse(y, stack_oof):.5f} alpha={clf.alpha_:.4f}", flush=True)

    # tree-only equal blend (exclude ridge — historically safer on this small set)
    tree_keys = [k for k in keys if not k.startswith("ridge")]
    tree_oof = np.mean([oofs[k] for k in tree_keys], axis=0)
    tree_te = np.mean([tes[k] for k in tree_keys], axis=0)
    print(f"tree-equal OOF RMSE={rmse(y, tree_oof):.5f}", flush=True)

    # conservative: 50% tree-equal + 50% stack
    final_te = 0.5 * tree_te + 0.5 * stack_te
    final_oof = 0.5 * tree_oof + 0.5 * stack_oof
    print(f"final OOF RMSE={rmse(y, final_oof):.5f}", flush=True)

    out = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("./_out")
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"Id": ids, "SalePrice": np.expm1(final_te)}).to_csv(out / "submission.csv", index=False)
    pd.DataFrame({"Id": ids, "SalePrice": np.expm1(stack_te)}).to_csv(out / "submission_stack.csv", index=False)
    pd.DataFrame({"Id": ids, "SalePrice": np.expm1(tree_te)}).to_csv(out / "submission_tree_equal.csv", index=False)
    np.save(out / "oof_equal.npy", blend_oof)
    np.save(out / "oof_stack.npy", stack_oof)
    np.save(out / "oof_tree_equal.npy", tree_oof)
    print("saved submission.csv / submission_stack.csv / submission_tree_equal.csv", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
