# -*- coding: utf-8 -*-
"""
Titanic v6：v4 特征 + 无泄漏的组大小特征
==========================================
v3 的教训：用训练集的【组生存率】迁移到测试集是假信号（公开榜 0.72248）。
v6 只加【组大小】特征——统计 train+test 拼接集上"同一船舱 / 同一票号"
有多少人，完全不用目标变量，不存在泄漏：

1. CabinCount：同舱人数（同一 Cabin 字符串出现几次）。缺失 -> 0
2. TicketCount：同票人数（同一 Ticket 字符串出现几次，整团购票）

真实动机：同行团体在灾难中一起生/死的相关性，来自"团体行为"而非"组标签"，
团体大小本身是可迁移的结构信号（v3 的 ticket_size 也验证了这一点）。

评估照旧：RepeatedStratifiedKFold，始终和性别基线规则对照（相同折）。

用法: .venv/Scripts/python titanic_v6.py    输出: submissions/submission_v6.csv
"""

import os
import sys

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    StackingClassifier,
)
from sklearn.metrics import accuracy_score
from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    StratifiedKFold,
    GridSearchCV,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RARE_TITLES = ["Lady", "Countess", "Capt", "Col", "Don", "Dr", "Major", "Rev",
               "Sir", "Jonkheer", "Dona", "Mme", "Ms"]


class FeatureTransformer:
    """v4 的 4 特征 + 组大小特征（大小只在拼接集上算，不含标签，无泄漏）。"""

    def __init__(self):
        self.title_age_medians = {}
        self.age_global = 30.0
        self.cabin_size = {}    # Cabin -> 同舱人数
        self.ticket_size = {}   # Ticket -> 同票人数
        self.columns = None

    def _base(self, df):
        X = df.copy()
        X["Title"] = X["Name"].map(
            lambda n: n.split(",")[1].split(".")[0].strip()
        ).replace(RARE_TITLES, "Rare")
        X["Sex"] = (X["Sex"] == "male").astype(int)
        X["CabinKey"] = X["Cabin"].fillna("NONE")
        X["TicketKey"] = X["Ticket"].astype(str)
        return X

    def fit(self, train, full):
        X = self._base(train)
        F = self._base(full)  # 拼接集只用于组大小统计（无标签，安全）

        self.title_age_medians = X.groupby(["Title", "Pclass"])["Age"].median().to_dict()
        self.age_global = X["Age"].median()
        # 组大小只统计真实舱位；缺失舱位（"NONE" 组）不参与，避免缺失被算成 1014 人同组
        real_cabins = F[F["Cabin"].notna()]
        self.cabin_size = real_cabins.groupby("CabinKey")["PassengerId"].size().to_dict()
        self.ticket_size = F.groupby("TicketKey")["PassengerId"].size().to_dict()
        self.columns = list(self._build(X).columns)
        return self

    def _build(self, X):
        X = X.copy()

        def fill_age(row):
            if pd.notna(row["Age"]):
                return row["Age"]
            return self.title_age_medians.get((row["Title"], row["Pclass"]), self.age_global)

        X["Age"] = X.apply(fill_age, axis=1).fillna(self.age_global)
        X["Fare"] = X["Fare"].fillna(X["Fare"].median())
        X["FarePerPerson"] = X["Fare"] / (X["SibSp"] + X["Parch"] + 1)

        # 组大小（缺失舱位 -> 0）
        X["CabinCount"] = X["CabinKey"].map(lambda c: self.cabin_size.get(c, 0))
        X["TicketCount"] = X["TicketKey"].map(lambda t: self.ticket_size.get(t, 1))

        keep = ["Sex", "Pclass", "Age", "FarePerPerson", "CabinCount", "TicketCount"]
        return X[keep]

    def transform(self, df):
        X = self._base(df)
        X = self._build(X)
        return X.reindex(columns=self.columns, fill_value=0)


def gender_rule_cv(X, y, cv):
    """性别基线规则（女性全活、男性全死）在相同折上的 CV 准确率。"""
    scores = []
    for tr_idx, va_idx in cv.split(X, y):
        pred = (X.iloc[va_idx]["Sex"] == 0).astype(int)
        scores.append(accuracy_score(y[va_idx], pred))
    return np.array(scores)


