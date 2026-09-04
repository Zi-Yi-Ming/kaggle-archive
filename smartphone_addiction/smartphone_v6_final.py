# -*- coding: utf-8 -*-
"""
S6E8 v6 收尾:重建 81 成员矩阵,最终 optuna 权重搜索,生成 4 个提交文件。
不重跑嵌套 CV(已确认 optuna 比等权 +0.00108)。
"""
import os
import numpy as np
import pandas as pd
import optuna
from sklearn.metrics import roc_auc_score

optuna.logging.set_verbosity(optuna.logging.WARNING)
BASE = os.path.dirname(os.path.abspath(__file__))
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
test = pd.read_csv(os.path.join(BASE, "data", "test.csv"))
y = train["addicted_label"].values

# 重建 81 成员全矩阵(与 v6_opt 相同顺序)
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
print(f"全候选 {M} 成员 | O {O_all.shape} / T {T_all.shape}")
np.save(os.path.join(OOF, "v6_Oall.npy"), O_all)
np.save(os.path.join(OOF, "v6_Tall.npy"), T_all)

# 精选 11 成员(与 v6_blend / v6_opt 相同:0.98 去冗余,按 AUC 降序贪心)
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
print(f"精选 {len(sel)} 成员: {[names_all[i] for i in sel]}")


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


# 精选 11 成员 optuna(已由嵌套 CV 验证,是主提交)
w2, v2 = opt_weights(O2, y)
print(f"[精选{len(sel)} optuna] OOF {v2:.5f}")

# 全 81 成员 optuna(探索性)
w_all, v_all = opt_weights(O_all, y)
print(f"[全{M} optuna]        OOF {v_all:.5f}")

print("\n=== 生成提交文件 ===")
subs = {
    "submission_v6_all_eq": T_all.mean(axis=1),
    "submission_v6_all_opt": T_all @ w_all,
    "submission_v6_sel_eq": T2.mean(axis=1),
    "submission_v6_sel_opt": T2 @ w2,
}
for k, p in subs.items():
    path = os.path.join(BASE, "submissions", f"{k}.csv")
    pd.DataFrame({"id": test["id"], "addicted_label": p}).to_csv(path, index=False)
    print(f"  {k}.csv  概率均值 {p.mean():.4f}  分位 {np.percentile(p, [25, 50, 75]).round(4)}")
