# -*- coding: utf-8 -*-
"""
Spaceship Titanic - v2 特征工程版
==================================

在 v1 基线基础上做特征工程 + 换用 LGBM/XGBoost：

v2 新增特征:
  1. Cabin 解析 -> Deck(甲板字母) / Side(左右舷 P/S)
  2. PassengerId 前缀组号 -> 组内人数 GroupSize(家庭/同行规模, 本赛最强特征之一)
  3. 消费聚合: TotalSpend 总消费 + NoSpend(全部消费为 0) 指示
  4. CryoSleep 一致性: 冷冻中却仍有消费 = 异常标记
  5. n_missing 每行缺失字段数
  6. 类别特征交给 LGBM 原生处理(不再手工 one-hot)

模型: LightGBM + XGBoost 5 折 CV, 概率平均混合, 与 v1(GB, CV 0.7928) 对比。

用法（项目根目录下）:
    C:/Users/Lenovo/.conda/envs/kaggle/python.exe spaceship_titanic/spaceship_v2.py
"""

import os

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
import xgboost as xgb

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
N_FOLDS = 5
SPEND_COLS = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]


# ---------------------------------------------------------------------------
# 特征工程（v2）
# ---------------------------------------------------------------------------
def engineer_features(df):
    """在训练/测试集上做同样的特征工程，返回处理后的 DataFrame（不含标签/ID）。"""
    df = df.copy()

    # --- 1. Cabin 解析: B/0/P -> Deck=B, Side=P ---
    cabin = df["Cabin"].fillna("U/0/U")
    df["Deck"] = cabin.str.split("/", expand=True)[0]
    df["CabinNum"] = cabin.str.split("/", expand=True)[1].astype(float)
    df["Side"] = cabin.str.split("/", expand=True)[2]

    # --- 2. 乘客组: PassengerId 前缀是组号, 组内人数即同行规模 ---
    df["Group"] = df["PassengerId"].str.split("_", expand=True)[0]
    # 组号 -> 组大小（用 train+test 全量统计，见 main 中合并后调用）
    df["GroupSize"] = df["Group"].map(df["Group"].value_counts())

    # --- 3. 消费聚合 ---
    df["TotalSpend"] = df[SPEND_COLS].sum(axis=1)
    df["NoSpend"] = (df["TotalSpend"] == 0).astype(int)

    # --- 4. CryoSleep 一致性: 冷冻中不应有消费 ---
    df["CryoSpend"] = (
        (df["CryoSleep"] == True) & (df["TotalSpend"] > 0)  # noqa: E712
    ).astype(int)

    # --- 5. n_missing 缺失字段数 ---
    df["n_missing"] = df[["HomePlanet", "CryoSleep", "Cabin", "Destination",
                          "Age", "VIP", "RoomService", "FoodCourt",
                          "ShoppingMall", "Spa", "VRDeck", "Name"]].isna().sum(axis=1)

    # --- 6. Age 缺失用中位数填充, 类别缺失用 'Unknown' ---
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["HomePlanet"] = df["HomePlanet"].fillna("Unknown")
    df["Destination"] = df["Destination"].fillna("Unknown")

    # --- 7. 类别 -> 整数编码 (LabelEncoder) ---
    # 注: 不用 category dtype 是因为 xgboost 3.2.0 + numpy 2.x 原生类别有兼容 bug,
    # 整数编码对树模型效果等价且最稳。
    for col in ["HomePlanet", "Destination", "Deck", "Side", "CryoSleep", "VIP"]:
        df[col] = df[col].fillna("Unknown").astype(str)
        df[col] = LabelEncoder().fit_transform(df[col])

    drop_cols = ["PassengerId", "Transported", "Name", "Cabin", "Group"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    return df


# ---------------------------------------------------------------------------
# 训练与交叉验证
# ---------------------------------------------------------------------------
def run_cv(X, y, X_test, test_ids):
    """5 折 CV: LGBM / XGB / 概率平均混合, 返回 (混合预测 OOF acc, 各模型 acc)。"""
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "LGBM": lgb.LGBMClassifier(
            n_estimators=500, learning_rate=0.05, num_leaves=31,
            min_child_samples=30, subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, n_jobs=-1, verbose=-1,
        ),
        "XGB": xgb.XGBClassifier(
            n_estimators=500, learning_rate=0.05, max_depth=5,
            subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
            enable_categorical=True, random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }

    oof = {name: np.zeros(len(X)) for name in models}
    test_pred = {name: np.zeros(len(X_test)) for name in models}

    for fold, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
        X_tr, X_va = X.iloc[tr_idx], X.iloc[va_idx]
        y_tr, y_va = y.iloc[tr_idx], y.iloc[va_idx]
        for name, model in models.items():
            model.fit(X_tr, y_tr)
            oof[name][va_idx] = model.predict_proba(X_va)[:, 1]
            test_pred[name] += model.predict_proba(X_test)[:, 1] / N_FOLDS

    print("\n===== 5 折 CV (Accuracy) =====")
    results = {}
    for name in models:
        acc = accuracy_score(y, (oof[name] > 0.5).astype(int))
        results[name] = acc
        print(f"{name:6s} OOF acc: {acc:.4f}")

    # 概率平均混合
    blend_prob = sum(oof[name] for name in models) / len(models)
    blend_acc = accuracy_score(y, (blend_prob > 0.5).astype(int))
    results["Blend"] = blend_acc
    print(f"{'Blend':6s} OOF acc: {blend_acc:.4f}")

    best_name = max(results, key=results.get)
    print(f"\n最佳: {best_name} (OOF {results[best_name]:.4f})")

    # 用混合概率生成提交（若单模型更优则用单模型）
    blend_test = sum(test_pred[name] for name in models) / len(models)
    if best_name == "Blend":
        test_prob = blend_test
    else:
        test_prob = test_pred[best_name]
    return best_name, results, test_prob, test_ids


def main():
    print("===== 加载数据 =====")
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    print(f"训练集: {train.shape}  测试集: {test.shape}")

    # 合并做特征工程，保证 train/test 列一致；GroupSize 需要全量统计
    n_train = len(train)
    merged = pd.concat([train.drop(columns=["Transported"]), test], axis=0,
                       ignore_index=True)
    X_all = engineer_features(merged)
    X = X_all.iloc[:n_train].reset_index(drop=True)
    X_test = X_all.iloc[n_train:].reset_index(drop=True)
    y = train["Transported"].astype(int).reset_index(drop=True)
    print(f"\n特征数: {X.shape[1]}  |  列: {list(X.columns)}")

    best_name, results, test_prob, test_ids = run_cv(X, y, X_test, test["PassengerId"])

    print("\n===== 生成提交文件 =====")
    sub = pd.DataFrame({
        "PassengerId": test["PassengerId"],
        "Transported": (test_prob > 0.5).astype(bool),
    })
    out = os.path.join(BASE_DIR, "submissions", "submission_v2.csv")
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行)")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
