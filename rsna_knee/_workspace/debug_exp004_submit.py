from __future__ import annotations

import os
import traceback
from pathlib import Path

import pandas as pd

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

comp = "rsna-knee-abnormality-detection"
path = Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission_exp004_axial_fold0.csv")
ss = Path(r"D:/桌面/Kaggle/rsna_knee/sample_submission.csv")
df = pd.read_csv(path)
s0 = pd.read_csv(ss)
print("ours cols", list(df.columns))
print("ss cols", list(s0.columns))
print("cols equal", list(df.columns) == list(s0.columns))
print("dtypes ok", df.select_dtypes("number").min().min(), df.select_dtypes("number").max().max())
print("nan", int(df.isna().sum().sum()))
print("rows", len(df), "ss rows", len(s0))

api = KaggleApi()
api.authenticate()
msg = "EXP-004 Axial fold0 only; same hparams as EXP-003 S+C fold0"
print("trying competition_submit_file / variants")
import inspect
print(inspect.signature(api.competition_submit))
# dump more error
import requests
try:
    api.competition_submit(str(path), msg, comp, quiet=False)
except Exception:
    traceback.print_exc()

# list recent submissions
print("--- recent ---")
for s in api.competition_submissions(comp) or []:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("status"), d.get("error_description"), d.get("description"))
