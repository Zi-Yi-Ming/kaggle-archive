# -*- coding: utf-8 -*-
"""P146: where does winners' extra fert come from? BUY_PRODUCT FERTILIZER resell?"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p139_h3x_live")
meta = json.loads((OUT / "meta.json").read_text(encoding="utf-8"))
losses = sorted([r for r in meta if not r["win"]], key=lambda r: r["gap"])


def mkt_ops(path, ai):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    c = Counter()
    fert_buy = 0
    fert_sell = 0
    collect = 0
    for si, st in enumerate(steps):
        if not isinstance(st, list) or ai >= len(st):
            continue
        act = st[ai].get("action") or {}
        for o in act.get("market") or []:
            if not isinstance(o, (list, tuple)) or not o:
                continue
            key = o[0] if len(o) < 2 else f"{o[0]}:{o[1]}"
            c[key] += 1
            if o[0] == "SELL" and len(o) >= 3 and o[1] == "FERTILIZER":
                fert_sell += int(o[2] or 0)
            if o[0] in ("BUY_PRODUCT", "BUY_SEED") and len(o) >= 3 and o[1] == "FERTILIZER":
                fert_buy += int(o[2] or 0)
        f = act.get("farmer") or []
        if isinstance(f, list) and f and f[0] == "COLLECT_FERTILIZER":
            collect += 1
        for h in act.get("hands") or []:
            if isinstance(h, list) and h and h[0] == "COLLECT_FERTILIZER":
                collect += 1
    return c, fert_buy, fert_sell, collect


print("=== FERT SOURCE ===", flush=True)
for r in losses[:4]:
    f = list(OUT.glob(f"episode-{r['eid']}-replay.json"))
    if not f:
        continue
    data = json.loads(f[0].read_text(encoding="utf-8", errors="replace"))
    scores = data.get("rewards") or []
    us = 0 if scores[0] == r["our"] else 1
    them = 1 - us
    uc, ub, usl, ucol = mkt_ops(f[0], us)
    tc, tb, tsl, tcol = mkt_ops(f[0], them)
    print(f"\n{r['opp']} gap={r['gap']:.0f}", flush=True)
    print(f"  US  buy_fert={ub} sell_fert={usl} collect={ucol}", flush=True)
    print(f"  THEM buy_fert={tb} sell_fert={tsl} collect={tcol}", flush=True)
    print(f"  US  fert-related ops: { {k:v for k,v in uc.items() if 'FERT' in k or 'fert' in k.lower()} }", flush=True)
    print(f"  THEM fert-related ops: { {k:v for k,v in tc.items() if 'FERT' in k or 'fert' in k.lower()} }", flush=True)
