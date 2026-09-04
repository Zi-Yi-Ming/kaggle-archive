# -*- coding: utf-8 -*-
"""
S6E8 v8: GBDT 二层 stacking(替代 v7 的 LR 元模型)
========================================================================
v7 用 LogisticRegression(C=10) 做 81 成员 rank 归一化 OOF 的 stacking 元模型
(OOF 0.96965)。本脚本换成 LightGBM 元模型——能捕捉成员间非线性交互,
通常比线性 LR stacking 更强。

防泄漏设计(关键):
  一层:81 成员的 OOF 都是各自 5 折内产生的(无泄漏),rank 归一化对齐;
  二层:在同一 StratifiedKFold(5, shuffle, seed=42) 上嵌套 CV——
        每折用 4/5 行拟合 LightGBM(输入=81 成员 rank OOF),
        预测 1/5 验证行 → 真正的 OOF;测试集取 5 折平均。
  一层与二层共用同一 fold 划分,保证二层验证行从未参与一层训练(防泄漏)。

用法: python smartphone_v8_gbdt_stack.py [--lr] [--gbt] [--topk N]
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression

import lightgbm as lgb

BASE = os.path.dirname(os.path.abspath(__file__))
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
test = pd.read_csv(os.path.join(BASE, "data", "test.csv"))
y = train["addicted_label"].values
N = len(y)
NT = len(test)

import smartphone_v6_blend as B  # noqa  (load_local_oof / load_local_test)


def rk(x):
    """rank 归一化到 (0,1]:对 AUC 单调无损,统一各成员尺度。"""
    return rankdata(x) / len(x)


def build_all():
    """组装全部 81 成员(rank 归一化),与 v6/v7 一致。返回 (names, O(N,M), T(NT,M))。"""
    names, oofs, tests = [], [], []
    manifest = pd.read_csv(os.path.join(BASE, "public_oof", "manifest.csv")).set_index("model")
    for m in ["lgb", "xgb"]:
        o, t = B.load_local_oof(m), B.load_local_test(m)
        if o is not None:
            names.append(f"local_{m}"); oofs.append(rk(o)); tests.append(rk(t))
    for model in manifest.index:
        po = os.path.join(BASE, "public_oof", "oof", f"oof_{model}.npy")
        pt = os.path.join(BASE, "public_oof", "oof", f"test_{model}.npy")
        if os.path.exists(po):
            names.append(model); oofs.append(rk(np.load(po))); tests.append(rk(np.load(pt)))
    fm_map = {"fmdeep": ("oof_fmdeep", "test_fmdeep"), "fmnum": ("oof_fmnum", "test_fmnum"),
              "fmplr": ("oof_fmplr", "test_fmplr"), "fmpure": ("oof_fmpure", "test_fmpure"),
              "fmwide": ("oof_fmwide", "test_fmwide"),
              "band_mid": ("bandoof_band_mid", "bandtest_band_mid"),
              "bandfm2": ("bandoof_bandfm2", "bandtest_bandfm2")}
    fm_src = os.path.join(BASE, "public_oof")
    for f, (po_f, pt_f) in fm_map.items():
        po, pt = os.path.join(fm_src, f"{po_f}.npy"), os.path.join(fm_src, f"{pt_f}.npy")
        if os.path.exists(po):
            o, t = np.load(po), np.load(pt)
            if len(o) != N or len(t) != NT:
                print(f"  跳过 {f}: OOF {len(o)} / test {len(t)} 非全量(中间产物)")
                continue
            names.append(f"fm_{f}"); oofs.append(rk(o)); tests.append(rk(t))
    return names, np.column_stack(oofs), np.column_stack(tests)


def gbdt_stack(O, T, y):
    """LightGBM 元模型二层 stacking,同折 CV 防泄漏。返回 (oof, test_pred, 各折 auc)。"""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(y))
    test_sum = np.zeros(T.shape[0])
    fold_aucs = []
    params = dict(objective="binary", metric="auc", learning_rate=0.02,
                  num_leaves=31, min_child_samples=50, colsample_bytree=0.6,
                  subsample=0.8, n_jobs=-1, verbosity=-1, random_state=42)
    for k, (tr, va) in enumerate(skf.split(O, y)):
        m = lgb.train(params, lgb.Dataset(O[tr], y[tr]),
                      num_boost_round=2000,
                      valid_sets=[lgb.Dataset(O[va], y[va])],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        va_p = m.predict(O[va], num_iteration=m.best_iteration)
        oof[va] = va_p
        test_sum += m.predict(T, num_iteration=m.best_iteration)
        a = roc_auc_score(y[va], va_p)
        fold_aucs.append(a)
        print(f"  GBDT 折{k}: AUC {a:.5f}", flush=True)
    return oof, test_sum / 5, fold_aucs


def lr_stack(O, T, y, C=10.0):
    """v7 的 LR stacking 对照。返回 (oof, test_pred)。"""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(y))
    test_sum = np.zeros(T.shape[0])
    for k, (tr, va) in enumerate(skf.split(O, y)):
        m = LogisticRegression(C=C, max_iter=2000)
        m.fit(O[tr], y[tr])
        oof[va] = m.predict_proba(O[va])[:, 1]
        test_sum += m.predict_proba(T)[:, 1]
    return oof, test_sum / 5


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--topk", type=int, default=0, help=">0 时只用 OOF AUC 前 topk 个成员")
    ap.add_argument("--lr", action="store_true", help="同时跑 LR stacking 对照")
    args = ap.parse_args()

    names, O_all, T_all = build_all()
    M = O_all.shape[1]
    print(f"全 {M} 成员(rank 归一化) | O {O_all.shape} / T {T_all.shape}")

    # 可选:按 OOF AUC 精选 topk
    if args.topk > 0:
        aucs = np.array([roc_auc_score(y, O_all[:, i]) for i in range(M)])
        sel = np.argsort(-aucs)[: args.topk]
        names = [names[i] for i in sel]
        O_all, T_all = O_all[:, sel], T_all[:, sel]
        print(f"精选 top{args.topk}: O {O_all.shape}")

    # 一层等权基线(参考)
    eq = roc_auc_score(y, O_all.mean(axis=1))
    print(f"[等权 81 成员] OOF AUC: {eq:.5f}")

    if args.lr:
        oof_lr, t_lr = lr_stack(O_all, T_all, y)
        print(f"[LR C=10 stacking] OOF AUC: {roc_auc_score(y, oof_lr):.5f}")

    oof_g, t_g, fold_aucs = gbdt_stack(O_all, T_all, y)
    auc_g = roc_auc_score(y, oof_g)
    print(f"\n[GBDT stacking] OOF AUC: {auc_g:.5f} (v7 LR 基线 0.96965)")

    out = os.path.join(BASE, "submissions", "submission_v8_gbdt_stack.csv")
    pd.DataFrame({"id": test["id"], "addicted_label": t_g}).to_csv(out, index=False)
    print(f"提交文件已生成: {out}")
    print(f"测试预测 均值 {t_g.mean():.4f}  分位 {np.percentile(t_g, [25, 50, 75]).round(4)}")


if __name__ == "__main__":
    main()
