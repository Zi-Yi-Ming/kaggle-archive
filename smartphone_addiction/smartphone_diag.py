# -*- coding: utf-8 -*-
"""
S6E8 v5 诊断:为什么种子平均+权重搜索没赢过 v4?
只加载本地已有 OOF npy,对比混合策略,不重训模型。
"""
import os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

BASE = os.path.dirname(os.path.abspath(__file__))
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
y = train["addicted_label"].values
N_FOLDS = 5
SEEDS = [42, 7, 2026]


def load_model_seed(name, seed):
    """读取一个 (模型, 种子) 的 OOF,缺折则返回 None。"""
    oof = np.zeros(len(y))
    for k in range(N_FOLDS):
        p = os.path.join(OOF, f"{name}_s{seed}_f{k}_va_pred.npy")
        vi = os.path.join(OOF, f"{name}_s{seed}_f{k}_va_idx.npy")
        if not (os.path.exists(p) and os.path.exists(vi)):
            return None
        oof[np.load(vi)] = np.load(p)
    return oof


def report(name, oof):
    print(f"  {name:28s} OOF AUC {roc_auc_score(y, oof):.5f}")


print("=== 各 (模型,种子) 单种子 OOF ===")
avail = {}
for m in ["lgb", "xgb", "cat"]:
    for s in SEEDS:
        o = load_model_seed(m, s)
        if o is not None:
            avail[(m, s)] = o
            report(f"{m} seed{s}", o)

print("\n=== 模型内种子平均 ===")
by_model = {}
for m in ["lgb", "xgb", "cat"]:
    oofs = [avail[(m, s)] for s in SEEDS if (m, s) in avail]
    if oofs:
        avg = np.mean(oofs, axis=0)
        by_model[m] = avg
        single_best = max(roc_auc_score(y, o) for o in oofs)
        report(f"{m} 种子平均 ({len(oofs)} seeds)", avg)
        print(f"    (单种子最佳 {single_best:.5f},提升 {roc_auc_score(y, avg) - single_best:+.5f})")

models = list(by_model)
print(f"\n=== 混合策略(可用模型: {models}) ===")
oofs = [by_model[m] for m in models]

# 1) 简单平均
sa = np.mean(oofs, axis=0)
report("简单平均", sa)

# 2) rank 平均(先转 rank,消除分布差异)
from scipy.stats import rankdata
ranks = np.mean([rankdata(o) / len(y) for o in oofs], axis=0)
report("rank 平均", ranks)

# 3) 0.01 步长权重搜索(当前 v5 的做法)
from itertools import product
best_w, best_auc = None, -1.0
if len(models) == 2:
    for w in np.arange(0, 1.0001, 0.01):
        a = roc_auc_score(y, w * oofs[0] + (1 - w) * oofs[1])
        if a > best_auc:
            best_auc, best_w = a, (w, 1 - w)
elif len(models) == 3:
    for w1, w2 in product(np.arange(0, 1.0001, 0.01), repeat=2):
        w3 = 1 - w1 - w2
        if w3 < -1e-9:
            continue
        a = roc_auc_score(y, w1 * oofs[0] + w2 * oofs[1] + w3 * oofs[2])
        if a > best_auc:
            best_auc, best_w = a, (w1, w2, w3)
print(f"  权重搜索: w={[round(x, 2) for x in best_w]}  OOF AUC {best_auc:.5f}")

# 4) LR stacking(OOF 上 5 折交叉验证评估,防过拟合)
X_stack = np.column_stack(oofs)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
stack_oof = np.zeros(len(y))
for tr, va in skf.split(X_stack, y):
    lr = LogisticRegression(C=1.0, max_iter=1000)
    lr.fit(X_stack[tr], y[tr])
    stack_oof[va] = lr.predict_proba(X_stack[va])[:, 1]
report("LR stacking (C=1.0)", stack_oof)

for c in (0.1, 10.0):
    o = np.zeros(len(y))
    for tr, va in skf.split(X_stack, y):
        lr = LogisticRegression(C=c, max_iter=1000)
        lr.fit(X_stack[tr], y[tr])
        o[va] = lr.predict_proba(X_stack[va])[:, 1]
    report(f"LR stacking (C={c})", o)

print("\n=== 对照 v4 单种子(seed42) ===")
oofs42 = [avail[(m, 42)] for m in models if (m, 42) in avail]
if len(oofs42) == len(models):
    sa42 = np.mean(oofs42, axis=0)
    report("v4 式简单平均(seed42)", sa42)
