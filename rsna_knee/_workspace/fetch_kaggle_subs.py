from __future__ import annotations

import os
from pathlib import Path

# clear proxy for kaggle api
for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_submission_timeline")
OUT.mkdir(parents=True, exist_ok=True)

try:
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    subs = list(api.competition_submissions("rsna-knee-abnormality-detection") or [])
except Exception as e:
    print("KAGGLE_API_FAIL:", type(e).__name__, e)
    subs = []

print(f"api_submissions={len(subs)}")
lines = ["# Kaggle submissions raw", ""]
for s in subs:
    row = {
        "ref": getattr(s, "ref", None),
        "date": str(getattr(s, "date", None)),
        "publicScore": getattr(s, "publicScore", None),
        "privateScore": getattr(s, "privateScore", None),
        "fileName": getattr(s, "fileName", None),
        "description": getattr(s, "description", None),
        "status": str(getattr(s, "status", None)),
    }
    print("{ref}|{date}|{publicScore}|{fileName}|{description}|{status}".format(**row))
    lines.append(
        f"- {row['ref']} | {row['date']} | public={row['publicScore']} | {row['fileName']} | desc={row['description']!r} | {row['status']}"
    )

(OUT / "kaggle_submissions_raw.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT / "kaggle_submissions_raw.md")
