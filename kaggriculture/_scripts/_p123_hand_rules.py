# -*- coding: utf-8 -*-
"""P123: learn hand action from LOCAL FEATURES (pos, tile, hour) not (hour,n)."""
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


def tile_char(cell):
    if cell is None:
        return "emp"
    if cell == "LOCKED":
        return "lock"
    if not isinstance(cell, dict):
        return "?"
    k = cell.get("kind") or "?"
    if k == "PLANT":
        return "pl_" + (cell.get("crop") or "?")
    return str(k).lower()


def hand_feat(hpos, tiles, hour, day, fert):
    x, y = int(hpos[0]), int(hpos[1])
    t = "oob"
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        t = tile_char(tiles[y][x])
    dx, dy = x - 3, y - 3
    return f"t={t}|dx={dx}|dy={dy}|h={hour}|d={day // 5}|fert={1 if fert else 0}"


def op_key(a):
    if not a:
        return "PASS"
    if len(a) >= 2:
        return f"{a[0]}:{a[1]}"
    return str(a[0])


feat_ops = defaultdict(Counter)

for p in sorted((OUT / "gold").glob("episode-*-replay.json"))[:6]:
    eid = int(p.name.split("-")[1])
    ai = idx.get(eid, 0)
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    for si, st in enumerate(data.get("steps") or []):
        ag = st[ai]
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        me = obs.get("player") if obs.get("player") is not None else ai
        farm = (obs.get("farms") or [])[me] if me < len(obs.get("farms") or []) else {}
        hands = farm.get("hands") or []
        hacts = act.get("hands") or []
        tiles = farm.get("tiles") or []
        shed = (obs.get("private") or {}).get("shed") or {}
        fert = int(shed.get("FERTILIZER") or 0)
        hour, day = si % 24, si // 24
        for i, h in enumerate(hands):
            if i >= len(hacts):
                continue
            hp = h.get("pos") if isinstance(h, dict) and "pos" in h else h
            if not (isinstance(hp, list) and len(hp) == 2):
                continue
            feat = hand_feat(hp, tiles, hour, day, fert)
            feat_ops[feat][op_key(hacts[i])] += 1

print(f"unique feats: {len(feat_ops)}", flush=True)
rules = []
for feat, ctr in feat_ops.items():
    op, n = ctr.most_common(1)[0]
    total = sum(ctr.values())
    rules.append((total, n / total, feat, op, dict(ctr.most_common(3))))
rules.sort(reverse=True)
print("=== top 30 rules ===", flush=True)
for total, pur, feat, op, dist in rules[:30]:
    print(f"  n={total:4d} p={pur:.2f} {feat} -> {op} {dist}", flush=True)

lookup = {feat: ctr.most_common(1)[0][0] for feat, ctr in feat_ops.items()}
(RESEARCH / "p123_hand_rules.json").write_text(json.dumps({
    "n_feats": len(lookup),
    "top_rules": [{"n": t, "purity": p, "feat": f, "op": o} for t, p, f, o, _ in rules[:200]],
    "lookup": lookup,
}, indent=2, ensure_ascii=False), encoding="utf-8")
print("WROTE lookup", len(lookup), flush=True)
