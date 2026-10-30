from pathlib import Path

import pandas as pd

src = Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission_exp004_axial_fold0.csv")
ss = Path(r"D:/桌面/Kaggle/rsna_knee/sample_submission.csv")
df = pd.read_csv(src)
s0 = pd.read_csv(ss)
print("ours", list(df.columns))
print("ss  ", list(s0.columns))
print("equal", list(df.columns) == list(s0.columns))
print("shape", df.shape, s0.shape)
print("nan", int(df.isna().sum().sum()))
num = df.drop(columns=["StudyInstanceUID"])
print("min/max", float(num.min().min()), float(num.max().max()))

# also write as submission.csv copy
dst = Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission_exp004_as_submission.csv")
df.to_csv(dst, index=False)
print("copy", dst)
