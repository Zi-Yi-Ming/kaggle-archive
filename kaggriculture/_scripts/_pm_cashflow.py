# -*- coding: utf-8 -*-
"""Cash-flow decomposition harness — RESEARCH ONLY, NOT production, NOT v14.

目的: 逐笔记录 engine 全部 money 变更, 实现 exact cash-flow reconciliation:
    initial(3000) + SELL - BUY_SEED - BUY_PRODUCT - BUY_ANIMAL - HIRE - BUY_LAND == final_money

方法(不修改任何生产/引擎文件, 进程内 monkeypatch):
  - import 与 KE 相同的 game 模块对象 (kaggle_environments.envs.kaggriculture.kaggriculture)
  - 包装 eng._process_market: 每步记录 step + farm-id->seat 映射
  - 包装 eng._commit_unit / eng._do_hire / eng._do_buy_land: 逐笔记录
    (op, item, price, qty=1, money_before, money_after, ok)
  - RNG 固定: make() 后覆写 env.info["seed"] (resolve_episode_seed 第一优先级;
    make() 会随机填充 env.info["seed"] 并把 configuration["seed"] 清成 None)

引擎 money 路径审计(1.32.7, 全部 7 处):
  L657 SELL  -> money += price      (_commit_unit)
  L669 BUY_PRODUCT -> money -= price (_commit_unit)
  L676 BUY_SEED -> money -= price   (_commit_unit)
  L684 BUY_ANIMAL -> money -= price (_commit_unit)
  L706 HIRE -> money -= cost        (_do_hire)
  L719 BUY_LAND -> money -= cost    (_do_buy_land)
  日终/动物/植物/草: 无 money 变更

输出: _pm_cashflow.jsonl — 每局一条 {seed, agent, opp, win, bank_m, bank_o, init,
      txs: [{step, seat, op, item, price, qty, before, after, ok}, ...]}

用法:
    python _pm_cashflow.py --n 100 --seed0 1 --opp closer_cleo --out _pm_cashflow.jsonl
"""
import os
import sys
import json
import time
import argparse
import importlib

os.environ.setdefault("NO_PROXY", "*")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import _pm_pool as P

# 与 KE 相同的模块对象 (KE: import_module(".envs.{name}.{name}", "kaggle_environments"))
eng = importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")

# ---------------- monkeypatch 状态 ----------------
_CUR = {"step": -1, "seat_of": {}}
TXS = []


def _log(step, seat, op, item, price, before, after, ok):
    TXS.append({
        "step": step, "seat": seat, "op": op, "item": item,
        "price": price, "qty": 1, "before": before, "after": after, "ok": ok,
    })


_orig_process_market = eng._process_market


def _wrap_process_market(state, env):
    obs0 = state[0].observation
    _CUR["step"] = int(obs0.step or 0)
    _CUR["seat_of"] = {id(f): i for i, f in enumerate(obs0.farms)}
    return _orig_process_market(state, env)


_orig_commit = eng._commit_unit


def _wrap_commit(op, item, price, farm, private, market, shed_capacity=100):
    seat = _CUR["seat_of"].get(id(farm), -1)
    before = farm["money"]
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    _log(_CUR["step"], seat, op, item, price, before, farm["money"], ok)
    return ok


_orig_hire = eng._do_hire


def _wrap_hire(farm, private, board_size, mult=None):
    seat = _CUR["seat_of"].get(id(farm), -1)
    before = farm["money"]
    if mult is None:
        _orig_hire(farm, private, board_size)
    else:
        _orig_hire(farm, private, board_size, mult)
    _log(_CUR["step"], seat, "HIRE", None, before - farm["money"], before, farm["money"], True)


_orig_land = eng._do_buy_land


def _wrap_land(farm, board_size):
    seat = _CUR["seat_of"].get(id(farm), -1)
    before = farm["money"]
    _orig_land(farm, board_size)
    _log(_CUR["step"], seat, "BUY_LAND", None, before - farm["money"], before, farm["money"], True)


def _patch():
    eng._process_market = _wrap_process_market
    eng._commit_unit = _wrap_commit
    eng._do_hire = _wrap_hire
    eng._do_buy_land = _wrap_land


def _unpatch():
    eng._process_market = _orig_process_market
    eng._commit_unit = _orig_commit
    eng._do_hire = _orig_hire
    eng._do_buy_land = _orig_land


def run_one(agent_key, opp_key, seed):
    """跑一局并逐笔记录 cash-flow。返回 (rec, txs)。"""
    global TXS
    from kaggle_environments import make
    agA = P.load_agent(agent_key)
    agB = P.load_agent(opp_key)
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed          # 固定 RNG (覆盖 make() 的随机值) — 已验证确定性
    TXS = []
    _CUR["step"] = -1
    _CUR["seat_of"] = {}
    env.run([a0, a1])

    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        bank_m, bank_o, win = b0, b1, (1 if b0 > b1 else (0 if b1 > b0 else "tie"))
    else:
        bank_m, bank_o, win = b1, b0, (1 if b1 > b0 else (0 if b0 > b1 else "tie"))
    rec = {
        "seed": seed, "agent": agent_key, "opp": opp_key,
        "seat_a_first": seat_a_first, "win": win,
        "bank_m": round(bank_m), "bank_o": round(bank_o),
        "init": 3000.0,
        "n_tx": len(TXS), "txs": TXS,
    }
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", type=str, default="v11E")
    ap.add_argument("--opp", type=str, default="closer_cleo")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--out", type=str, default="_pm_cashflow.jsonl")
    args = ap.parse_args()

    out = os.path.join(BASE, args.out)
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["seed"])
            except Exception:
                pass

    _patch()
    t0 = time.time()
    n_new = 0
    try:
        for seed in range(args.seed0, args.seed0 + args.n):
            if seed in done:
                continue
            rec = run_one(args.agent, args.opp, seed)
            with open(out, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
            n_new += 1
            if n_new % 10 == 0:
                print("[cashflow] %d 局 (%.0fs)" % (n_new, time.time() - t0), flush=True)
    finally:
        _unpatch()
    print("[cashflow] DONE 新跑=%d 总=%d -> %s (%.0fs)"
          % (n_new, len(done) + n_new, args.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
