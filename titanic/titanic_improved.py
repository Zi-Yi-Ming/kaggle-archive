# -*- coding: utf-8 -*-
"""
Titanic 改进版脚本
==================
针对 v1 的问题（CV 0.8384 vs LB 0.76315）做的三处改进：

1. 特征工程方法论修复：
   - FareBand 分箱边界、Age 填充中位数、Fare 填充中位数、Embarked 众数
     全部只从【训练集】拟合，测试集直接套用（旧版在测试集上自己重新算分位数，两边含义不一致）
2. 更稳健的评估：RepeatedStratifiedKFold（5 折 × 3 次重复 = 15 个 CV 分数），
   避免单次划分的运气成分
3. GridSearchCV 调参 + 三个模型 soft-voting 集成

用法:
    .venv/Scripts/python titanic_improved.py
输出: submission_v2.csv
"""

import os
import sys

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    StratifiedKFold,
    GridSearchCV,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
AGE_BINS = [0, 5, 12, 18, 25, 35, 60, 80]  # 固定边界，训练/测试完全一致
RARE_TITLES = ["Lady", "Countess", "Capt", "Col", "Don", "Dr", "Major", "Rev",
               "Sir", "Jonkheer", "Dona", "Mme", "Ms"]


# ---------------------------------------------------------------------------
# 特征工程：fit(训练集) -> transform(任意集)，所有边界/填充值来自训练集
# ---------------------------------------------------------------------------
class FeatureTransformer:
    def __init__(self):
        self.title_age_medians = {}   # (Title, Pclass) -> 年龄中位数
        self.age_global = 30.0        # 兜底中位数
        self.fare_median = 0.0
        self.embarked_mode = "S"
        self.fare_bins = None         # 训练集 qcut 的边界
        self.columns = None           # 训练集特征列（用于对齐测试集）

    def _base(self, df):
        """不依赖训练集统计的基础变换（提取类别、计算组合特征）。"""
        X = df.copy()

        # 称呼
        X["Title"] = X["Name"].map(
            lambda n: n.split(",")[1].split(".")[0].strip()
        ).replace(RARE_TITLES, "Rare")

        # 家庭
        X["FamilySize"] = X["SibSp"] + X["Parch"] + 1
        X["IsAlone"] = (X["FamilySize"] == 1).astype(int)

        # 舱位甲板
        X["CabinLetter"] = X["Cabin"].fillna("U").str[0]

        # 性别 -> 0/1
        X["Sex"] = (X["Sex"] == "male").astype(int)
        return X

    def fit(self, train):
        X = self._base(train)
        self.title_age_medians = (
            X.groupby(["Title", "Pclass"])["Age"].median().to_dict()
        )
        self.age_global = X["Age"].median()
        self.fare_median = X["Fare"].median()
        self.embarked_mode = X["Embarked"].mode()[0]
        # 关键修复：FareBand 分位边界只在训练集上计算一次
        _, self.fare_bins = pd.qcut(
            X["Fare"], q=4, labels=False, retbins=True, duplicates="drop"
        )
        self.columns = list(self._build(X).columns)
        return self

    def _build(self, X):
        X = X.copy()

        # 缺失值填充（全部用训练集学到的值）
        def fill_age(row):
            if pd.notna(row["Age"]):
                return row["Age"]
            return self.title_age_medians.get(
                (row["Title"], row["Pclass"]), self.age_global
            )

        X["Age"] = X.apply(fill_age, axis=1)
        X["Fare"] = X["Fare"].fillna(self.fare_median)
        X["Embarked"] = X["Embarked"].fillna(self.embarked_mode)

        # 分箱
        X["AgeBand"] = pd.cut(X["Age"], bins=AGE_BINS, labels=False)
        X["FareBand"] = pd.cut(X["Fare"], bins=self.fare_bins, labels=False)

        # 类别 -> one-hot
        X = pd.get_dummies(X, columns=["Title", "CabinLetter", "Embarked"], dtype=int)

        drop_cols = ["PassengerId", "Survived", "Name", "Ticket", "Cabin", "SibSp", "Parch"]
        X = X.drop(columns=[c for c in drop_cols if c in X.columns])
        return X

    def transform(self, df):
        X = self._base(df)
        X = self._build(X)
        # 与训练集列对齐：测试集多出的类别列丢弃，缺失的补 0
        return X.reindex(columns=self.columns, fill_value=0)


