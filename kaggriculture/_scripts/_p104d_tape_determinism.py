# -*- coding: utf-8 -*-
"""P104d: how deterministic is gold's FULL 720-step tape across games?"""
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

files = sorted((OUT / "gold").glob("episode-*-replay.json"))[:5]
tapes = []
for p in files:
    eid = int(p.name.split("-")[1])
    ai = idx.get(eid, 0)
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    tape = []
    for si, st in enumerate(data.get("steps") or []):
        act = st[ai].get("action") or {}
        tape.append({
            "f": act.get("farmer"),
            "h": act.get("hands"),
            "m": act.get("market"),
        })
    tapes.append((p.name, tape))
    print("loaded", p.name, "steps", len(tape), flush=True)

# compare tape0 vs others
base_name, base = tapes[0]
print("\nIdentity vs", base_name, flush=True)
for name, tape in tapes[1:]:
    n = min(len(base), len(tape))
    same_f = sum(1 for i in range(n) if base[i]["f"] == tape[i]["f"])
    same_m = sum(1 for i in range(n) if base[i]["m"] == tape[i]["m"])
    same_h = sum(1 for i in range(n) if base[i]["h"] == tape[i]["h"])
    same_all = sum(1 for i in range(n) if base[i] == tape[i])
    print(f"  {name}: farmer {same_f}/{n} market {same_m}/{n} hands {same_h}/{n} ALL {same_all}/{n}", flush=True)
    # where does it diverge
    for i in range(n):
        if base[i] != tape[i]:
            print(f"    first diverge @ {i} d{i//24} h{i%24}", flush=True)
            print(f"      base f={base[i]['f']} m={base[i]['m']}", flush=True)
            print(f"      this f={tape[i]['f']} m={tape[i]['m']}", flush=True)
            break

# dump full base tape
(RESEARCH / "p104_gold_full_tape.json").write_text(
    json.dumps({"source": base_name, "tape": base}, ensure_ascii=False), encoding="utf-8"
)
print("wrote full tape", len(base), flush=True)
