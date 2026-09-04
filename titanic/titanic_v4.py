# -*- coding: utf-8 -*-
"""
Titanic v4：最小可靠模型（新基线）
==================================
v1~v3 的教训：树模型在 891 行上学的"聪明特征"（年龄/票价/称呼/分组率）
很大程度是训练集噪音，公开榜分数与性别基线（0.76555）持平甚至更低。

v4 原则：
1. 只用信号最强、最不可能过拟合的特征：Sex / Pclass / 人均票价 / 年龄
2. 模型用逻辑回归（小数据上比树稳），对照随机森林
3. 本地同时评估"性别基线规则"的准确率作为对照线 ——
   模型 CV 必须显著高于性别规则，才值得提交
4. 输出"v4 预测 vs 性别基线"的逐行差异清单，提前发现提交层面的问题
   （行数对齐、PassengerId 错位、预测方向异常等）

用法: .venv/Scripts/python titanic_v4.py    输出: submissions/submission_v4.csv
"""

import os
import sys

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RARE_TITLES = ["Lady", "Countess", "Capt", "Col", "Don", "Dr", "Major", "Rev",
               "Sir", "Jonkheer", "Dona", "Mme", "Ms"]


class FeatureTransformer:
    """v4 最小特征集：fit(训练集) -> transform(任意集)，无任何组统计。"""

    def __init__(self):
        self.title_age_medians = {}
        self.age_global = 30.0
        self.columns = None

    def _base(self, df):
        X = df.copy()
        X["Title"] = X["Name"].map(
            lambda n: n.split(",")[1].split(".")[0].strip()
        ).replace(RARE_TITLES, "Rare")
        X["Sex"] = (X["Sex"] == "male").astype(int)
        return X

    def fit(self, train):
        X = self._base(train)
        self.title_age_medians = X.groupby(["Title", "Pclass"])["Age"].median().to_dict()
        self.age_global = X["Age"].median()
        self.columns = list(self._build(X).columns)
        return self

    def _build(self, X):
        X = X.copy()

        # 年龄缺失：按 (Title, Pclass) 中位数填充，兜底全局中位数
        def fill_age(row):
            if pd.notna(row["Age"]):
                return row["Age"]
            return self.title_age_medians.get((row["Title"], row["Pclass"]), self.age_global)

        X["Age"] = X.apply(fill_age, axis=1).fillna(self.age_global)
        X["Fare"] = X["Fare"].fillna(X["Fare"].median())

        # 人均票价：整团合买的票均摊到每个人，比总票价更稳定
        X["FarePerPerson"] = X["Fare"] / (X["SibSp"] + X["Parch"] + 1)

        # 只保留 4 个最稳的信号，其余全部丢弃
        keep = ["Sex", "Pclass", "Age", "FarePerPerson"]
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
    print(f"训练集: {train.shape}  测试集: {test.shape}")

    print("\n===== 特征工程（最小可靠集）=====")
    ft = FeatureTransformer().fit(train)
    y = train["Survived"].values
    X = ft.transform(train)
    X_test = ft.transform(test)
    print(f"特征: {list(X.columns)}  特征数: {X.shape[1]}")

    # ---- 对照线：性别基线规则在相同折上的准确率 ----
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=RANDOM_STATE)
    rule_scores = gender_rule_cv(X, y, cv)
    print(f"\n性别基线规则 CV(5x3): {rule_scores.mean():.4f} ± {rule_scores.std():.4f}  <- 对照线")

    # ---- 模型对比：LR vs RF，必须显著高于对照线才有意义 ----
    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(
            n_estimators=300, max_depth=4, min_samples_leaf=3,
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }
    print("\n===== 模型 CV（对照线 = 性别规则）=====")
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy", n_jobs=-1)
        results[name] = scores
        lift = scores.mean() - rule_scores.mean()
        print(f"{name:20s} CV: {scores.mean():.4f} ± {scores.std():.4f}   相对性别基线: {lift:+.4f}")

    # ---- 选 CV 最高的模型做最终提交 ----
    best_name = max(results, key=lambda k: results[k].mean())
    final = models[best_name]
    final.fit(X, y)
    y_pred = final.predict(X_test)
    print(f"\n选用: {best_name}")

    submission = pd.DataFrame({"PassengerId": test["PassengerId"], "Survived": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v4.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"提交文件已生成: {out}")
    print(f"预测分布: {np.bincount(y_pred)} (0=未生还, 1=生还)  生还率: {y_pred.mean():.1%}")

    # ---- 与性别基线的逐行差异（提交层面的健康检查）----
    gb = (test["Sex"] == "female").astype(int)  # 性别基线：女性生还
    diff = (y_pred != gb.values)
    print(f"\n===== v4 vs 性别基线 差异检查 =====")
    print(f"与性别基线一致的预测: {len(y_pred) - diff.sum()}/{len(y_pred)}"
          f" ({1 - diff.mean():.1%})")
    male_pred_survive = (diff) & (test["Sex"] == "male") & (y_pred == 1)
    print(f"其中'男性被预测生还'的差异行: {male_pred_survive.sum()}  <- 这类行最可疑，通常为噪音")

    # 按测试集原始顺序输出差异行，方便人工核对
    show = pd.DataFrame({
        "PassengerId": test["PassengerId"], "Sex": test["Sex"], "Pclass": test["Pclass"],
        "Age": test["Age"], "Fare": test["Fare"], "性别基线": gb, "v4预测": y_pred,
    })[diff]
    print(f"\n差异行明细（前 20 行）:")
    print(show.head(20).to_string(index=False))
    if diff.sum() == 0:
        print("（无差异：v4 预测与性别基线完全相同，说明额外特征没起作用）")

    # PassengerId 对齐检查：提交行序必须与测试集一致
    align = (submission["PassengerId"].values == test["PassengerId"].values).all()
    print(f"\nPassengerId 与 test.csv 顺序一致: {align}")


if __name__ == "__main__":
    main()
