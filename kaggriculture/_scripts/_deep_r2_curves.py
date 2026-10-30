# -*- coding: utf-8 -*-
"""Deep-dive R2 mirror games: money curve, first divergence, sell price quality."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\replays")


def analyze(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [0, 0]
    steps = data.get("steps") or []
    try:
        me = teams.index("ZiYiMing")
    except ValueError:
        return
    opp = 1 - me
    my_r, opp_r = float(rewards[me]), float(rewards[opp])
    win = my_r > opp_r
    flag = "WIN" if win else "LOSS"
    print("=" * 72)
    print(f"{flag} {path.name} seat={me} vs {teams[opp] if opp < len(teams) else '?'} "
          f"{my_r:.0f} vs {opp_r:.0f} m={my_r-opp_r:+.0f}")

    # money curve at each day boundary + first divergence
    curve = []  # (day, my, opp)
    sell_price_sum = [0.0, 0.0]
    sell_qty = [0, 0]
    milk_price_at_sell = [[], []]
    straw_price_at_sell = [[], []]
    wool_price_at_sell = [[], []]

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
            farms = obs.get("farms") or []
            prices = ((obs.get("market") or {}).get("prices") or {})
            if step % 24 == 0 and p == 0 and len(farms) >= 2:
                try:
                    m0 = float(farms[0].get("money") or 0)
                    m1 = float(farms[1].get("money") or 0)
                    # remap to my/opp
                    my_m = m0 if me == 0 else m1
                    opp_m = m1 if me == 0 else m0
                    curve.append((day, my_m, opp_m, my_m - opp_m))
                except Exception:
                    pass
            # sell quality for this player's own action
            if p != me:
                continue
            for o in action.get("market") or []:
                if not o or o[0] != "SELL" or len(o) < 3:
                    continue
                item, qty = o[1], int(o[2] or 0)
                if qty <= 0:
                    continue
                price = int(prices.get(item) or 1)
                sell_qty[0] += qty
                sell_price_sum[0] += qty * price
                if item == "MILK":
                    milk_price_at_sell[0].append((step, qty, price))
                elif item == "STRAWBERRY":
                    straw_price_at_sell[0].append((step, qty, price))
                elif item == "WOOL":
                    wool_price_at_sell[0].append((step, qty, price))

    if curve:
        print("  day  my$      opp$     diff")
        for day, my_m, opp_m, d in curve:
            if day % 3 == 0 or day >= 27:
                mark = " <-- first+" if d > 0 and (len(curve) > 1 and curve[max(0, curve.index((day, my_m, opp_m, d))-1)][3] <= 0) else ""
                print(f"  d{day:02d}  {my_m:8.0f} {opp_m:8.0f} {d:+8.0f}{mark}")
        # first sustained lead
        first_lead = None
        for day, my_m, opp_m, d in curve:
            if d > 500:
                first_lead = day
                break
        print(f"  first_lead_day(>500): {first_lead}")

    def avg_price(lst):
        if not lst:
            return None
        num = sum(q * p for _, q, p in lst)
        den = sum(q for _, q, p in lst)
        return num / den if den else None

    ap_m = avg_price(milk_price_at_sell[0])
    ap_s = avg_price(straw_price_at_sell[0])
    ap_w = avg_price(wool_price_at_sell[0])
    print(f"  avg sell price milk={ap_m} straw={ap_s} wool={ap_w} total_qty={sell_qty[0]}")


def main():
    files = [
        "episode-108046944-replay.json",
        "episode-108044422-replay.json",
        "episode-108043285-replay.json",
        "episode-108042129-replay.json",
        "episode-108028228-replay.json",
        "episode-108031887-replay.json",
        "episode-108036710-replay.json",
        "episode-108037122-replay.json",
        "episode-108025613-replay.json",
        "episode-108035090-replay.json",
    ]
    for name in files:
        p = REP / name
        if p.exists():
            try:
                analyze(p)
            except Exception as e:
                import traceback
                print("FAIL", name, e)
                traceback.print_exc()


if __name__ == "__main__":
    main()
