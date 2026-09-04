# -*- coding: utf-8 -*-
"""
House Prices v3: 特征增强 + CatBoost 入队的四模型混合
=======================================================
v2: 10 组合特征 + Ridge/XGB/LGBM 混合,公开榜 0.12223。

v3 两点:
1. 新增特征:MSSubClass 类别化(数值但实为 20 种户型)、QualSF(质量×总面积)、
   Has2ndFlr、HasFireplace
2. CatBoost 入队:它对类别特征是原生处理(哈希编码,不做 one-hot),
   在强类别数据的房价赛上通常单模型就很强;四模型权重搜索混合
   (广义单纯形:itertools.product 网格,归一,最小化 OOF RMSE)

用法: conda activate kaggle 后: python house_prices_v3.py
输出: submissions/submission_v3.csv (Id, SalePrice)
"""

import itertools
import os
import sys
import time

import numpy as np
import pandas as pd
import catboost as cb
import lightgbm as lgb
import xgboost as xgb

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import KFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CAT_PARAMS = {
    "iterations": 1200, "learning_rate": 0.05, "depth": 6,
    "loss_function": "RMSE", "thread_count": -1, "verbose": 0,
    "random_seed": RANDOM_STATE, "allow_writing_files": False,
}


def add_features(df):
    """组合特征(原始列直接计算,无泄漏)。返回副本。"""
    X = df.copy()
    X["TotalSF"] = X["TotalBsmtSF"].fillna(0) + X["1stFlrSF"] + X["2ndFlrSF"]
    X["QualArea"] = X["OverallQual"] * X["GrLivArea"]
    X["TotalBath"] = (X["FullBath"] + 0.5 * X["HalfBath"]
                      + X["BsmtFullBath"].fillna(0) + 0.5 * X["BsmtHalfBath"].fillna(0))
    X["HouseAge"] = X["YrSold"] - X["YearBuilt"]
    X["RemodAge"] = X["YrSold"] - X["YearRemodAdd"]
    X["TotalPorch"] = (X["OpenPorchSF"] + X["EnclosedPorch"] + X["3SsnPorch"]
                       + X["WoodDeckSF"] + X["ScreenPorch"])
    X["TotalBsmtFin"] = X["BsmtFinSF1"] + X["BsmtFinSF2"]
    X["HasPool"] = (X["PoolArea"].fillna(0) > 0).astype(int)
    X["HasGarage"] = (X["GarageArea"].fillna(0) > 0).astype(int)
    X["HasBsmt"] = (X["TotalBsmtSF"].fillna(0) > 0).astype(int)
    # v3 新增
    X["MSSubClass"] = X["MSSubClass"].astype(str)  # 数值但实为 20 种户型类别
    X["QualSF"] = X["OverallQual"] * X["TotalSF"]
    X["Has2ndFlr"] = (X["2ndFlrSF"] > 0).astype(int)
    X["HasFireplace"] = (X["Fireplaces"] > 0).astype(int)
    return X


def make_pipe(model, num_cols, cat_cols):
    return Pipeline([
        ("ct", ColumnTransformer([
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                              ("sc", StandardScaler())]), num_cols),
            ("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="None")),
                              ("ohe", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
        ])),
        ("model", model),
    ])


def oof_pipe(model, X, y, cv, num_cols, cat_cols):
    oof = np.zeros(len(y))
    for tr_idx, va_idx in cv.split(X, y):
        m = make_pipe(model, num_cols, cat_cols).fit(X.iloc[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X.iloc[va_idx])
    return oof


def oof_cat(Xc, y, cv, cat_idx):
    oof = np.zeros(len(y))
    t0 = time.time()
    for k, (tr_idx, va_idx) in enumerate(cv.split(Xc, y)):
        Xtr, Xes, ytr, yes = train_test_split(
            Xc.iloc[tr_idx], y[tr_idx], test_size=0.1, random_state=RANDOM_STATE)
        m = cb.CatBoostRegressor(**CAT_PARAMS)
        m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes),
              early_stopping_rounds=100, verbose=False)
        oof[va_idx] = m.predict(Xc.iloc[va_idx])
        print(f"  CatBoost 折{k}: {m.get_best_iteration()} 轮 ({time.time() - t0:.0f}s)", flush=True)
    return oof


