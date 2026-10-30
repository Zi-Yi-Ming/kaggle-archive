"""EXP-8 Phase 5 formal benchmark runner.

Usage:
  python phase5_bench.py <variant> <opponent> <seed_lo> <seed_hi> [--jobs N] [--out FILE]

Appends one JSON line per game:
  {variant, seed, opponent, seat, route, final_bank, recon, valid, n, first_mismatch}
Audits every game with the executed-ledger reconstruction (reconciliation must
be 0; the A5 gate is re-checked per game and reported, never tolerated).
"""
import argparse
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make

VARIANTS = {
    "V0": ("_audit_tmp/route_transfer/variants/v11e_base.py", "v0"),
    "V1": ("_audit_tmp/route_transfer/variants/v11e_multitape_fixed.py", "v1"),
    "V2": ("_audit_tmp/route_transfer/variants/v11e_multitape_router.py", "v2"),
}


def _load_variant(name):
    import importlib.util
    path, mod = VARIANTS[name]
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_one(args):
    variant, opponent, seed = args
    m = _load_variant(variant)
    opp = P.load_agent(opponent)
    seat = 0 if seed % 2 == 0 else 1
    a, b = (m.agent, opp) if seat == 0 else (opp, m.agent)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    agg, valid, n, mism = EL.replay_game(steps, seat)
    final = steps[-1][seat]["observation"]["farms"][seat]["money"]
    rev = agg["SELL"][1]
    cost = sum(agg[t][1] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND"))
    recon = final - (EL.INITIAL_BANK + rev - cost)
    route = "A"
    if variant == "V2":
        route = (m._LOCK.get(seat) or "A") if hasattr(m, "_LOCK") else "A"
    return {"variant": variant, "seed": seed, "opponent": opponent, "seat": seat,
            "route": route, "final_bank": round(final, 2), "recon": round(recon, 3),
            "valid": valid, "n": n, "first_mismatch": mism[0][0] if mism else None,
            "exec_sell": agg["SELL"][0], "exec_rev": round(agg["SELL"][1], 2),
            "exec_cost": round(cost, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=list(VARIANTS))
    ap.add_argument("opponent")
    ap.add_argument("seed_lo", type=int)
    ap.add_argument("seed_hi", type=int)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default="_audit_tmp/route_transfer/phase5_bench.jsonl")
    args = ap.parse_args()
    seeds = list(range(args.seed_lo, args.seed_hi + 1))
    tasks = [(args.variant, args.opponent, s) for s in seeds]
    results = []
    with mp.Pool(args.jobs) as pool:
        for r in pool.imap_unordered(run_one, tasks):
            results.append(r)
    results.sort(key=lambda r: r["seed"])
    with open(args.out, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    bad = [r for r in results if abs(r["recon"]) > 0.005]
    print(f"{args.variant} x {args.opponent} seeds {args.seed_lo}-{args.seed_hi}: "
          f"{len(results)} games, recon!=0: {len(bad)}, 校验<100%: "
          f"{sum(1 for r in results if r['valid'] != r['n'])}")
    for r in results[:3]:
        print(f"  seed {r['seed']}: bank {r['final_bank']:.0f} recon {r['recon']:+.2f} "
              f"route {r['route']} valid {r['valid']}/{r['n']}")


if __name__ == "__main__":
    main()
