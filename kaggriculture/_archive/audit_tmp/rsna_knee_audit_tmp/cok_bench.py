"""EXP-6 Phase-C: full-agent benchmark — COK V10 (repoC HEAD, agent L1599,
direct-compatible signature) vs pure v11E, paired fixed-RNG seeds 1-120,
alternating seats. Engine 1.32.7. No code modified on either side.
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


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


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
    if cok_left:
        bank_cok, bank_v = fin[0]["observation"]["farms"][0]["money"], fin[1]["observation"]["farms"][1]["money"]
    else:
        bank_v, bank_cok = fin[0]["observation"]["farms"][0]["money"], fin[1]["observation"]["farms"][1]["money"]
    rv = fin[0 if not cok_left else 1]["reward"]
    rc = fin[1 if not cok_left else 0]["reward"]
    return {"seed": seed, "cok_seat": 0 if cok_left else 1,
            "bank_v11e": bank_v, "bank_cok": bank_cok,
            "win_v11e": int(rv > rc), "win_cok": int(rc > rv), "tie": int(rv == rc)}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="_audit_tmp/cok_bench.jsonl")
    a = ap.parse_args()
    seeds = list(range(a.seed0, a.seed0 + a.n))
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(play_one, seeds)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[ck] {i + 1}/{len(seeds)} 局")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} 局 -> {a.out}")


if __name__ == "__main__":
    main()
