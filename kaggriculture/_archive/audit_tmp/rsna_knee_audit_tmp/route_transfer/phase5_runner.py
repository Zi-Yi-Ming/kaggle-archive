"""EXP-8 Phase-5 benchmark runner (preregistered causal experiment).

V0/V1/V2 frozen from Phase 0-4 (reused directly). Paired fixed-RNG seeds
1-120 per (candidate, opponent); candidate seat alternates by seed parity
(even -> seat 0, odd -> seat 1), matching the historical convention.

Per game records the full field set (Phase-5 spec section 5) plus exact
reconciliation accounting (initial 3000 + SELL revenue - buy costs = final).

Pricing (engine 1.32.7): SELL/BUY_PRODUCT at the obs price of the order's
step (post-action obs -> the engine's intra-step fill price may differ by a
price tick; reconciliation reports the actual residual, never assumed zero).
"""
import importlib.util
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

RT = os.path.join("_audit_tmp", "route_transfer")
VARIANT_PATHS = {
    "v0": os.path.join(RT, "variants", "v11e_base.py"),
    "v1": os.path.join(RT, "variants", "v11e_multitape_fixed.py"),
    "v2": os.path.join(RT, "variants", "v11e_multitape_router.py"),
}
OPPONENTS = {
    "cleo": "closer_cleo", "broker": "broker_bea", "slotter": "slotter_silas",
    "ledger": "ledger_lena", "melon": "melon_mateo", "rancher": "rancher_rita",
}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
HIRE_COST = 120
LAND_COST = 4000
INITIAL_BANK = 3000.0
PRODUCTIVE = {"WATER", "PLANT", "HARVEST", "FERTILIZE", "FEED", "CARE",
              "COLLECT_FERTILIZER", "PLACE", "PICKUP", "DROP"}


def load_variant(path):
    spec = importlib.util.spec_from_file_location("p5_" + os.path.basename(path), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sell_costs(order, prices):
    """(revenue, cost, unit) contribution of one market order at its step's obs prices."""
    if not isinstance(order, (list, tuple)) or len(order) < 3:
        return 0.0, 0.0, 0
    op, item, qty = order[0], order[1], int(order[2])
    px = float(prices.get(item, 0) or 0)
    if op == "SELL":
        return px * qty, 0.0, qty
    if op == "BUY_SEED":
        return 0.0, SEED_COST.get(item, 0) * qty, 0
    if op == "BUY_ANIMAL":
        return 0.0, ANIMAL_COST.get(item, 0) * qty, 0
    if op == "BUY_PRODUCT":
        return 0.0, px * qty, 0
    if op == "HIRE":
        return 0.0, HIRE_COST * qty, 0
    if op == "BUY_LAND":
        return 0.0, LAND_COST * qty, 0
    return 0.0, 0.0, 0


def play_one(args):
    seed, cand_name, opp_key = args
    mod = load_variant(VARIANT_PATHS[cand_name])
    cand = mod.agent
    opp = P.load_agent(OPPONENTS[opp_key])
    seat = 0 if seed % 2 == 0 else 1  # candidate seat (historical parity convention)
    a, b = (cand, opp) if seat == 0 else (opp, cand)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    fin = steps[-1]

    # per-seat accumulators
    rev = {0: 0.0, 1: 0.0}
    cost = {0: 0.0, 1: 0.0}
    sell_u = {0: 0, 1: 0}
    n_sell = {0: 0, 1: 0}
    n_buy = {0: 0, 1: 0}
    n_market = {0: 0, 1: 0}
    prod = {0: {}, 1: {}}
    day_bank = {0: {}, 1: {}}
    first_sig_step, route_sig = None, None

    for st in steps:
        for s in range(2):
            obs = st[s].get("observation") or {}
            act = st[s].get("action") or {}
            day = int(obs.get("day", 0) or 0)
            farms = obs.get("farms") or []
            farm = farms[s] if len(farms) == 2 else None
            if day not in day_bank[s] and farm is not None:
                day_bank[s][day] = float(farm.get("money", 0) or 0)
            prices = (obs.get("market") or {}).get("prices", {}) or {}
            for o in (act.get("market") or []):
                n_market[s] += 1
                r, c, u = sell_costs(o, prices)
                rev[s] += r
                cost[s] += c
                if isinstance(o, (list, tuple)) and o:
                    if o[0] == "SELL":
                        sell_u[s] += u
                        n_sell[s] += 1
                    elif o[0].startswith("BUY"):
                        n_buy[s] += 1
            for ua in ([act.get("farmer", ["PASS"])] + list(act.get("hands") or [])):
                if isinstance(ua, (list, tuple)) and ua and ua[0] in PRODUCTIVE:
                    prod[s][ua[0]] = prod[s].get(ua[0], 0) + 1
        # route audit for the candidate seat (V2: first non-empty signature step)
        if first_sig_step is None:
            obs0 = st[seat].get("observation") or {}
            sh = (obs0.get("town") or {}).get("unlocked_shops") or ()
            if isinstance(sh, (list, tuple)) and len(sh) > 0:
                first_sig_step = int(obs0.get("step", 0) or 0)
                route_sig = tuple(sorted(str(x) for x in sh))

    bank = {s: fin[s]["observation"]["farms"][s]["money"] for s in range(2)}
    rc = fin[seat]["reward"]
    ro = fin[1 - seat]["reward"]
    selected_route = "A"
    if cand_name == "v2":
        selected_route = (mod._LOCK.get(seat) or "A") if hasattr(mod, "_LOCK") else "A"
    elif cand_name == "v1":
        selected_route = "A"

    # exact reconciliation (candidate seat)
    computed = INITIAL_BANK + rev[seat] - cost[seat]
    recon_err = bank[seat] - computed

    return {
        "seed": seed, "candidate": cand_name, "opponent": opp_key, "candidate_seat": seat,
        "final_bank_candidate": bank[seat], "final_bank_opponent": bank[1 - seat],
        "bank_delta": bank[seat] - bank[1 - seat],
        "winner": "candidate" if rc > ro else ("opponent" if ro > rc else "draw"),
        "selected_route": selected_route, "first_sig_step": first_sig_step,
        "route_signature": route_sig,
        "per_day_bank": {str(k): v for k, v in day_bank[seat].items()},
        "per_day_bank_opp": {str(k): v for k, v in day_bank[1 - seat].items()},
        "sell_revenue_candidate": rev[seat], "sell_revenue_opponent": rev[1 - seat],
        "total_cost_candidate": cost[seat], "total_cost_opponent": cost[1 - seat],
        "sell_units_candidate": sell_u[seat],
        "production_actions": prod[seat], "market_actions": n_market[seat],
        "buy_actions": n_buy[seat], "sell_actions": n_sell[seat],
        "realization_price": (rev[seat] / sell_u[seat]) if sell_u[seat] else 0.0,
        "reconciliation_error": recon_err,
        "initial_bank": INITIAL_BANK,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, choices=list(VARIANT_PATHS))
    ap.add_argument("--opponent", required=True, choices=list(OPPONENTS))
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = [(s, a.candidate, a.opponent) for s in range(a.seed0, a.seed0 + a.n)]
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(play_one, jobs)):
            recs.append(r)
            if (i + 1) % 20 == 0:
                print(f"[p5] {a.candidate}/{a.opponent}: {i + 1}/{len(jobs)}")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {a.candidate}/{a.opponent} -> {a.out}")


if __name__ == "__main__":
    main()
