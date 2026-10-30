# -*- coding: utf-8 -*-
"""P104: dump gold first-120 exact actions + tile plans for clone."""
from __future__ import annotations

import json
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

# use one clean win and one other
files = [
    OUT / "gold" / "episode-111924042-replay.json",  # gold won 104032
    OUT / "gold" / "episode-111920350-replay.json",
]

for p in files:
    eid = int(p.name.split("-")[1])
    ai = idx.get(eid, 0)
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    print("========", p.name, "ai", ai, "rewards", data.get("rewards"), flush=True)
    for si in range(0, 96):
        st = steps[si]
        ag = st[ai]
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        # compact
        mkt = act.get("market") or []
        farmer = act.get("farmer") or []
        hands = act.get("hands") or []
        me = obs.get("player") if obs.get("player") is not None else ai
        farm = (obs.get("farms") or [])[me] if me < len(obs.get("farms") or []) else {}
        money = farm.get("money") if isinstance(farm, dict) else None
        hands_n = len(hands) if isinstance(hands, list) else 0
        hands_a = [h[0] if isinstance(h, list) and h else h for h in (hands or [])[:6]]
        print(f"s{si:03d} d{si//24} h{si%24:02d} $={money} f={farmer} hands({hands_n})={hands_a} m={mkt}", flush=True)

    # tile snapshot day0 end, day6, day10
    for si in (0, 23, 150, 240, 400):
        if si >= len(steps):
            continue
        ag = steps[si][ai]
        obs = ag.get("observation") or {}
        me = obs.get("player") if obs.get("player") is not None else ai
        farm = (obs.get("farms") or [])[me]
        tiles = farm.get("tiles") or []
        kinds = {}
        crops = {}
        structures = []
        for y, row in enumerate(tiles):
            for x, cell in enumerate(row):
                if not isinstance(cell, dict):
                    continue
                k = cell.get("kind")
                kinds[k] = kinds.get(k, 0) + 1
                if cell.get("crop"):
                    crops[cell.get("crop")] = crops.get(cell.get("crop"), 0) + 1
                if k in ("PASTURE", "COOP", "SHED"):
                    structures.append((x, y, k))
        print(f"  TILE s{si}: kinds={kinds} crops={crops} farm_pos={farm.get('farmer')} hands={len(farm.get('hands') or [])}", flush=True)
