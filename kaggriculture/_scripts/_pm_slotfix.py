# -*- coding: utf-8 -*-
"""Minimal Intervention Validation: terminal SELL slot-fix — RESEARCH ONLY.

唯一干预 (Fix-A, 用户规范):
  仅当 481 <= step <= 719:
    对 agent 已生成的 action["market"] 做 stable partition:
      [premium SELL orders(原相对顺序)] + [所有其他 orders(原相对顺序)]
  —— 只改变 SELL orders 的 slot 排列, 不改变订单集合本身
     (same products / quantities / block sizes / sell steps / non-SELL content).
  premium = STRAWBERRY, MILK, WOOL, MELON (诊断确认的 4 个溢价品).

固定不变项:
  - 不修改 cleo_v11_E_backup.py / _TRACE / farmer / hand / BUY / WHEAT / beam
  - 复用 _pm_sellmech.py 的 engine 级 ledger monkeypatch (逐笔 money+slot 记录)
  - fixed-RNG: make() 后覆写 env.info["seed"]

step 检测: obs["step"] 可能缺失(seat 1) → 回退 day*24+hour → 回退调用计数器。

用法:
    python _pm_slotfix.py --n 120 --seed0 1 --variant fixA --out _pm_slotfix.jsonl
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
import _pm_sellmech as SM   # 复用 ledger monkeypatch 机制 (_patch/_unpatch/TXS/_CUR)

V11_BACKUP = os.path.join(BASE, "cleo_v11_E_backup.py")
PREMIUM = {"STRAWBERRY", "MILK", "WOOL", "MELON"}
LO_WIN, HI_WIN = 481, 719


def _is_sell(o):
    return isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"


def _get_step(obs, counter):
    st = obs.get("step")
    if isinstance(st, int) and st is not None and st >= 0:
        return st
    day = obs.get("day")
    if day is not None:
        try:
            return int(day) * 24 + int(obs.get("hour", 0) or 0)
        except (TypeError, ValueError):
            pass
    return counter


def make_slotfix_agent(variant="fixA"):
    """载入 v11E 并包装实现终局 premium SELL 前移 (每次调用返回全新实例=干净状态)."""
    spec = importlib.util.spec_from_file_location("v11E_slotfix", V11_BACKUP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    base_agent = mod.agent
    counter = {"n": 0}

    def agent(obs, config=None):
        counter["n"] += 1
        try:
            act = base_agent(obs, config)
        except TypeError:
            act = base_agent(obs)
        if act is None:
            act = {"farmer": ["PASS"], "hands": [], "market": []}
        step = _get_step(obs, counter["n"])
        if not (LO_WIN <= step <= HI_WIN):
            return act
        mkt = act.get("market")
        if not isinstance(mkt, list) or not mkt:
            return act
        if variant == "fixA":
            premium = [o for o in mkt if _is_sell(o) and o[1] in PREMIUM]
            rest = [o for o in mkt if not (_is_sell(o) and o[1] in PREMIUM)]
            act["market"] = (premium + rest)[:10]
        return act

    return agent


def run_one(agent_key, opp_key, seed, variant):
    """跑一局并记录 ledger (复用 _pm_sellmech 的 monkeypatch)."""
    from kaggle_environments import make
    agA = make_slotfix_agent(variant) if variant != "none" else P.load_agent(agent_key)
    agB = P.load_agent(opp_key)
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed          # fixed-RNG
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
        "seed": seed, "agent": agent_key, "opp": opp_key, "variant": variant,
        "seat_a_first": seat_a_first, "win": win,
        "bank_m": round(bank_m), "bank_o": round(bank_o),
        "init": 3000.0, "n_tx": len(SM.TXS), "txs": list(SM.TXS),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", type=str, default="v11E")
    ap.add_argument("--opp", type=str, default="closer_cleo")
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--variant", type=str, default="fixA", choices=["none", "fixA"])
    ap.add_argument("--out", type=str, default="_pm_slotfix.jsonl")
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
            rec = run_one(args.agent, args.opp, seed, args.variant)
            with open(out, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            n_new += 1
            if n_new % 10 == 0:
                print("[slotfix] %s %d 局 (%.0fs)" % (args.variant, n_new, time.time() - t0), flush=True)
    finally:
        SM._unpatch()
    print("[slotfix] DONE %s 新跑=%d 总=%d -> %s (%.0fs)"
          % (args.variant, n_new, len(done) + n_new, args.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
