from pathlib import Path

import numpy as np
import pandas as pd

PULL = Path(r"D:/桌面/Kaggle/rsna_knee/_out/exp004_axial_pull")
ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
OUT = ROOT / "submissions"
LABELS = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]
axial = np.load(PULL / "artifacts/exp_004_axial_fold0/fold0/Axial/test_pred.npy").astype(np.float64)
uid = pd.read_csv(PULL / "artifacts/exp_004_axial_fold0/fold0/Axial/test_uid.csv")["StudyInstanceUID"].tolist()
df = pd.DataFrame(axial, columns=LABELS)
df.insert(0, "StudyInstanceUID", uid)
p = OUT / "submission_exp004_axial_fold0.csv"
df.to_csv(p, index=False)
print("wrote", p)

sag = np.load(ROOT / "artifacts/exp_003_sagittal_coronal/fold0/Sagittal/test_pred.npy").astype(np.float64)
cor = np.load(ROOT / "artifacts/exp_003_sagittal_coronal/fold0/Coronal/test_pred.npy").astype(np.float64)
sca = (sag + cor + axial) / 3
df2 = pd.DataFrame(sca, columns=LABELS)
df2.insert(0, "StudyInstanceUID", uid)
p2 = OUT / "submission_exp004_sca_fold0_mean.csv"
df2.to_csv(p2, index=False)
print("wrote", p2)
print("corr axial-sag", float(np.corrcoef(axial.ravel(), sag.ravel())[0, 1]))
print("corr axial-cor", float(np.corrcoef(axial.ravel(), cor.ravel())[0, 1]))
print("train_h", 6515.215463638306 / 3600)
print(df.head(2).to_string())
