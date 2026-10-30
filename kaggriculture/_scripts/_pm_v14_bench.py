# -*- coding: utf-8 -*-
"""V14 production bench — RESEARCH ONLY, NOT a submission.

加载已 patch 的 main.py (production V14 = v12 + Fix-A) 直跑 120 局,
复用 _pm_sellmech.py 的 engine 级 ledger monkeypatch (逐笔 money+slot 记录),
fixed-RNG: env.info["seed"] 覆写。

用法:
    python _pm_v14_bench.py --n 30 --seed0 1 --out _pm_v14.jsonl
"""
import os
import sys
import json
import time
import argparse
import importlib.util

os.environ.setdefault("NO_PROXY", "*")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import _pm_pool as P
import _pm_sellmech as SM


def load_prod():
    """每次调用返回全新 main.py 模块实例 (干净状态, 与 P.load_agent 同语义)."""
    spec = importlib.util.spec_from_file_location("v14_prod", os.path.join(BASE, "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_one(seed):
    from kaggle_environments import make
    agA = load_prod()
    agB = P.load_agent("closer_cleo")
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    SM.TXS.clear()
    SM._CUR["step"] = -1
    SM._CUR["seat_of"] = {}
    SM._CUR["orders"] = {}
    env.run([a0, a1])

    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        bank_m, bank_o, win = b0, b1, (1 if b0 > b1 else (0 if b1 > b0 else "tie"))
    else:
        bank_m, bank_o, win = b1, b0, (1 if b1 > b0 else (0 if b0 > b1 else "tie"))
    return {
        "seed": seed, "agent": "v14prod", "opp": "closer_cleo",
        "seat_a_first": seat_a_first, "win": win,
        "bank_m": round(bank_m), "bank_o": round(bank_o),
        "init": 3000.0, "n_tx": len(SM.TXS), "txs": list(SM.TXS),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--out", type=str, default="_pm_v14.jsonl")
    args = ap.parse_args()

    out = os.path.join(BASE, args.out)
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["seed"])
            except Exception:
                pass

    SM._patch()
    t0 = time.time()
    n_new = 0
    try:
        for seed in range(args.seed0, args.seed0 + args.n):
            if seed in done:
                continue
            rec = run_one(seed)
            with open(out, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            n_new += 1
            if n_new % 10 == 0:
                print("[v14] %d 局 (%.0fs)" % (n_new, time.time() - t0), flush=True)
    finally:
        SM._unpatch()
    print("[v14] DONE 新跑=%d 总=%d -> %s (%.0fs)"
          % (n_new, len(done) + n_new, args.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
