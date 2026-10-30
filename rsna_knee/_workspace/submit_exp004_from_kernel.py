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
slug = "ziyiming/rsna-exp-004-axial-fold0-gpu"

print("status", api.kernels_status(slug).to_dict())
# inspect competition_submit signature / code competition submit
import inspect

print(inspect.signature(api.competition_submit))
src = inspect.getsource(api.competition_submit)
print(src[:2500])

print("trying kernel-based submit kwargs")
for kwargs in [
    dict(file_name="submission.csv", message="EXP-004 Axial fold0", competition=comp, kernel=slug),
    dict(file_name="submission.csv", message="EXP-004 Axial fold0", competition=comp, kernel_slug=slug),
]:
    print("try", kwargs.keys())
    try:
        api.competition_submit(**kwargs)
        print("OK", kwargs)
        break
    except TypeError as e:
        print("TypeError", e)
    except Exception as e:
        print(type(e).__name__, str(e)[:300])

print("=== submissions ===")
for s in api.competition_submissions(comp) or []:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("url"))
