# -*- coding: utf-8 -*-
"""P42: isolate day-1 divergence cause — seat, shops, wheat qty, opponent."""
from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p42_replays")


def load():
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    rows = []
    for m in meta:
        d = json.loads(Path(m["path"]).read_text(encoding="utf-8"))
        seat = int(m.get("our_seat") or 0)
        steps = d["steps"]
        actions = [step[seat].get("action") or {} for step in steps]
        # shops at dawn days 0-3
        shops = {}
        for day in range(4):
            obs = steps[day * 24][seat].get("observation") or {}
            shops[day] = tuple((obs.get("town") or {}).get("unlocked_shops") or [])
        # first 48 market keys
        rows.append({
            "ep": m["episode_id"], "opp": m["opp_team"], "seat": seat,
            "reward": m["our_reward"], "actions": actions, "shops": shops,
            "seed": (d.get("info") or {}).get("seed"),
        })
    return rows


def mkt(a):
    return json.dumps(a.get("market"), sort_keys=True, default=str)


def wkr(a):
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def main():
    rows = load()
    print(f"n={len(rows)}")

    # day-1 = steps 24-47. first diverge within day1
    print("\n=== What differs on day1 (steps 24-47)? ===")
    diff_kinds = Counter()
    examples = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            A, B = rows[i], rows[j]
            for t in range(24, 48):
                if mkt(A["actions"][t]) != mkt(B["actions"][t]):
                    ma = A["actions"][t].get("market") or []
                    mb = B["actions"][t].get("market") or []
                    def sig(ms):
                        return tuple((o[0], o[1] if len(o)>1 else None, o[2] if len(o)>2 else None) for o in ms if o)
                    sa, sb = sig(ma), sig(mb)
                    # classify
                    items_a = {o[1] for o in ma if o and o[0]=="SELL"}
                    items_b = {o[1] for o in mb if o and o[0]=="SELL"}
                    if sa != sb:
                        if "HIRE" in str(sa) or "HIRE" in str(sb):
                            # hire count
                            ha = sum(1 for o in ma if o and o[0]=="HIRE")
                            hb = sum(1 for o in mb if o and o[0]=="HIRE")
                            if ha != hb:
                                diff_kinds["HIRE_COUNT"] += 1
                            else:
                                diff_kinds["MARKET_OTHER"] += 1
                        elif items_a != items_b:
                            diff_kinds["SELL_ITEMS"] += 1
                        else:
                            # same items different qty?
                            qa = {(o[1], o[2]) for o in ma if o and o[0]=="SELL"}
                            qb = {(o[1], o[2]) for o in mb if o and o[0]=="SELL"}
                            if qa != qb:
                                diff_kinds["SELL_QTY"] += 1
                                if len(examples) < 8:
                                    examples.append((A["ep"], B["ep"], t, sa, sb, A["seat"], B["seat"]))
                            else:
                                diff_kinds["ORDER_OR_OTHER"] += 1
                    break
                if wkr(A["actions"][t]) != wkr(B["actions"][t]):
                    diff_kinds["WORKER_ONLY"] += 1
                    break
    print(diff_kinds)
    for e in examples[:6]:
        print("  ex", e[0], e[1], "t", e[2], "seats", e[5], e[6])
        print("    A", e[3][:6])
        print("    B", e[4][:6])

    # seat effect: compare same-seat pairs vs cross-seat pairs first_div in day1
    print("\n=== Seat effect on early divergence ===")
    def first_div_in(A, B, lo, hi):
        for t in range(lo, hi):
            if mkt(A["actions"][t]) != mkt(B["actions"][t]) or wkr(A["actions"][t]) != wkr(B["actions"][t]):
                return t
        return None
    same_seat_d1 = 0
    same_seat_n = 0
    cross_d1 = 0
    cross_n = 0
    for i in range(len(rows)):
        for j in range(i+1, len(rows)):
            fd = first_div_in(rows[i], rows[j], 24, 48)
            if rows[i]["seat"] == rows[j]["seat"]:
                same_seat_n += 1
                if fd is not None:
                    same_seat_d1 += 1
            else:
                cross_n += 1
                if fd is not None:
                    cross_d1 += 1
    print(f"  same-seat pairs day1-div: {same_seat_d1}/{same_seat_n}")
    print(f"  cross-seat pairs day1-div: {cross_d1}/{cross_n}")

    # among same seat + same shops d0-d2, day1 div?
    print("\n=== same seat + same early shops ===")
    ok = 0
    div = 0
    for i in range(len(rows)):
        for j in range(i+1, len(rows)):
            if rows[i]["seat"] != rows[j]["seat"]:
                continue
            if rows[i]["shops"] != rows[j]["shops"]:
                continue
            ok += 1
            if first_div_in(rows[i], rows[j], 24, 48) is not None:
                div += 1
    print(f"  matched pairs={ok} day1_div={div}")

    # hire counts at step 24 (dawn day1) distribution
    print("\n=== HIRE count at step 24 ===")
    hires = []
    for r in rows:
        mk = r["actions"][24].get("market") or []
        n = sum(1 for o in mk if o and o[0]=="HIRE")
        hires.append(n)
    print(Counter(hires))

    # wheat sell qty at step 1
    print("\n=== WHEAT sell qty at step 1 ===")
    wq = []
    for r in rows:
        mk = r["actions"][1].get("market") or []
        q = sum(int(o[2]) for o in mk if o and o[0]=="SELL" and o[1]=="WHEAT")
        wq.append(q)
    print(Counter(wq))


if __name__ == "__main__":
    main()
