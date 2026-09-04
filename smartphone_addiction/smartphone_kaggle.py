# -*- coding: utf-8 -*-
"""
Smartphone Addiction (S6E8) v4 - Kaggle Notebook 版
====================================================
LGBM + XGBoost + CatBoost 异构集成,5 折 OOF + 权重搜索混合(权重归一)。

在 Kaggle Notebook 上运行(12 小时上限):
1. 新建 Notebook → Settings 里选 Accelerator = GPU T4(让 CatBoost 快几十倍)
2. 右侧 Add Input → 搜索并挂载比赛数据 "playground-series-s6e8"
3. 把本文件全部内容粘贴进代码单元格运行(或上传本文件后执行 !python smartphone_kaggle.py)
4. 运行完输出 /kaggle/working/submission_v4.csv → 点右侧 "Submit to Competition" 直接提交

本脚本自动适配环境:
- 存在 /kaggle/input/playground-series-s6e8/ 则用官网数据,否则用本地 smartphone_addiction/data/
- CatBoost 检测到 GPU 自动用 GPU,否则 CPU(也能跑,只是慢)
- 输出到 /kaggle/working/submission_v4.csv;本地运行时输出到 submissions/submission_v4.csv
"""

import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

RANDOM_STATE = 42
N_FOLDS = 5

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]

LGB_PARAMS = {
    "objective": "binary", "metric": "auc", "learning_rate": 0.05,
    "num_leaves": 63, "min_child_samples": 100, "subsample": 0.9,
    "subsample_freq": 1, "colsample_bytree": 0.9, "verbosity": -1,
    "random_state": RANDOM_STATE, "num_threads": 0,
}
XGB_PARAMS = {
    "n_estimators": 3000, "max_depth": 6, "learning_rate": 0.05,
    "tree_method": "hist", "n_jobs": -1, "enable_categorical": True,
    "eval_metric": "auc", "random_state": RANDOM_STATE,
}
try:
    from catboost.utils import get_gpu_device_count
    USE_GPU = get_gpu_device_count() > 0
except Exception:
    USE_GPU = False  # 检测不到 GPU 一律回退 CPU,保证可运行
CAT_PARAMS = {
    "iterations": 1500, "depth": 6, "learning_rate": 0.05,
    "loss_function": "Logloss", "eval_metric": "AUC",
    "bootstrap_type": "Bernoulli", "subsample": 0.7,
    "thread_count": -1, "verbose": 0, "random_seed": RANDOM_STATE,
    "allow_writing_files": False,
    "task_type": "GPU" if USE_GPU else "CPU",
}


def resolve_paths():
    """优先官网 /kaggle/input;本地回退按 脚本目录 -> 当前目录 -> 当前目录/smartphone_addiction 依次找。
    兼容 Notebook 粘贴运行(Jupyter 单元格没有 __file__,用 os.getcwd() 兜底)。"""
    # 1) Kaggle 环境:扫描 /kaggle/input 下所有目录(不猜固定名字)
    if os.path.isdir("/kaggle/input"):
        for sub in os.listdir("/kaggle/input"):
            d = os.path.join("/kaggle/input", sub)
            p = os.path.join(d, "train.csv")
            if os.path.isdir(d) and os.path.exists(p):
                return (p, os.path.join(d, "test.csv"), "/kaggle/working/submission_v4.csv")
    # 1.5) kagglehub 兜底:没挂载 Add Input 时自动下载/定位比赛数据(Kaggle 内置 kagglehub)
    try:
        import kagglehub
        d = kagglehub.competition_download("playground-series-s6e8")
        p = os.path.join(d, "train.csv")
        if os.path.exists(p):
            print(f"[路径] 使用 kagglehub 数据: {d}", flush=True)
            return (p, os.path.join(d, "test.csv"), "/kaggle/working/submission_v4.csv")
    except ImportError:
        pass  # 本地未装 kagglehub,走下面的本地兜底
    except Exception as e:
        print(f"[提示] kagglehub 获取数据失败: {e}", flush=True)
    # 2) 本地兜底:脚本目录 -> 当前目录 -> 当前目录/smartphone_addiction
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))  # 脚本运行时
    except NameError:
        pass  # Notebook 单元格:无 __file__
    cands.append(os.getcwd())
    cands.append(os.path.join(os.getcwd(), "smartphone_addiction"))
    for base in cands:
        p = os.path.join(base, "data", "train.csv")
        if os.path.exists(p):
            return (p, os.path.join(base, "data", "test.csv"),
                    os.path.join(base, "submissions", "submission_v4.csv"))
    # 3) 都找不到:打印诊断信息(在 Kaggle 上通常=没挂载数据)
    if os.path.isdir("/kaggle/input"):
        print("诊断: /kaggle/input 下内容:", os.listdir("/kaggle/input"))
    else:
        print("诊断: 不存在 /kaggle/input(不是 Kaggle 环境?)")
    sys.exit("找不到数据:如在 Kaggle 上,请点右侧 Add Input 挂载比赛数据后重跑;本地请确认在项目目录下运行。")


