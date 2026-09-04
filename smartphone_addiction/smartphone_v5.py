# -*- coding: utf-8 -*-
"""
Smartphone Addiction (S6E8) v5：种子平均 + 权重搜索
====================================================
在 v4(LGBM+XGB+CatBoost 异构集成)基础上叠加两个提升手段:
1. 种子平均(Seed Averaging):每个模型跑多个随机种子(SEEDS),同折预测取平均,
   消除单种子的方差,通常稳定 +0.0005~0.001;
2. 细粒度权重搜索:0.1 步长 → 0.01 步长,更精确的混合权重。

设计——兼容复用 + 可断点续跑:
- 折划分固定 StratifiedKFold(random_state=42),与 v4 一致;
- 已有旧文件 {model}_f{k}_*.npy(v4 的 seed42 折文件)自动当作 seed=42 的结果
  复用,不重训;新种子存为 {model}_s{seed}_f{k}_*.npy;
- 每个 (模型, 种子, 折) 单独存盘,超时重跑自动跳过已完成部分;
- 全部完成后:模型内种子平均 → 0.01 步长权重搜索 → 生成 submission_v5.csv。

用法(本地,只跑 LGBM 补种快速验证):
    python smartphone_v5.py --models lgb
Kaggle Notebook / 本地全量:
    python smartphone_v5.py            # 全部模型全部种子
输出: submissions/submission_v5.csv(概率,适配 AUC 评分)
"""

import argparse
import os
import sys
import time

import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

SEEDS = [42, 7, 2026]          # 种子平均:注意 42 必须在前(兼容 v4 旧文件)
N_FOLDS = 5
FOLD_RS = 42                   # 折划分固定,保证不同种子 OOF 位置一一对应

NUM_COLS = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
            "work_study_hours", "sleep_hours", "notifications_per_day",
            "app_opens_per_day", "weekend_screen_time"]
CAT_COLS = ["gender", "stress_level", "academic_work_impact"]

LGB_BASE = {
    "objective": "binary", "metric": "auc", "learning_rate": 0.05,
    "num_leaves": 63, "min_child_samples": 100, "subsample": 0.9,
    "subsample_freq": 1, "colsample_bytree": 0.9, "verbosity": -1,
    "num_threads": 0,
}
XGB_BASE = {
    "n_estimators": 3000, "max_depth": 6, "learning_rate": 0.05,
    "tree_method": "hist", "n_jobs": -1, "enable_categorical": True,
    "eval_metric": "auc",
}
try:
    from catboost.utils import get_gpu_device_count
    USE_GPU = get_gpu_device_count() > 0
except Exception:
    USE_GPU = False
CAT_BASE = {
    "iterations": 1500, "depth": 6, "learning_rate": 0.05,
    "loss_function": "Logloss", "eval_metric": "AUC",
    "bootstrap_type": "Bernoulli", "subsample": 0.7,
    "thread_count": -1, "verbose": 0,
    "allow_writing_files": False,
    "task_type": "GPU" if USE_GPU else "CPU",
}


def resolve_paths():
    """优先官网 /kaggle/input;本地回退按 脚本目录 -> 当前目录 -> 当前目录/smartphone_addiction。"""
    if os.path.isdir("/kaggle/input"):
        for sub in os.listdir("/kaggle/input"):
            d = os.path.join("/kaggle/input", sub)
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "train.csv")):
                return (os.path.join(d, "train.csv"), os.path.join(d, "test.csv"),
                        "/kaggle/working/submission_v5.csv", "/kaggle/working/oof5")
    try:
        import kagglehub
        d = kagglehub.competition_download("playground-series-s6e8")
        if os.path.exists(os.path.join(d, "train.csv")):
            return (os.path.join(d, "train.csv"), os.path.join(d, "test.csv"),
                    "/kaggle/working/submission_v5.csv", "/kaggle/working/oof5")
    except Exception:
        pass
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.getcwd())
    cands.append(os.path.join(os.getcwd(), "smartphone_addiction"))
    for base in cands:
        p = os.path.join(base, "data", "train.csv")
        if os.path.exists(p):
            return (p, os.path.join(base, "data", "test.csv"),
                    os.path.join(base, "submissions", "submission_v5.csv"),
                    os.path.join(base, "oof"))
    if os.path.isdir("/kaggle/input"):
        print("诊断: /kaggle/input 下内容:", os.listdir("/kaggle/input"))
    else:
        print("诊断: 不存在 /kaggle/input(不是 Kaggle 环境?)")
    sys.exit("找不到数据:如在 Kaggle 上,请点右侧 Add Input 挂载比赛数据后重跑;本地请确认在项目目录下运行。")


def prep_lgb_xgb(df, cats=None):
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    for c in CAT_COLS:
        X[c] = X[c].astype("category")
        if cats is not None:
            X[c] = X[c].cat.set_categories(cats[c])
    return X


