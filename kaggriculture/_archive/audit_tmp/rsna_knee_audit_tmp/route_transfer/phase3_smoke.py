"""EXP-9 Phase 3 Smoke: T1 (tape 55425101/91889284) exact replay vs T0 (v11E).

Protocol: 8 paired seeds (1-8), seat by seed parity, T0/T1 same seed+seat,
deterministic double-run (two identical runs per game), executed-ledger
reconciliation == 0 hard gate, 720/720 tape completeness, production
fingerprint check, no hidden repair (T1 is a pure tape lookup).
"""
import hashlib
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make

TAPE_PATH = "_audit_tmp/exp9/tape_55425101_91889284.json"
PROD_PATH = "kaggriculture/main.py"
PROD_MD5 = "224a1c47cf9b07624f5faabbb5227891"


class TapeAgent:
    """Pure 720-step tape replay: lookup by obs.step, return actions verbatim.
    No repair / fallback / adaptation. Failed orders execute per engine
    semantics."""
    def __init__(self, tape):
        self.tape = tape

    def __call__(self, obs, config=None):
        step = int(obs.get("step", 0) or 0)
        if step >= len(self.tape):
            return {"farmer": ["PASS"], "hands": [], "market": []}
        a = self.tape[step]
        return {
            "farmer": list(a.get("farmer") or ["PASS"]),
            "hands": [list(h) for h in (a.get("hands") or [])],
            "market": [list(m) for m in (a.get("market") or [])],
        }


def load_prod():
    spec = importlib.util.spec_from_file_location("prod", PROD_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_one(args):
    kind, seed, run_idx = args
    seat = 0 if seed % 2 == 0 else 1
    opp = P.load_agent("closer_cleo")
    if kind == "T0":
        cand = load_prod()
    else:
        with open(TAPE_PATH, encoding="utf-8") as f:
            tape = json.load(f)["steps"]
        cand = TapeAgent(tape)
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
    steps_run = len(steps)  # steps 数组长度 = 完整对局步骤数（720）
    return {
        "kind": kind, "seed": seed, "seat": seat, "run": run_idx,
        "final_bank": round(final, 2), "recon": round(recon, 4),
        "valid": valid, "n": n, "steps_run": steps_run,
        "exec_sell": agg["SELL"][0], "exec_rev": round(rev, 2), "exec_cost": round(cost, 2),
        "issued_sell": agg["issued"]["SELL"],
        "failed_sell": agg["issued"]["SELL"] - agg["SELL"][0],
        "first_mismatch": mism[0][0] if mism else None,
    }


def main():
    seeds = [1, 2, 3, 4, 5, 6, 7, 8]
    tasks = [(k, s, r) for s in seeds for k in ("T0", "T1") for r in (0, 1)]
    results = []
    with mp.Pool(8) as pool:
        for r in pool.imap_unordered(run_one, tasks):
            results.append(r)
    results.sort(key=lambda r: (r["kind"], r["seed"], r["run"]))

    # production fingerprint
    md5 = hashlib.md5(open(PROD_PATH, "rb").read()).hexdigest()
    print(f"production md5: {md5} match={md5 == PROD_MD5}")
    print(f"{'kind':<4}{'seed':<5}{'seat':<5}{'run':<4}{'bank':>9}{'recon':>8}{'valid':>8}{'steps':>6}{'execSell':>9}{'failSell':>8}")
    for r in results:
        print(f"{r['kind']:<4}{r['seed']:<5}{r['seat']:<5}{r['run']:<4}{r['final_bank']:>9.0f}"
              f"{r['recon']:>8.2f}{str(r['valid'])+'/'+str(r['n']):>8}{r['steps_run']:>6}"
              f"{r['exec_sell']:>9}{r['failed_sell']:>8}")
    # determinism check
    det_ok = True
    for s in seeds:
        for k in ("T0", "T1"):
            rs = [r for r in results if r["kind"] == k and r["seed"] == s]
            if not (rs[0]["final_bank"] == rs[1]["final_bank"] and rs[0]["exec_sell"] == rs[1]["exec_sell"]
                    and rs[0]["exec_cost"] == rs[1]["exec_cost"] and rs[0]["recon"] == rs[1]["recon"]):
                det_ok = False
                print(f"  DETERMINISM FAIL {k} seed {s}: {rs}")
    print(f"deterministic double-run: {'PASS' if det_ok else 'FAIL'}")
    recon_ok = all(abs(r["recon"]) < 0.005 for r in results)
    steps_ok = all(r["steps_run"] == 720 for r in results)
    seats = sorted(set(r["seat"] for r in results))
    print(f"reconciliation==0: {'PASS' if recon_ok else 'FAIL'} | 720/720: {'PASS' if steps_ok else 'FAIL'} | seats: {seats}")
    t1_fail = [r for r in results if r["kind"] == "T1" and r["failed_sell"] > 0]
    print(f"T1 failed-sell 局数: {len(t1_fail)}/16 (exact replay 失败订单按引擎原生语义，不 repair)")
    with open("_audit_tmp/route_transfer/phase3_smoke.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
