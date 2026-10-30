# -*- coding: utf-8 -*-
"""P141: item-level sell diff in mirror-match losses — what do winners sell?"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p139_h3x_live")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")

meta = json.loads((OUT / "meta.json").read_text(encoding="utf-8"))
losses = sorted([r for r in meta if not r["win"]], key=lambda r: r["gap"])


def sell_items(path, ai):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    by_item = Counter()
    qty = Counter()
    late_qty = Counter()  # day 15+
    for si, st in enumerate(steps):
        if not isinstance(st, list) or ai >= len(st):
            continue
        for o in (st[ai].get("action") or {}).get("market") or []:
            if isinstance(o, (list, tuple)) and o and o[0] == "SELL" and len(o) >= 3:
                item, q = o[1], int(o[2] or 0)
                by_item[item] += 1
                qty[item] += q
                if si // 24 >= 15:
                    late_qty[item] += q
    return by_item, qty, late_qty


print("=== ITEM DIFF in losses ===", flush=True)
for r in losses[:4]:
    f = list(OUT.glob(f"episode-{r['eid']}-replay.json"))
    if not f:
        continue
    data = json.loads(f[0].read_text(encoding="utf-8", errors="replace"))
    scores = data.get("rewards") or []
    us_ai = 0 if scores[0] == r["our"] else 1
    them_ai = 1 - us_ai
    _, uq, ul = sell_items(f[0], us_ai)
    _, tq, tl = sell_items(f[0], them_ai)
    print(f"\n-- {r['opp']} gap={r['gap']:.0f} --", flush=True)
    print(f"  US  total={dict(uq)}", flush=True)
    print(f"  THEM total={dict(tq)}", flush=True)
    print(f"  US  late={dict(ul)}", flush=True)
    print(f"  THEM late={dict(tl)}", flush=True)
    # value proxy: late qty * rough price
    px = {"WHEAT": 30, "CARROT": 40, "TOMATO": 70, "STRAWBERRY": 150, "MELON": 200,
          "EGG": 55, "MILK": 170, "WOOL": 210, "FERTILIZER": 70}
    uv = sum(ul.get(k, 0) * px.get(k, 50) for k in set(ul) | set(px))
    tv = sum(tl.get(k, 0) * px.get(k, 50) for k in set(tl) | set(px))
    print(f"  late value proxy US={uv} THEM={tv} diff={tv-uv}", flush=True)

(RESEARCH / "p141_item_diff.json").write_text(json.dumps({"note": "see stdout"}, indent=2), encoding="utf-8")
print("WROTE", flush=True)
