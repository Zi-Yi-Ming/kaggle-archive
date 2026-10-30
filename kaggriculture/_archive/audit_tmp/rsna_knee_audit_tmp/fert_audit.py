"""Fertilizer Economics Phase-0 — v11E usage audit harness (RESEARCH ONLY).

Loads kaggriculture/main.py (v11E) WITHOUT modifying it; plays fixed-RNG paired
games vs closer_cleo; records fertilizer usage statistics per game:

  - COLLECT_FERTILIZER / FERTILIZE / BUY_PRODUCT(FERTILIZER) / SELL(FERTILIZER) counts
    (from E's action stream, attributed via obs unit positions — engine ops
    WATER/FERTILIZE/COLLECT_FERTILIZER act on the unit's standing tile)
  - per-crop fertilize coverage = |unique tiles fertilized| / |unique tiles planted|
  - in-window watering events split by fertilized vs under-fertilized
  - end-game shed + carried FERTILIZER surplus

Fixed RNG: env.info["seed"] = seed (NOT configuration["seed"]).
Paired: seat alternation by seed parity.
"""
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")

import _pm_pool as P  # reference agent loader (closer_cleo)
from kaggle_environments import make

CROPS_WINDOW = {  # from engine 1.32.7 CROPS table
    "WHEAT":      {"ongoing": False, "max_yield_day": 4,  "first_yield_day": 2},
    "CARROT":     {"ongoing": False, "max_yield_day": 3,  "first_yield_day": 2},
    "TOMATO":     {"ongoing": True,  "max_yield_day": 8,  "first_yield_day": 8, "interval": 1},
    "STRAWBERRY": {"ongoing": True,  "max_yield_day": 10, "first_yield_day": 10, "interval": 2},
    "MELON":      {"ongoing": False, "max_yield_day": 12, "first_yield_day": 10},
}
CAP = {"WHEAT": 6, "CARROT": 4, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}  # engine max_yield


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def _in_window(crop, day, planted_day):
    cd = CROPS_WINDOW[crop]
    if cd["ongoing"]:
        dsf = day - planted_day - cd["first_yield_day"]
        return dsf >= 0 and dsf % cd["interval"] == 0
    ws = (cd["max_yield_day"] + 1) // 2
    return ws <= day - planted_day <= cd["max_yield_day"]


