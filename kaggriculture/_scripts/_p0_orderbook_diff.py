# -*- coding: utf-8 -*-
"""P0: order-book / execution trajectory features for elite vs R2 mirrors.

From ashok elite replays (both banks >= 100k) extract per-player:
- first-list turn per premium product
- n order modifications (same product re-listed)
- sell order qty/price series d15-29
- inventory phase: shed stock at day boundaries for MILK/STRAW/WOOL
- residual inventory at end
- town/shop unlocked counts

Also dump one R2 live replay if present for comparison.

This is descriptive, not a policy yet.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

ASHOK = Path(r"D:\桌面\Kaggle\kaggriculture\_external\public_data\ashok_top10\replays_2026-08-03.parquet")
R2_REPLAYS = Path(r"D:\桌面\Kaggle\kaggriculture\_external\replays")
PREMIUM = ("STRAWBERRY", "MILK", "WOOL", "MELON", "EGG")


def analyze_player(steps, player):
    """steps: list of [rec0, rec1]; player: 0/1. Use that player's own obs/actions."""
    first_list = {}
    n_lists = defaultdict(int)
    sell_events = []  # (step, item, qty, price)
    inv_day = {}  # day -> {item: qty}
    end_inv = {}
    shops_day = {}

    last_listed_step = {}

    for idx, snap in enumerate(steps):
        if player >= len(snap):
            continue
        rec = snap[player] or {}
        obs = rec.get("observation") or {}
        action = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        day = step // 24
        if int(obs.get("player") or player) != player:
            # still allow inventory from public? private only on own obs
            pass
        private = obs.get("private") or {}
        shed = private.get("shed") or {}
        if step % 24 == 0:
            inv_day[day] = {k: int(v or 0) for k, v in shed.items() if k in PREMIUM}
            shops = (obs.get("town") or {}).get("unlocked_shops") or []
            shops_day[day] = len(shops)
        if step >= 718:
            end_inv = {k: int(v or 0) for k, v in shed.items()}
        prices = ((obs.get("market") or {}).get("prices") or {})
        if int(obs.get("player") or player) != player:
            continue
        for o in action.get("market") or []:
            if not o or o[0] != "SELL" or len(o) < 3:
                continue
            item, q = o[1], int(o[2] or 0)
            if q <= 0 or item not in PREMIUM and item not in ("WHEAT", "FERTILIZER", "CARROT"):
                continue
            price = int(prices.get(item) or 1)
            n_lists[item] += 1
            if item not in first_list:
                first_list[item] = step
            if item in PREMIUM:
                sell_events.append((step, item, q, price))
            last_listed_step[item] = step

    return {
        "first_list": first_list,
        "n_lists": dict(n_lists),
        "n_prem_events": len(sell_events),
        "inv_day": inv_day,
        "end_inv": end_inv,
        "shops_day": shops_day,
        "sell_events_sample": sell_events[:20],
        "n_sell_events": len(sell_events),
    }


def main():
    df = pd.read_parquet(ASHOK)
    elite_feats = []
    for i in range(min(80, len(df))):
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
        fw = analyze_player(steps, w)
        fl = analyze_player(steps, l)
        elite_feats.append({"w": fw, "l": fl, "margin": abs(r0 - r1)})

    print(f"elite games analyzed: {len(elite_feats)}")
    if not elite_feats:
        return

    def mean_key(feats, side, key, default=0.0):
        vals = [f[side]["n_lists"].get(key, 0) for f in feats]
        return sum(vals) / len(vals) if vals else default

    print("\n=== mean SELL list-counts per game (winner vs loser) ===")
    for item in ("STRAWBERRY", "MILK", "WOOL", "MELON", "WHEAT", "FERTILIZER"):
        print(f"  {item:12s} win={mean_key(elite_feats,'w',item):6.1f}  lose={mean_key(elite_feats,'l',item):6.1f}")

    print("\n=== mean premium sell-events (qty>0, premium only) ===")
    print("  win", sum(f["w"]["n_prem_events"] for f in elite_feats) / len(elite_feats))
    print("  lose", sum(f["l"]["n_prem_events"] for f in elite_feats) / len(elite_feats))

    print("\n=== first-list step (median) winner ===")
    for item in PREMIUM:
        vals = sorted(f["w"]["first_list"].get(item, 999) for f in elite_feats if item in f["w"]["first_list"])
        if vals:
            print(f"  {item:12s} median_step={vals[len(vals)//2]}  (day {vals[len(vals)//2]//24})")

    print("\n=== day15/20/25/29 shed stock (mean) winner ===")
    for day in (15, 20, 25, 29):
        acc = defaultdict(list)
        for f in elite_feats:
            inv = f["w"]["inv_day"].get(day) or {}
            for item in PREMIUM:
                acc[item].append(inv.get(item, 0))
        line = " ".join(f"{k}={sum(v)/len(v):.1f}" for k, v in acc.items() if v)
        print(f"  d{day}: {line}")

    print("\n=== end residual shed (mean) win vs lose ===")
    for item in PREMIUM + ("WHEAT", "FERTILIZER"):
        ww = [f["w"]["end_inv"].get(item, 0) for f in elite_feats]
        ll = [f["l"]["end_inv"].get(item, 0) for f in elite_feats]
        if ww or ll:
            print(f"  {item:12s} win={sum(ww)/len(ww):.1f} lose={sum(ll)/len(ll):.1f}")

    # sample sell event trajectories for first elite winner
    f0 = elite_feats[0]
    print("\n=== sample winner premium sell events (first 15) ===")
    for ev in f0["w"]["sell_events_sample"][:15]:
        print(" ", ev)

    # if an R2 live replay exists, analyze seat ZiYiMing
    r2_files = sorted(R2_REPLAYS.glob("episode-1080*-replay.json"))
    if r2_files:
        data = json.loads(r2_files[-1].read_text(encoding="utf-8"))
        teams = (data.get("info") or {}).get("TeamNames") or []
        steps = data.get("steps") or []
        if "ZiYiMing" in teams:
            p = teams.index("ZiYiMing")
            fr = analyze_player(steps, p)
            print(f"\n=== R2 live sample {r2_files[-1].name} seat={p} ===")
            print("  n_lists", fr["n_lists"])
            print("  n_prem_events", fr["n_prem_events"])
            print("  first_list", fr["first_list"])
            print("  inv d15/20/25", {d: fr["inv_day"].get(d) for d in (15, 20, 25)})


if __name__ == "__main__":
    main()
