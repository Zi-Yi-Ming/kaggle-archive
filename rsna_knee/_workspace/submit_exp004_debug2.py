from __future__ import annotations

import os
from pathlib import Path

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.competitions.services.competition_api_service import (
    CompetitionApiService,
)

api = KaggleApi()
api.authenticate()
comp = "rsna-knee-abnormality-detection"

# list submissions + quota-like info
print("=== submissions ===")
subs = api.competition_submissions(comp) or []
print("n=", len(subs))
for s in subs:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("status"), d.get("error_description"), d.get("description"))

path = r"D:\桌面\Kaggle\rsna_knee\submissions\submission_exp004_axial_fold0.csv"
msg = "EXP-004 Axial fold0"

# try lower-level to capture response body
from kagglesdk.competitions.types.competition_api_service import ApiCreateSubmissionRequest

# inspect create_submission
print("create_submission sig:")
import inspect
from kagglesdk.competitions.services import competition_api_service as cas
print([x for x in dir(cas.CompetitionApiService) if "submit" in x.lower() or "create" in x.lower()])

try:
    # file upload via official method with message only
    api.competition_submit(file_name=path, message=msg, competition=comp, quiet=False)
    print("submit ok")
except Exception as e:
    print("submit fail", type(e).__name__, e)
    # try requests raw after authenticating session
    try:
        sess = api._session if hasattr(api, "_session") else None
        print("api attrs sample", [a for a in dir(api) if "session" in a.lower() or "http" in a.lower()][:20])
    except Exception as e2:
        print(e2)

print("=== after ===")
for s in api.competition_submissions(comp) or []:
    d = s.to_dict()
    print(d.get("ref"), d.get("date"), d.get("publicScore"), d.get("status"), d.get("error_description"))
