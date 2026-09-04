# -*- coding: utf-8 -*-
"""
Spaceship Titanic - 基线脚本
=============================

一条命令跑通完整流程：加载数据 → EDA → 特征工程 → 交叉验证 → 模型对比 → 生成提交文件

用法（在项目根目录 D:/桌面/Kaggle 下）:
    C:/Users/Lenovo/.conda/envs/kaggle/python.exe spaceship_titanic/spaceship_baseline.py

要求数据已放在 spaceship_titanic/data/ 目录下（train.csv / test.csv）。
评分指标: Accuracy（预测是否被传送 Transported，二分类，类别均衡）。
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ---------------------------------------------------------------------------
# 1. 加载数据
# ---------------------------------------------------------------------------
def load_data(train_path, test_path):
    """加载训练集和测试集；文件缺失时给出清晰的报错。"""
    if not os.path.exists(train_path):
        sys.exit(
            f"找不到训练数据: {train_path}\n"
            "请先从 Kaggle 比赛页面 (https://www.kaggle.com/competitions/spaceship-titanic/data)\n"
            "下载 train.csv / test.csv 放到 data/ 目录下。"
        )
    if not os.path.exists(test_path):
        sys.exit(f"找不到测试数据: {test_path}\n请同样把 test.csv 放到 data/ 目录下。")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    print(f"训练集: {train.shape}  测试集: {test.shape}")
    return train, test


# ---------------------------------------------------------------------------
# 2. EDA（探索性数据分析）
# ---------------------------------------------------------------------------
def run_eda(train, test):
    """打印关键统计信息：缺失值、目标分布、单特征与目标的关系。"""
    print("\n===== EDA =====")
    print("\n[缺失值统计]")
    missing = pd.concat(
        [train.isnull().sum(), test.isnull().sum()], axis=1, keys=["train", "test"]
    )
    print(missing[missing.sum(axis=1) > 0])

    print("\n[目标变量分布]")
    print(train["Transported"].value_counts(normalize=True).round(3))

    print("\n[各特征与目标的关系]")
    for col in ["HomePlanet", "CryoSleep", "Destination", "VIP"]:
        rate = train.groupby(col)["Transported"].mean().round(3)
        print(f"- {col}: {dict(rate)}")
    age = train.dropna(subset=["Age"])
    print(f"- Age: 传走均值 {age.loc[age.Transported, 'Age'].mean():.1f} vs "
          f"未传走均值 {age.loc[~age.Transported, 'Age'].mean():.1f}")
    spend_cols = ["RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
    total = train[spend_cols].sum(axis=1)
    print(f"- 总消费: 传走均值 {total[train.Transported].mean():.0f} vs "
          f"未传走均值 {total[~train.Transported].mean():.0f}")


# ---------------------------------------------------------------------------
# 3. 特征工程（v1 基线版：只做最基础的填充 + one-hot，不做深入特征）
# ---------------------------------------------------------------------------
def engineer_features(df):
    """
    在训练/测试集上做同样的特征工程（必须保持一致）。
    返回处理后的 DataFrame（不含 Transported / PassengerId）。
    """
    df = df.copy()

    # --- 类别列填充缺失（用众数）---
    for col in ["HomePlanet", "Destination", "CryoSleep", "VIP"]:
        df[col] = df[col].fillna(df[col].mode()[0])

    # --- 数值列填充缺失（用中位数）---
    numeric_cols = ["Age", "RoomService", "FoodCourt", "ShoppingMall", "Spa", "VRDeck"]
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # --- 布尔/类别 -> 0/1 ---
    df["CryoSleep"] = (df["CryoSleep"] == True).astype(int)  # noqa: E712
    df["VIP"] = (df["VIP"] == True).astype(int)  # noqa: E712

    # --- 类别特征 one-hot ---
    df = pd.get_dummies(df, columns=["HomePlanet", "Destination"], dtype=int)

    # 丢弃用不到的列（Transported 是标签，绝不能当特征，否则会泄漏）
    drop_cols = ["PassengerId", "Transported", "Name", "Cabin"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    return df


# ---------------------------------------------------------------------------
# 4. 训练与交叉验证
# ---------------------------------------------------------------------------
def make_models():
    """返回 {模型名: 流水线} 字典。流水线 = 缺失值填充 + 标准化 + 模型。"""
    return {
        "LogisticRegression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]),
        "RandomForest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("clf", RandomForestClassifier(
                n_estimators=300, max_depth=6, min_samples_leaf=3,
                random_state=RANDOM_STATE, n_jobs=-1,
            )),
        ]),
        "GradientBoosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("clf", GradientBoostingClassifier(
                n_estimators=300, max_depth=3, learning_rate=0.05,
                random_state=RANDOM_STATE,
            )),
        ]),
    }


def evaluate_models(models, X, y):
    """5 折分层交叉验证，打印各模型准确率，返回最好的模型。"""
    print("\n===== 交叉验证 (5-Fold, 指标=Accuracy) =====")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    best_name, best_score, best_model = None, 0.0, None
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
        mean, std = scores.mean(), scores.std()
        print(f"{name:20s} CV 准确率: {mean:.4f} ± {std:.4f}   (每折: {scores.round(3)})")
        if mean > best_score:
            best_name, best_score, best_model = name, mean, model
    print(f"\n最佳模型: {best_name} (CV 准确率 {best_score:.4f})")
    return best_name, best_model


# ---------------------------------------------------------------------------
# 5. 主流程
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Spaceship Titanic 基线流程")
    parser.add_argument("--train", default=os.path.join(DATA_DIR, "train.csv"))
    parser.add_argument("--test", default=os.path.join(DATA_DIR, "test.csv"))
    parser.add_argument("--output", default=os.path.join(BASE_DIR, "submissions", "submission_baseline.csv"))
    parser.add_argument("--no-eda", action="store_true", help="跳过 EDA")
    args = parser.parse_args()

    # 1. 加载
    train, test = load_data(args.train, args.test)

    # 2. EDA
    if not args.no_eda:
        run_eda(train, test)

    # 3. 特征工程（训练/测试一起处理，保证列一致）
    print("\n===== 特征工程 =====")
    y = train["Transported"].astype(int)
    X = engineer_features(train)
    X_test = engineer_features(test)
    # 训练/测试特征列取并集，缺失的列补 0（防止测试集出现训练时没见过的类别）
    all_cols = list(set(X.columns) | set(X_test.columns))
    X = X.reindex(columns=all_cols, fill_value=0)
    X_test = X_test.reindex(columns=all_cols, fill_value=0)
    print(f"特征数: {X.shape[1]}  |  示例: {list(X.columns[:8])}")

    # 4. 模型对比 + 交叉验证
    models = make_models()
    best_name, best_model = evaluate_models(models, X, y)

    # 5. 用最佳模型在全量训练集上训练并预测测试集，生成提交文件
    print("\n===== 生成提交文件 =====")
    best_model.fit(X, y)
    y_pred = best_model.predict(X_test)
    # 注意: 该比赛要求 Transported 列输出布尔 True/False（样例格式），
    # 输出 0/1 会被判 0 分，必须转成 bool。
    sub = pd.DataFrame({"PassengerId": test["PassengerId"],
                        "Transported": y_pred.astype(bool)})
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    sub.to_csv(args.output, index=False)
    print(f"提交文件已生成: {args.output}  (共 {len(sub)} 行)")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
