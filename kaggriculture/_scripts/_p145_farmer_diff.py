# -*- coding: utf-8 -*-
"""P145: farmer-ops diff in mirror losses — physical actions winners do more of."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p139_h3x_live")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")

meta = json.loads((OUT / "meta.json").read_text(encoding="utf-8"))
losses = sorted([r for r in meta if not r["win"]], key=lambda r: r["gap"])


def farmer_ops(path, ai):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    ops = Counter()
    late = Counter()
    hand_ops = Counter()
    for si, st in enumerate(steps):
        if not isinstance(st, list) or ai >= len(st):
            continue
        act = st[ai].get("action") or {}
        f = act.get("farmer") or []
        if isinstance(f, list) and f:
            ops[str(f[0])] += 1
            if si // 24 >= 15:
                late[str(f[0])] += 1
        for h in act.get("hands") or []:
            if isinstance(h, list) and h:
                hand_ops[str(h[0])] += 1
    return ops, late, hand_ops


print("=== FARMER OPS DIFF ===", flush=True)
for r in losses[:4]:
    f = list(OUT.glob(f"episode-{r['eid']}-replay.json"))
    if not f:
        continue
    data = json.loads(f[0].read_text(encoding="utf-8", errors="replace"))
    scores = data.get("rewards") or []
    us = 0 if scores[0] == r["our"] else 1
    them = 1 - us
    uo, ul, uh = farmer_ops(f[0], us)
    to, tl, th = farmer_ops(f[0], them)
    print(f"\n-- {r['opp']} gap={r['gap']:.0f} --", flush=True)
    print(f"  US  farmer={dict(uo.most_common(10))}", flush=True)
    print(f"  THEM farmer={dict(to.most_common(10))}", flush=True)
    # diff of interest
    for k in set(uo) | set(to):
        if uo.get(k, 0) != to.get(k, 0) and abs(uo.get(k, 0) - to.get(k, 0)) >= 3:
            print(f"    DIFF {k}: US={uo.get(k,0)} THEM={to.get(k,0)}", flush=True)
    print(f"  US  hands={dict(uh.most_common(8))}", flush=True)
    print(f"  THEM hands={dict(th.most_common(8))}", flush=True)

(RESEARCH / "p145_farmer_diff.json").write_text("see stdout", encoding="utf-8")
print("WROTE", flush=True)
