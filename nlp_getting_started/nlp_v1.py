# -*- coding: utf-8 -*-
"""
NLP Getting Started - 灾难推文分类 v1 基线
==========================================

判断推特是否在报道真实灾难(而非比喻/广告),二分类,评分指标 **F1**。

v1 思路(经典 NLP 基线):
  - 特征: TF-IDF(text 的词 1-2 gram + 字符 2-4 gram, 捕捉 #hashtag/@mention
    与拼写变体), 用 TfidfVectorizer 直接在 train 上拟合, test 只 transform;
  - 模型: LogisticRegression(稀疏高维特征的标配) 对比 MultinomialNB,
    5 折分层 CV 按 F1 选最优;
  - 输出: id + target(0/1), 与 sample_submission 格式一致。

用法（项目根目录下）:
    C:/Users/Lenovo/.conda/envs/kaggle/python.exe nlp_getting_started/nlp_v1.py
"""

import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import f1_score

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_data():
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    return train, test


def main():
    print("===== 加载数据 =====")
    train, test = load_data()
    print(f"训练集: {train.shape}  测试集: {test.shape}")
    print(f"目标分布: {dict(train['target'].value_counts(normalize=True).round(3))}")

    # --- TF-IDF: 词 1-2 gram + 字符 2-4 gram, 只在 train 上拟合 ---
    print("\n===== TF-IDF 特征 =====")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=3,
        stop_words="english",
    )
    X = vectorizer.fit_transform(train["text"].fillna(""))
    X_test = vectorizer.transform(test["text"].fillna(""))
    y = train["target"].values
    print(f"词特征维度: {X.shape[1]}")

    # --- 5 折分层 CV, 按 F1 选模型 ---
    print("\n===== 5 折交叉验证 (F1) =====")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "MultinomialNB": MultinomialNB(alpha=0.5),
    }
    best_name, best_score, best_model = None, 0.0, None
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
        mean = scores.mean()
        print(f"{name:20s} CV F1: {mean:.4f} ± {scores.std():.4f}  (每折: {scores.round(3)})")
        if mean > best_score:
            best_name, best_score, best_model = name, mean, model
    print(f"\n最佳模型: {best_name} (CV F1 {best_score:.4f})")

    # --- 全量训练 + 生成提交 ---
    print("\n===== 生成提交文件 =====")
    best_model.fit(X, y)
    y_pred = best_model.predict(X_test)
    sub = pd.DataFrame({"id": test["id"], "target": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v1.csv")
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行, 正例占比 {y_pred.mean():.3f})")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
