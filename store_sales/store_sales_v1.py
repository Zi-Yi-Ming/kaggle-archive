# -*- coding: utf-8 -*-
"""
Store Sales - Time Series Forecasting v1 基线
=============================================

预测厄瓜多尔 Favorita 超市 54 家店 × 33 个商品类别的日销售额。
测试窗口 = 2017-08-16 ~ 2017-08-31(16 天), 评分指标 **SMAPE**。

v1 思路(极简基线):
  - 验证方式: 时间序列窗口验证 —— 取训练集最后 16 天(2017-08-01~15)
    做验证, 与测试窗口同长度镜像, 避免随机 K 折泄漏时序信息;
  - 特征: 日期分量(year/month/day/dayofweek) + store_nbr + family
          + onpromotion + 油价(oil, 前向填充) + 全国节假日标记;
  - 模型: LightGBM 回归, 目标 log1p(sales)(销售额右偏严重, 25% 为 0),
          预测后 expm1 还原并 clip 到 >=0。

用法（项目根目录下）:
    C:/Users/Lenovo/.conda/envs/kaggle/python.exe store_sales/store_sales_v1.py
"""

import os

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_squared_error

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VALIDATION_DAYS = 16  # 与测试窗口同长度


def smape(y_true, y_pred):
    """SMAPE(该比赛评分指标)。"""
    denom = (np.abs(y_true) + np.abs(y_pred))
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / np.where(denom == 0, 1e-9, denom)))


def load_data():
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), parse_dates=["date"])
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), parse_dates=["date"])
    oil = pd.read_csv(os.path.join(DATA_DIR, "oil.csv"), parse_dates=["date"])
    holidays = pd.read_csv(os.path.join(DATA_DIR, "holidays_events.csv"),
                           parse_dates=["date"])
    return train, test, oil, holidays


def engineer_features(train, test, oil, holidays):
    """构造训练/测试共用特征; 返回 (train_feat, test_feat)。"""
    # --- 油价: 前向填充 + 最早缺失用首个有效值 ---
    oil = oil.sort_values("date")
    oil["dcoilwtico"] = oil["dcoilwtico"].ffill().bfill()

    # --- 全国节假日: 只看 locale=National 且非 Work Day ---
    nat = holidays[(holidays["locale"] == "National") &
                   (holidays["type"] != "Work Day")]
    nat_dates = set(nat["date"].dt.date)

    def add_features(df):
        df = df.copy()
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["dayofweek"] = df["date"].dt.dayofweek
        df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
        df["is_holiday"] = df["date"].dt.date.isin(nat_dates).astype(int)
        df = df.merge(oil, on="date", how="left")
        df["dcoilwtico"] = df["dcoilwtico"].ffill().bfill()
        df["store_nbr"] = df["store_nbr"].astype("category")
        df["family"] = df["family"].astype("category")
        return df

    train_feat = add_features(train)
    test_feat = add_features(test)
    return train_feat, test_feat


def main():
    print("===== 加载数据 =====")
    train, test, oil, holidays = load_data()
    print(f"train: {train.shape}  test: {test.shape}")

    print("\n===== 特征工程 =====")
    train_feat, test_feat = engineer_features(train, test, oil, holidays)

    # 时间窗口验证: 最后 VALIDATION_DAYS 天做验证(镜像测试窗口)
    cutoff = train_feat["date"].max() - pd.Timedelta(days=VALIDATION_DAYS)
    tr = train_feat[train_feat["date"] <= cutoff]
    va = train_feat[train_feat["date"] > cutoff]
    print(f"训练窗口: {tr.date.min().date()} ~ {tr.date.max().date()}  ({len(tr)} 行)")
    print(f"验证窗口: {va.date.min().date()} ~ {va.date.max().date()}  ({len(va)} 行)")

    feat_cols = ["year", "month", "day", "dayofweek", "weekofyear",
                 "is_holiday", "store_nbr", "family", "onpromotion", "dcoilwtico"]
    X_tr, y_tr = tr[feat_cols], np.log1p(tr["sales"])
    X_va, y_va = va[feat_cols], np.log1p(va["sales"])

    print("\n===== 训练 LightGBM =====")
    model = lgb.LGBMRegressor(
        n_estimators=400, learning_rate=0.05, num_leaves=127,
        min_child_samples=20, subsample=0.8, colsample_bytree=0.8,
        random_state=RANDOM_STATE, n_jobs=-1, verbose=-1,
    )
    model.fit(X_tr, y_tr,
              eval_set=[(X_va, y_va)],
              callbacks=[lgb.early_stopping(50, verbose=False)])

    # 验证集评估
    va_pred = np.clip(np.expm1(model.predict(X_va)), 0, None)
    va_true = va["sales"].values
    rmse = float(np.sqrt(mean_squared_error(va_true, va_pred)))
    print(f"验证集 SMAPE: {smape(va_true, va_pred):.4f}  RMSE: {rmse:.2f}")
    print(f"验证集预测均值 {va_pred.mean():.1f} vs 真实均值 {va_true.mean():.1f}")

    # 全量训练(含验证窗口)预测测试集
    print("\n===== 全量重训 + 预测测试集 =====")
    X_all, y_all = train_feat[feat_cols], np.log1p(train_feat["sales"])
    model.fit(X_all, y_all)
    test_pred = np.clip(np.expm1(model.predict(test_feat[feat_cols])), 0, None)

    sub = pd.DataFrame({"id": test["id"], "sales": test_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v1.csv")
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行)")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
