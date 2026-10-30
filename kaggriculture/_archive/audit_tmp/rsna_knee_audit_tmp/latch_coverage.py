"""EXP-2 Phase A extension — trigger coverage vs heterogeneous pool (RESEARCH ONLY).

Records public banks at step 577 (and the step-577 gap) for v11E vs each pool
opponent, fixed-RNG paired, seat alternation by seed parity. No agent changes.
"""
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

POOL = ["broker_bea", "slotter_silas", "ledger_lena", "melon_mateo", "rancher_rita"]


def load_v11e():
    import importlib.util
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def one(args):
    opp_name, seed = args
    agent = load_v11e()
    opp = P.load_agent(opp_name)
    seat_e = 0 if seed % 2 == 0 else 1
    a, b = (agent, opp) if seat_e == 0 else (opp, agent)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    s577 = steps[577][0]["observation"]
    bank_e = s577["farms"][seat_e]["money"]
    bank_o = s577["farms"][1 - seat_e]["money"]
    fin = steps[-1]
    return {
        "opp": opp_name, "seed": seed, "seat_e": seat_e,
        "b577_e": bank_e, "b577_o": bank_o, "gap577": bank_o - bank_e,
        "trigger": int(bank_o - bank_e <= -5000),
        "win": int(fin[seat_e]["reward"] > fin[1 - seat_e]["reward"]),
        "bankE": fin[seat_e]["observation"]["farms"][seat_e]["money"],
        "bankO": fin[1 - seat_e]["observation"]["farms"][1 - seat_e]["money"],
    }


def main():
    jobs = [(op, s) for op in POOL for s in range(1, 121)]
    recs = []
    with mp.Pool(12) as pool:
        for i, r in enumerate(pool.imap_unordered(one, jobs)):
            recs.append(r)
            if (i + 1) % 60 == 0:
                print(f"[cov] {i + 1}/{len(jobs)}")
    recs.sort(key=lambda r: (r["opp"], r["seed"]))
    with open("_audit_tmp/latch_coverage.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} -> _audit_tmp/latch_coverage.jsonl")


if __name__ == "__main__":
    main()
