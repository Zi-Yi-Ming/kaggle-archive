from __future__ import annotations

import os
import shutil
import tempfile
import traceback
from pathlib import Path

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
comp = "rsna-knee-abnormality-detection"
src = Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission_exp004_axial_fold0.csv")

print("=== current submissions ===")
for s in api.competition_submissions(comp) or []:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("status"), d.get("error_description"), repr(d.get("description"))[:80])

# submit from a clean dir with canonical filename
td = Path(tempfile.mkdtemp(prefix="kaggle_sub_"))
dst = td / "submission.csv"
shutil.copy(src, dst)
print("submitting", dst, "size", dst.stat().st_size)
try:
    api.competition_submit(file_name=str(dst), message="EXP-004 Axial fold0", competition=comp, quiet=False)
    print("SUBMIT_OK")
except Exception:
    traceback.print_exc()

print("=== after ===")
for s in api.competition_submissions(comp) or []:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("status"), d.get("error_description"))
