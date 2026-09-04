# -*- coding: utf-8 -*-
"""
S6E9 通用表格 baseline 模板(自动识别列,开赛后改路径即可用)
========================================================================
从 S6E8 管线抽取的通用版:自动识别 id/目标/数值/类别列,无需改代码。

核心流程(复用 S6E8 验证过的经验):
  LightGBM + XGBoost + CatBoost 各 5 折 OOF(内层 10% 早停),
  0.1 步长权重网格搜索最大化 OOF AUC/LogLoss,输出混合提交。

用法:
  本地(已有数据):  python s6e9_template.py --data <dir>
  Kaggle Notebook:  挂载比赛数据后直接跑(自动扫 /kaggle/input)

开赛后三步:
  1. 下载 S6E9 数据到 s6e9/data/ (或挂载)
  2. 确认目标列名(默认找 target / *_label / 0-1 二分类列)
  3. 运行本脚本,提交输出
"""

import os
import sys
import numpy as np
import pandas as pd

from scipy.sparse import issparse
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import roc_auc_score, log_loss, accuracy_score, f1_score

import lightgbm as lgb
import xgboost as xgb
import catboost as cb

N_FOLDS = 5
RANDOM_STATE = 42
USE_GPU = True if os.environ.get("KAGGLE_KERNEL_RUN_TYPE") or os.path.exists("/kaggle/input") else False

LGB_PARAMS = dict(objective="binary", metric="auc", learning_rate=0.05,
                  num_leaves=63, min_child_samples=100, n_jobs=-1,
                  verbosity=-1, random_state=RANDOM_STATE)
XGB_PARAMS = dict(objective="binary:logistic", eval_metric="auc",
                  learning_rate=0.05, max_depth=7, n_estimators=3000,
                  n_jobs=-1, random_state=RANDOM_STATE, tree_method="hist",
                  enable_categorical=True)
CAT_PARAMS = dict(loss_function="Logloss", eval_metric="AUC",
                  learning_rate=0.05, depth=8, iterations=3000,
                  random_seed=RANDOM_STATE, verbose=False,
                  task_type="GPU" if USE_GPU else "CPU")


# ---------------------------------------------------------------------------
# 路径解析: /kaggle/input 挂载 → kagglehub → 本地 --data 或 s6e9/data
# ---------------------------------------------------------------------------
def resolve_paths(data_dir=None):
    if data_dir and os.path.exists(os.path.join(data_dir, "train.csv")):
        return (os.path.join(data_dir, "train.csv"),
                os.path.join(data_dir, "test.csv"),
                os.path.join(data_dir, "submission.csv"))
    if os.path.isdir("/kaggle/input"):
        for sub in sorted(os.listdir("/kaggle/input")):
            for cand in (os.path.join("/kaggle/input", sub),
                         os.path.join("/kaggle/input", sub, sub)):
                p = os.path.join(cand, "train.csv")
                if os.path.exists(p):
                    return (p, os.path.join(cand, "test.csv"), "/kaggle/working/submission.csv")
    try:
        import kagglehub
        slug = os.environ.get("S6E9_SLUG", "playground-series-s6e9")
        d = kagglehub.competition_download(slug)
        return (os.path.join(d, "train.csv"), os.path.join(d, "test.csv"),
                "/kaggle/working/submission.csv")
    except Exception:
        pass
    for base in (os.path.dirname(os.path.abspath(__file__)), os.getcwd(),
                 os.path.join(os.getcwd(), "s6e9")):
        p = os.path.join(base, "data", "train.csv")
        if os.path.exists(p):
            return (p, os.path.join(base, "data", "test.csv"),
                    os.path.join(base, "submissions", "submission.csv"))
    sys.exit("找不到数据: Kaggle 上请 Add Input 挂载, 本地用 --data 指定含 train.csv 的目录")


# ---------------------------------------------------------------------------
# 自动识别列
# ---------------------------------------------------------------------------
def detect_columns(train, test):
    """自动识别 id 列 / 目标列 / 数值列 / 类别列(不依赖具体列名)。"""
    id_col = None
    for c in ("id", "ID", "Id", "index", "row_id", "RowId", "UID", "uuid"):
        if c in train.columns:
            id_col = c
            break

    target_col = None
    for c in ("target", "Target", "label", "Label", "addicted_label",
              "Class", "class", "y", "prediction_label"):
        if c in train.columns:
            target_col = c
            break
    if target_col is None:  # 兜底:找唯一 0/1 二分类列
        for c in train.columns:
            if c != id_col and train[c].dropna().isin([0, 1]).mean() > 0.99 \
                    and train[c].nunique() <= 2:
                target_col = c
                break
    if target_col is None:  # 最鲁棒:目标列 = train 有而 test 没有的列(Playground 通用)
        for c in train.columns:
            if c != id_col and c not in test.columns:
                target_col = c
                break
    if target_col is None:
        sys.exit("无法自动识别目标列,请手动指定 target_col")

    # 类别列: 非数值 dtype 的列(object/string);数值列全部保持数值
    # (避免低基数整数列转 category 后 XGB 报 float category 索引错误)
    cat_cols, num_cols = [], []
    for c in train.columns:
        if c in (id_col, target_col):
            continue
        if pd.api.types.is_numeric_dtype(train[c]):
            num_cols.append(c)
        else:
            cat_cols.append(c)
    return id_col, target_col, num_cols, cat_cols