def prep_lgb_xgb(df, cats=None):
    """LGBM/XGB 用:category dtype,NaN 保留;测试集类别与训练集对齐(未见->NaN)。"""
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    for c in CAT_COLS:
        X[c] = X[c].astype("category")
        if cats is not None:
            X[c] = X[c].cat.set_categories(cats[c])
    return X


def prep_cat(df):
    """CatBoost 用:类别列 NaN -> 'MISSING' 字符串。"""
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    for c in CAT_COLS:
        X[c] = X[c].fillna("MISSING").astype(str)
    return X


def fold_train(name, Xtr, Xes, ytr, yes, Xva, Xtest):
    """训练单折模型(内层 10% 早停),返回验证/测试概率。"""
    if name == "lgb":
        cat_idx = [Xtr.columns.get_loc(c) for c in CAT_COLS]
        m = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                      num_boost_round=3000,
                      valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        return (m.predict(Xva, num_iteration=m.best_iteration),
                m.predict(Xtest, num_iteration=m.best_iteration))
    if name == "xgb":
        m = xgb.XGBClassifier(**XGB_PARAMS)
        m.fit(Xtr, ytr, eval_set=[(Xes, yes)], verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]
    if name == "cat":
        cat_idx = [Xtr.columns.get_loc(c) for c in CAT_COLS]
        m = cb.CatBoostClassifier(**CAT_PARAMS)
        m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]


def oof_and_test(name, X, y, X_test):
    """5 折 OOF + 测试集概率(折模型平均)。"""
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    oof = np.zeros(len(y))
    test_sum = np.zeros(len(X_test))
    for k, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
        Xtr, Xes, ytr, yes = train_test_split(
            X.iloc[tr_idx], y[tr_idx], test_size=0.1,
            stratify=y[tr_idx], random_state=RANDOM_STATE)
        va_pred, test_pred = fold_train(name, Xtr, Xes, ytr, yes, X.iloc[va_idx], X_test)
        oof[va_idx] = va_pred
        test_sum += test_pred
        print(f"  {name} 折{k}: 完成", flush=True)
    print(f"{name} OOF AUC: {roc_auc_score(y, oof):.5f}", flush=True)
    return oof, test_sum / N_FOLDS


def weight_search(names, oofs, y):
    """0.1 步长网格搜索混合权重(权重必须归一),最大化 OOF AUC。"""
    best_w, best_auc = None, -1.0
    n = len(names)
    grid = np.arange(0, 1.0001, 0.1)
    for w1 in grid:
        for w2 in (grid if n >= 3 else [0.0]):
            ws = [w1, w2, 1 - w1 - w2][:n] if n >= 3 else [w1, 1 - w1]
            if any(w < -1e-9 for w in ws):
                continue
            blend = sum(wi * o for wi, o in zip(ws, oofs))
            auc = roc_auc_score(y, blend)
            if auc > best_auc:
                best_auc, best_w = auc, ws
    return best_w, best_auc


def main():
    train_path, test_path, out_path = resolve_paths()
    if not os.path.exists(train_path):
        sys.exit(f"找不到数据: {train_path}")

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    y = train["addicted_label"].values
    print(f"训练 {len(y)} 行 / 测试 {len(test)} 行 | CatBoost 用 {'GPU' if USE_GPU else 'CPU'}")

    train_raw = train.drop(columns=["id", "addicted_label"])
    cats = {c: pd.Categorical(train_raw[c]).categories for c in CAT_COLS}
    X_lgb = prep_lgb_xgb(train_raw)
    X_test_lgb = prep_lgb_xgb(test.drop(columns=["id"]), cats)
    X_cat = prep_cat(train_raw)
    X_test_cat = prep_cat(test.drop(columns=["id"]))
    print(f"特征 {X_lgb.shape[1]} 个")

    oofs, tests, names = [], [], []
    for name, X, Xt in [("lgb", X_lgb, X_test_lgb),
                        ("xgb", X_lgb, X_test_lgb),
                        ("cat", X_cat, X_test_cat)]:
        oof, t = oof_and_test(name, X, y, Xt)
        oofs.append(oof)
        tests.append(t)
        names.append(name)

    w, blend_auc = weight_search(names, oofs, y)
    print(f"\n混合权重: {dict(zip(names, [round(x, 3) for x in w]))}  OOF AUC: {blend_auc:.5f}")
    y_prob = sum(wi * t for wi, t in zip(w, tests))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pd.DataFrame({"id": test["id"], "addicted_label": y_prob}).to_csv(out_path, index=False)
    print(f"提交文件已生成: {out_path}")
    print(f"概率均值 {y_prob.mean():.4f} (应约 0.71) | 分位 {np.percentile(y_prob, [25, 50, 75]).round(4)}")


if __name__ == "__main__":
    main()
