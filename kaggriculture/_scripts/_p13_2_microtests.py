# -*- coding: utf-8 -*-
"""P13.2 micro-tests: melon survival + harvest → inv → shed → sell."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from _pm_pool import load_agent  # noqa: E402


def make_lab_agent(water: bool, harvest: bool, drop: bool, plant_day=0):
    """Minimal lab agent: buy+plant melon, optional water/harvest/drop/sell."""
    state = {"bought": False, "planted": 0}

    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        day = step // 24
        hour = step % 24
        farm = obs["farms"][obs["player"]]
        private = obs["private"]
        tiles = farm["tiles"]
        shed = private["shed"]
        seeds = private["seeds"]
        invs = private["inventories"]
        inv = invs[0] if invs else {}
        pos = tuple(farm["farmer"])
        money = farm["money"]
        market = []
        farmer = ["PASS"]

        if not state["bought"] and money >= 80:
            market.append(["BUY_SEED", "MELON", 1])
            state["bought"] = True

        x, y = pos
        tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else "LOCKED"

        # plant if empty and have seed
        if tile is None and int(seeds.get("MELON") or 0) > 0 and state["planted"] < 1:
            farmer = ["PLANT", "MELON"]
            state["planted"] += 1
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
            planted = int(tile.get("planted_day") or -1)
            yu = int(tile.get("yield_units") or 0)
            ready = yu > 0 and day - planted >= 10
            if harvest and ready:
                farmer = ["HARVEST"]
            elif water and not tile.get("watered_today"):
                farmer = ["WATER"]
        # walk to empty tile at (0,0) if not there
        elif tile is None or tile == "LOCKED" or (isinstance(tile, dict) and tile.get("kind") == "WEED"):
            if x > 0:
                farmer = ["WEST"]
            elif y > 0:
                farmer = ["NORTH"]
            elif x < 4:
                farmer = ["EAST"]
            elif y < 4:
                farmer = ["SOUTH"]

        # after harvest, melon in inv → drop at shed
        if drop and int(inv.get("MELON") or 0) > 0:
            if (x, y) in ((3, 3), (4, 3), (3, 4), (4, 4)):
                farmer = ["DROP"]
            else:
                # walk home
                if x < 3:
                    farmer = ["EAST"]
                elif x > 4:
                    farmer = ["WEST"]
                elif y < 3:
                    farmer = ["SOUTH"]
                elif y > 4:
                    farmer = ["NORTH"]

        # sell from shed
        q = int(shed.get("MELON") or 0)
        if q > 0:
            market.append(["SELL", "MELON", q])

        # also try walk toward (0,0) plant site from spawn (4,4)
        if state["planted"] == 0 and tile is not None and not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):
            if hour < 8:
                if x > 0 and farmer == ["PASS"]:
                    farmer = ["WEST"]
                elif y > 0 and farmer == ["PASS"]:
                    farmer = ["NORTH"]

        return {"farmer": farmer, "hands": [], "market": market}

    return agent


def run_case(name, water, harvest, drop, seed=1, steps=360):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = steps
    env.configuration["seed"] = seed
    lab = make_lab_agent(water, harvest, drop)
    env.run([lab, load_agent("fallow_finn")])
    # scan last obs-like from steps
    last = env.steps[-1][0]["observation"]
    # better: track day-by-day via env
    # re-scan all steps for melon shed / plants
    plants = []
    shed_m = []
    inv_m = []
    for s in env.steps:
        obs = s[0]["observation"]
        step = obs["step"]
        if step % 24 != 0:
            continue
        tiles = obs["farms"][0]["tiles"]
        n_m = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON")
        plants.append((step // 24, n_m))
        shed_m.append((step // 24, int(obs["private"]["shed"].get("MELON") or 0)))
        invs = obs["private"]["inventories"]
        im = sum(int((i or {}).get("MELON") or 0) for i in invs)
        inv_m.append((step // 24, im))
    final_shed = shed_m[-1][1] if shed_m else 0
    max_shed = max((v for _, v in shed_m), default=0)
    max_inv = max((v for _, v in inv_m), default=0)
    plants_d9 = next((v for d, v in plants if d == 9), None)
    plants_d11 = next((v for d, v in plants if d == 11), None)
    print(f"{name}: plants_d9={plants_d9} plants_d11={plants_d11} "
          f"max_inv_melon={max_inv} max_shed_melon={max_shed} final_shed={final_shed}")
    print(f"  plants={plants[:16]}")
    print(f"  shed={shed_m[:16]}")
    return {
        "name": name, "water": water, "harvest": harvest, "drop": drop,
        "plants_d9": plants_d9, "plants_d11": plants_d11,
        "max_inv_melon": max_inv, "max_shed_melon": max_shed,
        "final_shed_melon": final_shed,
        "pass_survive": (plants_d9 or 0) > 0,
        "pass_harvest_to_inv": max_inv > 0,
        "pass_shed": max_shed > 0,
    }


def main():
    rows = []
    print("=== P13.2 micro-tests ===")
    rows.append(run_case("T_no_water_no_harvest", False, False, False))
    rows.append(run_case("T_water_only", True, False, False))
    rows.append(run_case("T_water_harvest_drop", True, True, True))
    rows.append(run_case("T_harvest_no_water", False, True, True))

    import csv
    out = ROOT / "p13_2_harvest_microtests.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n=== GATE ===")
    for r in rows:
        print(f"  {r['name']}: survive={r['pass_survive']} inv={r['pass_harvest_to_inv']} shed={r['pass_shed']}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
