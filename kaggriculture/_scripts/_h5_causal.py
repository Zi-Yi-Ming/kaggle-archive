# -*- coding: utf-8 -*-
"""H5: minimal causal test — empty-tile count → weed RNG calls → shop draw.

Engine (kaggriculture.py _end_of_day):
  rng = Random((seed * 1_000_003) ^ day)
  for each farm: _spawn_weeds(...)  # rng.random() ONLY if tile is None
  if shop unlock: rng.choice(shops)

Hypothesis: filling empty tiles reduces rng.random() calls, shifting shop.choice.
"""
from __future__ import annotations

import json
from pathlib import Path

from kaggle_environments import make

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
OUT = ROOT / "experiments" / "h5_rng"
OUT.mkdir(parents=True, exist_ok=True)


def make_agent(plant_days):
    """If current day in plant_days, try to PLANT WHEAT on empty tile else PASS."""

    def agent(obs):
        day = int(obs.get("day") or 0)
        me = int(obs.get("player") or 0)
        farm = (obs.get("farms") or [])[me]
        x, y = farm.get("farmer") or [4, 4]
        tiles = farm.get("tiles") or []
        tile = tiles[y][x] if y < len(tiles) and x < len(tiles[0]) else None
        market = []
        seeds = (obs.get("private") or {}).get("seeds") or {}
        if day in plant_days and tile is None:
            if seeds.get("WHEAT", 0) <= 0 and float(farm.get("money") or 0) >= 10:
                market.append(["BUY_SEED", "WHEAT", 1])
            if seeds.get("WHEAT", 0) > 0:
                return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}
        # move randomly-ish deterministic to next empty-ish tile via NORTH
        return {"farmer": ["NORTH"], "hands": [], "market": market}

    return agent


def run(seed, plant_days, steps=72):
    a0 = make_agent(plant_days)
    a1 = make_agent(set())  # opponent never plants
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = steps
    env.configuration["seed"] = seed
    env.run([a0, a1])
    shops = []
    empty = []
    weeds = []
    for snap in env.steps:
        obs = snap[0]["observation"]
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        if step is None:
            continue
        town = obs.get("town") or {}
        unlocked = tuple(town.get("unlocked_shops") or [])
        if not shops or unlocked != shops[-1]:
            shops.append(unlocked)
        if int(step) % 24 == 0:
            farms = obs.get("farms") or []
            ne = 0
            nw = 0
            for f in farms:
                for row in f.get("tiles") or []:
                    for t in row or []:
                        if t is None:
                            ne += 1
                        elif isinstance(t, dict) and t.get("kind") == "WEED":
                            nw += 1
            empty.append((int(step) // 24, ne, nw))
    final = env.steps[-1]
    banks = [
        float(final[0]["observation"]["farms"][0]["money"]),
        float(final[1]["observation"]["farms"][1]["money"]),
    ]
    return {
        "seed": seed,
        "plant_days": sorted(plant_days),
        "shops": [list(s) for s in shops],
        "empty_weed_by_day": empty,
        "banks": banks,
        "final_shops": list(shops[-1]) if shops else [],
    }


def main():
    # C0: never plant
    # C1: plant many days (fill tiles → fewer empty → fewer rng.random in weeds)
    # C2: plant even more aggressively (different empty count)
    conditions = {
        "C0_pass": set(),
        "C1_plant_d0_5": set(range(0, 6)),
        "C2_plant_d0_15": set(range(0, 16)),
    }
    seeds = [1, 2, 3, 4, 5]
    rows = []
    for cname, pdays in conditions.items():
        for seed in seeds:
            r = run(seed, pdays)
            r["condition"] = cname
            rows.append(r)
            print(f"{cname} seed={seed} shops_n={len(r['shops'])} "
                  f"final={r['final_shops']} d0_empty={r['empty_weed_by_day'][0][1] if r['empty_weed_by_day'] else None} "
                  f"banks={r['banks']}", flush=True)

    # compare shop sequences C0 vs C1 vs C2 per seed
    print("\n=== shop sequence equality per seed ===")
    by_seed = {}
    for r in rows:
        by_seed.setdefault(r["seed"], {})[r["condition"]] = tuple(tuple(s) for s in r["shops"])
    n_diff_c1 = n_diff_c2 = 0
    for seed, m in sorted(by_seed.items()):
        c0 = m.get("C0_pass")
        c1 = m.get("C1_plant_d0_5")
        c2 = m.get("C2_plant_d0_15")
        d1 = c1 != c0
        d2 = c2 != c0
        n_diff_c1 += d1
        n_diff_c2 += d2
        print(f"  seed {seed}: C1_diff={d1} C2_diff={d2}")
        if d1 or d2:
            print(f"    C0={c0}")
            if d1:
                print(f"    C1={c1}")
            if d2:
                print(f"    C2={c2}")
    print(f"\nC1 differs from C0 on {n_diff_c1}/{len(by_seed)} seeds")
    print(f"C2 differs from C0 on {n_diff_c2}/{len(by_seed)} seeds")

    # also dump empty counts at first shop-unlock day (day 2 end → shop at start of day3?)
    # shop unlock when next_day % 3 == 0 i.e. after day 2,5,8,...
    print("\n=== empty tiles at end of day 2 (before first shop draw) ===")
    for r in rows:
        d2 = next((e for e in r["empty_weed_by_day"] if e[0] == 2), None)
        print(f"  {r['condition']:16s} seed={r['seed']} day2 empty/weed={d2}")

    path = OUT / "h5_shop_sequence_comparison.json"
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", path)

    # CSV
    import csv
    csv_path = ROOT / "h5_shop_sequence_comparison.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["condition", "seed", "n_shop_events", "final_shops", "day2_empty", "day2_weed", "bank0", "bank1"])
        for r in rows:
            d2 = next((e for e in r["empty_weed_by_day"] if e[0] == 2), (2, None, None))
            w.writerow([
                r["condition"], r["seed"], len(r["shops"]),
                "|".join(r["final_shops"]),
                d2[1], d2[2], r["banks"][0], r["banks"][1],
            ])
    print("wrote", csv_path)


if __name__ == "__main__":
    main()
