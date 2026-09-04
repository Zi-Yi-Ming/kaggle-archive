# -*- coding: utf-8 -*-
"""
S6E8 v6 混合主脚本:公开库 74 成员 + FM 7 成员 + 本地 lgb/xgb
1) 等权平均基线(全 83 成员)
2) 相关性去冗余(贪心:按 AUC 降序,跳过与已选成员相关 > 阈值的)
3) optuna 权重搜索(嵌套 CV 评估泛化,防 OOF 过拟合)
4) 生成 submission_v6.csv
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

BASE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(BASE, "public_oof", "oof")
OOF = os.path.join(BASE, "oof")
train = pd.read_csv(os.path.join(BASE, "data", "train.csv"))
test = pd.read_csv(os.path.join(BASE, "data", "test.csv"))
y = train["addicted_label"].values
N = len(y)
NT = len(test)
SEEDS = [42, 7, 2026]


def load_local_oof(name):
    oofs = []
    for s in SEEDS:
        parts, ok = [], True
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
    return np.mean(oofs, axis=0) if oofs else None


def load_local_test(name):
    tsum = np.zeros(NT)
    n = 0
    for s in SEEDS:
        ok = all(os.path.exists(os.path.join(OOF, f"{name}_s{s}_f{k}_test.npy")) for k in range(5))
        if ok:
            for k in range(5):
                tsum += np.load(os.path.join(OOF, f"{name}_s{s}_f{k}_test.npy"))
            n += 1
    return tsum / (n * 5) if n else None


def main():
    names, oofs, tests = [], [], []
    manifest = pd.read_csv(os.path.join(BASE, "public_oof", "manifest.csv")).set_index("model")

    # 本地模型
    for m in ["lgb", "xgb"]:
        o, t = load_local_oof(m), load_local_test(m)
        if o is not None:
            names.append(f"local_{m}"); oofs.append(o); tests.append(t)
            print(f"[本地] {m}: OOF {roc_auc_score(y, o):.5f}")

    # 公开库 74 成员
    for model in manifest.index:
        po, pt = os.path.join(PUB, f"oof_{model}.npy"), os.path.join(PUB, f"test_{model}.npy")
        if os.path.exists(po):
            names.append(model); oofs.append(np.load(po)); tests.append(np.load(pt))

    # FM 库成员(根目录下 oof_fm*.npy / bandoof_*.npy)
    fm_files = ["fmdeep", "fmnum", "fmplr", "fmpure", "fmwide", "band_mid", "bandfm2"]
    fm_src = os.path.join(BASE, "public_oof")
    for f in fm_files:
        po, pt = os.path.join(fm_src, f"oof_{f}.npy"), os.path.join(fm_src, f"test_{f}.npy")
        if os.path.exists(po):
            names.append(f"fm_{f}"); oofs.append(np.load(po)); tests.append(np.load(pt))

    O = np.column_stack(oofs)  # (N, M)
    T = np.column_stack(tests)  # (NT, M)
    print(f"\n候选成员: {len(names)} 个 | OOF 矩阵 {O.shape}")

    # ---------- 1) 等权平均基线 ----------
    eq = O.mean(axis=1)
    eq_auc = roc_auc_score(y, eq)
    print(f"[基线] 全 {len(names)} 成员等权平均 OOF AUC: {eq_auc:.5f}")

    # ---------- 2) 相关性去冗余(贪心) ----------
    corr = np.corrcoef(O.T)
    aucs = np.array([roc_auc_score(y, o) for o in oofs])
    order = np.argsort(-aucs)
    sel, picked = [], []
    for i in order:
        if not picked:
            sel.append(i); picked.append(i); continue
        if max(abs(corr[i, p]) for p in picked) < 0.98:
            sel.append(i); picked.append(i)
    sel = np.array(sel)
    print(f"[去冗余] 阈值 0.98: {len(names)} -> {len(sel)} 成员")
    for i in sel:
        print(f"  {names[i]:20s} OOF {aucs[i]:.5f}")

    O2, T2 = O[:, sel], T[:, sel]
    names2 = [names[i] for i in sel]

    # 去冗余后等权
    eq2 = O2.mean(axis=1)
    print(f"[基线] 去冗余后等权平均 OOF AUC: {roc_auc_score(y, eq2):.5f}")

    np.save(os.path.join(OOF, "v6_names.npy"), np.array(names2, dtype=object), allow_pickle=True)
    np.save(os.path.join(OOF, "v6_O2.npy"), O2)
    np.save(os.path.join(OOF, "v6_T2.npy"), T2)
    print(f"已保存 v6 精选矩阵 {O2.shape} / {T2.shape}")


if __name__ == "__main__":
    main()
