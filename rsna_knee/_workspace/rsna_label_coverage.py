from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
sys.path.insert(0, str(ROOT))

import rsna_report_labels as RL  # noqa: E402

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

OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_status_audit/label_coverage.md")
lines = []


def log(s=""):
    print(s)
    lines.append(s)


train = pd.read_csv(ROOT / "train.csv")
log(f"train studies={len(train)} reports_nonnull={train['Report'].notna().sum()}")
log(f"gold non-null per label:")
for c in LABELS:
    log(f"  {c:18s} gold={int(train[c].notna().sum()):4d}")

log("\nbuilding pseudo table from reports...")
pseudo = RL.build_pseudo_table(train, verbose=True)
log(f"pseudo shape={pseudo.shape}")

log("\n=== combined effective labels (gold first, then report fill) ===")
df = train[["StudyInstanceUID"] + LABELS].copy()
pseudo = pseudo.set_index("StudyInstanceUID")
stats = []
for c in LABELS:
    gold = int(df[c].notna().sum())
    mask = df[c].isna().values
    uids = df.loc[mask, "StudyInstanceUID"]
    vals = pseudo["pseudo_" + c].reindex(uids).values
    n_fill = int(pd.notna(vals).sum())
    # positive/negative among filled
    filled = pd.Series(vals).dropna()
    n_pos = int((filled > 0.5).sum())
    n_neg = int((filled < 0.5).sum())
    n_mid = int(((filled >= 0.4) & (filled <= 0.6)).sum())
    eff = gold + n_fill
    stats.append((c, gold, n_fill, eff, n_pos, n_neg, n_mid, eff / len(df)))
    log(
        f"  {c:18s} gold={gold:4d} +fill={n_fill:4d} => eff={eff:4d} ({eff/len(df):.1%}) "
        f"pos={n_pos:4d} neg={n_neg:4d} midish={n_mid:4d}"
    )

# macro implication: labels with low effective coverage are hard to rank
log("\n=== weakest labels by effective coverage ===")
for row in sorted(stats, key=lambda x: x[3]):
    c, gold, n_fill, eff, n_pos, n_neg, n_mid, ratio = row
    log(f"  {c:18s} eff={eff:4d} ({ratio:.1%}) pos={n_pos} neg={n_neg}")

# compare EXP-003 plane diversity already known
log("\n=== decision inputs already measured ===")
log("test_series planes: Axial 3/3 studies, Sagittal 3/3, Coronal 3/3")
log("fold0 S vs C corr=0.47; fold0 vs fold1 same-plane corr~0.83-0.88")
log("LB: fold0 S+C=0.685 BEST; +fold1=0.679; 5-fold sagittal=0.667")
log("EXP-002 A3 Contusion-only label change: 0.659 (worse)")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT)
