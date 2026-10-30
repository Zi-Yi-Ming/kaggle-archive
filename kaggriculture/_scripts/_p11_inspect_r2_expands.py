# -*- coding: utf-8 -*-
import csv, json
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
rows = list(csv.DictReader((ROOT / "p11_r2_plan_summary.csv").open(encoding="utf-8")))
ev = json.loads(rows[0]["expand_events"])
print("=== plan0 expand events (first 40) ===")
for e in ev:
    print(e)
print("\n=== buy animals plan0 ===")
print(rows[0]["buy_animals"])
print("\n=== buy seeds plan0 ===")
print(rows[0]["buy_seeds"])

tl = list(csv.DictReader((ROOT / "p11_r2_tape_timeline.csv").open(encoding="utf-8")))
p0 = [r for r in tl if r["plan"] == "0"]
print("\n=== plan0 BUY_ANIMAL / BUY_LAND / non-zero HIRE turns ===")
for r in p0:
    detail = r["buy_detail"]
    hire = int(r["hire"])
    if "BUY_ANIMAL" in detail or "BUY_LAND" in detail or hire > 0:
        print(f"s{r['step']} d{r['day']}h{r['hour']} hire={hire} {detail}")

print("\n=== plan0 daily hire count ===")
by_day = Counter()
for r in p0:
    by_day[int(r["day"])] += int(r["hire"])
for d in sorted(by_day):
    if by_day[d]:
        print(f"  day {d}: hire x{by_day[d]}")

print("\n=== plan0 sell item frequency by day-phase ===")
phases = {0: Counter(), 1: Counter(), 2: Counter()}  # early d0-9, mid d10-19, late d20-29
for r in p0:
    if r["sell"]:
        d = int(r["day"])
        phase = 0 if d < 10 else (1 if d < 20 else 2)
        for item in r["sell_items"].split("|"):
            if item:
                phases[phase][item] += 1
for phase, c in phases.items():
    print(f"  phase{phase}: {dict(c)}")

print("\n=== plan0 worker op frequency ===")
ops = Counter()
for r in p0:
    for op in r["worker_ops"].split("|"):
        if op:
            ops[op] += 1
print(dict(ops))
