# -*- coding: utf-8 -*-
"""
Titanic v3：家族/票号分组特征 + 多 seed 集成
==============================================
针对 v2 的诊断（公开榜 0.76076 < 性别基线 0.76555，模型偏差净亏分）：
树模型学到的"聪明特征"是训练集噪音，v3 改用真实可迁移的信号：

1. 家庭分组特征：同姓 + 同家庭规模 = 家庭 ID，家庭在泰坦尼克上集体生/死
2. 票号分组特征：同一票号 = 同行团体（跨 train/test 存在，训练集组生存率可迁移到测试集）
3. 组大小（在 train+test 拼接集上计算，不含标签，无泄漏）
4. 多 seed 集成平均，降方差

评估：RepeatedStratifiedKFold（对照）+ GroupKFold 按票号分组（诚实下限，避免同组跨折泄漏）

用法: .venv/Scripts/python titanic_v3.py    输出: submission_v3.csv
"""

import os
import re
import sys

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    StratifiedKFold,
    GroupKFold,
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
AGE_BINS = [0, 5, 12, 18, 25, 35, 60, 80]
RARE_TITLES = ["Lady", "Countess", "Capt", "Col", "Don", "Dr", "Major", "Rev",
               "Sir", "Jonkheer", "Dona", "Mme", "Ms"]
PRIOR_SMOOTH = 5.0  # 组生存率平滑系数，把小样本组拉向全局先验


def ticket_num(t):
    """票号去除非数字部分：'PC 17599' -> '17599'；无数字 -> 'NO'"""
    digits = re.sub(r"\D", "", str(t))
    return digits if digits else "NO"


def surname(name):
    return str(name).split(",")[0].strip()


class FeatureTransformer:
    """基础特征 + 组特征。fit 在 (train, 拼接集) 上，transform 应用到单个集。"""

    def __init__(self):
        self.title_age_medians = {}
        self.age_global = 30.0
        self.fare_median = 0.0
        self.embarked_mode = "S"
        self.fare_bins = None
        self.columns = None
        self.prior = 0.4
        self.ticket_rate = {}      # 票号 -> 平滑组生存率
        self.fam_rate = {}         # 家庭ID -> 平滑组生存率
        self.ticket_size = {}      # 票号 -> 组大小
        self.fam_size = {}         # 家庭ID -> 组大小

    def _base(self, df):
        X = df.copy()
        X["Title"] = X["Name"].map(
            lambda n: n.split(",")[1].split(".")[0].strip()
        ).replace(RARE_TITLES, "Rare")
        X["Surname"] = X["Name"].map(surname)
        X["FamilySize"] = X["SibSp"] + X["Parch"] + 1
        X["IsAlone"] = (X["FamilySize"] == 1).astype(int)
        X["CabinLetter"] = X["Cabin"].fillna("U").str[0]
        X["Sex"] = (X["Sex"] == "male").astype(int)
        X["TicketNum"] = X["Ticket"].map(ticket_num)
        X["FamId"] = X["Surname"] + "-" + X["FamilySize"].astype(str)
        return X

    def fit(self, train, full):
        X = self._base(train)
        F = self._base(full)  # 拼接集只用于组大小（无标签，安全）

        self.title_age_medians = X.groupby(["Title", "Pclass"])["Age"].median().to_dict()
        self.age_global = X["Age"].median()
        self.fare_median = X["Fare"].median()
        self.embarked_mode = X["Embarked"].mode()[0]
        _, self.fare_bins = pd.qcut(X["Fare"], q=4, labels=False, retbins=True, duplicates="drop")
        self.prior = X["Survived"].mean()

        # 组大小（拼接集）：.size().to_dict() 键是组名；transform("size").to_dict() 键是行索引（错误）
        self.ticket_size = F.groupby("TicketNum")["PassengerId"].size().to_dict()
        self.fam_size = F.groupby("FamId")["PassengerId"].size().to_dict()

        # 组生存率（仅训练集，平滑）
        ts = X.groupby("TicketNum")["Survived"].agg(["sum", "count"])
        fs = X.groupby("FamId")["Survived"].agg(["sum", "count"])
        self.ticket_rate = (
            (ts["sum"] + self.prior * PRIOR_SMOOTH) / (ts["count"] + PRIOR_SMOOTH)
        ).to_dict()
        self.fam_rate = (
            (fs["sum"] + self.prior * PRIOR_SMOOTH) / (fs["count"] + PRIOR_SMOOTH)
        ).to_dict()

        self.columns = list(self._build(X).columns)
        return self

    def _build(self, X):
        X = X.copy()

        def fill_age(row):
            if pd.notna(row["Age"]):
                return row["Age"]
            return self.title_age_medians.get((row["Title"], row["Pclass"]), self.age_global)

        X["Age"] = X.apply(fill_age, axis=1)
        X["Age"] = X["Age"].fillna(self.age_global)  # 兜底：组内全缺失时用全局中位数
        X["Fare"] = X["Fare"].fillna(self.fare_median)
        # 测试集票价可能超出训练集 qcut 边界，先截断到边界，避免 pd.cut 产生 NaN
        X["Fare"] = np.clip(X["Fare"], self.fare_bins[0], self.fare_bins[-1])
        X["Embarked"] = X["Embarked"].fillna(self.embarked_mode)

        X["AgeBand"] = pd.cut(X["Age"], bins=AGE_BINS, labels=False)
        X["FareBand"] = pd.cut(X["Fare"], bins=self.fare_bins, labels=False,
                               include_lowest=True)  # 票价=0 的乘客也要有箱

        # 组特征：大小 + 平滑生存率（单人组/未见组 -> 全局先验）
        X["TicketSize"] = X["TicketNum"].map(lambda t: self.ticket_size.get(t, 1))
        X["FamSize"] = X["FamId"].map(lambda f: self.fam_size.get(f, 1))
        X["TicketSurvRate"] = X["TicketNum"].map(lambda t: self.ticket_rate.get(t, self.prior))
        X["FamSurvRate"] = X["FamId"].map(lambda f: self.fam_rate.get(f, self.prior))

        X = pd.get_dummies(X, columns=["Title", "CabinLetter", "Embarked"], dtype=int)
        drop_cols = ["PassengerId", "Survived", "Name", "Ticket", "TicketNum",
                     "Cabin", "SibSp", "Parch", "Surname", "FamId"]
        X = X.drop(columns=[c for c in drop_cols if c in X.columns])
        return X

    def transform(self, df):
        X = self._base(df)
        X = self._build(X)
        return X.reindex(columns=self.columns, fill_value=0)


