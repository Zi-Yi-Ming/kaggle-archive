# -*- coding: utf-8 -*-
"""S6E9 CatBoost 快速验证:2 折小样本,确认 cat 对混合的贡献方向。"""
import sys
import numpy as np
import pandas as pd
import catboost as cb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

train = pd.read_csv(r"D:\桌面\Kaggle\s6e9\data\train.csv", nrows=40000)
y = pd.factorize(train["Will_Buy_EV"])[0].astype(int)
base = train.drop(columns=["id", "Will_Buy_EV"]).copy()
cats = [c for c in base.columns if not pd.api.types.is_numeric_dtype(base[c])]
for c in cats:
    base[c] = base[c].astype(str).fillna("MISSING")
cat_idx = [base.columns.get_loc(c) for c in cats]

params = dict(loss_function="Logloss", eval_metric="AUC", learning_rate=0.1,
              depth=6, iterations=400, random_seed=42, verbose=False, task_type="CPU")
cv = StratifiedKFold(2, shuffle=True, random_state=42)
oof = np.zeros(len(y))
for k, (tr, va) in enumerate(cv.split(base, y)):
    m = cb.CatBoostClassifier(**params)
    m.fit(base.iloc[tr], y[tr], cat_features=cat_idx,
          eval_set=(base.iloc[va], y[va]), verbose=False)
    oof[va] = m.predict_proba(base.iloc[va])[:, 1]
    print(f"cat 折{k}: {roc_auc_score(y[va], oof[va]):.5f}", flush=True)
print(f"cat(4万行,2折,400iter): OOF AUC {roc_auc_score(y, oof):.5f}", flush=True)
