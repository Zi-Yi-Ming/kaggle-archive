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
methods = [m for m in dir(api) if "kernel" in m.lower()]
print("kernel methods:")
for m in methods:
    print(" ", m)

# try common variants
slug = "ziyiming/rsna-exp004-axial-fold0-gpu"
for name in [
    "kernels_run",
    "kernel_run",
    "kernels_start",
    "kernels_push",
    "kernels_status",
    "kernel_get",
    "kernels_get",
    "kernels_list",
]:
    if hasattr(api, name):
        print("HAS", name)
        fn = getattr(api, name)
        try:
            import inspect

            print("  sig", inspect.signature(fn))
        except Exception:
            pass

# list own kernels search exp004
try:
    ks = api.kernels_list(user="ziyiming", search="exp004", page_size=10)
    print("list exp004:")
    for k in ks or []:
        d = k.to_dict() if hasattr(k, "to_dict") else k
        print(d)
except Exception as e:
    print("list err", type(e).__name__, e)

# try status with different formats
for ref in [slug, "rsna-exp004-axial-fold0-gpu", "ziyiming/rsna-exp004-axial-fold0-gpu"]:
    try:
        st = api.kernels_status(ref)
        print("status", ref, st)
    except Exception as e:
        print("status fail", ref, type(e).__name__, str(e)[:200])
