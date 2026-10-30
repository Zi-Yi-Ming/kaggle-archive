# -*- coding: utf-8 -*-
"""P14: R2 vs B early production commitment timeline (d0-d10). Read-only."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
BASE_PRICE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250}


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p14_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_b():
    import p13_1_melon
    import p13_3_water
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(False)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def snapshot_day(obs):
    player = int(obs.get("player") or 0)
    farm = (obs.get("farms") or [])[player]
    private = obs.get("private") or {}
    tiles = farm.get("tiles") or []
    shed = dict(private.get("shed") or {})
    seeds = dict(private.get("seeds") or {})
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    prices = dict((obs.get("market") or {}).get("prices") or {})
    plants = defaultdict(int)
    empty = locked = weed = structs = animals = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif t == "LOCKED":
                locked += 1
            elif isinstance(t, dict):
                if t.get("kind") == "WEED":
                    weed += 1
                elif t.get("kind") == "PLANT":
                    plants[t.get("crop")] += 1
                elif t.get("kind") in ("COOP", "PASTURE"):
                    structs += 1
                    if t.get("animal"):
                        animals += 1
    return {
        "money": float(farm.get("money") or 0),
        "hands": len(farm.get("hands") or []),
        "n_land": len(farm.get("unlocked_quadrants") or []),
        "empty": empty, "locked": locked, "weed": weed,
        "structs": structs, "animals": animals,
        "plants": dict(plants),
        "shed": shed, "seeds": seeds,
        "shops": shops, "prices": prices,
    }


def run_trace(factory, seed, seat, label):
    own = factory()
    # weak opponent for cleaner own-side trajectory
    from _pm_pool import load_agent
    opp = load_agent("fallow_finn")
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_rows = []
    buy_seed_log = []  # (day, crop, qty)
    plant_log = []  # (day, crop)
    last_snap = None

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if is_own and step <= 250:
                prices = dict((obs.get("market") or {}).get("prices") or {})
                for o in action.get("market") or []:
                    if o and o[0] == "BUY_SEED" and len(o) >= 3:
                        buy_seed_log.append((day, o[1], int(o[2] or 0)))
                cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
                for c in cmds:
                    if c and c[0] == "PLANT" and len(c) >= 2:
                        plant_log.append((day, c[1]))
                if step % 24 == 0:
                    snap = snapshot_day(obs)
                    snap.update({"label": label, "seed": seed, "seat": seat, "day": day, "step": step})
                    day_rows.append(snap)
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    final = float(f[seat]["observation"]["farms"][seat]["money"])
    return day_rows, buy_seed_log, plant_log, final


def main():
    all_days = []
    all_buys = []
    all_plants = []
    finals = []
    for label, fac in (("R2", load_r2), ("B", load_b)):
        for seed in (1, 2):
            days, buys, plants, final = run_trace(fac, seed, 0, label)
            all_days.extend(days)
            all_buys.extend([(label, seed) + b for b in buys])
            all_plants.extend([(label, seed) + p for p in plants])
            finals.append((label, seed, final))
            print(f"{label} s{seed} final={final:.0f} days_logged={len(days)} "
                  f"buys={len(buys)} plants={len(plants)}", flush=True)

    out = ROOT / "p14_r2_production_timeline.csv"
    # flatten plants
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "seed", "day", "money", "hands", "n_land", "empty", "weed",
                    "structs", "animals", "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                    "shed_WHEAT", "shed_MILK", "shed_WOOL", "shed_FERT", "shed_MELON",
                    "seed_WHEAT", "seed_MELON", "seed_CARROT", "shops"])
        for r in all_days:
            p = r.get("plants") or {}
            sh = r.get("shed") or {}
            sd = r.get("seeds") or {}
            w.writerow([
                r["label"], r["seed"], r["day"], r["money"], r["hands"], r["n_land"],
                r["empty"], r["weed"], r["structs"], r["animals"],
                p.get("WHEAT", 0), p.get("CARROT", 0), p.get("TOMATO", 0),
                p.get("STRAWBERRY", 0), p.get("MELON", 0),
                sh.get("WHEAT", 0), sh.get("MILK", 0), sh.get("WOOL", 0),
                sh.get("FERTILIZER", 0), sh.get("MELON", 0),
                sd.get("WHEAT", 0), sd.get("MELON", 0), sd.get("CARROT", 0),
                "|".join(r.get("shops") or []),
            ])

    out2 = ROOT / "p14_seed_buys.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "seed", "day", "crop", "qty"])
        for row in all_buys:
            w.writerow(row)

    out3 = ROOT / "p14_plant_cmds.csv"
    with open(out3, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "seed", "day", "crop"])
        for row in all_plants:
            w.writerow(row)

    print("wrote", out.name, out2.name, out3.name)


if __name__ == "__main__":
    main()
