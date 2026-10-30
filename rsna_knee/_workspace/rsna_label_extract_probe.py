from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
sys.path.insert(0, str(ROOT))
import rsna_report_labels as RL  # noqa: E402

phrases = [
    "Incipient OA of all three compartmens",
    "OA of medial compartment",
    "Effusion with synovitis",
    "Large effusion",
    "Minimal degenerative subchondral bone marrow edema",
    "Insufficient fracture of medial femoral condyl with adjacent bone marrow oedema",
    "bone contusion is noted in the posterolateral corner",
    "osteoarthritis of the knee",
    "chondrosis",
    "diffuse high grade chondrosis",
    "Osteophytes are present",
    "synovitis",
    "Small joint effusion with synovial thickening compatible with synovitis",
    "Effusion with synovitis. OA of medial compartment.",
    "all three compartments show osteoarthritis",
    "tricompartmental osteoarthritis",
    "Incipient OA of all three compartments",
]

rows = []
for ph in phrases:
    res = RL.extract(ph)
    row = {"phrase": ph}
    for t in RL.TARGETS:
        row[t] = res.get(t)
        row[t + "_npos"] = res.get(t + "__npos")
        row[t + "_nneg"] = res.get(t + "__nneg")
        row[t + "_pseudo"] = RL.report_score_to_target(res, t)
    rows.append(row)

for row in rows:
    print("=" * 60)
    print(row["phrase"])
    for t in ["Synovitis", "Medial OA", "Lateral OA", "PF OA", "Fracture", "Contusion", "Effusion"]:
        print(
            f"  {t:14s} score={row[t]} npos={row[t+'_npos']} nneg={row[t+'_nneg']} -> pseudo={row[t+'_pseudo']}"
        )

# gold synovitis: how many have pE evidence that would fire proxy if kept
train = pd.read_csv(ROOT / "train.csv")
pseudo = RL.build_pseudo_table(train, verbose=False)
print("\n=== gold Synovitis + pseudo_Effusion available but pseudo_Synovitis NaN ===")
m = train.merge(pseudo, on="StudyInstanceUID")
sub = m[(m["Synovitis"] > 0.5) & (m["pseudo_Synovitis"].isna())]
print("count", len(sub))
print("of which pseudo_Effusion notna", int(sub["pseudo_Effusion"].notna().sum()))
print("of which pseudo_Effusion>0.5", int((sub["pseudo_Effusion"] > 0.5).sum()))
print("extract-level synovitis score distribution on those:")
for _, r in sub.head(8).iterrows():
    res = RL.extract(str(r["Report"]))
    print("  extS", res.get("Synovitis"), "npos", res.get("Synovitis__npos"), "pE", r["pseudo_Effusion"], "|", str(r["Report"])[:100].replace("\n", " "))
