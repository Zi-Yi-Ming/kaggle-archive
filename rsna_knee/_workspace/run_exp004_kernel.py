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
slug = "ziyiming/rsna-exp004-axial-fold0-gpu"
print("starting kernel", slug)
try:
    api.kernels_run(slug)
    print("kernels_run returned")
except Exception as e:
    print("kernels_run error:", type(e).__name__, e)

# status
try:
    st = api.kernels_status(slug)
    print("status:", st)
    if hasattr(st, "to_dict"):
        print(st.to_dict())
except Exception as e:
    print("status error:", type(e).__name__, e)
