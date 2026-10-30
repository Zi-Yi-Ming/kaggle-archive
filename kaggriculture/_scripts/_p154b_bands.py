import csv
from pathlib import Path

p = next(Path(r"D:\桌面\Kaggle\kaggriculture\_research\lb").glob("*.csv"))
rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
print("n", len(rows), "cols", list(rows[0].keys()), flush=True)
rows.sort(key=lambda r: int(r["Rank"]))
print("rank1", rows[0], flush=True)
print("rank1585", rows[1584], flush=True)
for k in (50, 100, 250, 500, 1000, 1500, 1585, 2000, 2500, 3000):
    if k - 1 < len(rows):
        r = rows[k - 1]
        print(f"rank {k}: score {r['Score']}  {r['TeamName']}", flush=True)
print("--- pct ---", flush=True)
n = len(rows)
for pct in (0.01, 0.05, 0.1, 0.15, 0.2, 0.25):
    idx = min(int(n * pct), n - 1)
    r = rows[idx]
    print(f"top {pct:.0%} rank {idx+1}: score {r['Score']}", flush=True)
