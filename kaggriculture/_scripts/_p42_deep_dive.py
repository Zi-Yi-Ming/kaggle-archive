# -*- coding: utf-8 -*-
"""P42 deep dive: later sells, qty, shop-day divergence."""
from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "p42_replays"


def load():
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    rows = []
    for m in meta:
        d = json.loads(Path(m["path"]).read_text(encoding="utf-8"))
        seat = int(m.get("our_seat") or 0)
        steps = d.get("steps") or []
        actions = []
        shops_at = {}
        for i, step in enumerate(steps):
            a = step[seat].get("action") or {}
            actions.append(a)
            if i % 24 == 0:  # dawn
                obs = step[seat].get("observation") or {}
                shops_at[i // 24] = tuple((obs.get("town") or {}).get("unlocked_shops") or [])
        sells = []  # (step, item, qty)
        for i, a in enumerate(actions):
            for o in a.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    sells.append((i, o[1], int(o[2])))
        rows.append({
            "ep": m["episode_id"], "opp": m["opp_team"], "seat": seat,
            "reward": m.get("our_reward"), "actions": actions, "sells": sells,
            "shops_at": shops_at,
        })
    return rows


def main():
    rows = load()
    print(f"n={len(rows)}")

    # 1) per-item ALL sell steps distribution
    print("\n=== ALL SELL EVENTS: step stdev by item ===")
    by_item = defaultdict(list)
    for r in rows:
        for st, item, q in r["sells"]:
            by_item[item].append(st)
    for item, ts in sorted(by_item.items(), key=lambda x: -len(x[1])):
        print(f"  {item:12s} n_events={len(ts):4d} unique_steps={len(set(ts)):4d} "
              f"stdev={statistics.pstdev(ts):.2f} range={min(ts)}-{max(ts)}")

    # 2) sell qty at fixed steps: for each item, qty at its first-sell step across eps
    print("\n=== QTY at first-sell step (is quantity adaptive?) ===")
    for item in ("WHEAT", "FERTILIZER", "WOOL", "MILK", "MELON", "EGG", "STRAWBERRY"):
        qs = []
        for r in rows:
            ev = [q for st, it, q in r["sells"] if it == item]
            qs.append(sum(ev) if ev else 0)
        print(f"  {item:12s} total_qty mean={statistics.mean(qs):.1f} "
              f"stdev={statistics.pstdev(qs):.1f} range={min(qs)}-{max(qs)} unique={len(set(qs))}")

    # 3) first divergence day histogram + is it shop-unlock day?
    print("\n=== First divergence vs shop-unlock days (unlock every 3d) ===")
    def fdiv(a, b):
        for i in range(min(len(a), len(b))):
            if json.dumps(a[i], sort_keys=True, default=str) != json.dumps(b[i], sort_keys=True, default=str):
                return i
        return None

    shop_days = set()
    for r in rows[:5]:
        shop_days |= set(r["shops_at"].keys())
    # actually shops grow over time; unlock days are 3,6,9,...
    unlock_days = {d for d in range(30) if d > 0 and d % 3 == 0}

    fd_days = []
    fd_on_shop = 0
    n_pairs = 0
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            fd = fdiv(rows[i]["actions"], rows[j]["actions"])
            if fd is None:
                continue
            n_pairs += 1
            day = fd // 24
            fd_days.append(day)
            if day in unlock_days or day == 0:
                fd_on_shop += 1
    print(f"  pairs={n_pairs} first_div on shop-unlock day or d0: {fd_on_shop} ({100*fd_on_shop/max(1,n_pairs):.0f}%)")
    print(f"  first_div day histogram: {Counter(fd_days).most_common(10)}")

    # 4) same-opponent pairs detail
    print("\n=== SAME-OPPONENT pairs (seed noise?) ===")
    by_opp = defaultdict(list)
    for r in rows:
        by_opp[r["opp"]].append(r)
    for opp, group in by_opp.items():
        if len(group) < 2:
            continue
        A, B = group[0], group[1]
        fd = fdiv(A["actions"], B["actions"])
        print(f"  {opp}: ep {A['ep']} vs {B['ep']} first_div={fd} day={(fd//24) if fd is not None else None} "
              f"rewards={A['reward']}/{B['reward']}")

    # 5) market-only first divergence
    print("\n=== Market vs Worker first divergence ===")
    def mkey(a):
        return json.dumps(a.get("market"), sort_keys=True, default=str)
    def wkey(a):
        return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)
    mw = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            A, B = rows[i]["actions"], rows[j]["actions"]
            fdm = fdw = None
            for t in range(min(len(A), len(B))):
                if fdm is None and mkey(A[t]) != mkey(B[t]):
                    fdm = t
                if fdw is None and wkey(A[t]) != wkey(B[t]):
                    fdw = t
                if fdm is not None and fdw is not None:
                    break
            if fdm is not None:
                mw.append((fdm, fdw if fdw is not None else 720))
    if mw:
        print(f"  market_first_div median={statistics.median([x[0] for x in mw]):.0f}")
        print(f"  worker_first_div median={statistics.median([x[1] for x in mw]):.0f}")
        both = sum(1 for m, w in mw if abs(m - w) <= 2)
        print(f"  market&worker diverge within 2 steps: {both}/{len(mw)}")

    # 6) Does later sell qty of MILK depend on opp animals/cash? sample
    print("\n=== MILK total qty vs our reward / opp reward ===")
    milk = []
    for r in rows:
        q = sum(q for st, it, q in r["sells"] if it == "MILK")
        milk.append((q, r["reward"], r["opp"]))
    milk.sort(reverse=True)
    print("  top5 milk qty:", milk[:5])
    print("  bot5 milk qty:", milk[-5:])
    qs = [m[0] for m in milk]
    print(f"  milk qty stdev={statistics.pstdev(qs):.2f} (adaptive if large)")


if __name__ == "__main__":
    main()
