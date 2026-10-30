from __future__ import annotations

import os
import time
from pathlib import Path

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
slug = "ziyiming/rsna-exp-004-axial-fold0-gpu"
print("STATUS", api.kernels_status(slug).to_dict())

out = Path(r"D:/桌面/Kaggle/rsna_knee/_out/exp004_axial_pull")
out.mkdir(parents=True, exist_ok=True)
print("pulling output to", out)
api.kernels_output(slug, path=str(out), quiet=False)
print("files:")
for p in sorted(out.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(out)} {p.stat().st_size}")
