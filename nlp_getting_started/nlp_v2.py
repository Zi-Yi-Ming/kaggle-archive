# -*- coding: utf-8 -*-
"""
NLP Getting Started - 灾难推文分类 v2
=====================================

在 v1(TF-IDF + LR, CV F1 0.7459) 基础上提升:

v2 新增:
  1. TF-IDF 加 char 2-4 gram(v1 只有 word 1-2 gram, 字符 n-gram 能捕捉
     #hashtag/@mention/拼写变体)
  2. keyword 特征: 拼进 text(缺失填 "unknown" 标记)——keyword 缺失本身是信号
  3. Word2Vec 词向量(在 train+test 文本上自训练, dim=100) →
     TF-IDF 加权句子向量 → LR
  4. 概率平均混合: LR(TF-IDF) + LR(W2V 句向量), 5 折 CV 按 F1 评估

用法（项目根目录下）:
    C:/Users/Lenovo/.conda/envs/kaggle/python.exe nlp_getting_started/nlp_v2.py
"""

import os
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
from sklearn.preprocessing import normalize
from gensim.models import Word2Vec

RANDOM_STATE = 42
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
N_FOLDS = 5
W2V_DIM = 100

_TOKEN_RE = re.compile(r"[a-z0-9#@]+")


def tokenize(text):
    """小写 + 只留字母数字#@(保留 hashtag/@mention 信号)。"""
    return _TOKEN_RE.findall(text.lower())


def load_data():
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    return train, test


def main():
    print("===== 加载数据 =====")
    train, test = load_data()
    print(f"训练集: {train.shape}  测试集: {test.shape}")

    # --- keyword 拼进 text(缺失填 unknown 标记) ---
    for df in (train, test):
        df["text_aug"] = df["text"].fillna("") + " " + df["keyword"].fillna("unknown")

    # --- 1. TF-IDF: word 1-2 + char 2-4 gram ---
    print("\n===== TF-IDF(word + char) =====")
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        analyzer="word",
        sublinear_tf=True,
        min_df=3,
        stop_words="english",
    )
    X_tfidf = tfidf.fit_transform(train["text_aug"])
    X_test_tfidf = tfidf.transform(test["text_aug"])
    char_tfidf = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        sublinear_tf=True,
        min_df=3,
    )
    X_char = char_tfidf.fit_transform(train["text_aug"])
    X_test_char = char_tfidf.transform(test["text_aug"])
    from scipy.sparse import hstack
    X_wc = hstack([X_tfidf, X_char]).tocsr()
    X_test_wc = hstack([X_test_tfidf, X_test_char]).tocsr()
    print(f"word+char 特征维度: {X_wc.shape[1]}")

    # --- 2. Word2Vec 自训练 + TF-IDF 加权句向量 ---
    print(f"\n===== Word2Vec(dim={W2V_DIM}, 在 train+test 上训练) =====")
    sentences = [tokenize(t) for t in pd.concat([train["text_aug"], test["text_aug"]])]
    w2v = Word2Vec(sentences=sentences, vector_size=W2V_DIM, window=5,
                   min_count=2, workers=4, seed=RANDOM_STATE, epochs=10)
    print(f"词表大小: {len(w2v.wv)}")

    def w2v_sentence_vector(text, tfidf_row, vocab):
        """TF-IDF 加权的词向量平均; 词不在 W2V 词表(min_count 丢弃了低频词)则跳过。"""
        vec = np.zeros(W2V_DIM)
        total = 0.0
        for tok in tokenize(text):
            if tok in vocab and tok in w2v.wv.key_to_index:
                vec += w2v.wv[tok] * tfidf_row[0, vocab[tok]]
                total += tfidf_row[0, vocab[tok]]
        return vec / total if total > 0 else vec

    word_vocab = tfidf.vocabulary_
    X_w2v = np.vstack([w2v_sentence_vector(t, X_tfidf[i], word_vocab)
                       for i, t in enumerate(train["text_aug"])])
    X_test_w2v = np.vstack([w2v_sentence_vector(t, X_test_tfidf[i], word_vocab)
                            for i, t in enumerate(test["text_aug"])])
    X_w2v = normalize(X_w2v)
    X_test_w2v = normalize(X_test_w2v)
    print(f"句向量矩阵: {X_w2v.shape}")

    y = train["target"].values

    # --- 3. 5 折 CV: 各模型 + 混合 ---
    print("\n===== 5 折交叉验证 (F1) =====")
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    models = {
        "LR_TFIDF": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "LR_W2V": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
    }
    Xs = {"LR_TFIDF": X_wc, "LR_W2V": X_w2v}
    X_test_s = {"LR_TFIDF": X_test_wc, "LR_W2V": X_test_w2v}

    oof = {name: np.zeros(X_wc.shape[0]) for name in models}
    test_pred = {name: np.zeros(X_test_wc.shape[0]) for name in models}

    for fold, (tr_idx, va_idx) in enumerate(cv.split(X_wc, y)):
        for name, model in models.items():
            X_tr, X_va = Xs[name][tr_idx], Xs[name][va_idx]
            model.fit(X_tr, y[tr_idx])
            oof[name][va_idx] = model.predict_proba(X_va)[:, 1]
            test_pred[name] += model.predict_proba(X_test_s[name])[:, 1] / N_FOLDS

    results = {}
    for name in models:
        f1 = f1_score(y, (oof[name] > 0.5).astype(int))
        results[name] = f1
        print(f"{name:10s} OOF F1: {f1:.4f}")

    blend_prob = sum(oof[name] for name in models) / len(models)
    results["Blend"] = f1_score(y, (blend_prob > 0.5).astype(int))
    print(f"{'Blend':10s} OOF F1: {results['Blend']:.4f}")

    best_name = max(results, key=results.get)
    print(f"\n最佳: {best_name} (OOF F1 {results[best_name]:.4f}), v1 基线 0.7459")

    # --- 4. 生成提交 ---
    print("\n===== 生成提交文件 =====")
    if best_name == "Blend":
        test_prob = sum(test_pred[name] for name in models) / len(models)
    else:
        test_prob = test_pred[best_name]
    y_pred = (test_prob > 0.5).astype(int)
    sub = pd.DataFrame({"id": test["id"], "target": y_pred})
    out = os.path.join(BASE_DIR, "submissions", "submission_v2.csv")
    sub.to_csv(out, index=False)
    print(f"提交文件已生成: {out}  (共 {len(sub)} 行, 正例占比 {y_pred.mean():.3f})")
    print(sub.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
