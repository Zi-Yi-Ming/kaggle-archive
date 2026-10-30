from __future__ import annotations

import os
import pprint

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
subs = list(api.competition_submissions("rsna-knee-abnormality-detection") or [])
print("n=", len(subs))
if subs:
    s = subs[0]
    print("type", type(s))
    print("dir sample", [a for a in dir(s) if not a.startswith("_")][:40])
    pprint.pp(s.__dict__ if hasattr(s, "__dict__") else s)
    # also try iterable row style
    print("repr", repr(s)[:500])
    if hasattr(s, "to_dict"):
        pprint.pp(s.to_dict())
