# -*- coding: utf-8 -*-
"""Heterogeneous benchmark harness (TEMP, NOT production).

被测 agent: E / D / A(≈v10 rollback) / closer_cleo(≈v9 对标)
对手 pool: 社区高 tier(broker_bea/ledger_lena/slotter_silas/rancher_rita/
           melon_mateo/homestead_hana) + synthetic 4 类 + B/D(同族对照)

每 matchup 默认 50 局(seed 递增),交替 seat(奇 seed A-first,偶 seed opp-first),
Wilson CI + binomial p。结果追加写 CSV,断点续跑。

用法:
  python _pm_bench.py --agent E --opp broker_bea --n 50     # 单个
  python _pm_bench.py --agent E --all-opps --n 50           # E vs 全部对手
  python _pm_bench.py --agents E,D --all-opps --n 50        # 多被测
"""
import os
import sys
import time
import math
import uuid
import argparse
import importlib.util

os.environ.setdefault("NO_PROXY", "*")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))

import _pm_pool as P
import _pm_synth as S


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


AGENT_ALIAS = {  # CLI 短名 -> pool key
    "E": "v11E", "e": "v11E", "v11": "v11E", "v11e": "v11E",
    "v12": "v12", "D": "D", "d": "D", "B": "B", "b": "B",
    "A": "A", "a": "A",
    "v9": "closer_cleo", "cleo": "closer_cleo", "closer_cleo": "closer_cleo",
    "v7": "broker_bea", "bea": "broker_bea", "broker_bea": "broker_bea",
}


def _resolve_agent(key):
    return AGENT_ALIAS.get(key, key)


def run_matchup_task(task):
    """pool worker 任务:task=(agent_key, opp_key, seed)。返回 (ag,op,seed,win,ba,bb)。"""
    agent_key, opp_key, seed = task
    from kaggle_environments import make
    agA = P.load_agent(_resolve_agent(agent_key))
    agB = load_opp(opp_key, fresh=True)
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
        ba, bb = b0, b1
        win = 1 if b0 > b1 else (0 if b1 > b0 else "tie")
    else:
        ba, bb = b1, b0
        win = 1 if b1 > b0 else (0 if b0 > b1 else "tie")
    return agent_key, opp_key, seed, win, ba, bb


def run_matchup(agent_key, opp_key, seed):
    """单局(串行入口,供冒烟)。"""
    ag, op, sd, win, ba, bb = run_matchup_task((agent_key, opp_key, seed))
    return win, ba, bb


_OPP_CACHE = {}


def load_opp(key, fresh=False):
    """加载对手。fresh=True 时每局重载(避免模块级状态跨局泄漏)。"""
    if fresh or key not in _OPP_CACHE:
        if key in P.POOL:
            _OPP_CACHE[key] = P.load_agent(key)
        elif key in S.SYNTHETIC:
            _OPP_CACHE[key] = S.load_synthetic(key)
        else:
            raise KeyError(key)
    return _OPP_CACHE[key]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", type=str, default="E",
                    help="被测 agent 逗号分隔: E,D,A,closer_cleo")
    ap.add_argument("--opp", type=str, default="",
                    help="单个对手;与 --all-opps 互斥")
    ap.add_argument("--all-opps", action="store_true",
                    help="vs 全部 pool 对手")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=12,
                    help="并行进程数(24 核建议 12-16)")
    args = ap.parse_args()

    OPP_ORDER = ["broker_bea", "ledger_lena", "slotter_silas", "rancher_rita",
                 "melon_mateo", "homestead_hana", "closer_cleo",
                 "aggressive", "hoarder", "balanced", "delayed",
                 "B", "D"]
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    opps = [args.opp] if args.opp else (OPP_ORDER if args.all_opps else [])

    out = os.path.join(BASE, "_pm_bench.csv")
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            p = line.strip().split(",")
            if len(p) >= 3:
                done.add((p[0], p[1], int(p[2])))
    n_todo = 2 if args.smoke else args.n
    tasks = []
    for ag in agents:
        for op in opps:
            for seed in range(args.seed0, args.seed0 + n_todo):
                if (ag, op, seed) in done:
                    continue
                tasks.append((ag, op, seed))
    if not tasks:
        print("[bench] 无新任务(全部已完成)")
        return

    import multiprocessing as mp
    t0 = time.time()
    done_new = 0
    if args.smoke or args.workers <= 1:
        for task in tasks:
            ag, op, sd, win, ba, bb = run_matchup_task(task)
            with open(out, "a", encoding="utf-8") as f:
                f.write("%s,%s,%d,%s,%.2f,%.2f\n" % (ag, op, sd, win, ba, bb))
            done_new += 1
    else:
        with mp.Pool(args.workers) as pool:
            for ag, op, sd, win, ba, bb in pool.imap_unordered(
                    run_matchup_task, tasks, chunksize=4):
                with open(out, "a", encoding="utf-8") as f:
                    f.write("%s,%s,%d,%s,%.2f,%.2f\n" % (ag, op, sd, win, ba, bb))
                done_new += 1
                if done_new % 20 == 0:
                    print("[bench] 完成 %d/%d 局 (%.0fs)" % (done_new, len(tasks),
                                                             time.time() - t0), flush=True)
    print("[bench] DONE 新跑=%d 总时长=%.0fs" % (done_new, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
