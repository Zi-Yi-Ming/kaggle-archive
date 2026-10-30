"""EXP-6 differential observer: COK V10 vs v11E in the SAME game (paired
fixed-RNG seeds), recording per-day trajectories for BOTH seats:
  bank (day-start money), SELL volume+realized price by item, sell timing,
  animal counts, productive action counts (WATER/PLANT/HARVEST/FEED/CARE).
Purpose: verify hypotheses H2 (meta market layer -> better realized prices /
sell timing) and H3 (cow choreography + repair -> production closer to plan).
OBS SEMANTICS: observation at step s is POST-action (EXP-4 probe) -> use
state(s) - state(s-1) for execution signals; day-start money = first step's
obs money.
"""
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

_spec = importlib.util.spec_from_file_location("cok_v10", "_audit_tmp/repoC/main.py")
COK = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(COK)

PRODUCTIVE = {"WATER", "PLANT", "HARVEST", "FERTILIZE", "FEED", "CARE",
              "COLLECT_FERTILIZER", "PLACE", "PICKUP", "DROP"}
MOVES = {"NORTH", "SOUTH", "WEST", "EAST"}
ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
         "MILK", "WOOL", "EGG", "FERTILIZER"]


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def count_animals(tiles):
    n = 0
    for row in tiles:
        for tt in row:
            if isinstance(tt, dict) and "animal" in tt:
                n += 1
    return n


def play_one(seed):
    cok_left = seed % 2 == 0
    v11e = load_v11e()
    a, b = (COK.agent, v11e) if cok_left else (v11e, COK.agent)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    fin = steps[-1]

    out = {"seed": seed, "cok_seat": 0 if cok_left else 1,
           "day": {}, "sell": {"COK": {i: [0, 0.0] for i in ITEMS},
                               "V11E": {i: [0, 0.0] for i in ITEMS}},
           "prod": {"COK": {i: 0 for i in PRODUCTIVE},
                    "V11E": {i: 0 for i in PRODUCTIVE}},
           "animals": {"COK": [], "V11E": []},
           "bank_e": fin[cok_left]["observation"]["farms"][cok_left]["money"],
           "bank_v": fin[1 - cok_left]["observation"]["farms"][1 - cok_left]["money"]}

    for st in steps:
        for seat in range(2):
            tag = "COK" if (seat == (0 if cok_left else 1)) else "V11E"
            obs = st[seat].get("observation") or {}
            act = st[seat].get("action") or {}
            day = int(obs.get("day", 0) or 0)
            farms = obs.get("farms") or []
            farm = farms[seat] if len(farms) == 2 else None
            tiles = (farm or {}).get("tiles") or []
            money = float(farm.get("money", 0) or 0) if farm else 0.0
            prices = (obs.get("market") or {}).get("prices", {}) or {}
            step = int(obs.get("step", 0) or 0)

            if day not in out["day"]:
                out["day"][day] = {"COK": None, "V11E": None}
            if out["day"][day][tag] is None:
                out["day"][day][tag] = money  # day-start snapshot

            for o in (act.get("market") or []):
                if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL":
                    item, qty = o[1], int(o[2])
                    if item in ITEMS:
                        px = float(prices.get(item, 0) or 0)
                        out["sell"][tag][item][0] += qty
                        out["sell"][tag][item][1] += px * qty

            ua = [act.get("farmer", ["PASS"])] + list(act.get("hands") or [])
            for u in ua:
                if isinstance(u, (list, tuple)) and u and u[0] in PRODUCTIVE:
                    out["prod"][tag][u[0]] += 1
            out["animals"][tag].append(count_animals(tiles))
    return out


def run_one(seed):
    return play_one(seed)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="_audit_tmp/cok_diff_obs.jsonl")
    a = ap.parse_args()
    seeds = list(range(a.seed0, a.seed0 + a.n))
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_one, seeds)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[df] {i + 1}/{len(seeds)} 局")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} 局 -> {a.out}")


if __name__ == "__main__":
    main()
