# -*- coding: utf-8 -*-
"""WHEAT control A/B/C + sensitivity matchup harness (TEMP research).

Matchups:
  A:  v11E                  vs closer_cleo   (baseline, 已有 Kaggle 50 局可复用)
  B:  v11E+WHEAT-control    vs closer_cleo   (intervention, level 可选 mild/medium)
  C:  v11E+WHEAT-control    vs v11E          (regression check)
  S:  sensitivity: none/mild/medium vs closer_cleo

输出: _pm_wheat_match.csv (matchup,agent,level,opp,seed,win,bank_a,bank_b)
断点续跑: 已存在的 (agent,level,opp,seed) 跳过。

用法:
    python _pm_wheat_match.py --matchup A --n 50 --seed0 51
    python _pm_wheat_match.py --matchup B --level mild --n 100
    python _pm_wheat_match.py --matchup C --level mild --n 100
    python _pm_wheat_match.py --sensitivity --n 100   # none/mild/medium × closer_cleo
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
import _pm_wheat_control as WC

CSV = os.path.join(BASE, "_pm_wheat_match.csv")


def _load_plain(key):
    return P.load_agent(key)


def _load_agent(agent_spec):
    """agent_spec: 'v11E' 或 'v11E+mild' / 'v11E+medium'。"""
    if "+" in agent_spec:
        base, level = agent_spec.split("+", 1)
        if base == "v11E":
            return WC.make_wheat_controlled("v11E", level)
    return _load_plain(agent_spec)


def run_one(a_spec, b_spec, seed):
    from kaggle_environments import make
    agA = _load_agent(a_spec)
    agB = _load_agent(b_spec)
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        win = 1 if b0 > b1 else (0 if b1 > b0 else "tie")
        ba, bb = b0, b1
    else:
        win = 1 if b1 > b0 else (0 if b0 > b1 else "tie")
        ba, bb = b1, b0
    return win, ba, bb


def _done():
    done = set()
    if os.path.exists(CSV):
        for line in open(CSV, encoding="utf-8"):
            p = line.strip().split(",")
            if len(p) >= 5:
                done.add((p[1], p[2], p[3], int(p[4])))  # agent,level,opp,seed
    return done


def _append(agent, level, opp, seed, win, ba, bb):
    with open(CSV, "a", encoding="utf-8") as f:
        f.write("%s,%s,%s,%d,%s,%.2f,%.2f\n" % (agent, level, opp, seed, win, ba, bb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matchup", type=str, default="", choices=["A", "B", "C", ""])
    ap.add_argument("--level", type=str, default="mild", choices=["none", "mild", "medium"])
    ap.add_argument("--sensitivity", action="store_true")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed0", type=int, default=1)
    args = ap.parse_args()

    # 任务 → [(agent_spec_a, agent_spec_b, level)]
    jobs = []
    if args.sensitivity:
        for level in ["none", "mild", "medium"]:
            jobs.append(("v11E+%s" % level, "closer_cleo", level))
    elif args.matchup == "A":
        jobs.append(("v11E", "closer_cleo", "none"))
    elif args.matchup == "B":
        jobs.append(("v11E+%s" % args.level, "closer_cleo", args.level))
    elif args.matchup == "C":
        jobs.append(("v11E+%s" % args.level, "v11E", args.level))

    done = _done()
    t0 = time.time()
    n_new = 0
    for a_spec, b_spec, level in jobs:
        for seed in range(args.seed0, args.seed0 + args.n):
            if (a_spec, level, b_spec, seed) in done:
                continue
            win, ba, bb = run_one(a_spec, b_spec, seed)
            _append(a_spec, level, b_spec, seed, win, ba, bb)
            n_new += 1
            if n_new % 10 == 0:
                print("[wheat-match] %d 局 (%.0fs)" % (n_new, time.time() - t0), flush=True)
    print("[wheat-match] DONE 新跑=%d (%.0fs)" % (n_new, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
