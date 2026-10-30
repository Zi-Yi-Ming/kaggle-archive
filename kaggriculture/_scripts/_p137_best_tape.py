# -*- coding: utf-8 -*-
"""P137: extract gold BEST game tape + compare opening to ours."""
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
            idx[row["episode_id"]] = (int(a.get("index") or 0), a.get("reward"))

best = None
for p in sorted((OUT / "gold").glob("episode-*-replay.json")):
    eid = int(p.name.split("-")[1])
    if eid not in idx:
        continue
    ai, reward = idx[eid]
    if best is None or (reward or 0) > (best[1] or 0):
        best = (p, reward, ai, eid)

print("BEST gold game:", best[0].name, "reward", best[1], flush=True)
data = json.loads(best[0].read_text(encoding="utf-8"))
ai = best[2]
tape = []
for st in data.get("steps") or []:
    act = st[ai].get("action") or {}
    tape.append({"f": act.get("farmer") or ["PASS"], "h": act.get("hands") or [], "m": act.get("market") or []})

(RESEARCH / "p137_best_tape.json").write_text(json.dumps({
    "source": best[0].name, "eid": best[3], "reward": best[1], "tape": tape,
}, ensure_ascii=False), encoding="utf-8")
print("steps", len(tape), "wrote p137_best_tape.json", flush=True)
for i in range(5):
    print(f"  s{i} m={tape[i]['m'][:4]}", flush=True)
