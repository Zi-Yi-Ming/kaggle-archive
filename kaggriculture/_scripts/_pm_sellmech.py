# -*- coding: utf-8 -*-
"""Sell-mechanism pooled dataset harness — RESEARCH ONLY, NOT production, NOT v14.

目的: 为终局 -0.99/unit 卖出实现差定位具体机制 (block size / slot / timing)。
在 _pm_cashflow.py 已验证的 engine 级逐笔 ledger 基础上, 增加订单级元数据:

对每一笔 commit (每单位一条) 记录:
  {seed, seat, step, op, item, price, qty=1, before, after, ok,
   slot            = market 列表中的订单位置 (0..9)
   unit_idx        = 该订单内已执行单位序号 (0-based, 仅成功单位递增)
   block_decl      = 订单声明的总数量 (意图块大小, 含可能失败的尾部)
   mkt_inv         = 该商品步初市场库存}

保留 cash-flow 完整性: initial + SELL - 全部cost == final_money 仍可 exact 对平。

方法: 同 _pm_cashflow.py — monkeypatch kaggle_environments.envs.kaggriculture.kaggliculture
  (实际包名 kaggriculture) 的 _process_market/_commit_unit/_do_hire/_do_buy_land;
  RNG 固定: make() 后覆写 env.info["seed"] (已验证跨进程确定)。

引擎 market 订单语义 (1.32.7, _process_market):
  action["market"] 最多 10 单; HIRE/BUY_LAND 原子处理(一次); SELL/BUY_SEED/BUY_PRODUCT/
  BUY_ANIMAL 逐单位 lockstep; 失败单位不推进库存/价格阶梯, 且该订单被 abort。

用法:
    python _pm_sellmech.py --n 120 --seed0 1 --out _pm_sellmech.jsonl
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

eng = importlib.import_module("kaggle_environments.envs.kaggriculture.kaggriculture")

_CUR = {"step": -1, "seat_of": {}, "orders": {}}   # orders[seat] = [{slot,op,item,qty,rem}]
TXS = []


def _log(t):
    TXS.append(t)


def _parse_orders(action):
    """镜像引擎 _process_market 的队列解析: (slot, op, item, qty)."""
    out = []
    m = (action or {}).get("market") if isinstance(action, dict) else []
    if not isinstance(m, list):
        return out
    for slot, o in enumerate(m[:10]):
        if not isinstance(o, list) or not o:
            continue
        op = o[0]
        if op == "HIRE":
            out.append({"slot": slot, "op": op, "item": None, "qty": 1, "rem": 1})
        elif op == "BUY_LAND":
            out.append({"slot": slot, "op": op, "item": None, "qty": 1, "rem": 1})
        elif len(o) >= 3:
            try:
                qty = max(1, int(o[2]))
            except (TypeError, ValueError):
                qty = 1
            out.append({"slot": slot, "op": op, "item": o[1], "qty": qty, "rem": qty})
        else:
            out.append({"slot": slot, "op": op, "item": None, "qty": 1, "rem": 1})
    return out


def _find_order(seat, op, item):
    """找第一个未消费的匹配订单 (slot 顺序); 返回订单或 None."""
    for ord_ in _CUR["orders"].get(seat, []):
        if ord_["rem"] > 0 and ord_["op"] == op and ord_["item"] == item:
            return ord_
    return None


_orig_process_market = eng._process_market


def _wrap_process_market(state, env):
    obs0 = state[0].observation
    _CUR["step"] = int(obs0.step or 0)
    _CUR["seat_of"] = {id(f): i for i, f in enumerate(obs0.farms)}
    _CUR["orders"] = {}
    for i, s in enumerate(state):
        _CUR["orders"][i] = _parse_orders(s.action)
    return _orig_process_market(state, env)


_orig_commit = eng._commit_unit


def _wrap_commit(op, item, price, farm, private, market, shed_capacity=100):
    seat = _CUR["seat_of"].get(id(farm), -1)
    before = farm["money"]
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    rec = {"step": _CUR["step"], "seat": seat, "op": op, "item": item,
           "price": price, "qty": 1, "before": before, "after": farm["money"],
           "ok": ok, "slot": None, "unit_idx": None, "block_decl": None,
           "mkt_inv": float((market.get("inventory") or {}).get(item, 10000) or 10000)}
    ord_ = _find_order(seat, op, item)
    if ord_ is not None:
        rec["slot"] = ord_["slot"]
        rec["block_decl"] = ord_["qty"]
        if ok:
            ord_["rem"] -= 1
            rec["unit_idx"] = ord_["qty"] - ord_["rem"] - 1
            if ord_["rem"] <= 0:
                ord_["rem"] = 0
        else:
            ord_["rem"] = 0  # 失败即 abort
    _log(rec)
    return ok


_orig_hire = eng._do_hire


def _wrap_hire(farm, private, board_size, mult=None):
    seat = _CUR["seat_of"].get(id(farm), -1)
    before = farm["money"]
    if mult is None:
        _orig_hire(farm, private, board_size)
    else:
        _orig_hire(farm, private, board_size, mult)
    rec = {"step": _CUR["step"], "seat": seat, "op": "HIRE", "item": None,
           "price": before - farm["money"], "qty": 1, "before": before,
           "after": farm["money"], "ok": True, "slot": None, "unit_idx": None,
           "block_decl": None, "mkt_inv": None}
    ord_ = _find_order(seat, "HIRE", None)
    if ord_ is not None:
        rec["slot"] = ord_["slot"]; rec["block_decl"] = 1; ord_["rem"] = 0
    _log(rec)


_orig_land = eng._do_buy_land


def _wrap_land(farm, board_size):
    seat = _CUR["seat_of"].get(id(farm), -1)
    before = farm["money"]
    _orig_land(farm, board_size)
    rec = {"step": _CUR["step"], "seat": seat, "op": "BUY_LAND", "item": None,
           "price": before - farm["money"], "qty": 1, "before": before,
           "after": farm["money"], "ok": True, "slot": None, "unit_idx": None,
           "block_decl": None, "mkt_inv": None}
    ord_ = _find_order(seat, "BUY_LAND", None)
    if ord_ is not None:
        rec["slot"] = ord_["slot"]; rec["block_decl"] = 1; ord_["rem"] = 0
    _log(rec)


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
    global TXS
    from kaggle_environments import make
    agA = P.load_agent(agent_key)
    agB = P.load_agent(opp_key)
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed          # fixed-RNG
    TXS = []
    _CUR["step"] = -1
    _CUR["seat_of"] = {}
    _CUR["orders"] = {}
    env.run([a0, a1])

    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        bank_m, bank_o, win = b0, b1, (1 if b0 > b1 else (0 if b1 > b0 else "tie"))
    else:
        bank_m, bank_o, win = b1, b0, (1 if b1 > b0 else (0 if b0 > b1 else "tie"))
    return {
        "seed": seed, "agent": agent_key, "opp": opp_key,
        "seat_a_first": seat_a_first, "win": win,
        "bank_m": round(bank_m), "bank_o": round(bank_o),
        "init": 3000.0, "n_tx": len(TXS), "txs": TXS,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", type=str, default="v11E")
    ap.add_argument("--opp", type=str, default="closer_cleo")
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--out", type=str, default="_pm_sellmech.jsonl")
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
                print("[sellmech] %d 局 (%.0fs)" % (n_new, time.time() - t0), flush=True)
    finally:
        _unpatch()
    print("[sellmech] DONE 新跑=%d 总=%d -> %s (%.0fs)"
          % (n_new, len(done) + n_new, args.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
