"""EXP-9 Phase 4 benchmark runner: T0 (v11E production) vs T1 (tape 55425101
exact replay) × EXP-8 opponent pool, executed-ledger accounting hard gate.

Usage:
  python phase4_bench.py <candidate:T0|T1> <opponent> <seed_lo> <seed_hi> [--jobs N] [--out FILE]
Appends one JSON line per game with paired-relevant diagnostics.
"""
import argparse
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make

TAPE_PATH = "_audit_tmp/exp9/tape_55425101_91889284.json"
TAPE = None  # loaded per worker


def _load_tape():
    global TAPE
    if TAPE is None:
        with open(TAPE_PATH, encoding="utf-8") as f:
            TAPE = json.load(f)["steps"]
    return TAPE


class TapeAgent:
    def __init__(self, tape):
        self.tape = tape

    def __call__(self, obs, config=None):
        step = int(obs.get("step", 0) or 0)
        if step >= len(self.tape):
            return {"farmer": ["PASS"], "hands": [], "market": []}
        a = self.tape[step]
        return {"farmer": list(a.get("farmer") or ["PASS"]),
                "hands": [list(h) for h in (a.get("hands") or [])],
                "market": [list(m) for m in (a.get("market") or [])]}


def _load_prod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("prod", "kaggriculture/main.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_one(args):
    kind, opponent, seed = args
    seat = 0 if seed % 2 == 0 else 1
    opp = P.load_agent(opponent)
    if kind == "T0":
        cand = _load_prod()
    else:
        cand = TapeAgent(_load_tape())
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
    recon = final - (EL.INITIAL_BANK + rev - cost)
    iss = agg["issued"]
    exec_q = {t: agg[t][0] for t in ("SELL", "BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND")}
    return {"kind": kind, "seed": seed, "opponent": opponent, "seat": seat,
            "final_bank": round(final, 2), "recon": round(recon, 4),
            "valid": valid, "n": n,
            "issued_sell": iss["SELL"], "exec_sell": exec_q["SELL"],
            "issued_buy": sum(iss[t] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL")),
            "exec_buy": sum(exec_q[t] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL")),
            "exec_rev": round(rev, 2), "exec_cost": round(cost, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["T0", "T1"])
    ap.add_argument("opponent")
    ap.add_argument("seed_lo", type=int)
    ap.add_argument("seed_hi", type=int)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default="_audit_tmp/route_transfer/phase4_bench.jsonl")
    args = ap.parse_args()
    tasks = [(args.kind, args.opponent, s) for s in range(args.seed_lo, args.seed_hi + 1)]
    results = []
    with mp.Pool(args.jobs) as pool:
        for r in pool.imap_unordered(run_one, tasks):
            results.append(r)
    results.sort(key=lambda r: r["seed"])
    with open(args.out, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    bad = [r for r in results if abs(r["recon"]) > 0.005]
    print(f"{args.kind} x {args.opponent} seeds {args.seed_lo}-{args.seed_hi}: "
          f"{len(results)} games | recon!=0: {len(bad)}")


if __name__ == "__main__":
    main()
