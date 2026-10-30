"""EXP-3A Phase-0 — Endgame fill-seed feasibility observer (RESEARCH ONLY).

Runs RAW v11E (no treatment) vs closer_cleo, fixed-RNG, and records per late
day (24-29) for E's seat:

  spatial: empty (plantable) tiles, unlocked tiles, crop/animal occupancy
  labor:   unit actions per day split movement / productive / PASS (idle)
  seed:    seeds held (private), tape-PLANT actions on empty slots by crop
  cash:    money at day start, WHEAT/CARROT seed price, would-be cost

Key derivation (engine 1.32.7): PLANT requires the crop in action[1] and a
held seed (engine L417-429) -> "requires_buy" = late tape-PLANT on an empty
slot whose crop seed is NOT held (the exact BUY_SEED opportunity E2 targets).

Maturity (engine CROPS): WHEAT first_yield 2 / max_yield_day 4; CARROT 2/3.
  lonespear rule: days_left > max_yield_day
  minimal rule:   days_left >= first_yield_day (>=1 unit still possible)
"""
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

CROPS = {  # engine 1.32.7
    "WHEAT": {"first": 2, "maxday": 4},
    "CARROT": {"first": 2, "maxday": 3},
    "TOMATO": {"first": 8, "maxday": 8},
    "STRAWBERRY": {"first": 10, "maxday": 10},
    "MELON": {"first": 10, "maxday": 12},
}
LATE_DAYS = list(range(24, 30))  # days_left = 6..1
_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}
PRODUCTIVE = {"WATER", "PLANT", "HARVEST", "FERTILIZE", "FEED", "CARE",
              "COLLECT_FERTILIZER", "PLACE", "PICKUP", "DROP", "DIG", "BUILD_PASTURE", "BUILD_COOP"}


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


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

    day_stats = {d: {
        "empty": 0, "unlocked": 0, "crop_tiles": 0, "animal_tiles": 0,
        "actions": 0, "movement": 0, "productive": 0, "idle": 0,
        "plant_planned": {}, "seed_held": {}, "requires_buy": {},
        "money": 0.0, "price": {},
    } for d in LATE_DAYS}

    for st in steps:
        obs = st[e_idx].get("observation") or {}
        act = st[e_idx].get("action") or {}
        day = int(obs.get("day", 0) or 0)
        if day not in day_stats:
            continue
        ds = day_stats[day]
        farms = obs.get("farms") or []
        farm = farms[e_idx] if len(farms) == 2 else None
        tiles = (farm or {}).get("tiles") or []
        priv = obs.get("private") or {}

        # spatial snapshot (state at step start of the day's first step)
        if ds["unlocked"] == 0 and day == obs.get("day", 0):
            for row in tiles:
                for tt in row:
                    if isinstance(tt, dict):
                        if tt.get("kind") == "PLANT":
                            ds["crop_tiles"] += 1
                        elif "animal" in tt:
                            ds["animal_tiles"] += 1
                        else:
                            ds["unlocked"] += 1  # structures/shed etc
                    elif tt is None:
                        ds["empty"] += 1
                        ds["unlocked"] += 1
        # seeds + money (public-ish: private seeds are what the agent sees)
        seeds = priv.get("seeds", {}) or {}
        ds["seed_held"] = {k: int(v or 0) for k, v in seeds.items() if k in CROPS}
        ds["money"] = float(farm.get("money", 0) or 0) if farm else 0.0
        prices = (obs.get("market") or {}).get("prices", {}) or {}
        ds["price"] = {"WHEAT": float(prices.get("WHEAT", 25) or 25),
                       "CARROT": float(prices.get("CARROT", 35) or 35)}

        # unit actions: movement / productive / idle + tape-PLANT on empty slots
        fp = list((farm or {}).get("farmer", [0, 0]))
        hs = (farm or {}).get("hands") or []
        up = [fp] + [list(h) for h in hs]
        ua = [act.get("farmer", ["PASS"])] + list(act.get("hands") or [])
        track = [list(p) for p in up]
        for u in range(min(len(up), len(ua))):
            o = ua[u]
            if not isinstance(o, (list, tuple)) or not o:
                continue
            op = o[0]
            ds["actions"] += 1
            if op in _MOVES:
                ds["movement"] += 1
                dx, dy = _MOVES[op]
                fx, fy = int(track[u][0]), int(track[u][1])
                track[u] = [max(0, min(len(tiles) - 1, fx + dx)), max(0, min(len(tiles) - 1, fy + dy))]
                continue
            if op == "MOVE" and len(o) >= 3:
                track[u] = [int(o[1]), int(o[2])]
                ds["movement"] += 1
                continue
            if op in PRODUCTIVE:
                ds["productive"] += 1
            elif op == "PASS":
                ds["idle"] += 1
            if op == "PLANT" and len(o) >= 2:
                fx, fy = int(track[u][0]), int(track[u][1])
                tt = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]) else None
                crop = o[1]
                if crop in CROPS and tt is None:
                    ds["plant_planned"][crop] = ds["plant_planned"].get(crop, 0) + 1
                    if int(seeds.get(crop, 0) or 0) <= 0:
                        ds["requires_buy"][crop] = ds["requires_buy"].get(crop, 0) + 1

    return {"seed": seed, "seat": seat_e,
            "bank_e": fin[e_idx]["observation"]["farms"][e_idx]["money"],
            "bank_o": fin[1 - e_idx]["observation"]["farms"][1 - e_idx]["money"],
            "win": int(fin[e_idx]["reward"] > fin[1 - e_idx]["reward"]),
            "days": day_stats}


def run_one(args):
    return play_one(args[0], args[1])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="_audit_tmp/fillseed_obs.jsonl")
    a = ap.parse_args()
    jobs = [(s, 0 if s % 2 == 0 else 1) for s in range(a.seed0, a.seed0 + a.n)]
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_one, jobs)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[fs] {i + 1}/{len(jobs)} 局")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} 局 -> {a.out}")


if __name__ == "__main__":
    main()
