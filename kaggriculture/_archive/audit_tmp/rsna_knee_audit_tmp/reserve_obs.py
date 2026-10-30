"""EXP-4 Phase-0 — Price-gated cash reserve observer (RESEARCH ONLY).

Runs RAW v11E (no treatment) vs closer_cleo, fixed-RNG seeds 1-120; records:

  - every BUY_ANIMAL market order: step/day/type/qty/money-before/wheat-price/
    animal-count/candidate-reserve (as-coded = 300 + max(px,25)*(n+1)*0) /
    price-gated reference (feeding_days=3, README-implied) / v11E _cash_needed
    replica (flat costs of that turn's buy orders) / shed-delta execution signal
  - per-day: money, shed WHEAT, animal count, feed need (animals/day)

Candidate reserve per lonespear HEAD source (main_v18.py L787-788):
  wheat_px = max(market WHEAT price, 25); reserve = 300 + wheat_px * (n_animals+1) * ANIMAL_BUY_FEED_DAYS
  ANIMAL_BUY_FEED_DAYS = 0 (L119) -> as-coded reserve == 300 flat.
"""
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def _cash_needed_replica(market, prices):
    """v11E _cash_needed semantics (main.py L591-610): flat costs of turn's buy orders."""
    total = 0.0
    for o in market or []:
        if not isinstance(o, (list, tuple)) or len(o) < 3:
            continue
        op = o[0]
        if op == "BUY_SEED":
            total += SEED_COST.get(o[1], 0) * int(o[2])
        elif op == "BUY_ANIMAL":
            total += ANIMAL_COST.get(o[1], 0) * int(o[2])
        elif op == "BUY_PRODUCT":
            total += float(prices.get(o[1], 50) or 50) * int(o[2])
        elif op == "BUY_LAND":
            total += 4000
    return total


def count_animals(tiles):
    n = 0
    for row in tiles:
        for tt in row:
            if isinstance(tt, dict) and "animal" in tt:
                n += 1
    return n


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

    buys = []
    daily = {}
    min_money = 1e18
    prev_shed = None
    for st in steps:
        obs = st[e_idx].get("observation") or {}
        act = st[e_idx].get("action") or {}
        day = int(obs.get("day", 0) or 0)
        farms = obs.get("farms") or []
        farm = farms[e_idx] if len(farms) == 2 else None
        tiles = (farm or {}).get("tiles") or []
        money = float(farm.get("money", 0) or 0) if farm else 0.0
        min_money = min(min_money, money)
        priv = obs.get("private") or {}
        shed = dict(priv.get("shed", {}) or {})
        prices = (obs.get("market") or {}).get("prices", {}) or {}
        wp = float(prices.get("WHEAT", 25) or 25)
        n_animals = count_animals(tiles)
        step = int(obs.get("step", 0) or 0)

        if day not in daily:
            daily[day] = {"money": money, "wheat": int(shed.get("WHEAT", 0) or 0),
                          "animals": n_animals}   # day-start snapshot (first step of day)
        else:
            daily[day]["wheat"] = int(shed.get("WHEAT", 0) or 0)
            daily[day]["animals"] = n_animals

        for o in (act.get("market") or []):
            if not isinstance(o, (list, tuple)) or len(o) < 3 or o[0] != "BUY_ANIMAL":
                continue
            atype, qty = o[1], int(o[2])
            cost = ANIMAL_COST.get(atype, 0) * qty
            cand_asc = 300 + max(wp, 25) * (n_animals + 1) * 0          # as-coded (feed_days=0)
            cand_px3 = 300 + max(wp, 25) * (n_animals + 1) * 3          # README-implied reference
            needed = _cash_needed_replica(act.get("market"), prices)
            # OBS IS POST-ACTION (probe-verified): a buy at step s already shows
            # in shed(s) -> exec signal = shed(s) - shed(s-1).
            exec_signal = 1 if prev_shed is None else (
                int(shed.get(atype, 0) or 0) - int(prev_shed.get(atype, 0) or 0))
            buys.append({
                "step": step, "day": day, "type": atype, "qty": qty,
                "money_before": money, "wheat_price": wp, "n_animals": n_animals,
                "cost": cost, "cand_reserve_ascoded": cand_asc,
                "cand_reserve_px3": cand_px3, "cash_needed": needed,
                "exec_shed_delta": exec_signal,
            })
        prev_shed = shed

    return {"seed": seed, "seat": seat_e,
            "bank_e": fin[e_idx]["observation"]["farms"][e_idx]["money"],
            "bank_o": fin[1 - e_idx]["observation"]["farms"][1 - e_idx]["money"],
            "win": int(fin[e_idx]["reward"] > fin[1 - e_idx]["reward"]),
            "buys": buys, "daily": {str(k): v for k, v in daily.items()}}


def run_one(args):
    return play_one(args[0], args[1])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="_audit_tmp/reserve_obs.jsonl")
    a = ap.parse_args()
    jobs = [(s, 0 if s % 2 == 0 else 1) for s in range(a.seed0, a.seed0 + a.n)]
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_one, jobs)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[rs] {i + 1}/{len(jobs)} 局")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} 局 -> {a.out}")


if __name__ == "__main__":
    main()
