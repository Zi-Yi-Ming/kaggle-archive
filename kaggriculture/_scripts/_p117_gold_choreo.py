# -*- coding: utf-8 -*-
"""P117: reverse gold multi-unit choreography — positions, task waves, fert post."""
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

# take the clean win
p = OUT / "gold" / "episode-111924042-replay.json"
ai = idx[int(p.name.split("-")[1])]
data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
steps = data["steps"]

print("GOLD UNIT CHOREOGRAPHY", p.name, "ai", ai, flush=True)

# track farmer pos + hand positions + actions every step for first 3 days + a mid day + late
for si in list(range(0, 72)) + [144, 150, 154, 216, 217, 240, 400, 600, 648, 700]:
    if si >= len(steps):
        continue
    ag = steps[si][ai]
    act = ag.get("action") or {}
    obs = ag.get("observation") or {}
    me = obs.get("player") if obs.get("player") is not None else ai
    farm = (obs.get("farms") or [])[me] if me < len(obs.get("farms") or []) else {}
    fpos = farm.get("farmer")
    hands = farm.get("hands") or []
    hpos = [h.get("pos") if isinstance(h, dict) else h for h in hands[:8]]
    fact = act.get("farmer") or []
    hacts = act.get("hands") or []
    mkt = act.get("market") or []
    print(f"s{si:03d} d{si//24} h{si%24:02d} fpos={fpos} fact={fact} nh={len(hands)} hpos={hpos} hacts={hacts[:6]} m={mkt[:4]}", flush=True)

# tile map at key steps: where is fert post / shed / pasture?
for si in (0, 23, 154, 400):
    ag = steps[si][ai]
    obs = ag.get("observation") or {}
    me = obs.get("player") if obs.get("player") is not None else ai
    farm = (obs.get("farms") or [])[me]
    tiles = farm.get("tiles") or []
    print(f"\n=== TILE MAP s{si} farmer={farm.get('farmer')} ===", flush=True)
    for y, row in enumerate(tiles):
        cells = []
        for x, cell in enumerate(row):
            if cell is None:
                cells.append(".")
            elif cell == "LOCKED":
                cells.append("#")
            elif isinstance(cell, dict):
                k = cell.get("kind", "?")
                m = {"SHED": "S", "PASTURE": "P", "COOP": "C", "PLANT": "T"}.get(k, k[:1])
                if k == "PLANT":
                    crop = (cell.get("crop") or "?")[0]
                    cells.append(crop.lower())
                else:
                    cells.append(m)
            else:
                cells.append("?")
        print(f"  y{y}: {''.join(cells)}", flush=True)
    town = obs.get("town") or {}
    print("  town", town, flush=True)
    market = obs.get("market") or {}
    print("  prices", {k: market.get("prices", {}).get(k) for k in ("WHEAT", "FERTILIZER", "MELON", "STRAWBERRY")}, flush=True)

(RESEARCH / "p117_gold_choreo.json").write_text(json.dumps({
    "file": p.name, "ai": ai,
    "note": "see stdout for maps; fert post inferred from COLLECT_FERTILIZER positions",
}, indent=2), encoding="utf-8")
print("WROTE p117", flush=True)
