# -*- coding: utf-8 -*-
"""Ashok top-10: extract d25-29 sell cadence for winner vs loser in mirror games."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

P = Path(r"D:\桌面\Kaggle\kaggriculture\_external\public_data\ashok_top10\replays_2026-08-03.parquet")


def analyze_episode(data):
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [0, 0]
    steps = data.get("steps") or []
    try:
        r0, r1 = float(rewards[0]), float(rewards[1])
    except Exception:
        return None
    winner = 0 if r0 >= r1 else 1
    loser = 1 - winner

    # per player: sell qty and value by day for d24-29
    qty = [defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))]
    val = [defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(float))]
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
            if step % 24 == 0 and p == 0:
                farms = obs.get("farms") or []
                if len(farms) >= 2:
                    money[0][day] = float(farms[0].get("money") or 0)
                    money[1][day] = float(farms[1].get("money") or 0)
            if day < 24:
                continue
            prices = ((obs.get("market") or {}).get("prices") or {})
            # only own actions
            if int(obs.get("player") or p) != p:
                continue
            for o in action.get("market") or []:
                if not o or o[0] != "SELL" or len(o) < 3:
                    continue
                item, q = o[1], int(o[2] or 0)
                if q <= 0:
                    continue
                price = int(prices.get(item) or 1)
                qty[p][day][item] += q
                val[p][day][item] += q * price

    return {
        "teams": teams,
        "rewards": rewards,
        "winner": winner,
        "loser": loser,
        "money": money,
        "qty": qty,
        "val": val,
        "margin": abs(r0 - r1),
    }


def main():
    df = pd.read_parquet(P)
    # take episodes with both banks > 100k (elite mirrors)
    elite = []
    for i in range(len(df)):
        row = df.iloc[i]
        try:
            data = json.loads(row["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            if min(float(rew[0]), float(rew[1])) >= 100000:
                a = analyze_episode(data)
                if a:
                    a["episode_id"] = int(row["episode_id"])
                    elite.append(a)
        except Exception:
            continue
    print(f"elite episodes (both >=100k): {len(elite)} / {len(df)}")
    if not elite:
        print("none; lowering threshold")
        return

    # aggregate winner vs loser sell value d24-29
    item_win = defaultdict(float)
    item_lose = defaultdict(float)
    day_diff = defaultdict(list)
    for a in elite:
        w, l = a["winner"], a["loser"]
        for day in range(24, 30):
            for item, v in a["val"][w][day].items():
                item_win[item] += v
            for item, v in a["val"][l][day].items():
                item_lose[item] += v
            dw = sum(a["val"][w][day].values())
            dl = sum(a["val"][l][day].values())
            day_diff[day].append(dw - dl)

    print("\n=== d24-29 total sell-order value: winner vs loser ===")
    for item in sorted(set(item_win) | set(item_lose), key=lambda x: -(item_win[x] + item_lose[x])):
        print(f"  {item:12s} win={item_win[item]:12.0f} lose={item_lose[item]:12.0f} d={item_win[item]-item_lose[item]:+12.0f}")

    print("\n=== per-day winner-loser sell-order value gap ===")
    for day in sorted(day_diff):
        gaps = day_diff[day]
        print(f"  d{day}: mean_gap={sum(gaps)/len(gaps):+10.0f}  n_pos={sum(1 for g in gaps if g>0)}/{len(gaps)}")

    # money gap at day 25 vs 29
    print("\n=== money gap at day boundaries (winner-loser) ===")
    for day in (20, 24, 25, 26, 27, 28, 29):
        gaps = []
        for a in elite:
            if day in a["money"][0] and day in a["money"][1]:
                w, l = a["winner"], a["loser"]
                gaps.append(a["money"][w][day] - a["money"][l][day])
        if gaps:
            print(f"  d{day}: mean={sum(gaps)/len(gaps):+8.0f} median={sorted(gaps)[len(gaps)//2]:+8.0f}")

    # sample one elite game money curve
    a = elite[0]
    print(f"\nsample ep{a['episode_id']} teams={a['teams']} rewards={a['rewards']}")
    for day in range(15, 30):
        if day in a["money"][0]:
            print(f"  d{day}: p0={a['money'][0][day]:.0f} p1={a['money'][1][day]:.0f}")


if __name__ == "__main__":
    main()
