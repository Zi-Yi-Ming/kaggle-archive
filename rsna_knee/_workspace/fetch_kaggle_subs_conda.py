from __future__ import annotations

import os
import sys

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

print("python", sys.executable)
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
subs = list(api.competition_submissions("rsna-knee-abnormality-detection") or [])
print("n=", len(subs))
for s in subs:
    print(
        "|".join(
            str(x)
            for x in [
                getattr(s, "ref", ""),
                getattr(s, "date", ""),
                getattr(s, "publicScore", ""),
                getattr(s, "privateScore", ""),
                getattr(s, "fileName", ""),
                getattr(s, "description", ""),
                getattr(s, "status", ""),
            ]
        )
    )