def main():
    train_path, test_path = os.path.join(DATA_DIR, "train.csv"), os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    full = pd.concat([train.drop(columns=["Survived"]), test], ignore_index=True)
    print(f"训练集: {train.shape}  测试集: {test.shape}")

    print("\n===== 特征工程（v4 特征 + 组大小）=====")
    ft = FeatureTransformer().fit(train, full)
    y = train["Survived"].values
    X = ft.transform(train)
    X_test = ft.transform(test)
    print(f"特征: {list(X.columns)}  特征数: {X.shape[1]}")
    print(f"CabinCount 分布: {dict(X['CabinCount'].value_counts().sort_index())}")
    print(f"TicketCount>1 占比: {(X['TicketCount'] > 1).mean():.1%}")

    # ---- 对照线：性别基线规则 ----
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=RANDOM_STATE)
    rule_scores = gender_rule_cv(X, y, cv)
    print(f"\n性别基线规则 CV(5x2): {rule_scores.mean():.4f} ± {rule_scores.std():.4f}  <- 对照线")

    # ---- 精细调参（沿用 v5 的参数空间）----
    print("\n===== GridSearchCV 调参 =====")
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        {"n_estimators": [400],
         "max_depth": [3, 4, 5],
         "min_samples_leaf": [2, 4],
         "max_features": [0.5, 0.7]},
        cv=inner, scoring="accuracy", n_jobs=-1,
    )
    rf_grid.fit(X, y)
    print(f"RF     {rf_grid.best_params_}  内层CV {rf_grid.best_score_:.4f}")

    gbm_grid = GridSearchCV(
        GradientBoostingClassifier(random_state=RANDOM_STATE),
        {"n_estimators": [200, 400],
         "max_depth": [2, 3],
         "learning_rate": [0.03, 0.05],
         "subsample": [0.8, 1.0]},
        cv=inner, scoring="accuracy", n_jobs=-1,
    )
    gbm_grid.fit(X, y)
    print(f"GBM    {gbm_grid.best_params_}  内层CV {gbm_grid.best_score_:.4f}")

    # ---- 模型对比：TunedRF / TunedGBM / Stacking ----
    stacking = StackingClassifier(
        estimators=[("rf", rf_grid.best_estimator_), ("gbm", gbm_grid.best_estimator_)],
        final_estimator=Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        ]),
        cv=3, stack_method="predict_proba", n_jobs=-1,
    )
    models = {
        "TunedRF": rf_grid.best_estimator_,
        "TunedGBM": gbm_grid.best_estimator_,
        "Stacking": stacking,
    }

    print("\n===== 模型 CV（对照线 = 性别规则）=====")
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy", n_jobs=-1)
        results[name] = scores
        lift = scores.mean() - rule_scores.mean()
        print(f"{name:10s} CV: {scores.mean():.4f} ± {scores.std():.4f}   相对性别基线: {lift:+.4f}")

    best_name = max(results, key=lambda k: results[k].mean())
    print(f"\n选用: {best_name}")

    # ---- 最终模型：重训 + 预测 ----
    final = models[best_name]
    final.fit(X, y)
    y_pred = final.predict(X_test)

    submission = pd.DataFrame({"PassengerId": test["PassengerId"], "Survived": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v6.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"提交文件已生成: {out}")
    print(f"预测分布: {np.bincount(y_pred)} (0=未生还, 1=生还)  生还率: {y_pred.mean():.1%}")

    # ---- 与性别基线的逐行差异（提交健康检查）----
    gb = (test["Sex"] == "female").astype(int)
    diff = (y_pred != gb.values)
    print(f"\n===== {best_name} vs 性别基线 差异检查 =====")
    print(f"与性别基线一致的预测: {len(y_pred) - diff.sum()}/{len(y_pred)} ({1 - diff.mean():.1%})")
    male_pred_survive = (diff) & (test["Sex"] == "male") & (y_pred == 1)
    print(f"其中'男性被预测生还'的差异行: {male_pred_survive.sum()}")

    show = pd.DataFrame({
        "PassengerId": test["PassengerId"], "Sex": test["Sex"], "Pclass": test["Pclass"],
        "Age": test["Age"], "Fare": test["Fare"], "性别基线": gb, "预测": y_pred,
    })[diff]
    print("\n差异行明细（前 20 行）:")
    print(show.head(20).to_string(index=False))

    align = (submission["PassengerId"].values == test["PassengerId"].values).all()
    print(f"\nPassengerId 与 test.csv 顺序一致: {align}")


if __name__ == "__main__":
    main()
