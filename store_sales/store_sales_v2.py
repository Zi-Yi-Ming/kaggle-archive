# -*- coding: utf-8 -*-
"""
Store Sales - Time Series Forecasting v2
========================================

在 v1(日期+油价+节假日, 本地 SMAPE 0.5656 / 公开榜 0.47986) 基础上加
**时序专有特征** + 多种子平均:

v2 新增:
  1. 滞后特征(每个 store×family 组内, 按日期排序):
     - sales 滞后 1/7/364 天(364 天 = 去年同天, 季节项)
     - 滞后销售的滚动均值 7/14/28 天
  2. 促销滞后: onpromotion 当前值 + 过去 7 天均值
  3. 节假日精细化: 全国节假日 + Transfer(调休)标记 +
     "距最近节日 N 天"(前后两个方向)
  4. 油价滞后 1/7 天
  5. 3 个种子的 LGBM 平均(每折/每种子预测存 npy, 可断点续跑)

验证方式同 v1: 训练集最后 16 天(2017-07-31 ~ 08-15)做验证, 镜像测试窗口。
目标 log1p(sales), 预测 expm1 后 clip >=0。

用法（项目根目录下, 超时可重复执行直到输出提交文件）:
    C:/Users/Lenovo/.conda/envs/kaggle/python.exe store_sales/store_sales_v2.py
"""

import os
import time

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_squared_error

RANDOM_SEEDS = [42, 2026, 7]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CKPT_DIR = os.path.join(BASE_DIR, "ckpt_v2")
VALIDATION_DAYS = 16  # 与测试窗口同长度
NATIONAL_HOLIDAY_TYPES = ("Holiday", "Event", "Additional", "Bridge")


def smape(y_true, y_pred):
    denom = (np.abs(y_true) + np.abs(y_pred))
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / np.where(denom == 0, 1e-9, denom)))


def load_data():
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), parse_dates=["date"])
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), parse_dates=["date"])
    oil = pd.read_csv(os.path.join(DATA_DIR, "oil.csv"), parse_dates=["date"])
    holidays = pd.read_csv(os.path.join(DATA_DIR, "holidays_events.csv"),
                           parse_dates=["date"])
    return train, test, oil, holidays


def holiday_features(dates, national_dates, transfer_dates):
    """距最近节日的天数(前/后) + 是否节日/调休。dates 是 DatetimeIndex。"""
    nd = np.array(sorted(national_dates), dtype="datetime64[D]")
    d = dates.values.astype("datetime64[D]")
    idx = np.searchsorted(nd, d, side="left")
    days_until = np.where(idx < len(nd), (nd[np.minimum(idx, len(nd) - 1)] - d).astype(int),
                          np.full(len(d), 999))
    days_since = np.where(idx > 0, (d - nd[np.maximum(idx - 1, 0)]).astype(int),
                          np.full(len(d), 999))
    is_holiday = np.isin(d, nd).astype(int)
    is_transfer = np.isin(d, np.array(sorted(transfer_dates), dtype="datetime64[D]")).astype(int)
    return days_until, days_since, is_holiday, is_transfer


