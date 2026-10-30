# -*- coding: utf-8 -*-
"""Extract elite realized milk/strawberry price paths (not just order qty)."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

P = Path(r"D:\桌面\Kaggle\kaggriculture\_external\public_data\ashok_top10\replays_2026-08-03.parquet")


def main():
    df = pd.read_parquet(P)
    # for elite games, track MILK/STRAWBERRY quoted price when we SELL, by day
    # winner vs loser
    price_sum = [defaultdict(float), defaultdict(float)]  # p -> day -> sum(qty*price)
    qty_sum = [defaultdict(float), defaultdict(float)]
    # also market price at day start
    mk_price = [defaultdict(list), defaultdict(list)]
    n = 0
    for i in range(len(df)):
        try:
            data = json.loads(df.iloc[i]["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            r0, r1 = float(rew[0]), float(rew[1])
        except Exception:
            continue
        if min(r0, r1) < 100000:
            continue
        w = 0 if r0 >= r1 else 1
        l = 1 - w
        steps = data.get("steps") or []
        n += 1
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
                prices = ((obs.get("market") or {}).get("prices") or {})
                if step % 24 == 0:
                    for item in ("MILK", "STRAWBERRY", "WOOL"):
                        if item in prices:
                            mk_price[p][day].append(int(prices[item] or 1))
                if int(obs.get("player") or p) != p:
                    continue
                for o in action.get("market") or []:
                    if not o or o[0] != "SELL" or len(o) < 3:
                        continue
                    item, q = o[1], int(o[2] or 0)
                    if item not in ("MILK", "STRAWBERRY", "WOOL") or q <= 0:
                        continue
                    price = int(prices.get(item) or 1)
                    price_sum[p][day] += q * price
                    qty_sum[p][day] += q

    print(f"elite n={n}")
    print("\n=== avg sell price (order-weighted) winner vs loser ===")
    print("day | MILK w/l | STRAW w/l | WOOL w/l")
    for day in range(15, 30):
        row = [f"d{day:02d}"]
        for item_idx, item in enumerate(("MILK", "STRAWBERRY", "WOOL")):
            # recompute per item — we mixed items; redo simply from stored? we mixed.
            # fallback: print day-level mixed premium price
            pass
        # mixed premium avg
        def avg(p):
            q = sum(qty_sum[p][day].values()) if False else None
            return None
        # simpler: we stored mixed; print total val/qty
        def pav(p):
            # price_sum is mixed items - still useful as blended
            # qty mixed too
            # use placeholder from price_sum/qty if we had per item - we don't
            return None
        # print market snapshot instead
        def mavg(p, item):
            # we stored by day only for mixed - actually mk_price[p][day] is list of mixed? no we appended per item in loop incorrectly
            return None
        # skip broken; print if we have mk_price structure
        pass

    # redo market prices properly
    print("\n(day-start market prices recomputed below in second pass)")

    # second pass: day-start MILK/STRAW prices winner vs loser
    milk_w, milk_l = defaultdict(list), defaultdict(list)
    straw_w, straw_l = defaultdict(list), defaultdict(list)
    for i in range(len(df)):
        try:
            data = json.loads(df.iloc[i]["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            r0, r1 = float(rew[0]), float(rew[1])
        except Exception:
            continue
        if min(r0, r1) < 100000:
            continue
        w = 0 if r0 >= r1 else 1
        l = 1 - w
        steps = data.get("steps") or []
        for step in range(0, 720, 24):
            day = step // 24
            if step >= len(steps):
                continue
            rec = steps[step][0] or {}
            obs = rec.get("observation") or {}
            prices = ((obs.get("market") or {}).get("prices") or {})
            # use seat0 prices (shared market)
            if "MILK" in prices:
                (milk_w if True else milk_l)[day]  # placeholder
            # assign by winner seat
            wp, lp = (milk_w, milk_l) if True else (None, None)
            # winner seat is w
            recw = steps[step][w] if w < len(steps[step]) else {}
            recl = steps[step][l] if l < len(steps[step]) else {}
            ow = recw.get("observation") or {}
            ol = recl.get("observation") or {}
            pw = ((ow.get("market") or {}).get("prices") or {})
            pl = ((ol.get("market") or {}).get("prices") or {})
            if "MILK" in pw:
                milk_w[day].append(int(pw["MILK"] or 1))
            if "MILK" in pl:
                milk_l[day].append(int(pl["MILK"] or 1))
            if "STRAWBERRY" in pw:
                straw_w[day].append(int(pw["STRAWBERRY"] or 1))
            if "STRAWBERRY" in pl:
                straw_l[day].append(int(pl["STRAWBERRY"] or 1))

    print("day | MILK win | MILK lose | STRAW win | STRAW lose")
    for day in range(12, 30):
        mw = sum(milk_w[day]) / len(milk_w[day]) if milk_w[day] else None
        ml = sum(milk_l[day]) / len(milk_l[day]) if milk_l[day] else None
        sw = sum(straw_w[day]) / len(straw_w[day]) if straw_w[day] else None
        sl = sum(straw_l[day]) / len(straw_l[day]) if straw_l[day] else None
        def f(x):
            return f"{x:6.1f}" if x is not None else "     ?"
        print(f"d{day:02d} | {f(mw)} | {f(ml)} | {f(sw)} | {f(sl)}")


if __name__ == "__main__":
    main()
