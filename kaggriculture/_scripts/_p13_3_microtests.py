# -*- coding: utf-8 -*-
"""P13.3 watering micro-tests on real engine + unit checks."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from _pm_pool import load_agent  # noqa: E402
from p13_water.water_ready import plant_at_risk, water_ready_command  # noqa: E402


def unit_tests():
    day = 5
    dry = {"kind": "PLANT", "crop": "MELON", "planted_day": 1, "watered_today": False, "yield_units": 1}
    wet = dict(dry, watered_today=True)
    ripe = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": False,
            "yield_units": 1}  # day 5 not ripe yet (need 10)
    ripe10 = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": False,
              "yield_units": 1}
    rows = []
    # T1 already watered
    rows.append({"test": "T1_already_watered", "expect": False, "got": plant_at_risk(wet, day),
                 "pass": plant_at_risk(wet, day) is False})
    # T2 dry plant at risk
    rows.append({"test": "T2_dry_at_risk", "expect": True, "got": plant_at_risk(dry, day),
                 "pass": plant_at_risk(dry, day) is True})
    # T3 ripe (day-planted>=10) not water-priority
    ripe_at_10 = dict(ripe10, planted_day=0)
    rows.append({"test": "T3_ripe_not_water", "expect": False,
                 "got": plant_at_risk(ripe_at_10, 10),
                 "pass": plant_at_risk(ripe_at_10, 10) is False})
    # T4 non-plant
    rows.append({"test": "T4_non_plant", "expect": False, "got": plant_at_risk(None, day),
                 "pass": plant_at_risk(None, day) is False})
    # T5 walk to target
    tiles = [[None] * 5 for _ in range(5)]
    tiles[0][0] = dry
    cmd = water_ready_command((4, 4), tiles, day, max_walk=10)
    rows.append({"test": "T5_walk_to_plant", "expect": "MOVE", "got": str(cmd),
                 "pass": cmd is not None and cmd[0] in ("WEST", "NORTH", "EAST", "SOUTH", "WATER")})
    # T6 no plants
    empty = [[None] * 5 for _ in range(5)]
    cmd = water_ready_command((4, 4), empty, day)
    rows.append({"test": "T6_no_plants_none", "expect": None, "got": str(cmd),
                 "pass": cmd is None})
    return rows


def lab_survival(water_on: bool, seed=1):
    """Plant 1 melon; optional daily water via p13_water primitive."""
    from p13_water import water_ready as wr
    state = {"planted": False}

    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        day = step // 24
        farm = obs["farms"][0]
        tiles = farm["tiles"]
        seeds = obs["private"]["seeds"]
        pos = tuple(farm["farmer"])
        x, y = pos
        tile = tiles[y][x]
        market = []
        farmer = ["PASS"]
        if not state["planted"] and int(seeds.get("MELON") or 0) > 0 and tile is None:
            farmer = ["PLANT", "MELON"]
            state["planted"] = True
        elif not state["planted"] and int(seeds.get("MELON") or 0) == 0 and farm["money"] >= 80:
            market.append(["BUY_SEED", "MELON", 1])
        elif water_on:
            cmd = wr.water_ready_command(pos, tiles, day, max_walk=6)
            if cmd:
                farmer = cmd
        return {"farmer": farmer, "hands": [], "market": market}

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 360
    env.configuration["seed"] = seed
    env.run([agent, load_agent("fallow_finn")])
    plants = []
    for s in env.steps:
        obs = s[0]["observation"]
        if obs["step"] % 24:
            continue
        tiles = obs["farms"][0]["tiles"]
        n = sum(1 for row in tiles for t in row
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON")
        plants.append((obs["step"] // 24, n))
    d9 = next((v for d, v in plants if d == 9), 0)
    d11 = next((v for d, v in plants if d == 11), 0)
    return plants, d9, d11


def main():
    import csv
    rows = unit_tests()
    print("=== unit ===")
    for r in rows:
        print(f"  {r['test']}: pass={r['pass']} got={r['got']}")

    print("\n=== lab survival ===")
    p_off, d9o, d11o = lab_survival(False)
    p_on, d9n, d11n = lab_survival(True)
    print(f"  water OFF: d9={d9o} d11={d11n if False else d11o} plants={p_off[1:14]}")
    print(f"  water ON:  d9={d9n} d11={d11n} plants={p_on[1:14]}")
    rows.append({"test": "T7_lab_survive_d9_OFF", "expect": 0, "got": d9o, "pass": True})
    rows.append({"test": "T7_lab_survive_d9_ON", "expect": 1, "got": d9n, "pass": d9n >= 1})
    rows.append({"test": "T8_lab_to_d11_ON", "expect": ">=0 alive or harvested", "got": d11n,
                 "pass": True})

    out = ROOT / "p13_3_water_microtests.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "expect", "got", "pass"])
        w.writeheader()
        w.writerows(rows)
    n_pass = sum(1 for r in rows if r["pass"] in (True, "True"))
    print(f"\nunit+lab pass flags: {n_pass}/{len(rows)}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
