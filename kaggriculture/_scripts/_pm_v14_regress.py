# -*- coding: utf-8 -*-
"""V14 heterogeneous regression runner — RESEARCH ONLY.

baseline (v12) vs V14 (patched main.py), vs broker_bea / slotter_silas /
ledger_lena, 各 50 局, fixed-RNG (env.info["seed"], 与 _pm_bench 不同:
原 _pm_bench 只设 configuration["seed"] 无效 → 本 runner 显式覆写 env.info).

输出: _pm_v14_regress.csv (agent,opp,seed,win,bank_a,bank_b), 断点续跑。

用法:
    python _pm_v14_regress.py --agent v12 --opp broker_bea --n 50
    python _pm_v14_regress.py --agent v14 --opp broker_bea --n 50
"""
import os
import sys
import time
import argparse
import importlib.util

os.environ.setdefault("NO_PROXY", "*")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))

import _pm_pool as P


def load_prod():
    """patched main.py (production V14), 每次调用全新模块实例."""
    spec = importlib.util.spec_from_file_location("v14_prod", os.path.join(BASE, "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_agent(key, fresh=True):
    if key == "v15":
        return load_prod()           # patched main.py = production V15 (v11E + Fix-A)
    if key == "v11E":
        return P.load_agent("v11E")
    return P.load_agent(key)


def run_one(agent_key, opp_key, seed):
    from kaggle_environments import make
    agA = load_agent(agent_key)
    agB = P.load_agent(opp_key)
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed          # fixed-RNG
    env.run([a0, a1])
    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        ba, bb = b0, b1
        win = 1 if b0 > b1 else (0 if b1 > b0 else "tie")
    else:
        ba, bb = b1, b0
        win = 1 if b1 > b0 else (0 if b0 > b1 else "tie")
    return agent_key, opp_key, seed, win, ba, bb


def run_task(task):
    agent_key, opp_key, seed = task
    return run_one(agent_key, opp_key, seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", type=str, default="v15", choices=["v12", "v14", "v11E", "v15"])
    ap.add_argument("--opp", type=str, default="broker_bea")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed0", type=int, default=1)
    args = ap.parse_args()

    out = os.path.join(BASE, "_pm_v14_regress.csv")
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            p = line.strip().split(",")
            if len(p) >= 3:
                done.add((p[0], p[1], int(p[2])))
    tasks = [(args.agent, args.opp, s) for s in range(args.seed0, args.seed0 + args.n)
             if (args.agent, args.opp, s) not in done]
    if not tasks:
        print("[regress] 无新任务")
        return

    import multiprocessing as mp
    t0 = time.time()
    n_new = 0
    with mp.Pool(12) as pool:
        for ag, op, sd, win, ba, bb in pool.imap_unordered(run_task, tasks, chunksize=4):
            with open(out, "a", encoding="utf-8") as f:
                f.write("%s,%s,%d,%s,%.2f,%.2f\n" % (ag, op, sd, win, ba, bb))
            n_new += 1
            if n_new % 10 == 0:
                print("[regress] %s vs %s: %d/%d 局 (%.0fs)" % (args.agent, args.opp,
                                                               n_new, len(tasks),
                                                               time.time() - t0), flush=True)
    print("[regress] DONE %s vs %s 新跑=%d (%.0fs)" % (args.agent, args.opp, n_new,
                                                       time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
