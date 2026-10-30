# -*- coding: utf-8 -*-
"""P13.4: generic WATER_READY_CROP on natural B crops. Melon hook FORCED OFF."""
from __future__ import annotations

import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
PRODUCTS = CROPS + ("EGG", "MILK", "WOOL", "FERTILIZER")


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_gw_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(label, water_on, seed, seat):
    import p13_1_melon
    import p13_3_water
    p13_1_melon.set_enabled(False)  # CRITICAL: no melon hook
    p13_3_water.set_enabled(water_on)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    # per-day crop field counts
    field = defaultdict(lambda: defaultdict(int))  # day -> crop -> n
    weed = defaultdict(int)
    day_cash = {}
    ops = defaultdict(lambda: defaultdict(int))  # day -> op -> n
    # track plant events: (step, crop) list of planted positions we saw appear
    prev_plants = {}  # (x,y) -> (crop, planted_day)
    plant_events = []  # (day, crop)
    weed_events = []  # (day, crop_lost)
    harvest_events = []  # (day, crop) inferred when plant disappears after ready age
    shed = defaultdict(lambda: defaultdict(int))
    sell_rev = defaultdict(lambda: defaultdict(float))
    sell_qty = defaultdict(lambda: defaultdict(float))
    inv_prod = defaultdict(lambda: defaultdict(int))

    FIRST = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            tiles = farm.get("tiles") or []
            sh = dict(private.get("shed") or {})
            invs = list(private.get("inventories") or [])
            day_cash[day] = float(farm.get("money") or 0)
            for p in PRODUCTS:
                shed[day][p] = int(sh.get(p) or 0)
            inv_sum = defaultdict(int)
            for inv in invs:
                for k, v in (inv or {}).items():
                    inv_sum[k] += int(v or 0)
            for p in PRODUCTS:
                inv_prod[day][p] = inv_sum.get(p, 0)

            cur_plants = {}
            fc = defaultdict(int)
            wcount = 0
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if t is None:
                        continue
                    if t == "LOCKED":
                        continue
                    if not isinstance(t, dict):
                        continue
                    if t.get("kind") == "WEED":
                        wcount += 1
                        continue
                    if t.get("kind") == "PLANT":
                        crop = t.get("crop")
                        fc[crop] += 1
                        cur_plants[(x, y)] = (crop, int(t.get("planted_day") or -1), int(t.get("yield_units") or 0))
            for c in CROPS:
                field[day][c] = fc.get(c, 0)
            weed[day] = wcount

            # detect new plants and vanished plants
            new_set = set(cur_plants.keys())
            old_set = set(prev_plants.keys())
            for pos in new_set - old_set:
                crop = cur_plants[pos][0]
                plant_events.append((day, crop))
            for pos in old_set - new_set:
                crop, pd, yu = prev_plants[pos]
                age = day - pd if pd >= 0 else -1
                need = FIRST.get(crop, 2)
                if age >= need or yu > 0:
                    harvest_events.append((day, crop))
                else:
                    weed_events.append((day, crop))
            # update snapshot at day boundary only to avoid mid-day flicker
            if step % 24 == 23 or step == 719:
                prev_plants.clear()
                prev_plants.update(cur_plants)
            elif not prev_plants:
                prev_plants.update(cur_plants)

            prices = dict((obs.get("market") or {}).get("prices") or {})
            cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            for c in cmds:
                if c:
                    ops[day][c[0]] += 1
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    item, q = o[1], int(o[2] or 0)
                    px = int(prices.get(item) or 0)
                    sell_qty[day][item] += q
                    sell_rev[day][item] += q * px
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])

    # crop totals
    planted_c = defaultdict(int)
    for d, c in plant_events:
        planted_c[c] += 1
    harvested_c = defaultdict(int)
    for d, c in harvest_events:
        harvested_c[c] += 1
    weeded_c = defaultdict(int)
    for d, c in weed_events:
        weeded_c[c] += 1
    rev_c = defaultdict(float)
    qty_c = defaultdict(float)
    for d in sell_rev:
        for p, v in sell_rev[d].items():
            rev_c[p] += v
            qty_c[p] += sell_qty[d].get(p, 0)

    # survival: plants that lived to first_yield age (seen on field at day pd+need)
    # approximate: harvested + still alive at end with age>=need
    survived_c = defaultdict(int)
    for c in CROPS:
        survived_c[c] = harvested_c[c]  # lower bound

    def cash(d):
        return day_cash.get(d)

    rec = {
        "label": label, "water": int(water_on), "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op, "win": int(my > op),
        "d10": cash(10), "d15": cash(15), "d20": cash(20), "d25": cash(25), "d29": cash(29),
        "weed_d10": weed.get(10), "weed_d15": weed.get(15), "weed_d20": weed.get(20),
        "WATER": sum(ops[d].get("WATER", 0) for d in ops),
        "MOVE": sum(ops[d].get("NORTH", 0) + ops[d].get("SOUTH", 0) +
                    ops[d].get("EAST", 0) + ops[d].get("WEST", 0) for d in ops),
        "PLANT": sum(ops[d].get("PLANT", 0) for d in ops),
        "HARVEST": sum(ops[d].get("HARVEST", 0) for d in ops),
        "PICKUP": sum(ops[d].get("PICKUP", 0) for d in ops),
        "FEED": sum(ops[d].get("FEED", 0) for d in ops),
        "CARE": sum(ops[d].get("CARE", 0) for d in ops),
        "planted_total": len(plant_events),
        "harvest_events": len(harvest_events),
        "weed_events": len(weed_events),
    }
    for c in CROPS:
        rec[f"plant_{c}"] = planted_c[c]
        rec[f"harv_{c}"] = harvested_c[c]
        rec[f"weed_{c}"] = weeded_c[c]
        rec[f"rev_{c}"] = rev_c[c]
        rec[f"qty_{c}"] = qty_c[c]
    for p in ("MILK", "WOOL", "EGG", "FERTILIZER"):
        rec[f"rev_{p}"] = rev_c[p]
        rec[f"qty_{p}"] = qty_c[p]
    rec["rev_total"] = sum(rev_c.values())

    print(f"{label} s{seed} seat{seat}: d15={rec['d15']} d29={my:.0f} "
          f"WATER={rec['WATER']} plants={rec['planted_total']} harv={rec['harvest_events']} "
          f"weed={rec['weed_events']} rev={rec['rev_total']:.0f} "
          f"W={rec['plant_WHEAT']}/{rec['harv_WHEAT']}/{rec['rev_WHEAT']:.0f} "
          f"C={rec['plant_CARROT']}/{rec['harv_CARROT']}/{rec['rev_CARROT']:.0f} "
          f"S={rec['plant_STRAWBERRY']}/{rec['harv_STRAWBERRY']}", flush=True)
    return rec