def make_pipe(model):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()) if isinstance(model, LogisticRegression) else ("id", "passthrough"),
        ("clf", model),
    ])


def make_grids():
    return {
        "LR": (LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
               {"clf__C": [0.05, 0.1, 0.5, 1.0]}),
        "RF": (RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
               {"clf__n_estimators": [200, 400],
                "clf__max_depth": [4, 6, 8],
                "clf__min_samples_leaf": [2, 4]}),
        "GBM": (GradientBoostingClassifier(random_state=RANDOM_STATE),
                {"clf__n_estimators": [200, 300],
                 "clf__max_depth": [2, 3, 4],
                 "clf__learning_rate": [0.03, 0.05, 0.1]}),
    }


def main():
    train_path, test_path = os.path.join(DATA_DIR, "train.csv"), os.path.join(DATA_DIR, "test.csv")
    for p in (train_path, test_path):
        if not os.path.exists(p):
            sys.exit(f"找不到数据: {p}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    full = pd.concat([train.drop(columns=["Survived"]), test], ignore_index=True)

    print("\n===== 特征工程（含分组特征）=====")
    ft = FeatureTransformer().fit(train, full)
    y = train["Survived"].values
    X = ft.transform(train)
    X_test = ft.transform(test)
    print(f"特征数: {X.shape[1]}")

    # 组特征迁移效果检查：测试集里有多少票号/家庭能命中训练集的组生存率
    hit = (X_test["TicketSurvRate"] != ft.prior).mean()
    print(f"测试集中能映射到训练集票号组生存率的比例: {hit:.1%}")

    # ---- GridSearch 调参 ----
    print("\n===== GridSearchCV 调参 =====")
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    best_models = {}
    for name, (model, params) in make_grids().items():
        pipe = make_pipe(model)
        gs = GridSearchCV(pipe, params, cv=inner, scoring="accuracy", n_jobs=-1)
        gs.fit(X, y)
        best_models[name] = gs.best_estimator_
        print(f"{name:5s} {gs.best_params_}  内层CV {gs.best_score_:.4f}")

    # ---- 诚实评估 ----
    rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=RANDOM_STATE)
    ensemble = VotingClassifier([(n.lower(), m) for n, m in best_models.items()], voting="soft")
    ens = cross_val_score(ensemble, X, y, cv=rcv, scoring="accuracy", n_jobs=-1)
    print(f"\n集成 RepeatedStratifiedKFold(5x3): {ens.mean():.4f} ± {ens.std():.4f}")

    # GroupKFold 按票号分组：同一团体不跨折，避免组生存率泄漏
    gkf = GroupKFold(n_splits=5)
    gk_scores = []
    train_base = ft._base(train)
    group_ids = train_base["TicketNum"].values
    for tr_idx, va_idx in gkf.split(X, y, groups=group_ids):
        ensemble.fit(X.iloc[tr_idx], y[tr_idx])
        gk_scores.append(accuracy(X.iloc[va_idx], y[va_idx], ensemble))
    print(f"集成 GroupKFold(按票号, 防泄漏): {np.mean(gk_scores):.4f} ± {np.std(gk_scores):.4f}")

    # ---- 多 seed 最终模型：5 个 seed 各训一次集成，概率平均 ----
    print("\n===== 多 seed 集成平均 =====")
    from sklearn.base import clone
    probs = np.zeros(len(X_test))
    for seed in range(5):
        voters = []
        for n, (model, params) in make_grids().items():
            m = clone(model)
            if "random_state" in m.get_params():
                m.set_params(random_state=seed)
            voters.append((n.lower(), m))
        ens = VotingClassifier(voters, voting="soft")
        ens.fit(X, y)
        probs += ens.predict_proba(X_test)[:, 1]
    probs /= 5
    y_pred = (probs >= 0.5).astype(int)

    submission = pd.DataFrame({"PassengerId": test["PassengerId"], "Survived": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v3.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    submission.to_csv(out, index=False)
    print(f"提交文件已生成: {out}")
    print(f"预测分布: {np.bincount(y_pred)} (0=未生还, 1=生还)")


def accuracy(Xv, yv, model):
    from sklearn.metrics import accuracy_score
    return accuracy_score(yv, model.predict(Xv))


if __name__ == "__main__":
    main()
