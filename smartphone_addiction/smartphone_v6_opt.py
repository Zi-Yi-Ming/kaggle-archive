# -*- coding: utf-8 -*-
"""
S6E8 v6 权重优化:optuna 搜索 + 嵌套 CV 评估 + 生成提交
1) 全 81 成员 vs 精选 11 成员:等权基线对比
2) optuna 搜索权重(最大化 OOF AUC)
3) 嵌套 CV(外层5折)无偏评估权重搜索的真实收益(防 OOF 过拟合)
4) 用全量 OOF 优化权重,生成 submission_v6.csv
"""
import os
import numpy as np
import pandas as pd
import optuna
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

optuna.logging.set_verbosity(optuna.logging.WARNING)
BASE = os.path.dirname(os.path.abspath(__file__))
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
test = pd.read_csv(os.path.join(BASE, "data", "test.csv"))
y = train["addicted_label"].values

# 重新构建 81 成员全矩阵
import smartphone_v6_blend as B  # noqa

names_all, oofs_all, tests_all = [], [], []
manifest = pd.read_csv(os.path.join(BASE, "public_oof", "manifest.csv")).set_index("model")
for m in ["lgb", "xgb"]:
    o, t = B.load_local_oof(m), B.load_local_test(m)
    if o is not None:
        names_all.append(f"local_{m}"); oofs_all.append(o); tests_all.append(t)
for model in manifest.index:
    po, pt = os.path.join(BASE, "public_oof", "oof", f"oof_{model}.npy"), os.path.join(BASE, "public_oof", "oof", f"test_{model}.npy")
    if os.path.exists(po):
        names_all.append(model); oofs_all.append(np.load(po)); tests_all.append(np.load(pt))
for f in ["fmdeep", "fmnum", "fmplr", "fmpure", "fmwide", "band_mid", "bandfm2"]:
    po, pt = os.path.join(BASE, "public_oof", f"oof_{f}.npy"), os.path.join(BASE, "public_oof", f"test_{f}.npy")
    if os.path.exists(po):
        names_all.append(f"fm_{f}"); oofs_all.append(np.load(po)); tests_all.append(np.load(pt))

O_all = np.column_stack(oofs_all)
T_all = np.column_stack(tests_all)
M = len(names_all)
print(f"全候选 {M} 成员")

# 精选 11 成员(0.98 去冗余,与 v6_blend 相同逻辑)
corr = np.corrcoef(O_all.T)
aucs = np.array([roc_auc_score(y, o) for o in oofs_all])
order = np.argsort(-aucs)
picked = []
for i in order:
    if not picked or max(abs(corr[i, p]) for p in picked) < 0.98:
        picked.append(i)
sel = np.array(picked)
O2, T2 = O_all[:, sel], T_all[:, sel]
names2 = [names_all[i] for i in sel]

def eq_auc(O):
    return roc_auc_score(y, O.mean(axis=1))

print(f"[等权] 全 {M} 成员: {eq_auc(O_all):.5f}  | 精选 {len(sel)} 成员: {eq_auc(O2):.5f}")

# ---------- optuna 搜索(softmax 权重,全 OOF 上优化) ----------
def make_obj(O, y_true):
    def obj(trial):
        raw = np.array([trial.suggest_float(f"w{i}", -3.0, 3.0) for i in range(O.shape[1])])
        w = np.exp(raw - raw.max()); w /= w.sum()
        return roc_auc_score(y_true, O @ w)
    return obj

n_trials = 300
study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(make_obj(O2, y), n_trials=n_trials, show_progress_bar=False)
w2 = np.exp(np.array([study.best_params[f"w{i}"] for i in range(len(sel))]))
w2 /= w2.sum()
print(f"[optuna] 精选 {len(sel)} 成员权重搜索: OOF AUC {study.best_value:.5f}")
top = np.argsort(-w2)[:10]
for i in top:
    print(f"    {names2[i]:20s} w={w2[i]:.3f}  OOF {aucs[sel[i]]:.5f}")

# ---------- 嵌套 CV 评估权重搜索的真实收益 ----------
print("\n=== 嵌套 CV(外层5折):权重搜索 vs 等权 的无偏对比 ===")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
opt_scores, eq_scores = [], []
for fold, (tr, va) in enumerate(skf.split(O2, y)):
    Ot, Ov = O2[tr], O2[va]
    yt, yv = y[tr], y[va]
    s = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    s.optimize(make_obj(Ot, yt), n_trials=120, show_progress_bar=False)
    wv = np.exp(np.array([s.best_params[f"w{i}"] for i in range(len(sel))])); wv /= wv.sum()
    opt_scores.append(roc_auc_score(yv, Ov @ wv))
    eq_scores.append(roc_auc_score(yv, Ov.mean(axis=1)))
    print(f"  折{fold}: optuna {opt_scores[-1]:.5f} vs 等权 {eq_scores[-1]:.5f} ({opt_scores[-1]-eq_scores[-1]:+.5f})")
print(f"  optuna 平均 {np.mean(opt_scores):.5f} | 等权 平均 {np.mean(eq_scores):.5f} | 差异 {np.mean(opt_scores)-np.mean(eq_scores):+.5f}")

# ---------- 生成提交:全量 OOF 优化权重(用更稳的精选集),也可选全 81 ----------
print("\n=== 生成提交 ===")
# 在全 81 上也搜索一次对比
study_all = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
study_all.optimize(make_obj(O_all), n_trials=n_trials, show_progress_bar=False)
w_all = np.exp(np.array([study_all.best_params[f"w{i}"] for i in range(M)])); w_all /= w_all.sum()
print(f"[optuna] 全 {M} 成员: OOF AUC {study_all.best_value:.5f}")

# 提交用哪个?嵌套 CV 里如果 optuna 没明显赢,用等权更稳;这里综合:全81等权 + 精选optuna 都生成
subs = {
    "v6_all_eq": T_all.mean(axis=1),
    "v6_all_opt": T_all @ w_all,
    "v6_sel_eq": T2.mean(axis=1),
    "v6_sel_opt": T2 @ w2,
}
for k, p in subs.items():
    pd.DataFrame({"id": test["id"], "addicted_label": p}).to_csv(
        os.path.join(BASE, "submissions", f"{k}.csv"), index=False)
    print(f"  已写 {k}.csv  prob均值 {p.mean():.4f}")
