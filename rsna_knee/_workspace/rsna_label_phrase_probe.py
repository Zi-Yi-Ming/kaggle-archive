from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
sys.path.insert(0, str(ROOT))
import rsna_report_labels as RL  # noqa: E402

OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_label_weakspots")
train = pd.read_csv(ROOT / "train.csv")
pseudo = RL.build_pseudo_table(train, verbose=False).set_index("StudyInstanceUID")

# Why synovitis proxy may not show up
g = train[["StudyInstanceUID", "Report", "Synovitis", "Effusion"]].dropna(subset=["Synovitis"])
rows = []
for _, r in g.iterrows():
    p = pseudo.loc[r["StudyInstanceUID"], "pseudo_Synovitis"]
    e = pseudo.loc[r["StudyInstanceUID"], "pseudo_Effusion"]
    rows.append((r["Synovitis"], r["Effusion"], p, e, str(r["Report"])[:180].replace("\n", " ")))
print("=== gold Synovitis rows: pseudo vs effusion pseudo ===")
for gold, gold_e, p, e, head in rows:
    if gold > 0.5:
        print(f"goldS={gold} goldE={gold_e} pS={p} pE={e} | {head[:140]}")

print("\n=== phrase coverage tests ===")
phrases = [
    "Incipient OA of all three compartmens",
    "OA of medial compartment",
    "Effusion with synovitis",
    "Minimal degenerative subchondral bone marrow edema",
    "Insufficient fracture of medial femoral condyl",
    "bone contusion is noted",
    "osteoarthritis of the knee",
    "chondrosis",
    "diffuse high grade chondrosis",
    "Osteophytes are present",
    "synovitis",
]
for ph in phrases:
    # score via extractor on synthetic train row
    df = pd.DataFrame([{"StudyInstanceUID": "u1", "Report": ph}])
    tab = RL.build_pseudo_table(df, verbose=False)
    vals = {c: tab.iloc[0][c] for c in RL.TARGETS if c in tab.columns}
    interesting = {k: v for k, v in vals.items() if pd.notna(v) and (v > 0.3 or v < 0.25)}
    print(f"\nPHRASE: {ph}")
    print("  non-null:", {k: round(float(v), 3) for k, v in vals.items() if pd.notna(v)})
    print("  synovitis/oa*/fx/eff:", {k: vals.get(k) for k in ["Synovitis", "Medial OA", "Lateral OA", "PF OA", "Fracture", "Contusion", "Effusion"]})

# Count how often weak gold-pos reports contain GLOBAL_OA / OA_EVIDENCE / synovit stems
print("\n=== stem presence on gold-pos weak labels ===")
pats = {
    "Synovitis": [r"synovit", r"sinovit", r"effusion", r"derrame", r"υγρ", r"излив", r"sivi"],
    "OA_any": [r"\bOA\b", r"osteoarthrit", r"chondros", r"chondropath", r"artros", r"osteofit", r"osteophyt", r"compartm", r"compartment", r"gonarthros"],
    "Fracture": [r"fractur", r"contusion", r"bone bruise", r"bone marrow", r"edema", r"oedema", r"καταγμα", r"фрактур"],
}
for lab, plist in pats.items():
    col = "Synovitis" if lab == "Synovitis" else ("Fracture" if lab == "Fracture" else None)
    if col is None:
        # any OA gold positive
        mask = (train[["Medial OA", "Lateral OA", "PF OA"]] > 0.5).any(axis=1)
        subset = train[mask]
    else:
        subset = train[train[col] > 0.5]
    n = 0
    hit = 0
    for _, r in subset.iterrows():
        n += 1
        t = str(r["Report"])
        if any(re.search(p, t, re.I) for p in plist):
            hit += 1
    print(f"{lab}: gold_pos={n} stem_hit={hit} ({hit/max(n,1):.1%})")

(OUT / "phrase_probe.md").write_text("see stdout\n", encoding="utf-8")