def engineer_features(train, test, oil, holidays):
    """构造特征; 返回 (combined_feat, n_train)。"""
    # --- 节假日: 全国(非 Work Day) + Transfer 调休 ---
    nat = holidays[(holidays["locale"] == "National") &
                   (holidays["type"].isin(NATIONAL_HOLIDAY_TYPES))]
    transfer = holidays[(holidays["type"] == "Transfer")]
    nat_dates = set(nat["date"].dt.date)
    transfer_dates = set(transfer["date"].dt.date)

    # --- 油价: 前向填充 + 滞后 ---
    oil = oil.sort_values("date")
    oil["dcoilwtico"] = oil["dcoilwtico"].ffill().bfill()

    # --- 合并 train+test(测试集 sales 置 NaN, 只用来取滞后) ---
    test_merged = test.copy()
    test_merged["sales"] = np.nan
    combined = pd.concat([train, test_merged], ignore_index=True)
    # 关键: 打 is_train 标记再排序——train.csv 本身并非按
    # (store,family,date) 排序, 排序后不能靠位置 [:n_train] 切训练集,
    # 否则每组末尾的 16 天测试行( sales=NaN )会混进训练集。
    n_train = len(train)
    combined["is_train"] = np.concatenate(
        [np.ones(n_train, dtype=bool), np.zeros(len(test), dtype=bool)])
    combined = combined.sort_values(["store_nbr", "family", "date"]).reset_index(drop=True)

    grp = combined.groupby(["store_nbr", "family"], sort=False)

    # --- 滞后特征(组内 shift 保证只用过去数据, 不含当日) ---
    sales_shift1 = grp["sales"].shift(1)
    combined["sales_lag1"] = sales_shift1
    combined["sales_lag7"] = grp["sales"].shift(7)
    combined["sales_lag364"] = grp["sales"].shift(364)  # 去年同天(季节项)
    # 滞后销售滚动均值 7/14/28 天(分组 rolling, 等价于慢 lambda 且快得多)
    key = combined["store_nbr"].astype(str) + "_" + combined["family"]
    combined["r7"] = sales_shift1.groupby(key).transform(
        lambda s: s.rolling(7, min_periods=1).mean())
    combined["r14"] = sales_shift1.groupby(key).transform(
        lambda s: s.rolling(14, min_periods=1).mean())
    combined["r28"] = sales_shift1.groupby(key).transform(
        lambda s: s.rolling(28, min_periods=1).mean())
    # --- 促销滞后: 过去 7 天 onpromotion 均值 ---
    promo_shift1 = grp["onpromotion"].shift(1)
    combined["promo_r7"] = promo_shift1.groupby(key).transform(
        lambda s: s.rolling(7, min_periods=1).mean())

    # --- 日期特征 ---
    d = combined["date"]
    combined["year"] = d.dt.year
    combined["month"] = d.dt.month
    combined["day"] = d.dt.day
    combined["dayofweek"] = d.dt.dayofweek
    combined["weekofyear"] = d.dt.isocalendar().week.astype(int)
    combined["days_since_2013"] = (d - pd.Timestamp("2013-01-01")).dt.days

    # --- 节假日距离 ---
    (combined["days_until_holiday"], combined["days_since_holiday"],
     combined["is_holiday"], combined["is_transfer"]) = holiday_features(
        d, nat_dates, transfer_dates)

    # --- 油价 ---
    combined = combined.merge(oil, on="date", how="left")
    combined["dcoilwtico"] = combined["dcoilwtico"].ffill().bfill()
    combined["oil_lag1"] = combined["dcoilwtico"].shift(1)
    combined["oil_lag7"] = combined["dcoilwtico"].shift(7)

    # --- 修复: 测试行滞后特征回填(公开榜 1.76 的根因) ---
    # 测试行在合并帧里 sales=NaN, 8/17 之后的滞后特征(lag1/lag7/r7/r14)全是
    # NaN, 模型把 NaN 路由到"冷启动"分支 → 8/23 后预测塌成近 0。
    # 用每组训练期最后一天(2017-08-15)的滞后值回填测试行(只填测试行,
    # 不碰训练行的冷启动 NaN, 否则会污染模型对冷启动的学习)。
    fill_cols = ["sales_lag1", "sales_lag7", "r7", "r14", "r28"]
    end_date = combined.loc[combined["is_train"], "date"].max()
    tail = combined[combined["is_train"] & (combined["date"] == end_date)]
    tail_vals = tail[["store_nbr", "family"] + fill_cols]
    combined = combined.merge(tail_vals, on=["store_nbr", "family"], how="left",
                              suffixes=("", "_tail"))
    mask_test = ~combined["is_train"].values
    for c in fill_cols:
        combined.loc[mask_test, c] = combined.loc[mask_test, c].fillna(
            combined.loc[mask_test, c + "_tail"])
    combined = combined.drop(columns=[c + "_tail" for c in fill_cols])

    combined["store_nbr"] = combined["store_nbr"].astype("category")
    combined["family"] = combined["family"].astype("category")
    return combined