def prep_cat(df):
    X = df.copy()
    X["n_missing"] = X[NUM_COLS + CAT_COLS].isna().sum(axis=1)
    for c in CAT_COLS:
        X[c] = X[c].fillna("MISSING").astype(str)
    return X


def fold_train(name, seed, Xtr, Xes, ytr, yes, Xva, Xtest):
    """训练单折模型(内层 10% 早停),返回验证/测试概率。"""
    if name == "lgb":
        cat_idx = [Xtr.columns.get_loc(c) for c in CAT_COLS]
        p = dict(LGB_BASE, random_state=seed)
        m = lgb.train(p, lgb.Dataset(Xtr, ytr, categorical_feature=cat_idx),
                      num_boost_round=3000,
                      valid_sets=[lgb.Dataset(Xes, yes, categorical_feature=cat_idx)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        return (m.predict(Xva, num_iteration=m.best_iteration),
                m.predict(Xtest, num_iteration=m.best_iteration))
    if name == "xgb":
        p = dict(XGB_BASE, random_state=seed)
        m = xgb.XGBClassifier(**p)
        m.fit(Xtr, ytr, eval_set=[(Xes, yes)], verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]
    if name == "cat":
        cat_idx = [Xtr.columns.get_loc(c) for c in CAT_COLS]
        p = dict(CAT_BASE, random_seed=seed)
        m = cb.CatBoostClassifier(**p)
        m.fit(Xtr, ytr, cat_features=cat_idx, eval_set=(Xes, yes), verbose=False)
        return m.predict_proba(Xva)[:, 1], m.predict_proba(Xtest)[:, 1]


def run_seed_folds(name, seed, X, y, X_test, oof_dir):
    """跑一个 (模型, 种子) 的全部折;折文件已存在则跳过。seed=42 优先复用 v4 旧文件。"""
    t0 = time.time()
    for k in range(N_FOLDS):
        # seed=42:先看 v4 旧文件 {name}_f{k}_*.npy,存在则复制为新命名统一读盘
        old_va = os.path.join(oof_dir, f"{name}_f{k}_va_pred.npy")
        new_va = os.path.join(oof_dir, f"{name}_s{seed}_f{k}_va_pred.npy")
        if seed == 42 and os.path.exists(old_va) and not os.path.exists(new_va):
            for suffix in ("va_pred.npy", "va_idx.npy", "test.npy"):
                src = os.path.join(oof_dir, f"{name}_f{k}_{suffix}")
                dst = os.path.join(oof_dir, f"{name}_s{seed}_f{k}_{suffix}")
                if os.path.exists(src):
                    np.save(dst, np.load(src))
            print(f"  {name} seed{seed} 折{k}: 复用 v4 旧文件", flush=True)
            continue
        if os.path.exists(new_va):
            continue
        cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=FOLD_RS)
        for kk, (tr_idx, va_idx) in enumerate(cv.split(X, y)):
            if kk != k:
                continue
            Xtr, Xes, ytr, yes = train_test_split(
                X.iloc[tr_idx], y[tr_idx], test_size=0.1,
                stratify=y[tr_idx], random_state=FOLD_RS)
            va_pred, test_pred = fold_train(name, seed, Xtr, Xes, ytr, yes,
                                            X.iloc[va_idx], X_test)
            np.save(os.path.join(oof_dir, f"{name}_s{seed}_f{k}_va_idx.npy"), va_idx)
            np.save(new_va, va_pred)
            np.save(os.path.join(oof_dir, f"{name}_s{seed}_f{k}_test.npy"), test_pred)
            print(f"  {name} seed{seed} 折{k}: 完成 ({time.time() - t0:.0f}s)", flush=True)
            break


def collect_model(name, seed, y, X_test, oof_dir):
    """汇总一个 (模型, 种子) 的 OOF 与 test 预测。统一读新命名文件
    (run_seed_folds 已把 seed42 的 v4 旧文件复制成新命名,新训练折也存新命名)。"""
    oof = np.zeros(len(y))
    test_sum = np.zeros(len(X_test))
    for k in range(N_FOLDS):
        va = np.load(os.path.join(oof_dir, f"{name}_s{seed}_f{k}_va_pred.npy"))
        va_idx = np.load(os.path.join(oof_dir, f"{name}_s{seed}_f{k}_va_idx.npy"))
        tt = np.load(os.path.join(oof_dir, f"{name}_s{seed}_f{k}_test.npy"))
        oof[va_idx] = va
        test_sum += tt
    return oof, test_sum / N_FOLDS


def weight_search(names, oofs, y, step=0.01):
    """细粒度网格搜索混合权重(归一,0.01 步长),最大化 OOF AUC。"""
    best_w, best_auc = None, -1.0
    n = len(names)
    grid = np.arange(0, 1.0001, step)
    for w1 in grid:
        for w2 in (grid if n >= 3 else [0.0]):
            ws = [w1, w2, 1 - w1 - w2][:n] if n >= 3 else [w1, 1 - w1]
            if any(w < -1e-9 for w in ws):
                continue
            auc = roc_auc_score(y, sum(wi * o for wi, o in zip(ws, oofs)))
            if auc > best_auc:
                best_auc, best_w = auc, ws
    return best_w, best_auc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="lgb,xgb,cat", help="逗号分隔的模型列表")
    # parse_known_args:Jupyter/Colab 内核会在 sys.argv 注入 -f <kernel.json>,
    # 普通 parse_args 会把它当未知参数报错;known 版忽略它们即可。
    args, _ = ap.parse_known_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    full_set = ["lgb", "xgb", "cat"]

    train_path, test_path, out_path, oof_dir = resolve_paths()
    if not os.path.exists(train_path):
        sys.exit(f"找不到数据: {train_path}")
    os.makedirs(oof_dir, exist_ok=True)

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    y = train["addicted_label"].values
    print(f"训练 {len(y)} 行 / 测试 {len(test)} 行 | CatBoost: {'GPU' if USE_GPU else 'CPU'} | 模型 {models}", flush=True)

    train_raw = train.drop(columns=["id", "addicted_label"])
    cats = {c: pd.Categorical(train_raw[c]).categories for c in CAT_COLS}
    X_lgb = prep_lgb_xgb(train_raw)
    X_test_lgb = prep_lgb_xgb(test.drop(columns=["id"]), cats)
    X_cat = prep_cat(train_raw)
    X_test_cat = prep_cat(test.drop(columns=["id"]))
    print(f"特征 {X_lgb.shape[1]} 个 | 种子 {SEEDS}", flush=True)

    Xs = {"lgb": X_lgb, "xgb": X_lgb, "cat": X_cat}
    Xts = {"lgb": X_test_lgb, "xgb": X_test_lgb, "cat": X_test_cat}

    # 1) 逐模型逐种子训练(断点续跑)
    for name in models:
        for seed in SEEDS:
            print(f"[{name} seed{seed}] 开始", flush=True)
            run_seed_folds(name, seed, Xs[name], y, Xts[name], oof_dir)

    # 2) 汇总:单种子 OOF + 种子平均
    seed_oofs = {m: {} for m in models}
    seed_tests = {m: {} for m in models}
    for name in models:
        for seed in SEEDS:
            oof, tst = collect_model(name, seed, y, Xts[name], oof_dir)
            seed_oofs[name][seed] = oof
            seed_tests[name][seed] = tst
            print(f"  {name} seed{seed} OOF AUC: {roc_auc_score(y, oof):.5f}", flush=True)

    names, oofs, tests = [], [], []
    for name in models:
        oof_avg = np.mean([seed_oofs[name][s] for s in SEEDS], axis=0)
        tst_avg = np.mean([seed_tests[name][s] for s in SEEDS], axis=0)
        single_best = max(roc_auc_score(y, seed_oofs[name][s]) for s in SEEDS)
        print(f"  {name} 种子平均 OOF AUC: {roc_auc_score(y, oof_avg):.5f}"
              f"  (单种子最佳 {single_best:.5f})", flush=True)
        names.append(name)
        oofs.append(oof_avg)
        tests.append(tst_avg)

    # 3) 0.01 步长权重搜索
    w, blend_auc = weight_search(names, oofs, y, step=0.01)
    y_prob = sum(wi * t for wi, t in zip(w, tests))
    print(f"\n===== v5 混合({' + '.join(names)}) =====", flush=True)
    for n, o in zip(names, oofs):
        print(f"  {n:4s} 种子平均 OOF AUC: {roc_auc_score(y, o):.5f}")
    print(f"  权重(0.01 步长): {dict(zip(names, [round(x, 3) for x in w]))}  混合 OOF AUC: {blend_auc:.5f}", flush=True)

    # 4) 对照:v4 式单种子(seed42)+ 0.1 步长,报告提升量
    oofs42 = [seed_oofs[m][42] for m in names]
    w42, auc42 = weight_search(names, oofs42, y, step=0.1)
    print(f"[对照 v4] 单种子(seed42) 0.1 步长混合 OOF AUC: {auc42:.5f}", flush=True)
    print(f"[提升]  种子平均+细粒度搜索 vs v4: {blend_auc - auc42:+.5f}", flush=True)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if models == full_set:
        pd.DataFrame({"id": test["id"], "addicted_label": y_prob}).to_csv(out_path, index=False)
        print(f"提交文件已生成: {out_path}")
        print(f"概率均值 {y_prob.mean():.4f} | 分位 {np.percentile(y_prob, [25, 50, 75]).round(4)}")
    else:
        print(f"(子集运行 {models},不写提交文件;完整集合 {full_set} 完成才写盘)")


if __name__ == "__main__":
    main()
