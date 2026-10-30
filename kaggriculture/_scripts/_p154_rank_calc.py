import csv
from pathlib import Path

p = next(Path(r"D:\桌面\Kaggle\kaggriculture\_research\lb").glob("*.csv"))
rows = list(csv.DictReader(p.open(encoding="utf-8")))
print("total teams", len(rows), flush=True)
print("cols", rows[0].keys() if rows else None, flush=True)
print("first", rows[0] if rows else None, flush=True)
print("last", rows[-1] if rows else None, flush=True)

# find ZiYiMing
for i, r in enumerate(rows):
    name = " ".join(str(v) for v in r.values())
    if "ZiYiMing" in name or "ZiYi" in name or "ming" in name.lower():
        print("FOUND", i + 1, r, flush=True)

# score distribution
scores = []
for r in rows:
    for k, v in r.items():
        if "score" in k.lower() or "Rank" not in k:
            try:
                scores.append((float(v), r))
                break
            except Exception:
                continue

# better: parse numeric last-ish field
parsed = []
for i, r in enumerate(rows):
    vals = list(r.values())
    sc = None
    for v in vals[::-1]:
        try:
            sc = float(str(v).replace(",", ""))
            break
        except Exception:
            continue
    parsed.append((i + 1, sc, r))

parsed_valid = [x for x in parsed if x[1] is not None]
parsed_valid.sort(key=lambda x: -x[1])
print("\nTOP 15:", flush=True)
for rank, sc, r in parsed_valid[:15]:
    print(f"  {rank:4d} {sc:8.1f} {r}", flush=True)

print("\nSCORE BANDS:", flush=True)
n = len(parsed_valid)
for pctl in (0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5):
    idx = min(int(n * pctl), n - 1)
    print(f"  top {pctl:.0%} ({idx+1}) score={parsed_valid[idx][1]:.1f}", flush=True)

# our score 2036
ours = 2036.4
better = sum(1 for _, sc, _ in parsed_valid if sc >= ours)
print(f"\nOUR {ours}: rank {better+1} / {n} (top {better/n:.1%})", flush=True)
print(f"score at rank 10%: {parsed_valid[min(int(n*0.1),n-1)][1]:.1f}", flush=True)
print(f"score at rank 20%: {parsed_valid[min(int(n*0.2),n-1)][1]:.1f}", flush=True)
print(f"score at rank 25%: {parsed_valid[min(int(n*0.25),n-1)][1]:.1f}", flush=True)
print(f"score at rank 30%: {parsed_valid[min(int(n*0.3),n-1)][1]:.1f}", flush=True)
print(f"score at rank 40%: {parsed_valid[min(int(n*0.4),n-1)][1]:.1f}", flush=True)
