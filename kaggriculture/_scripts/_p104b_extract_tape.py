# -*- coding: utf-8 -*-
"""P104b: extract exact gold action tape (first 72 steps) as a Python prefix policy."""
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

# take the clean win
p = OUT / "gold" / "episode-111924042-replay.json"
eid = int(p.name.split("-")[1])
ai = idx[eid]
data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
steps = data["steps"]

tape = []
for si in range(72):
    ag = steps[si][ai]
    act = ag.get("action") or {}
    tape.append({
        "step": si,
        "farmer": act.get("farmer") or ["PASS"],
        "hands": act.get("hands") or [],
        "market": act.get("market") or [],
    })

# verify tape matches a second game's first 24 steps (opening is deterministic)
p2 = OUT / "gold" / "episode-111920350-replay.json"
ai2 = idx[int(p2.name.split("-")[1])]
data2 = json.loads(p2.read_text(encoding="utf-8", errors="replace"))
same = 0
for si in range(24):
    a1 = steps[si][ai].get("action") or {}
    a2 = data2["steps"][si][ai2].get("action") or {}
    if (a1.get("farmer") == a2.get("farmer") and a1.get("market") == a2.get("market")):
        same += 1
print(f"day0 farmer+market identical across games: {same}/24")

# write as python literal
out_py = RESEARCH / "p104_gold_tape.json"
out_py.write_text(json.dumps({"source": p.name, "ai": ai, "tape": tape}, indent=2, ensure_ascii=False), encoding="utf-8")
print("tape steps", len(tape), "wrote", out_py)
print("s0", tape[0])
print("s1", tape[1])
print("s2", tape[2])
print("s6", tape[6])
print("s28", tape[28] if len(tape) > 28 else None)