def play_one(seed, seat_e):
    agent = load_v11e()
    opp = P.load_agent("closer_cleo")
    a, b = (agent, opp) if seat_e == 0 else (opp, agent)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    fin = steps[-1]
    e_idx = 0 if seat_e == 0 else 1

    stat = {
        "seed": seed, "seat": seat_e,
        "win": int(fin[e_idx]["reward"] > fin[1 - e_idx]["reward"]),
        "bank_e": fin[e_idx]["observation"]["farms"][e_idx]["money"],
        "bank_o": fin[1 - e_idx]["observation"]["farms"][1 - e_idx]["money"],
        "collect": 0, "fertilize": 0, "buy_fert": 0, "sell_fert": 0,
        "water_in_window": 0, "water_fert_in_window": 0, "water_unfert_in_window": 0,
        "w_in": {}, "w_fert": {}, "w_unfert": {},   # per-crop water counters
        "harvested": {}, "harvest_actions": {},     # per-crop realized yield (sum of yield_units at harvest) + action count
        "fert_shed_end": 0,
    }
    planted = {}   # crop -> set of (fx, fy)
    ferted = {}    # crop -> set of (fx, fy)
    tile_yield = {}  # (fx, fy) -> {"crop", "yield", "max"}  simulated per-tile yield
    real_yield = {}  # crop -> list of realized per-tile yields at harvest

    for st in steps:
        obs = st[e_idx].get("observation") or {}
        act = st[e_idx].get("action") or {}
        day = obs.get("day", 0)
        farms = obs.get("farms") or []
        farm = farms[e_idx] if len(farms) == 2 else None
        tiles = (farm or {}).get("tiles") or []

        # unit positions: farmer + hands (aligned with action stream)
        farmer_pos = list((farm or {}).get("farmer", [0, 0]))
        hands = (farm or {}).get("hands") or []
        unit_pos = [farmer_pos] + [list(h) for h in hands]
        unit_acts = [act.get("farmer", ["PASS"])] + list(act.get("hands") or [])
        n_units = len(unit_pos)
        track = [list(p) for p in unit_pos]  # per-step truth; move ops update in-step
        _MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}

        # unique planted tiles (from obs tiles)
        for fy, row in enumerate(tiles):
            for fx, tt in enumerate(row):
                if isinstance(tt, dict) and tt.get("kind") == "PLANT" and tt.get("crop"):
                    planted.setdefault(tt["crop"], set()).add((fx, fy))

        for u in range(min(n_units, len(unit_acts))):
            order = unit_acts[u]
            if not isinstance(order, (list, tuple)) or not order:
                continue
            op = order[0]
            pos = track[u]
            fx, fy = int(pos[0]), int(pos[1])
            if op in _MOVES:
                dx, dy = _MOVES[op]
                track[u] = [max(0, min(len(tiles) - 1, fx + dx)), max(0, min(len(tiles) - 1, fy + dy))]
                continue
            if op == "MOVE" and len(order) >= 3:
                track[u] = [int(order[1]), int(order[2])]
                continue
            tt = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]) else None
            if op == "COLLECT_FERTILIZER":
                stat["collect"] += 1
            elif op == "FERTILIZE":
                stat["fertilize"] += 1
                if isinstance(tt, dict) and tt.get("crop"):
                    ferted.setdefault(tt["crop"], set()).add((fx, fy))
            elif op == "WATER":
                if isinstance(tt, dict) and tt.get("kind") == "PLANT" and tt.get("crop"):
                    crop = tt["crop"]
                    planted_day = tt.get("planted_day", 0)
                    if _in_window(crop, day, planted_day):
                        stat["water_in_window"] += 1
                        stat["w_in"][crop] = stat["w_in"].get(crop, 0) + 1
                        fertilized_now = tt.get("fertilized_until_day", -1) >= day
                        if fertilized_now:
                            stat["water_fert_in_window"] += 1
                            stat["w_fert"][crop] = stat["w_fert"].get(crop, 0) + 1
                        else:
                            stat["water_unfert_in_window"] += 1
                            stat["w_unfert"][crop] = stat["w_unfert"].get(crop, 0) + 1
                        # simulate per-tile yield (engine: +2 fertilized / +1 unfertilized, cap max_yield)
                        ty = tile_yield.setdefault((fx, fy), {"crop": crop, "yield": 0, "max": CAP[crop]})
                        ty["yield"] = min(ty["max"], ty["yield"] + (2 if fertilized_now else 1))
            elif op == "HARVEST":
                if isinstance(tt, dict) and tt.get("kind") == "PLANT" and tt.get("crop"):
                    crop = tt["crop"]
                    stat["harvest_actions"][crop] = stat["harvest_actions"].get(crop, 0) + 1
                    ty = tile_yield.get((fx, fy), {"yield": 0})
                    stat["harvested"][crop] = stat["harvested"].get(crop, 0) + ty["yield"]
                    real_yield.setdefault(crop, []).append(ty["yield"])
                    ty["yield"] = 0  # engine resets yield_units on harvest

        for order in (act.get("market") or []):
            if not isinstance(order, (list, tuple)) or len(order) < 2:
                continue
            if order[0] == "BUY_PRODUCT" and order[1] == "FERTILIZER":
                stat["buy_fert"] += 1
            elif order[0] == "SELL" and order[1] == "FERTILIZER":
                stat["sell_fert"] += 1

    stat["tiles_planted"] = {k: len(v) for k, v in planted.items()}
    stat["tiles_fertilized"] = {k: len(v) for k, v in ferted.items()}

    priv = fin[e_idx].get("observation", {}).get("private", {}) or {}
    shed = priv.get("shed", {}) or {}
    stat["fert_shed_end"] = int(shed.get("FERTILIZER", 0) or 0)
    return stat


def run_one(args):
    seed, seat = args
    return play_one(seed, seat)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="_audit_tmp/fert_audit.jsonl")
    a = ap.parse_args()
    jobs = [(s, 0 if s % 2 == 0 else 1) for s in range(a.seed0, a.seed0 + a.n)]
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_one, jobs)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[fert] {i + 1}/{len(jobs)} 局")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} 局 -> {a.out}")


if __name__ == "__main__":
    main()
