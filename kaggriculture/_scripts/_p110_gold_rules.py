# -*- coding: utf-8 -*-
"""P110: extract gold crop layout + per-day market/physical rules table."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")
GOLD = "吃白饭的大肥鱼"

meta = json.loads((OUT / "gold_meta.json").read_text(encoding="utf-8"))
idx = {}
for row in meta:
    for a in row.get("agents") or []:
        if a.get("teamName") == GOLD:
            idx[row["episode_id"]] = int(a.get("index") or 0)

files = sorted((OUT / "gold").glob("episode-*-replay.json"))[:5]

# per-day: market ops counter, farmer op counter, tile crop mix
day_mkt = defaultdict(Counter)
day_farm = defaultdict(Counter)
day_crops = defaultdict(Counter)
day_structs = defaultdict(Counter)
open_hour_mkt = defaultdict(Counter)  # hour -> ops in first 10 days

for p in files:
    eid = int(p.name.split("-")[1])
    ai = idx.get(eid, 0)
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    for si, st in enumerate(data.get("steps") or []):
        ag = st[ai]
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        day = si // 24
        hour = si % 24
        me = obs.get("player") if obs.get("player") is not None else ai
        farm = (obs.get("farms") or [])[me] if me < len(obs.get("farms") or []) else {}
        for o in act.get("market") or []:
            if not isinstance(o, (list, tuple)) or not o:
                continue
            op = o[0]
            key = op if len(o) < 2 else f"{op}:{o[1]}"
            day_mkt[day][key] += 1
            if day < 10:
                open_hour_mkt[hour][key] += 1
        f = act.get("farmer") or []
        if isinstance(f, list) and f:
            day_farm[day][str(f[0])] += 1
        if si % 24 == 12:  # mid-day snapshot
            for row in farm.get("tiles") or []:
                if not isinstance(row, list):
                    continue
                for cell in row:
                    if not isinstance(cell, dict):
                        continue
                    if cell.get("kind") == "PLANT" and cell.get("crop"):
                        day_crops[day][cell.get("crop")] += 1
                    elif cell.get("kind") in ("PASTURE", "COOP"):
                        day_structs[day][cell.get("kind")] += 1

print("=== MARKET by day (top) ===", flush=True)
for d in sorted(day_mkt):
    print(f"  d{d}: {day_mkt[d].most_common(10)}", flush=True)

print("\n=== FARMER by day ===", flush=True)
for d in sorted(day_farm):
    print(f"  d{d}: {day_farm[d].most_common(8)}", flush=True)

print("\n=== CROPS mid-day ===", flush=True)
for d in sorted(day_crops):
    print(f"  d{d}: {dict(day_crops[d])} structs={dict(day_structs[d])}", flush=True)

print("\n=== hour->mkt day0-9 ===", flush=True)
for h in range(24):
    print(f"  h{h:02d}: {open_hour_mkt[h].most_common(8)}", flush=True)

# sell items over game
sell_by_item = Counter()
for d, ctr in day_mkt.items():
    for k, v in ctr.items():
        if k.startswith("SELL"):
            sell_by_item[k] += v
print("\n=== SELL totals ===", dict(sell_by_item), flush=True)

(RESEARCH / "p110_gold_rules.json").write_text(json.dumps({
    "day_mkt": {str(d): dict(c) for d, c in day_mkt.items()},
    "day_farm": {str(d): dict(c) for d, c in day_farm.items()},
    "day_crops": {str(d): dict(c) for d, c in day_crops.items()},
    "open_hour_mkt": {str(h): dict(c) for h, c in open_hour_mkt.items()},
}, indent=2, ensure_ascii=False), encoding="utf-8")
print("WROTE p110_gold_rules.json", flush=True)
