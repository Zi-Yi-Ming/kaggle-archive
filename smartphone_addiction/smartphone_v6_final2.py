# -*- coding: utf-8 -*-
"""
S6E8 v6 收尾 v2(修复量纲问题):
FM 库成员是 log-odds 尺度(-14~+48),不能与概率成员直接线性混合。
方案:全部成员(本地/公开/FM)统一做 rank 归一化(rankdata / N,对 AUC 完全无损),
再等权/optuna 加权混合。同时补全 band 成员(bandoof_/bandtest_ 前缀)。
"""
import os
import numpy as np
import pandas as pd
import optuna
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

optuna.logging.set_verbosity(optuna.logging.WARNING)
BASE = os.path.dirname(os.path.abspath(__file__))
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
test = pd.read_csv(os.path.join(BASE, "data", "test.csv"))
y = train["addicted_label"].values
N = len(y)
NT = len(test)

import smartphone_v6_blend as B  # noqa


def rk(x):
    """rank 归一化到 (0,1]:对 AUC 单调无损,统一各成员尺度。"""
    return rankdata(x) / len(x)


def build_all():
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
    # FM:fm_* 用 oof_/test_ 前缀;band_* 用 bandoof_/bandtest_ 前缀
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


names_all, O_all, T_all = build_all()
M = len(names_all)
print(f"全候选 {M} 成员(rank 归一化) | O {O_all.shape} / T {T_all.shape}")

# 精选:0.98 去冗余(基于原始 AUC 排序,用 rank 后相关)
corr = np.corrcoef(O_all.T)
aucs = np.array([roc_auc_score(y, rk(np.load(po))) for po in
                 [os.path.join(BASE, "public_oof", "oof", f"oof_{m}.npy") for m in names_all if m in pd.read_csv(os.path.join(BASE, "public_oof", "manifest.csv")).set_index("model").index]] + [0.0])
# 简化:用 O_all 各列 AUC(rank 后与原始相同)
aucs = np.array([roc_auc_score(y, O_all[:, i]) for i in range(M)])
order = np.argsort(-aucs)
picked = []
for i in order:
    if not picked or max(abs(corr[i, p]) for p in picked) < 0.98:
        picked.append(i)
sel = np.array(picked)
O2, T2 = O_all[:, sel], T_all[:, sel]
names2 = [names_all[i] for i in sel]
print(f"精选 {len(sel)} 成员: {names2}")

# 等权基线(rank 后,尺度一致,等权有意义)
eq_all = roc_auc_score(y, O_all.mean(axis=1))
eq_sel = roc_auc_score(y, O2.mean(axis=1))
print(f"[等权] 全 {M}: {eq_all:.5f} | 精选 {len(sel)}: {eq_sel:.5f}")


def make_obj(O, y_true):
    def obj(trial):
        raw = np.array([trial.suggest_float(f"w{i}", -3.0, 3.0) for i in range(O.shape[1])])
        w = np.exp(raw - raw.max()); w /= w.sum()
        return roc_auc_score(y_true, O @ w)
    return obj


def opt_weights(O, y_true, n_trials=300):
    s = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    s.optimize(make_obj(O, y_true), n_trials=n_trials, show_progress_bar=False)
    w = np.exp(np.array([s.best_params[f"w{i}"] for i in range(O.shape[1])]))
    w /= w.sum()
    return w, s.best_value


w2, v2 = opt_weights(O2, y)
print(f"[optuna] 精选 {len(sel)}: OOF {v2:.5f}")
top = np.argsort(-w2)[:8]
for i in top:
    print(f"    {names2[i]:20s} w={w2[i]:.3f}  OOF {aucs[sel[i]]:.5f}")

w_all, v_all = opt_weights(O_all, y)
print(f"[optuna] 全 {M}: OOF {v_all:.5f}")

# 嵌套 CV(精选集,验证 optuna vs 等权的真实收益)
print("\n=== 嵌套 CV(精选集) ===")
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
opt_s, eq_s = [], []
for k, (tr, va) in enumerate(skf.split(O2, y)):
    s = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    s.optimize(make_obj(O2[tr], y[tr]), n_trials=120, show_progress_bar=False)
    wv = np.exp(np.array([s.best_params[f"w{i}"] for i in range(len(sel))])); wv /= wv.sum()
    opt_s.append(roc_auc_score(y[va], O2[va] @ wv))
    eq_s.append(roc_auc_score(y[va], O2[va].mean(axis=1)))
    print(f"  折{k}: optuna {opt_s[-1]:.5f} vs 等权 {eq_s[-1]:.5f} ({opt_s[-1]-eq_s[-1]:+.5f})")
print(f"  optuna {np.mean(opt_s):.5f} | 等权 {np.mean(eq_s):.5f} | 差异 {np.mean(opt_s)-np.mean(eq_s):+.5f}")

print("\n=== 生成提交文件(rank 概率,0-1 范围) ===")
subs = {
    "submission_v6_all_eq": T_all.mean(axis=1),
    "submission_v6_all_opt": T_all @ w_all,
    "submission_v6_sel_eq": T2.mean(axis=1),
    "submission_v6_sel_opt": T2 @ w2,
}
for k, p in subs.items():
    path = os.path.join(BASE, "submissions", f"{k}.csv")
    pd.DataFrame({"id": test["id"], "addicted_label": p}).to_csv(path, index=False)
    print(f"  {k}.csv  均值 {p.mean():.4f}  分位 {np.percentile(p, [25, 50, 75]).round(4)}  min {p.min():.3f} max {p.max():.3f}")
