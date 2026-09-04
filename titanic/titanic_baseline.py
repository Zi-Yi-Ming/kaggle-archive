# -*- coding: utf-8 -*-
"""
Titanic - Machine Learning from Disaster 基线脚本
==================================================

一条命令跑通完整流程：加载数据 → EDA → 特征工程 → 交叉验证 → 模型对比 → 生成提交文件

用法（在项目根目录 D:/桌面/Kaggle 下）:
    .venv/Scripts/python titanic_baseline.py

要求数据已放在 data/ 目录下（train.csv / test.csv），否则脚本会给出提示。
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 无图形界面环境下也能运行，不弹窗
import matplotlib.pyplot as plt
import seaborn as sns

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
            "请先从 Kaggle 比赛页面 (https://www.kaggle.com/competitions/titanic/data)\n"
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
    """打印关键统计信息并保存几张生存率分析图。"""
    print("\n===== EDA =====")
    print("\n[缺失值统计]")
    missing = pd.concat(
        [train.isnull().sum(), test.isnull().sum()], axis=1, keys=["train", "test"]
    )
    print(missing[missing.sum(axis=1) > 0])

    print("\n[目标变量分布]")
    print(train["Survived"].value_counts(normalize=True).round(3))

    print("\n[各特征与生存率的关系]")
    for col in ["Sex", "Pclass", "Embarked"]:
        rate = train.groupby(col)["Survived"].mean().round(3)
        print(f"- {col}: {dict(rate)}")

    # 画三张图：性别/舱位/年龄 vs 生存率
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sns.barplot(x="Pclass", y="Survived", data=train, ax=axes[0])
    axes[0].set_title("Survival by Pclass")
    sns.barplot(x="Sex", y="Survived", data=train, ax=axes[1])
    axes[1].set_title("Survival by Sex")
    age = train.dropna(subset=["Age"])
    sns.histplot(x="Age", hue="Survived", data=age, kde=True, bins=30, ax=axes[2])
    axes[2].set_title("Age distribution by Survival")
    fig.tight_layout()
    fig.savefig(os.path.join(BASE_DIR, "eda_overview.png"), dpi=100)
    print("\nEDA 图已保存: eda_overview.png")


# ---------------------------------------------------------------------------
# 3. 特征工程
# ---------------------------------------------------------------------------
def extract_title(name):
    """从姓名中提取称呼，如 Mr / Mrs / Miss / Master。"""
    return name.split(",")[1].split(".")[0].strip()


def engineer_features(df):
    """
    在训练/测试集上做同样的特征工程（必须保持一致，否则模型会出错）。
    返回处理后的 DataFrame（不含 Survived / PassengerId）。
    """
    df = df.copy()

    # --- 3.1 姓名 -> 称呼 Title ---
    df["Title"] = df["Name"].map(extract_title)
    # 把稀有称呼合并成 Rare，避免出现训练/测试集分布不一致的分类
    rare_titles = ["Lady", "Countess", "Capt", "Col", "Don", "Dr", "Major", "Rev",
                   "Sir", "Jonkheer", "Dona", "Mme", "Ms"]
    df["Title"] = df["Title"].replace(rare_titles, "Rare")

    # --- 3.2 家庭规模 FamilySize 与是否独自一人 IsAlone ---
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

    # --- 3.3 舱位 Cabin 首字母（A/B/C/D/E 为甲板编号，缺失填 U）---
    df["CabinLetter"] = df["Cabin"].fillna("U").str[0]

    # --- 3.4 Age 缺失值：按 (Title, Pclass) 分组的中位数填充 ---
    df["Age"] = df.groupby(["Title", "Pclass"])["Age"].transform(
        lambda s: s.fillna(s.median())
    )

    # --- 3.5 Fare 缺失值：用全体中位数填充（测试集偶发）---
    df["Fare"] = df["Fare"].fillna(df["Fare"].median())

    # --- 3.6 Embarked 缺失值：用众数填充 ---
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # --- 3.7 分箱：把连续变量变成有序类别，让树模型更好用 ---
    df["AgeBand"] = pd.cut(df["Age"], bins=[0, 12, 18, 30, 50, 80], labels=False)
    df["FareBand"] = pd.qcut(df["Fare"], q=4, labels=False, duplicates="drop")

    # --- 3.8 性别 -> 0/1 ---
    df["Sex"] = (df["Sex"] == "male").astype(int)

    # --- 3.9 把类别特征做 one-hot（避免模型误认为有大小关系）---
    df = pd.get_dummies(df, columns=["Title", "CabinLetter", "Embarked"], dtype=int)

    # 丢弃用不到的列（Survived 是标签，绝不能当特征，否则会泄漏）
    drop_cols = ["PassengerId", "Survived", "Name", "Ticket", "Cabin", "SibSp", "Parch"]
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
    parser = argparse.ArgumentParser(description="Titanic 基线流程")
    parser.add_argument("--train", default=os.path.join(DATA_DIR, "train.csv"))
    parser.add_argument("--test", default=os.path.join(DATA_DIR, "test.csv"))
    parser.add_argument("--output", default=os.path.join(BASE_DIR, "submissions", "submission.csv"))
    parser.add_argument("--no-eda", action="store_true", help="跳过 EDA 绘图")
    args = parser.parse_args()

    # 1. 加载
    train, test = load_data(args.train, args.test)

    # 2. EDA
    if not args.no_eda:
        run_eda(train, test)

    # 3. 特征工程（训练/测试一起处理，保证列一致）
    print("\n===== 特征工程 =====")
    y = train["Survived"]
    X = engineer_features(train)
    X_test = engineer_features(test)
    # 训练/测试特征列取并集，缺失的列补 0（防止测试集出现训练时没见过的类别）
    all_cols = list(set(X.columns) | set(X_test.columns))
    X = X.reindex(columns=all_cols, fill_value=0)
    X_test = X_test.reindex(columns=all_cols, fill_value=0)
    print(f"特征数: {X.shape[1]}  |  示例: {list(X.columns[:8])}")

    # 4. 模型对比 + 交叉验证
    best_name, best_model = evaluate_models(make_models(), X, y)

    # 5. 用全部训练数据重训最佳模型，预测测试集
    print(f"\n===== 用全部数据重训 {best_name} 并预测 =====")
    best_model.fit(X, y)
    y_pred = best_model.predict(X_test)

    # 6. 生成提交文件
    submission = pd.DataFrame({
        "PassengerId": test["PassengerId"],
        "Survived": y_pred,
    })
    submission.to_csv(args.output, index=False)
    print(f"提交文件已生成: {args.output}")
    print(f"预测分布: {np.bincount(y_pred)} (0=未生还, 1=生还)")


if __name__ == "__main__":
    main()