def weight_search_min(names, oofs, y, step=0.1):
    """广义权重网格(任意模型数,归一),最小化 OOF RMSE。"""
    n = len(names)
    grid = np.arange(0, 1.0001, step)
    best_w, best_rmse = None, np.inf
    for combo in itertools.product(grid, repeat=n - 1):
        ws = list(combo) + [1 - sum(combo)]
        if any(w < -1e-9 for w in ws):
            continue
        blend = sum(wi * o for wi, o in zip(ws, oofs))
        rmse = root_mean_squared_error(y, blend)
        if rmse < best_rmse:
            best_rmse, best_w = rmse, ws
    return best_w, best_rmse


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    y = np.log1p(train["SalePrice"].values)
    X = add_features(train.drop(columns=["Id", "SalePrice"]))
    X_test = add_features(test.drop(columns=["Id"]))
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    print(f"特征 {X.shape[1]} 个 | 数值 {len(num_cols)} / 类别 {len(cat_cols)}")

    # CatBoost 变体:类别列填 'None' 字符串,数值列保留 NaN(原生处理)
    X_cat = X.copy()
    X_test_cat = X_test.copy()
    for c in cat_cols:
        X_cat[c] = X_cat[c].fillna("None").astype(str)
        X_test_cat[c] = X_test_cat[c].fillna("None").astype(str)
    cat_idx = [X_cat.columns.get_loc(c) for c in cat_cols]

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "Ridge": Ridge(alpha=10.0),
        "XGBoost": xgb.XGBRegressor(n_estimators=600, max_depth=5, learning_rate=0.05,
                                    tree_method="hist", n_jobs=-1, random_state=RANDOM_STATE),
        "LightGBM": lgb.LGBMRegressor(n_estimators=1000, learning_rate=0.05, num_leaves=31,
                                      min_child_samples=20, n_jobs=-1, random_state=RANDOM_STATE,
                                      verbose=-1),
    }
    print("\n===== 5 折 OOF(log 空间 RMSE)=====")
    oofs, names = [], []
    for name, model in models.items():
        oof = oof_pipe(model, X, y, cv, num_cols, cat_cols)
        oofs.append(oof)
        names.append(name)
        print(f"{name:10s} OOF RMSE: {root_mean_squared_error(y, oof):.5f}")
    oof_c = oof_cat(X_cat, y, cv, cat_idx)
    oofs.append(oof_c)
    names.append("CatBoost")
    print(f"CatBoost   OOF RMSE: {root_mean_squared_error(y, oof_c):.5f}")

    w, blend_rmse = weight_search_min(names, oofs, y)
    print(f"\n混合权重: {dict(zip(names, [round(x, 2) for x in w]))}  "
          f"OOF RMSE: {blend_rmse:.5f}")

    # 最终:全量重训 + 预测 + 混合
    test_preds = []
    for name, model in models.items():
        m = make_pipe(model, num_cols, cat_cols).fit(X, y)
        test_preds.append(m.predict(X_test))
    m_cat = cb.CatBoostRegressor(**CAT_PARAMS)
    Xtr, Xes, ytr, yes = train_test_split(X_cat, y, test_size=0.05, random_state=RANDOM_STATE)
    m_cat.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes),
              early_stopping_rounds=100, verbose=False)
    test_preds.append(m_cat.predict(X_test_cat))
    y_log = sum(wi * t for wi, t in zip(w, test_preds))
    sale_price = np.expm1(y_log)

    submission = pd.DataFrame({"Id": test["Id"], "SalePrice": sale_price})
    out = os.path.join(BASE_DIR, "submissions", "submission_v3.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"\n提交文件已生成: {out}")
    print(f"预测房价: 均值 {sale_price.mean():.0f} | 中位数 {np.median(sale_price):.0f} "
          f"| 范围 [{sale_price.min():.0f}, {sale_price.max():.0f}]")
    align = (submission["Id"].values == test["Id"].values).all()
    print(f"行数: {len(submission)} (应为 {len(test)})  |  Id 顺序一致: {align}")


if __name__ == "__main__":
    main()
