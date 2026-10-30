from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
sys.path.insert(0, str(ROOT))
import rsna_report_labels as RL  # noqa: E402

train = pd.read_csv(ROOT / "train.csv")
pseudo = RL.build_pseudo_table(train, verbose=False)

# How many silent cells would plumbing admit?
print("=== plumbing impact estimate (npos=nneg=0 but extract score > floor) ===")
# re-extract is slow; use pseudo NaN + report extract on sample of NaN gold-related
# For speed: count extract scores on all reports once
res = RL._extract_cached(train["Report"].fillna("").tolist())
rows = []
for i, r in enumerate(res):
    for t in ["Synovitis", "Medial OA", "Lateral OA", "PF OA"]:
        npos = r.get(t + "__npos", 0)
        nneg = r.get(t + "__nneg", 0)
        score = r.get(t, None)
        if npos == 0 and nneg == 0 and score is not None and score > 0.35:
            rows.append((t, score, r.get("Effusion"), r.get("Synovitis")))
df = pd.DataFrame(rows, columns=["target", "score", "effusion", "synovitis"])
print("silent-but-corrected cells score>0.35:")
print(df.groupby("target").agg(n=("score", "size"), mean_score=("score", "mean")))
print("\nSynovitis silent-corrected score bins:")
s = df[df.target == "Synovitis"]["score"]
print(pd.cut(s, [0.35, 0.5, 0.6, 0.7, 0.8, 1.0]).value_counts().sort_index())

# gold agreement if we admitted proxy
print("\n=== if plumbing admitted score>0.5 as pos on gold ===")
g = train[["StudyInstanceUID", "Synovitis", "Medial OA", "Lateral OA", "PF OA", "Effusion"]].copy()
# map uid to extract
uid2res = {u: r for u, r in zip(train["StudyInstanceUID"], res)}
for t in ["Synovitis", "Medial OA", "Lateral OA", "PF OA"]:
    sub = g[g[t] > 0.5]
    hit_proxy = 0
    miss = 0
    for _, row in sub.iterrows():
        r = uid2res[row["StudyInstanceUID"]]
        npos, nneg = r.get(t + "__npos", 0), r.get(t + "__nneg", 0)
        score = r.get(t, 0)
        if npos > 0:
            continue  # already covered
        if score > 0.5:
            hit_proxy += 1
        else:
            miss += 1
    print(f"{t}: gold_pos={len(sub)} already_npos_covered≈{len(sub)-hit_proxy-miss} proxy_would_fill={hit_proxy} still_miss={miss}")
