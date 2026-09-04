# -*- coding: utf-8 -*-
"""
House Prices - Advanced Regression Techniques 基线脚本
========================================================
回归任务,评分指标:RMSE(预测 log 房价 与 实际 log 房价 之差)。

基线方法:
1. 目标 log1p 变换(房价右偏,log 后近正态;Kaggle 评分也在 log 空间)
2. 数值列中位数填充 + 标准化;类别列 fillna('None') + one-hot(缺失类别本身是信息)
3. Ridge / RandomForest / XGBoost 三模型,5 折 KFold CV 对比(log 空间 RMSE)
4. 最优模型全量重训,预测后 expm1 还原为真实房价

用法: conda activate kaggle 后: python house_prices_baseline.py
输出: submissions/submission_baseline.csv (Id, SalePrice)
"""

import os
import sys

import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


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
    print(f"目标 SalePrice: 均值 {train['SalePrice'].mean():.0f} | 中位数 "
          f"{train['SalePrice'].median():.0f} | 偏度 {train['SalePrice'].skew():.2f}")
    miss = train.drop(columns=["Id", "SalePrice"]).isnull().sum()
    print(f"含缺失列数: {(miss > 0).sum()} / {len(miss)}")

    y = np.log1p(train["SalePrice"].values)  # log 空间训练与评分
    X = train.drop(columns=["Id", "SalePrice"])
    X_test = test.drop(columns=["Id"])

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    print(f"数值列 {len(num_cols)} 个 / 类别列 {len(cat_cols)} 个")

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "Ridge": Ridge(alpha=10.0),
        "RandomForest": RandomForestRegressor(n_estimators=400, max_depth=10,
                                              min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=-1),
        "XGBoost": xgb.XGBRegressor(n_estimators=600, max_depth=5, learning_rate=0.05,
                                    tree_method="hist", n_jobs=-1, random_state=RANDOM_STATE),
    }
    print("\n===== 5 折 CV(log 空间 RMSE,越低越好)=====")
    results = {}
    for name, model in models.items():
        pipe = make_pipe(model, num_cols, cat_cols)
        scores = -cross_val_score(pipe, X, y, cv=cv,
                                  scoring="neg_root_mean_squared_error", n_jobs=1)
        results[name] = scores
        print(f"{name:15s} RMSE: {scores.mean():.4f} ± {scores.std():.4f}")

    best_name = min(results, key=lambda k: results[k].mean())
    print(f"\n选用: {best_name} (RMSE {results[best_name].mean():.4f})")

    final = make_pipe(models[best_name], num_cols, cat_cols).fit(X, y)
    sale_price = np.expm1(final.predict(X_test))

    submission = pd.DataFrame({"Id": test["Id"], "SalePrice": sale_price})
    out = os.path.join(BASE_DIR, "submissions", "submission_baseline.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"\n提交文件已生成: {out}")
    print(f"预测房价: 均值 {sale_price.mean():.0f} | 中位数 {np.median(sale_price):.0f} "
          f"| 范围 [{sale_price.min():.0f}, {sale_price.max():.0f}]")
    align = (submission["Id"].values == test["Id"].values).all()
    print(f"行数: {len(submission)} (应为 {len(test)})  |  Id 顺序一致: {align}")


if __name__ == "__main__":
    main()
