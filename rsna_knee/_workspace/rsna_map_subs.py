from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
LABELS = [
    "ACL",
    "MCL",
    "Medial Meniscus",
    "Lateral Meniscus",
    "Medial OA",
    "Lateral OA",
    "PF OA",
    "Effusion",
    "Synovitis",
    "Baker's",
    "Contusion",
    "Fracture",
]


def load_pred(p: Path):
    return np.load(p) if p.exists() else None


def mean_stack(arrs):
    return np.mean(np.stack(arrs, 0), 0) if arrs else None


e1 = ROOT / "artifacts/exp_001_5fold_sagittal"
preds1 = {k: load_pred(e1 / f"fold{k}" / "test_pred.npy") for k in range(5)}
cands = {}
if all(preds1[k] is not None for k in range(5)):
    cands["exp001_mean5"] = mean_stack([preds1[k] for k in range(5)]).astype(np.float64)
for k, a in preds1.items():
    if a is not None:
        cands[f"exp001_fold{k}"] = a.astype(np.float64)

e2 = ROOT / "artifacts/exp_002_a3_fold0/fold0/test_pred.npy"
if e2.exists():
    cands["exp002_fold0"] = np.load(e2).astype(np.float64)

e3 = ROOT / "artifacts/exp_003_sagittal_coronal"
f0 = [load_pred(e3 / "fold0" / pl / "test_pred.npy") for pl in ["Sagittal", "Coronal"]]
if all(x is not None for x in f0):
    cands["exp003_fold0_SC"] = mean_stack(f0).astype(np.float64)
for pl in ["Sagittal", "Coronal"]:
    a = load_pred(e3 / f"fold0/{pl}/test_pred.npy")
    if a is not None:
        cands[f"exp003_fold0_{pl}"] = a.astype(np.float64)

e3p = ROOT / "_out/exp003_fold1_pull/artifacts/exp_003_sagittal_coronal"
f01 = []
for k in [0, 1]:
    arrs = [load_pred(e3p / f"fold{k}" / pl / "test_pred.npy") for pl in ["Sagittal", "Coronal"]]
    if all(x is not None for x in arrs):
        f01.append(mean_stack(arrs))
if len(f01) == 2:
    cands["exp003_2fold_SC"] = mean_stack(f01).astype(np.float64)

# old baseline files as raw arrays
for name in [
    "submissions/submission.csv",
    "submissions/submission_v3_2epoch.csv",
    "submissions/submission.csv__from_Kaggle",
    "submissions/submission_exp001_5fold.csv",
    "submissions/submission_exp002_a3_fold0.csv",
    "submissions/submission_exp003_sc_fold0.csv",
    "_out/exp003_fold1_pull/submission.csv",
    "_out/fold0_probe_out/submission.csv",
    "_out/fold4_final/submission.csv",
]:
    p = ROOT / name
    if not p.exists():
        continue
    df = pd.read_csv(p)
    key = "file:" + name
    cands[key] = df[LABELS].to_numpy(np.float64)

print("=== local submission files vs prediction candidates ===")
sub_files = [
    ROOT / "submissions/submission.csv",
    ROOT / "submissions/submission_v3_2epoch.csv",
    ROOT / "submissions/submission.csv__from_Kaggle",
    ROOT / "submissions/submission_exp001_5fold.csv",
    ROOT / "submissions/submission_exp002_a3_fold0.csv",
    ROOT / "submissions/submission_exp003_sc_fold0.csv",
    ROOT / "_out/exp003_fold1_pull/submission.csv",
    ROOT / "_out/fold0_probe_out/submission.csv",
    ROOT / "_out/fold4_final/submission.csv",
]
for p in sub_files:
    if not p.exists():
        continue
    df = pd.read_csv(p)
    vals = df[LABELS].to_numpy(np.float64)
    # mtime as UTC-naive from epoch
    m = datetime.utcfromtimestamp(p.stat().st_mtime)
    best = None
    best_d = 1e9
    for name, arr in cands.items():
        if name.startswith("file:"):
            continue
        if arr.shape != vals.shape:
            continue
        d = float(np.max(np.abs(arr - vals)))
        if d < best_d:
            best_d, best = d, name
    print(f"{m:%Y-%m-%d %H:%M:%S} UTC | {p.relative_to(ROOT)} | best={best} d={best_d:.3e}")

print("\n=== prediction candidates summary ===")
for name, arr in cands.items():
    if name.startswith("file:"):
        continue
    print(f"{name}: shape={arr.shape} mean={arr.mean():.6f}")

# Known API timeline from this session's successful CLI pull
api = [
    ("56331070", "2026-09-18 13:19:00", 0.679),
    ("56299753", "2026-09-17 08:25:51", 0.685),
    ("56256422", "2026-09-15 14:19:11", 0.659),
    ("56203211", "2026-09-13 08:40:28", 0.667),
    ("56162074", "2026-09-11 08:38:48", 0.663),
    ("56139481", "2026-09-10 07:04:13", 0.658),
]
print("\n=== API submissions vs nearest local file (UTC) ===")
for ref, date_s, score in api:
    dt = datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")
    near = []
    for p in sub_files:
        if not p.exists():
            continue
        m = datetime.utcfromtimestamp(p.stat().st_mtime)
        delta = abs((m - dt).total_seconds())
        df = pd.read_csv(p)
        vals = df[LABELS].to_numpy(np.float64)
        best, best_d = None, 1e9
        for name, arr in cands.items():
            if name.startswith("file:"):
                continue
            if arr.shape != vals.shape:
                continue
            d = float(np.max(np.abs(arr - vals)))
            if d < best_d:
                best_d, best = d, name
        near.append((delta, str(p.relative_to(ROOT)), m, best, best_d))
    near.sort()
    print(f"\n{ref} score={score} api_utc={date_s}")
    for delta, rel, m, best, d in near[:3]:
        print(f"  dt={delta/3600:.2f}h file={rel} mtime={m} content={best} d={d:.3e}")
