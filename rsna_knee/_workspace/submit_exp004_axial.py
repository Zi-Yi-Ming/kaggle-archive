from __future__ import annotations

import os

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
comp = "rsna-knee-abnormality-detection"
path = r"D:\桌面\Kaggle\rsna_knee\submissions\submission_exp004_axial_fold0.csv"
msg = "EXP-004 Axial fold0 only; same hparams as EXP-003 S+C fold0; single variable=plane axial"
print("submitting", path)
api.competition_submit(path, msg, comp)
print("submitted, listing:")
for s in api.competition_submissions(comp) or []:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("url"))