def main():
    # force melon off at import time
    import p13_1_melon
    p13_1_melon.set_enabled(False)
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            rows.append(run("B0", False, seed, seat))
            rows.append(run("B1_water", True, seed, seat))

    out = ROOT / "p13_4_generic_water.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(label, k):
        v = [r[k] for r in rows if r["label"] == label and r.get(k) is not None]
        return sum(v) / len(v) if v else 0

    print("\n=== SUMMARY (melon hook OFF) ===")
    keys = ["d10", "d15", "d20", "d29", "WATER", "PLANT", "HARVEST", "PICKUP", "FEED",
            "MOVE", "planted_total", "harvest_events", "weed_events", "rev_total",
            "plant_WHEAT", "harv_WHEAT", "rev_WHEAT", "plant_CARROT", "harv_CARROT", "rev_CARROT",
            "plant_STRAWBERRY", "harv_STRAWBERRY", "rev_STRAWBERRY", "rev_MILK", "rev_WOOL",
            "rev_FERTILIZER"]
    print(f"{'metric':20s} {'B0':>10} {'B1':>10} {'Δ':>10}")
    for k in keys:
        a, b = mean("B0", k), mean("B1_water", k)
        print(f"{k:20s} {a:10.1f} {b:10.1f} {b-a:+10.1f}")

    print("\n=== PAIRED ===")
    b0 = [r for r in rows if r["label"] == "B0"]
    b1 = [r for r in rows if r["label"] == "B1_water"]
    for s0, s1 in zip(b0, b1):
        print(f"  s{s0['seed']} seat{s0['seat']}: "
              f"Δd15={(s1['d15'] or 0)-(s0['d15'] or 0):+.0f} "
              f"Δd29={(s1['my'] or 0)-(s0['my'] or 0):+.0f} "
              f"Δrev={(s1['rev_total'] or 0)-(s0['rev_total'] or 0):+.0f} "
              f"ΔW={(s1['WATER'] or 0)-(s0['WATER'] or 0):+.0f} "
              f"Δharv={(s1['harvest_events'] or 0)-(s0['harvest_events'] or 0):+.0f} "
              f"Δweed={(s1['weed_events'] or 0)-(s0['weed_events'] or 0):+.0f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
