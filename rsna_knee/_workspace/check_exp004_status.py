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
slug = "ziyiming/rsna-exp-004-axial-fold0-gpu"
print("=== status ===")
try:
    st = api.kernels_status(slug)
    print(st)
    if hasattr(st, "to_dict"):
        print(st.to_dict())
    if hasattr(st, "__dict__"):
        print(st.__dict__)
except Exception as e:
    print("status err", type(e).__name__, e)

print("=== list mine search exp004 ===")
ks = api.kernels_list(user="ziyiming", search="exp004", page_size=10)
for k in ks or []:
    print(k.to_dict() if hasattr(k, "to_dict") else k)

print("=== kernels_push help ===")
import inspect
print(inspect.signature(api.kernels_push))
print(api.kernels_push.__doc__)
