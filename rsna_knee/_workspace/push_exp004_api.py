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
folder = r"D:\桌面\Kaggle\rsna_knee\_push_exp004"
print("pushing", folder)
resp = api.kernels_push(folder)
print("resp", resp.to_dict() if hasattr(resp, "to_dict") else resp)
print("status", api.kernels_status("ziyiming/rsna-exp-004-axial-fold0-gpu").to_dict())
