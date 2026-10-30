# -*- coding: utf-8 -*-
"""P140: autopsy H3x worst live losses — what do winners do?"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p139_h3x_live")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")

meta = json.loads((OUT / "meta.json").read_text(encoding="utf-8"))
losses = sorted([r for r in meta if not r["win"]], key=lambda r: r["gap"])
print("LOSSES:", flush=True)
for r in losses:
    print(f"  {r['gap']:.0f} vs {r['opp']} eid={r['eid']}", flush=True)


def profile(path, ai):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    sells = 0
    sell_day = Counter()
    hires = 0
    money_path = []
    for si, st in enumerate(steps):
        if not isinstance(st, list) or ai >= len(st):
            continue
        ag = st[ai]
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        for o in act.get("market") or []:
            if isinstance(o, (list, tuple)) and o and o[0] == "SELL":
                sells += 1
                sell_day[si // 24] += 1
            elif isinstance(o, (list, tuple)) and o and o[0] == "HIRE":
                hires += 1
        farms = obs.get("farms") or []
        me = obs.get("player") if obs.get("player") is not None else ai
        if 0 <= me < len(farms) and isinstance(farms[me], dict):
            money_path.append(float(farms[me].get("money") or 0))
    return {
        "sells": sells, "hires": hires,
        "sell_day": dict(sorted(sell_day.items())),
        "money_d0": money_path[0] if money_path else None,
        "money_d5": money_path[120] if len(money_path) > 120 else None,
        "money_d10": money_path[240] if len(money_path) > 240 else None,
        "money_d15": money_path[360] if len(money_path) > 360 else None,
        "money_end": money_path[-1] if money_path else None,
    }


print("\n=== LOSS GAME PROFILES ===", flush=True)
for r in losses[:4]:
    eid = r["eid"]
    f = list(OUT.glob(f"episode-{eid}-replay.json"))
    if not f:
        print("no file", eid, flush=True)
        continue
    data = json.loads(f[0].read_text(encoding="utf-8", errors="replace"))
    scores = data.get("rewards") or []
    # find indices
    print(f"\n-- {r['opp']} gap={r['gap']:.0f} rewards={scores} --", flush=True)
    for ai in (0, 1):
        p = profile(f[0], ai)
        label = "US" if scores[ai] == r["our"] else "THEM"
        print(f"  {label} ai{ai}: sells={p['sells']} hires={p['hires']} "
              f"m_d5={p['money_d5']} m_d10={p['money_d10']} m_d15={p['money_d15']} end={p['money_end']}", flush=True)
        print(f"       sell_day={p['sell_day']}", flush=True)

(RESEARCH / "p140_h3x_loss_autopsy.json").write_text(json.dumps(losses, indent=2, ensure_ascii=False), encoding="utf-8")
print("WROTE", flush=True)
