# -*- coding: utf-8 -*-
"""
S6E8 v6 选成员:验证公开库对齐 + 相关性分析,挑选与本地模型异构的公开成员。
只读 OOF,不训练。
"""
import os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

BASE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(BASE, "public_oof", "oof")
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
y = train["addicted_label"].values
N = len(y)
SEEDS = [42, 7, 2026]

manifest = pd.read_csv(os.path.join(BASE, "public_oof", "manifest.csv"))
manifest = manifest.set_index("model")

# ---------- 1) 本地模型种子平均 ----------
def load_local(name):
    oofs = []
    for s in SEEDS:
        parts = []
        ok = True
        for k in range(5):
            p = os.path.join(OOF, f"{name}_s{s}_f{k}_va_pred.npy")
            vi = os.path.join(OOF, f"{name}_s{s}_f{k}_va_idx.npy")
            if not (os.path.exists(p) and os.path.exists(vi)):
                ok = False
                break
            parts.append((np.load(vi), np.load(p)))
        if ok:
            o = np.zeros(N)
            for vi, p in parts:
                o[vi] = p
            oofs.append(o)
    if not oofs:
        return None
    return np.mean(oofs, axis=0)

local = {}
for m in ["lgb", "xgb"]:
    o = load_local(m)
    if o is not None:
        local[m] = o
        print(f"[本地] {m} 种子平均 OOF AUC {roc_auc_score(y, o):.5f}")

# ---------- 2) 加载公开库全部成员,验证对齐 ----------
print("\n=== 公开库对齐验证(计算 AUC vs manifest) ===")
pub = {}
for model in manifest.index:
    p = os.path.join(PUB, f"oof_{model}.npy")
    if not os.path.exists(p):
        continue
    o = np.load(p)
    assert len(o) == N, f"{model} 长度 {len(o)} != {N}"
    auc = roc_auc_score(y, o)
    ref = manifest.loc[model, "oof_auc"]
    d = auc - ref
    flag = "OK" if abs(d) < 5e-4 else "**MISMATCH**"
    if abs(d) < 5e-4:
        pub[model] = o
    print(f"  {model:16s} 计算 {auc:.5f} vs manifest {ref:.5f} ({d:+.5f}) {flag}")
print(f"对齐通过: {len(pub)}/{len(manifest)} 个成员可用")

# ---------- 3) 相关性:本地 vs 公开最强成员 ----------
print("\n=== 相关性分析 ===")
names = list(local) + list(pub)
mat = np.column_stack([local[m] if m in local else pub[m] for m in names])
corr = np.corrcoef(mat.T)

print("本地模型与公开成员的相关性(升序,最异构在前):")
rows = []
for m in names:
    if m in local:
        continue
    c = max(corr[names.index(m), names.index(ml)] for ml in local)
    rows.append((m, manifest.loc[m, "oof_auc"] if m in manifest.index else 0.0, c))
rows.sort(key=lambda r: (r[2], -r[1]))
for m, auc, c in rows[:25]:
    print(f"  {m:16s} OOF {auc:.5f}  与本地最大相关 {c:.4f}")

np.save(os.path.join(BASE, "oof", "v6_names.npy"), np.array(names, dtype=object), allow_pickle=True)
np.save(os.path.join(BASE, "oof", "v6_mat.npy"), mat)
print(f"\n已保存 v6 候选矩阵 {mat.shape}({len(names)} 成员)")
