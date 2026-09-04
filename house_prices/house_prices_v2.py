# -*- coding: utf-8 -*-
"""
House Prices v2: 组合特征工程 + Ridge/XGB/LGBM 权重混合
=========================================================
v1 基线: XGB CV RMSE 0.1345 / 公开榜 0.13325。

v2 两点:
1. 新增 ~10 个可靠组合特征(总面积/质量面积交互/总浴室/房龄/门廊面积/指标)
   —— 全部用原始列直接计算,无泄漏
2. Ridge + XGBoost + LightGBM 三模型 5 折 OOF(log 空间),
   权重网格搜索(0.1 步长,归一)最小化 OOF RMSE 后混合

用法: conda activate kaggle 后: python house_prices_v2.py
输出: submissions/submission_v2.csv (Id, SalePrice)
"""

import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


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


def oof_predict(model, X, y, cv):
    """5 折 OOF 预测(log 空间)。"""
    oof = np.zeros(len(y))
    for tr_idx, va_idx in cv.split(X, y):
        m = make_pipe(model, X.select_dtypes(include=[np.number]).columns.tolist(),
                      X.select_dtypes(include=["object", "category"]).columns.tolist())
        m.fit(X.iloc[tr_idx], y[tr_idx])
        oof[va_idx] = m.predict(X.iloc[va_idx])
    return oof


def weight_search_min(names, oofs, y):
    """0.1 步长网格搜索混合权重(归一),最小化 OOF RMSE。"""
    best_w, best_rmse = None, np.inf
    n = len(names)
    grid = np.arange(0, 1.0001, 0.1)
    for w1 in grid:
        for w2 in (grid if n >= 3 else [0.0]):
            ws = [w1, w2, 1 - w1 - w2][:n] if n >= 3 else [w1, 1 - w1]
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
    print(f"特征数: {X.shape[1]} (原始 79 + 新增 10)")

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
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
        oof = oof_predict(model, X, y, cv)
        oofs.append(oof)
        names.append(name)
        print(f"{name:10s} OOF RMSE: {root_mean_squared_error(y, oof):.5f}")

    w, blend_rmse = weight_search_min(names, oofs, y)
    print(f"\n混合权重: {dict(zip(names, [round(x, 2) for x in w]))}  "
          f"OOF RMSE: {blend_rmse:.5f}")

    # 最终:各模型全量重训,预测测试集后按权重混合
    test_preds = []
    for name, model in models.items():
        m = make_pipe(model, num_cols, cat_cols).fit(X, y)
        test_preds.append(m.predict(X_test))
    y_log = sum(wi * t for wi, t in zip(w, test_preds))
    sale_price = np.expm1(y_log)

    submission = pd.DataFrame({"Id": test["Id"], "SalePrice": sale_price})
    out = os.path.join(BASE_DIR, "submissions", "submission_v2.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"\n提交文件已生成: {out}")
    print(f"预测房价: 均值 {sale_price.mean():.0f} | 中位数 {np.median(sale_price):.0f} "
          f"| 范围 [{sale_price.min():.0f}, {sale_price.max():.0f}]")
    align = (submission["Id"].values == test["Id"].values).all()
    print(f"行数: {len(submission)} (应为 {len(test)})  |  Id 顺序一致: {align}")


if __name__ == "__main__":
    main()
