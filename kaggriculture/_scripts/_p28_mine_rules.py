# -*- coding: utf-8 -*-
"""P28b: mine decision rules from R2 trajectories (no raw tape)."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
rows = list(csv.DictReader((ROOT / "p28_r2_trajectories.csv").open(encoding="utf-8")))
for r in rows:
    for k in ("step", "day", "hour", "hands", "n_land", "plants", "melon", "animals", "empty", "seed"):
        r[k] = int(float(r[k]))
    r["money"] = float(r["money"])

# 1) market ops at hour 0 by day
print("=== hour-0 market by day (first 3 seeds) ===")
h0 = [r for r in rows if r["hour"] == 0]
for day in range(0, 16):
    ds = [r for r in h0 if r["day"] == day and r["seed"] <= 3]
    if not ds:
        continue
    ops = Counter()
    for r in ds:
        for o in (r["market_ops"] or "").split("|"):
            if o:
                ops[o] += 1
    avg_hands = sum(r["hands"] for r in ds) / len(ds)
    avg_money = sum(r["money"] for r in ds) / len(ds)
    print(f"  d{day:02d} n={len(ds)} money={avg_money:.0f} hands={avg_hands:.1f} ops={dict(ops)}")

# 2) worker op distribution by day phase
print("\n=== worker ops by phase ===")
phases = [(0, 2, "SETUP"), (3, 9, "GROW"), (10, 15, "CASH"), (16, 25, "SCALE"), (26, 29, "TERM")]
for lo, hi, name in phases:
    ops = Counter()
    for r in rows:
        if lo <= r["day"] <= hi:
            for o in (r["worker_ops"] or "").split("|"):
                if o:
                    ops[o] += 1
    total = sum(ops.values()) or 1
    top = ops.most_common(8)
    print(f"  {name}: " + ", ".join(f"{k}={v/total:.0%}" for k, v in top))

# 3) sell intensity by day
print("\n=== sell ops by day ===")
for day in range(0, 30, 3):
    ds = [r for r in rows if r["day"] == day]
    sells = sum(1 for r in ds if "SELL" in (r["market_ops"] or ""))
    print(f"  d{day}: steps_with_sell={sells}/{len(ds)}")

# 4) state → hire pattern (hour 0)
print("\n=== hire at hour0 vs money/hands ===")
for r in h0:
    if r["seed"] != 1:
        continue
    if r["day"] <= 12:
        print(f"  d{r['day']:02d} money={r['money']:.0f} hands={r['hands']} "
              f"ani={r['animals']} mel={r['melon']} ops={r['market_ops'][:80]}")