def prep_lgb_xgb(df, cats=None):
    X = df.copy()
    X["n_missing"] = X.isna().sum(axis=1)
    for c in cats:
        X[c] = X[c].astype("category")
        if cats is not None and c in cats:
            X[c] = X[c].cat.set_categories(cats[c])
    return X


def prep_cat(df, cats):
    X = df.copy()
    X["n_missing"] = X.isna().sum(axis=1)
    for c in cats:
        X[c] = X[c].fillna("MISSING").astype(str)
    return X


def fold_train(name, Xtr, Xes, ytr, yes, Xva, Xtest, cats):
    if name == "lgb":
        cat_idx = [Xtr.columns.get_loc(c) for c in cats]
        m = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                      num_boost_round=3000,
                      valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        return m.predict(Xva, num_iteration=m.best_iteration), m.predict(Xtest, num_iteration=m.best_iteration)
    if name == "xgb":
        m = xgb.XGBClassifier(**XGB_PARAMS)
        m.fit(Xtr, ytr, eval_set=[(Xes, yes)], verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]
    if name == "cat":
        cat_idx = [Xtr.columns.get_loc(c) for c in cats]
        m = cb.CatBoostClassifier(**CAT_PARAMS)
        m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]


def oof_and_test(name, X, y, X_test, cats):
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    oof, test_sum = np.zeros(len(y)), np.zeros(len(X_test))
    for k, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
        Xtr, Xes, ytr, yes = train_test_split(
            X.iloc[tr_idx], y[tr_idx], test_size=0.1,
            stratify=y[tr_idx], random_state=RANDOM_STATE)
        va_pred, test_pred = fold_train(name, Xtr, Xes, ytr, yes, X.iloc[va_idx], X_test, cats)
        oof[va_idx], test_sum = va_pred, test_sum + test_pred
        print(f"  {name} 折{k}: 完成", flush=True)
    try:
        auc = roc_auc_score(y, oof)
        print(f"{name} OOF AUC: {auc:.5f}", flush=True)
    except Exception:
        auc = float("nan")
    return oof, test_sum / N_FOLDS, auc


def weight_search(names, oofs, y, metric="auc"):
    best_w, best_v = None, -1.0
    n = len(names)
    grid = np.arange(0, 1.0001, 0.1)
    for w1 in grid:
        for w2 in (grid if n >= 3 else [0.0]):
            ws = [w1, w2, 1 - w1 - w2][:n] if n >= 3 else [w1, 1 - w1]
            if any(w < -1e-9 for w in ws):
                continue
            blend = sum(wi * o for wi, o in zip(ws, oofs))
            v = roc_auc_score(y, blend) if metric == "auc" else -log_loss(y, np.clip(blend, 1e-7, 1 - 1e-7))
            if v > best_v:
                best_v, best_w = v, ws
    return best_w, best_v


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None, help="含 train.csv/test.csv 的目录")
    ap.add_argument("--metric", default="auc", choices=["auc", "logloss"])
    ap.add_argument("--models", default="lgb,xgb,cat")
    args = ap.parse_args()

    train_path, test_path, out_path = resolve_paths(args.data)
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    id_col, target_col, num_cols, cat_cols = detect_columns(train, test)
    print(f"[列] id={id_col} 目标={target_col} | 数值 {len(num_cols)} 个 / 类别 {len(cat_cols)} 个")

    y = train[target_col]
    # pandas 3.0 Arrow 字符串类型(如 'No'/'Yes')需转 0/1 numpy 数组
    if not pd.api.types.is_numeric_dtype(y):
        y = pd.factorize(y)[0].astype(int)
    else:
        y = y.to_numpy().astype(int)
    train_raw = train.drop(columns=[c for c in (id_col, target_col) if c])
    test_raw = test.drop(columns=[c for c in (id_col,) if c])

    # 测试集类别对齐训练集
    cats_map = {c: pd.Categorical(train_raw[c]).categories for c in cat_cols if c in train_raw.columns}
    models = [m for m in args.models.split(",") if m in ("lgb", "xgb", "cat")]

    oofs, tests, names = [], [], []
    for name in models:
        if name in ("lgb", "xgb"):
            X = prep_lgb_xgb(train_raw, cats_map)
            Xt = prep_lgb_xgb(test_raw, cats_map)
        else:
            X = prep_cat(train_raw, cat_cols)
            Xt = prep_cat(test_raw, cat_cols)
        oof, t, auc = oof_and_test(name, X, y, Xt, cat_cols)
        oofs.append(oof)
        tests.append(t)
        names.append(name)

    w, v = weight_search(names, oofs, y, args.metric)
    print(f"\n混合权重: {dict(zip(names, [round(x, 3) for x in w]))}  OOF {args.metric.upper()}: {v:.5f}")
    y_prob = sum(wi * t for wi, t in zip(w, tests))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if id_col and id_col in test.columns:
        sub = pd.DataFrame({id_col: test[id_col], target_col: y_prob})
    else:
        sub = pd.DataFrame({target_col: y_prob})
    sub.to_csv(out_path, index=False)
    print(f"提交文件已生成: {out_path}  ({len(sub)} 行)")
    print(f"概率均值 {y_prob.mean():.4f} | 分位 {np.percentile(y_prob, [25, 50, 75]).round(4)}")


if __name__ == "__main__":
    main()