# ---------------------------------------------------------------------------
# 模型：三份参数字典 + 网格搜索 + 集成
# ---------------------------------------------------------------------------
def make_grids():
    return {
        "LogisticRegression": {
            "model": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
            "pipe": Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
            ]),
            "params": {"clf__C": [0.05, 0.1, 0.5, 1.0, 5.0]},
        },
        "RandomForest": {
            "model": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
            "pipe": Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("clf", RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)),
            ]),
            "params": {
                "clf__n_estimators": [200, 400],
                "clf__max_depth": [4, 6, 8],
                "clf__min_samples_leaf": [2, 4],
            },
        },
        "GradientBoosting": {
            "model": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "pipe": Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("clf", GradientBoostingClassifier(random_state=RANDOM_STATE)),
            ]),
            "params": {
                "clf__n_estimators": [200, 300],
                "clf__max_depth": [2, 3, 4],
                "clf__learning_rate": [0.03, 0.05, 0.1],
            },
        },
    }


def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    test_path = os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    print(f"训练集: {train.shape}  测试集: {test.shape}")

    # ---- 特征工程（fit on train, transform both）----
    print("\n===== 特征工程 =====")
    ft = FeatureTransformer().fit(train)
    y = train["Survived"].values
    X = ft.transform(train)
    X_test = ft.transform(test)
    print(f"特征数: {X.shape[1]}")

    # ---- 网格搜索调参（内层 5 折）----
    print("\n===== GridSearchCV 调参 =====")
    inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    best_models = {}
    for name, cfg in make_grids().items():
        gs = GridSearchCV(cfg["pipe"], cfg["params"], cv=inner_cv,
                          scoring="accuracy", n_jobs=-1)
        gs.fit(X, y)
        best_models[name] = gs.best_estimator_
        print(f"{name:20s} 最佳参数: {gs.best_params_}  内层CV: {gs.best_score_:.4f}")

    # ---- 重复 K 折 CV 诚实评估（5 折 × 3 次）----
    print("\n===== 重复交叉验证 (5折 x 3次, 指标=Accuracy) =====")
    rcv = RepeatedStratifiedKFold(
        n_splits=5, n_repeats=3, random_state=RANDOM_STATE
    )
    results = {}
    for name, model in best_models.items():
        scores = cross_val_score(model, X, y, cv=rcv, scoring="accuracy", n_jobs=-1)
        results[name] = scores
        print(f"{name:20s} CV: {scores.mean():.4f} ± {scores.std():.4f}")

    # ---- 集成：三个调参后模型 soft voting ----
    ensemble = VotingClassifier(
        estimators=[(n.lower(), m) for n, m in best_models.items()],
        voting="soft",
    )
    ens_scores = cross_val_score(ensemble, X, y, cv=rcv, scoring="accuracy", n_jobs=-1)
    results["Ensemble(Voting)"] = ens_scores
    print(f"{'Ensemble(Voting)':20s} CV: {ens_scores.mean():.4f} ± {ens_scores.std():.4f}")

    # ---- 选 CV 最好的模型，重训并预测 ----
    best_name = max(results, key=lambda k: results[k].mean())
    print(f"\nCV 最高: {best_name} ({results[best_name].mean():.4f})")
    final_model = ensemble if best_name == "Ensemble(Voting)" else best_models[best_name]
    final_model.fit(X, y)
    y_pred = final_model.predict(X_test)

    submission = pd.DataFrame({
        "PassengerId": test["PassengerId"],
        "Survived": y_pred,
    })
    out = os.path.join(BASE_DIR, "submissions", "submission_v2.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"提交文件已生成: {out}")
    print(f"预测分布: {np.bincount(y_pred)} (0=未生还, 1=生还)")


if __name__ == "__main__":
    main()
