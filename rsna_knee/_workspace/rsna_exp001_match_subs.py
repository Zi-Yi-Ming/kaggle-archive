from pathlib import Path

import numpy as np
import pandas as pd

root = Path(r"D:/桌面/Kaggle/rsna_knee/artifacts/exp_001_5fold_sagittal")
labels = [
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
preds = {k: np.load(root / f"fold{k}" / "test_pred.npy") for k in range(5)}
cands = {
    "mean5": np.mean([preds[k] for k in range(5)], 0),
    "fold0_only": preds[0],
    "fold4_only": preds[4],
    "mean01": np.mean([preds[0], preds[1]], 0),
    "mean0123": np.mean([preds[k] for k in range(4)], 0),
    "mean1234": np.mean([preds[k] for k in range(1, 5)], 0),
}
files = {
    "local_exp001": r"D:/桌面/Kaggle/rsna_knee/submissions/submission_exp001_5fold.csv",
    "kaggle_like": r"D:/桌面/Kaggle/rsna_knee/submissions/submission.csv__from_Kaggle",
    "baseline": r"D:/桌面/Kaggle/rsna_knee/submissions/submission.csv",
}
for name, path in files.items():
    sub = pd.read_csv(path)
    print("==", name, "==")
    for cname, arr in cands.items():
        d = float(np.max(np.abs(sub[labels].to_numpy() - arr)))
        print(f"  vs {cname}: {d:.8f}")

print("fold pairwise max abs diff:")
for i in range(5):
    for j in range(i + 1, 5):
        print(f"  {i}-{j}: {float(np.max(np.abs(preds[i]-preds[j]))):.4f}")
