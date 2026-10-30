from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path

api = KaggleApi()
api.authenticate()

# download full leaderboard if possible
out = Path(r"D:\桌面\Kaggle\kaggriculture\_research\leaderboard.csv")
try:
    api.competition_leaderboard_download("kaggriculture", path=str(out.parent), quiet=False)
    print("downloaded to", out.parent, list(out.parent.glob("*.csv")) + list(out.parent.glob("*leader*")))
except Exception as e:
    print("dl fail", e)

# paginate view
rows = []
token = None
for page in range(200):
    batch = api.competition_leaderboard_view("kaggriculture", page_size=100, page_token=token)
    if not batch:
        print("empty page", page, flush=True)
        break
    for r in batch:
        d = r.to_dict() if hasattr(r, "to_dict") else r
        rows.append(d)
    print(f"page {page} got {len(batch)} total {len(rows)}", flush=True)
    # find token
    token = None
    for r in batch[-1:]:
        d = r.to_dict() if hasattr(r, "to_dict") else {}
        token = d.get("nextPageToken") or d.get("next_page_token")
    if not token:
        # try view result metadata
        break
    if len(rows) > 10000:
        break

print("total rows", len(rows), flush=True)
if rows:
    print("sample keys", rows[0].keys() if isinstance(rows[0], dict) else rows[0], flush=True)
    print("first", rows[0], flush=True)
    print("last", rows[-1], flush=True)

# find us
for i, d in enumerate(rows):
    name = str(d.get("teamName") or d.get("team_name") or "")
    if "ZiYiMing" in name or "2036" in str(d.get("score") or d.get("publicScore") or ""):
        print("FOUND rank", i + 1, d, flush=True)

Path(r"D:\桌面\Kaggle\kaggriculture\_research\leaderboard_paginated.json").write_text(
    __import__("json").dumps(rows[:5000], indent=2, ensure_ascii=False, default=str),
    encoding="utf-8",
)
print("saved", flush=True)