def main():
    t0 = time.time()
    print("===== 加载数据 =====")
    train, test, oil, holidays = load_data()
    print(f"train: {train.shape}  test: {test.shape}")

    print("\n===== 特征工程 =====")
    combined = engineer_features(train, test, oil, holidays)
    feat_cols = [c for c in ["year", "month", "day", "dayofweek", "weekofyear",
                             "days_since_2013", "store_nbr", "family",
                             "onpromotion", "promo_r7",
                             "sales_lag1", "sales_lag7", "sales_lag364",
                             "r7", "r14", "r28",
                             "dcoilwtico", "oil_lag1", "oil_lag7",
                             "days_until_holiday", "days_since_holiday",
                             "is_holiday", "is_transfer"]]
    X_all = combined[feat_cols]
    y_all = np.log1p(combined["sales"].values)
    is_train = combined["is_train"].values
    X_train = X_all[is_train].reset_index(drop=True)
    y_train = y_all[is_train]
    X_test = X_all[~is_train].reset_index(drop=True)
    print(f"特征数: {len(feat_cols)}")

    # --- 时间窗口验证(同 v1; 掩码基于排序后的训练行日期, 与 X_train 对齐) ---
    cutoff = train["date"].max() - pd.Timedelta(days=VALIDATION_DAYS)
    sorted_train_dates = combined.loc[is_train, "date"].values
    tr_mask = sorted_train_dates <= cutoff
    X_tr, y_tr = X_train[tr_mask], y_train[tr_mask]
    X_va, y_va = X_train[~tr_mask], y_train[~tr_mask]
    va_true = np.expm1(y_va)
    print(f"训练 {len(X_tr)} 行, 验证 {len(X_va)} 行")

    os.makedirs(CKPT_DIR, exist_ok=True)
    print("\n===== 3 种子 LGBM =====")
    test_preds = []
    for seed in RANDOM_SEEDS:
        ckpt = os.path.join(CKPT_DIR, f"test_pred_seed{seed}.npy")
        if os.path.exists(ckpt):
            print(f"种子 {seed}: 已有断点, 跳过")
            test_preds.append(np.load(ckpt))
            continue
        print(f"\n种子 {seed}: 训练中...")
        model = lgb.LGBMRegressor(
            n_estimators=600, learning_rate=0.05, num_leaves=127,
            min_child_samples=20, subsample=0.8, colsample_bytree=0.8,
            random_state=seed, n_jobs=-1, verbose=-1,
        )
        model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)],
                  callbacks=[lgb.early_stopping(50, verbose=False)])
        va_pred = np.clip(np.expm1(model.predict(X_va)), 0, None)
        print(f"种子 {seed}: val SMAPE {smape(va_true, va_pred):.4f}"
              f"  best_iter {model.best_iteration_}")
        model.fit(X_train, y_train)  # 全量重训(用全部数据)
        tp = np.clip(np.expm1(model.predict(X_test)), 0, None)
        np.save(ckpt, tp)
        test_preds.append(tp)
        print(f"种子 {seed}: 完成并保存断点, 累计用时 {time.time()-t0:.0f}s")

    test_pred = np.mean(test_preds, axis=0)
    print(f"\n平均后: {len(test_preds)} 个种子")

    print("\n===== 生成提交文件 =====")
    # 关键: id 必须用排序后测试行的 id(combined 里保留了原始 id 列),
    # 与 test_pred 的 (store,family,date) 顺序对齐。若用 test["id"]
    # (原始顺序是 (date,store,family)) 会整份错位洗牌 → 公开榜灾难分。
    test_ids = combined.loc[~is_train, "id"].values
    sub = pd.DataFrame({"id": test_ids, "sales": test_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v2.csv")
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行)")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
