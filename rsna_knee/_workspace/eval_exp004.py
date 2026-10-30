from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

PULL = Path(r"D:/桌面/Kaggle/rsna_knee/_out/exp004_axial_pull")
ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
OUT = Path(r"D:/桌面/Kaggle/rsna_knee/submissions")
OUT.mkdir(parents=True, exist_ok=True)
W = Path(r"D:/桌面/Kaggle/_workspace/exp004_eval")
W.mkdir(parents=True, exist_ok=True)

LABELS = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

meta = json.loads((PULL / "artifacts/exp_004_axial_fold0/fold0/Axial/meta.json").read_text(encoding="utf-8"))
print("META", json.dumps(meta, ensure_ascii=False, indent=2))

axial = np.load(PULL / "artifacts/exp_004_axial_fold0/fold0/Axial/test_pred.npy").astype(np.float64)
uid_ax = pd.read_csv(PULL / "artifacts/exp_004_axial_fold0/fold0/Axial/test_uid.csv")["StudyInstanceUID"].tolist()
sub = pd.read_csv(PULL / "submission.csv")
print("sub shape", sub.shape, "uid_match", sub["StudyInstanceUID"].tolist() == uid_ax)
print("axial range", float(axial.min()), float(axial.max()), "mean", float(axial.mean()))

# S+C fold0 from exp003
e3 = ROOT / "artifacts/exp_003_sagittal_coronal/fold0"
sag = np.load(e3 / "Sagittal/test_pred.npy").astype(np.float64)
cor = np.load(e3 / "Coronal/test_pred.npy").astype(np.float64)
uid_sc = pd.read_csv(ROOT / "artifacts/exp_003_sagittal_coronal/test_uid.csv")["StudyInstanceUID"].tolist()
print("uid axial vs sc", uid_ax == uid_sc)
sc = 0.5 * (sag + cor)
sca = (sag + cor + axial) / 3.0
sca_w = 0.4 * sag + 0.3 * cor + 0.3 * axial  # mild diversity-aware mix, not trained

print("corr axial vs sag", float(np.corrcoef(axial.ravel(), sag.ravel())[0,1]))
print("corr axial vs cor", float(np.corrcoef(axial.ravel(), cor.ravel())[0,1]))
print("corr axial vs sc", float(np.corrcoef(axial.ravel(), sc.ravel())[0,1]))
print("mean|axial-sc|", float(np.mean(np.abs(axial - sc))))
print("mean|sag-cor|", float(np.mean(np.abs(sag - cor))))

# per-label mean shift
print("\nper-label means:")
for i, lab in enumerate(LABELS):
    print(f"  {lab:18s} axial={axial[:,i].mean():.3f} sc={sc[:,i].mean():.3f} sca={(sag[:,i]+cor[:,i]+axial[:,i])/3:.3f}")

# write candidate submissions
def write_sub(arr, path):
    df = pd.DataFrame(arr, columns=LABELS)
    df.insert(0, "StudyInstanceUID", uid_ax)
    df.to_csv(path, index=False)
    print("wrote", path, df.shape)

write_sub(axial, OUT / "submission_exp004_axial_fold0.csv")
write_sub(sc, W / "submission_exp003_sc_fold0_recomputed.csv")
write_sub(sca, W / "submission_exp004_sca_fold0_mean.csv")

# log excerpts
log = (PULL / "rsna-exp-004-axial-fold0-gpu.log").read_text(encoding="utf-8", errors="ignore")
# log is jsonl-ish
for pat in ["artifact", "ensemble", "submission", "Axial", "train", "returncode", "OOF", "preflight", "epoch"]:
    pass
# extract useful stdout lines
lines = []
for m in re.finditer(r'"data":"([^"]*)"', log):
    s = m.group(1).encode("utf-8").decode("unicode_escape")
    if any(k in s for k in ["artifact", "Axial", "submission", "returncode", "epoch", "preflight", "train", "ensemble", "GPU", "exp004"]):
        if "wheel" in s or "nvidia" in s or "pip" in s:
            continue
        lines.append(s.strip())
print("\n=== log highlights ===")
for s in lines[-40:]:
    print(s)

print("\nTIMING from meta: train_sec=", meta.get("fold_train_time_sec"), "infer_sec=", meta.get("fold_inference_time_sec"))
print("hours=", None if not meta.get("fold_train_time_sec") else meta["fold_train_time_sec"]/3600)
