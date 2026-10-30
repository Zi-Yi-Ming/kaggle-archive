from __future__ import annotations

import os
from pathlib import Path

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_submission_timeline/submission_map.md")
OUT.parent.mkdir(parents=True, exist_ok=True)

api = KaggleApi()
api.authenticate()
subs = list(api.competition_submissions("rsna-knee-abnormality-detection") or [])

# content map from local verification
# score -> likely experiment based on url + local file content match
rows = []
for s in subs:
    d = s.to_dict()
    rows.append(d)

lines = []
lines.append("# RSNA 已提交映射（Kaggle API `url` 字段 = 提交来源 kernel）")
lines.append("")
lines.append("| ref | date (UTC) | publicScore | kernel/url | 判定 |")
lines.append("|---|---|---|---|---|")

# manual judgment after we print urls
for d in rows:
    url = d.get("url") or ""
    score = d.get("publicScore")
    ref = d.get("ref")
    date = d.get("date")
    lines.append(f"| {ref} | {date} | {score} | `{url}` | |")

print("REF|DATE|SCORE|URL")
for d in rows:
    print(f"{d.get('ref')}|{d.get('date')}|{d.get('publicScore')}|{d.get('url')}")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT)
