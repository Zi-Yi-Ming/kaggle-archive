"""EXP-10B collection: V0 (production v11E) vs V1 (frozen SELL decision),
60 seeds x 2 seats x closer_cleo = 120 paired games per arm.

Gates: fingerprint unchanged, executed-ledger recon==0 per game,
deterministic double-run spot-check (4 games x 2 arms).
Output: _audit_tmp/exp10b/exp10b_results.json
"""
import hashlib
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "rsna_knee/_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make

OUT = "_audit_tmp/exp10b"
PROD_PATH = "kaggregator_main_prod.py"  # placeholder, overridden below
PROD_PATH = "kaggriculture/main.py"
PROD_MD5 = "224a1c47cf9b07624f5faabbb5227891"
V1_PATH = "_audit_tmp/exp10b/v11e_frozen_sell.py"

SEEDS = list(range(1, 61))
SEATS = (0, 1)


def _load(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.replace("/", "_").replace(".", "_"), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_one(args):
    arm, seed, seat, run_idx = args
    opp = P.load_agent("closer_cleo")
    cand = _load(PROD_PATH if arm == "V0" else V1_PATH)
    a, b = (cand, opp) if seat == 0 else (opp, cand)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    agg, valid, n, mism = EL.replay_game(steps, seat)
    final = steps[-1][seat]["observation"]["farms"][seat]["money"]
    rev = agg["SELL"][1]
    cost = sum(agg[t][1] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND"))
    recon = round(final - (EL.INITIAL_BANK + rev - cost), 4)
    # SELL-level metrics from executed ledger:
    # executed count/value vs issued count -> failure rate; first SELL step for timing.
    sell_exec = agg["SELL"][0]
    sell_rev = agg["SELL"][1]
    sell_issued = agg["issued"]["SELL"]
    first_sell_step = None
    for s in range(1, len(steps)):
        acts = steps[s][seat].get("action") or {}
        for m in (acts.get("market") or []):
            if isinstance(m, list) and m and m[0] == "SELL":
                first_sell_step = s
                break
        if first_sell_step is not None:
            break
    rec = {"arm": arm, "seed": seed, "seat": seat, "run": run_idx,
           "steps": len(steps), "valid": valid, "recon": recon,
           "bank": round(float(final), 2), "sell_rev": round(float(sell_rev), 2),
           "sell_exec": sell_exec, "sell_issued": sell_issued,
           "first_sell_step": first_sell_step}
    return rec


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("V0", "V1"), required=False)
    ap.add_argument("--seed-lo", type=int, default=1)
    ap.add_argument("--seed-hi", type=int, default=60)
    ap.add_argument("--out", default=None, help="partial results json (batch mode)")
    args = ap.parse_args()

    md5 = hashlib.md5(open(PROD_PATH, "rb").read()).hexdigest()
    assert md5 == PROD_MD5, f"fingerprint changed: {md5}"
    print("Gate D fingerprint OK:", md5[:8])

    if args.arm is None:
        # single-shot mode (small runs): deterministic double-run spot-check
        spot = [(a, s, seat, r) for a in ("V0", "V1") for s in (7, 23)
                for seat in (0, 1) for r in (0, 1)]
        with mp.Pool(8) as pool:
            rs = list(pool.imap_unordered(run_one, spot))
        by_cfg = {}
        for r in rs:
            by_cfg.setdefault((r["arm"], r["seed"], r["seat"]), []).append(r["bank"])
        det_ok = all(len(v) == 2 and abs(v[0] - v[1]) < 1e-9 for v in by_cfg.values())
        print("deterministic double-run spot-check (8 configs):", "PASS" if det_ok else "FAIL")
        return

    # batch mode: one arm, seed range
    tasks = [(args.arm, s, seat, 0) for s in range(args.seed_lo, args.seed_hi + 1)
             for seat in SEATS]
    with mp.Pool(8) as pool:
        res = list(pool.imap_unordered(run_one, tasks))
    res.sort(key=lambda r: (r["seed"], r["seat"]))
    bad = [r for r in res if r["steps"] != 720 or abs(r["recon"]) > 0.005]
    banks = [r["bank"] for r in res]
    print(f"{args.arm} seeds {args.seed_lo}-{args.seed_hi}: {len(res)} games | "
          f"gate failures {len(bad)} | mean bank {sum(banks)/max(1,len(banks)):.0f}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)
    print("batch DONE ->", args.out)


if __name__ == "__main__":
    main()
