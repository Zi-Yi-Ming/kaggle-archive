# -*- coding: utf-8 -*-
"""P121: extract hand-count change points -> action map for supervised binder."""
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

# For each (hour, live_n) collect hand action patterns
# and for hand-count change points log what happens
pat = defaultdict(Counter)
changes = []

for p in sorted((OUT / "gold").glob("episode-*-replay.json"))[:6]:
    eid = int(p.name.split("-")[1])
    ai = idx.get(eid, 0)
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    prev_n = None
    for si, st in enumerate(data.get("steps") or []):
        ag = st[ai]
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        me = obs.get("player") if obs.get("player") is not None else ai
        farm = (obs.get("farms") or [])[me] if me < len(obs.get("farms") or []) else {}
        hands = farm.get("hands") or []
        n = len(hands)
        hacts = tuple(tuple(h) if isinstance(h, list) else h for h in (act.get("hands") or []))
        hour = si % 24
        day = si // 24
        pat[(hour, n)][hacts] += 1
        if prev_n is not None and n != prev_n:
            changes.append({
                "step": si, "day": day, "hour": hour,
                "from_n": prev_n, "to_n": n,
                "hacts": [list(h) for h in hacts],
                "mkt": act.get("market") or [],
            })
        prev_n = n

print("=== hand-count changes (first 40) ===", flush=True)
for c in changes[:40]:
    print(f"  s{c['step']} d{c['day']} h{c['hour']} {c['from_n']}->{c['to_n']} hacts={c['hacts'][:6]} m={c['mkt'][:3]}", flush=True)

print("\n=== modal hand pattern by (hour, n) for h=2,4,8,14 ===", flush=True)
for hour in (2, 4, 8, 14, 16):
    for n in range(0, 12):
        ctr = pat.get((hour, n))
        if not ctr:
            continue
        top = ctr.most_common(2)
        print(f"  h{hour} n={n}: {top[0][1]}x {top[0][0][:5]}...", flush=True)

# save binder table: (hour, n) -> modal hands
binder = {}
for (hour, n), ctr in pat.items():
    if not ctr:
        continue
    best = ctr.most_common(1)[0][0]
    binder[f"{hour}_{n}"] = [list(h) for h in best]

(RESEARCH / "p121_hand_binder.json").write_text(json.dumps({
    "n_changes": len(changes),
    "changes_sample": changes[:30],
    "binder": binder,
}, indent=2, ensure_ascii=False), encoding="utf-8")
print("WROTE p121_hand_binder.json binder keys", len(binder), flush=True)
