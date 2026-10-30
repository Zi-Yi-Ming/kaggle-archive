# -*- coding: utf-8 -*-
"""Parse ashok top-10 day parquet: final banks and mid-game structure sample."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

P = Path(r"D:\桌面\Kaggle\kaggriculture\_external\public_data\ashok_top10\replays_2026-08-03.parquet")


def farm_struct(farm):
    animals = Counter()
    plants = Counter()
    for row in farm.get("tiles") or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            if tile.get("animal"):
                animals[tile["animal"]] += 1
            elif tile.get("kind") == "PLANT" and tile.get("crop"):
                plants[tile["crop"]] += 1
    return {
        "money": float(farm.get("money") or 0),
        "quads": len(farm.get("unlocked_quadrants") or []),
        "an": sum(animals.values()),
        "animals": dict(animals),
        "pl": sum(plants.values()),
    }


def analyze_row(row):
    data = json.loads(row["replay_json"])
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [None, None]
    steps = data.get("steps") or []
    snaps = {}
    for idx in (0, 240, 360, 480, 600, 719):  # d0,10,15,20,25,end
        if idx >= len(steps):
            continue
        rec = steps[idx][0] if steps[idx] else {}
        obs = rec.get("observation") or {}
        farms = obs.get("farms") or []
        if len(farms) >= 2:
            snaps[idx] = (farm_struct(farms[0]), farm_struct(farms[1]))
    return {
        "id": row["episode_id"],
        "teams": teams,
        "rewards": rewards,
        "snaps": snaps,
    }


def main():
    df = pd.read_parquet(P)
    print("n_episodes", len(df))
    # sample first 30
    rows = []
    for i in range(min(30, len(df))):
        try:
            rows.append(analyze_row(df.iloc[i]))
        except Exception as e:
            print("fail", i, e)
    # rank by max bank
    def maxb(r):
        rs = [x for x in r["rewards"] if x is not None]
        return max(rs) if rs else 0
    rows.sort(key=maxb, reverse=True)
    print("\n=== TOP 8 by max bank ===")
    for r in rows[:8]:
        print(f"  ep{r['id']} teams={r['teams']} rewards={r['rewards']}")
        for step, (p0, p1) in sorted(r["snaps"].items()):
            day = step // 24
            print(f"    d{day:02d} p0 ${p0['money']:.0f} q={p0['quads']} an={p0['an']}{p0['animals']} | "
                  f"p1 ${p1['money']:.0f} q={p1['quads']} an={p1['an']}{p1['animals']}")
    # aggregate day15 structure of winner
    print("\n=== d15 winner structure histogram (top 20 games) ===")
    an_hist = Counter()
    q_hist = Counter()
    for r in rows[:20]:
        snaps = r["snaps"].get(360)
        if not snaps:
            continue
        p0, p1 = snaps
        # winner by final reward
        try:
            w = 0 if float(r["rewards"][0]) >= float(r["rewards"][1]) else 1
        except Exception:
            continue
        wsn = p0 if w == 0 else p1
        an_hist[(wsn["an"], tuple(sorted(wsn["animals"].items())))] += 1
        q_hist[wsn["quads"]] += 1
    print("animals", an_hist.most_common(8))
    print("quads", q_hist)


if __name__ == "__main__":
    main()
