# -*- coding: utf-8 -*-
"""Mid-game (d15-21) actual sell execution vs order for R2 loss games.

We cannot see executed qty directly; we approximate:
- order qty * quoted price = intended revenue
- shed inventory drop between turns = realized outflow (incl. town drain)
Focus: per-item order volume and avg price in d15-21 for me vs opp.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\replays")
GAMES = [
    "episode-108057090-replay.json",  # LOSS Muhammad -4186
    "episode-108051854-replay.json",  # LOSS matcha -4988
    "episode-108028228-replay.json",  # LOSS Audric -1461
    "episode-108031887-replay.json",  # LOSS Khalid -2128
    "episode-108046944-replay.json",  # WIN yuuuki +19120
    "episode-108035090-replay.json",  # WIN Lucas +2762
]


def analyze(name: str):
    data = json.loads((REP / name).read_text(encoding="utf-8"))
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [0, 0]
    steps = data.get("steps") or []
    me = teams.index("ZiYiMing")
    opp = 1 - me
    my_r, opp_r = float(rewards[me]), float(rewards[opp])
    print("=" * 72)
    print(f"{'WIN' if my_r>opp_r else 'LOSS'} {name} vs {teams[opp]} {my_r:.0f} vs {opp_r:.0f} m={my_r-opp_r:+.0f}")

    # per-player per-day sell order qty and value for d15-21
    qty = [defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))]
    val = [defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(float))]
    # money at day start
    money = {0: {}, 1: {}}

    for idx, snap in enumerate(steps):
        for p in (0, 1):
            if p >= len(snap):
                continue
            rec = snap[p] or {}
            obs = rec.get("observation") or {}
            action = rec.get("action") or {}
            if not isinstance(obs, dict):
                continue
            step = obs.get("step")
            step = int(step) if step is not None else idx
            day = step // 24
            if not (15 <= day <= 21):
                continue
            prices = ((obs.get("market") or {}).get("prices") or {})
            farms = obs.get("farms") or []
            if step % 24 == 0 and p == 0 and len(farms) >= 2:
                try:
                    m0 = float(farms[0].get("money") or 0)
                    m1 = float(farms[1].get("money") or 0)
                    money[0][day] = m0 if me == 0 else m1
                    money[1][day] = m1 if me == 0 else m0
                except Exception:
                    pass
            # map p to me/opp bucket
            bucket = 0 if p == me else 1
            # only count the player's own action when obs.player matches
            if int(obs.get("player") or p) != p:
                continue
            for o in action.get("market") or []:
                if not o or o[0] != "SELL" or len(o) < 3:
                    continue
                item, q = o[1], int(o[2] or 0)
                if q <= 0:
                    continue
                price = int(prices.get(item) or 1)
                qty[bucket][day][item] += q
                val[bucket][day][item] += q * price

    print("  day | my$     opp$    diff   | my_top_sells")
    for day in range(15, 22):
        my_m = money[0].get(day, 0)
        op_m = money[1].get(day, 0)
        top = sorted(val[0][day].items(), key=lambda kv: -kv[1])[:4]
        top_s = " ".join(f"{k}:{qty[0][day][k]}@{val[0][day][k]/max(1,qty[0][day][k]):.0f}" for k, _ in top)
        print(f"  d{day:02d}  | {my_m:7.0f} {op_m:7.0f} {my_m-op_m:+7.0f} | {top_s}")

    # compare total milk/wool/straw value me vs opp in window
    for item in ("MILK", "WOOL", "STRAWBERRY", "EGG", "WHEAT"):
        my_q = sum(qty[0][d][item] for d in range(15, 22))
        op_q = sum(qty[1][d][item] for d in range(15, 22))
        my_v = sum(val[0][d][item] for d in range(15, 22))
        op_v = sum(val[1][d][item] for d in range(15, 22))
        print(f"  {item:10s} d15-21 my_qty={my_q:5d} opp_qty={op_q:5d}  my_val={my_v:8.0f} opp_val={op_v:8.0f} dval={my_v-op_v:+8.0f}")


def main():
    for name in GAMES:
        p = REP / name
        if p.exists():
            try:
                analyze(name)
            except Exception as e:
                import traceback
                print("FAIL", name, e)
                traceback.print_exc()


if __name__ == "__main__":
    main()
