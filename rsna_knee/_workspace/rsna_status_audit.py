from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_status_audit")
OUT.mkdir(parents=True, exist_ok=True)

lines = []


def log(s=""):
    print(s)
    lines.append(s)


# CSV presence
for name in ["train.csv", "test.csv", "test_series.csv", "sample_submission.csv", "train_series.csv"]:
    p = ROOT / name
    log(f"{name}: exists={p.exists()} size={p.stat().st_size if p.exists() else '-'}")

# train labels
train = pd.read_csv(ROOT / "train.csv")
log(f"\ntrain.csv shape={train.shape} cols={list(train.columns)}")
label_cols = [c for c in train.columns if c not in {"StudyInstanceUID", "series", "prediction"}]
# typical RSNA knee: 12 label columns
id_like = {"StudyInstanceUID"}
cand_labels = [c for c in train.columns if c not in id_like]
log(f"non-id cols={cand_labels}")
for c in cand_labels:
    s = train[c]
    nn = s.notna().sum()
    if nn and s.dropna().dtype != object:
        log(f"  {c}: non-null={nn}/{len(s)} ({nn/len(s):.1%}) unique={s.dropna().nunique()} value_counts_head={s.value_counts(dropna=False).head(5).to_dict()}")
    else:
        log(f"  {c}: non-null={nn}/{len(s)}")

# test
test = pd.read_csv(ROOT / "test.csv")
log(f"\ntest.csv shape={test.shape} cols={list(test.columns)}")
log(test.head(10).to_string())

# test series planes
ts = pd.read_csv(ROOT / "test_series.csv")
log(f"\ntest_series.csv shape={ts.shape} cols={list(ts.columns)}")
plane_col = None
for c in ts.columns:
    if "plane" in c.lower() or "anatom" in c.lower():
        plane_col = c
if plane_col:
    log(f"test plane counts:\n{ts[plane_col].value_counts(dropna=False)}")
    log(f"test studies by plane:\n{ts.groupby(plane_col)['StudyInstanceUID'].nunique() if 'StudyInstanceUID' in ts.columns else 'no StudyInstanceUID'}")
else:
    log(f"test_series head:\n{ts.head(20).to_string()}")

# train_series if present
tr_s_path = ROOT / "train_series.csv"
if tr_s_path.exists():
    trs = pd.read_csv(tr_s_path)
    log(f"\ntrain_series.csv shape={trs.shape} cols={list(trs.columns)}")
    pc = None
    for c in trs.columns:
        if "plane" in c.lower() or "anatom" in c.lower():
            pc = c
            break
    if pc:
        log(f"train plane counts:\n{trs[pc].value_counts(dropna=False)}")
        if "StudyInstanceUID" in trs.columns:
            log(f"train unique studies total={trs['StudyInstanceUID'].nunique()}")
            log(f"studies per plane:\n{trs.groupby(pc)['StudyInstanceUID'].nunique()}")
            # studies having each plane
            for pl, g in trs.groupby(pc):
                log(f"  studies with {pl}: {g['StudyInstanceUID'].nunique()}")
else:
    log("train_series.csv missing locally — plane coverage on train unknown from CSV")

# report labels artifacts
for p in [
    ROOT / "artifacts/exp_002_a3_fold0/label_manifest.json",
    ROOT / "artifacts/exp_002_a3/label_manifest.json",
]:
    if p.exists():
        log(f"\nfound label manifest {p}")

# search pseudo label stats in code comments / logs
log("\n=== nearby label-related notes ===")
for p in ROOT.rglob("*.json"):
    if "label" in p.name.lower() and p.stat().st_size < 2_000_000:
        log(f"json {p.relative_to(ROOT)} size={p.stat().st_size}")

# sample_submission expected rows
ss = pd.read_csv(ROOT / "sample_submission.csv")
log(f"\nsample_submission shape={ss.shape}")
log(ss.head().to_string())

text = "\n".join(lines) + "\n"
(OUT / "audit.md").write_text(text, encoding="utf-8")
