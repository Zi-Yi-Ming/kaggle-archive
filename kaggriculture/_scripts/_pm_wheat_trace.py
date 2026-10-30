# -*- coding: utf-8 -*-
"""WHEAT over-selling 细粒度 trace 采集 (TEMP research, NOT production).

目标:回答 WHEAT overselling 是前中期 market damage 还是末期 liquidation。
对每局逐 step 记录我方(E)与对手的 WHEAT sell/库存/价格/市场压力,按 6 桶
(每 120 step)聚合输出 jsonl。

用法:
    python _pm_wheat_trace.py --opp closer_cleo --n 30 --seed0 1
"""
import os
import sys
import json
import time
import importlib.util

os.environ.setdefault("NO_PROXY", "*")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))

import _pm_pool as P


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _market_state(obs):
    """从 obs 读市场价格/库存/我方现金。"""
    mkt = obs.get("market") or {}
    prices = mkt.get("prices") or {}
    inv = mkt.get("inventory") or {}
    player = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    cash = float(farms[player].get("money", 0) or 0) if player < len(farms) else 0.0
    return prices, inv, cash


def _sell_events(action):
    """从 action 提取 market SELL 事件列表 [(item, qty)]。"""
    out = []
    for o in (action or {}).get("market") or []:
        if isinstance(o, list) and o and o[0] == "SELL":
            out.append((o[1], int(o[2])))
    return out


def run_one(agent_key, opp_key, seed):
    """跑一局并逐 step 采集 WHEAT 相关轨迹。"""
    from kaggle_environments import make
    agA = P.load_agent(agent_key)     # 我方
    agB = P.load_agent(opp_key)       # 对手
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])

    # 逐 step 回溯采集(agent 是 seat 0/1,我方位置按 seat_a_first 决定)
    my_seat = 0 if seat_a_first else 1
    opp_seat = 1 if seat_a_first else 0
    rec = {"seed": seed, "agent": agent_key, "opp": opp_key,
           "seat_a_first": seat_a_first,
           "steps": [],  # 每 10 step 采一个点,控制 jsonl 大小
           "my_sell_wheat_total": 0, "opp_sell_wheat_total": 0,
           "wheat_price_first": None, "wheat_price_min": 1e9, "wheat_price_end": None}
    my_cum = 0
    opp_cum = 0
    for i, s in enumerate(env.steps):
        obs_m = s[my_seat]["observation"]
        obs_o = s[opp_seat]["observation"]
        act_m = s[my_seat].get("action") or {}
        act_o = s[opp_seat].get("action") or {}
        pm, im, cash_m = _market_state(obs_m)
        po, io, _ = _market_state(obs_o)
        wp = float(pm.get("WHEAT", 50) or 50)
        if rec["wheat_price_first"] is None:
            rec["wheat_price_first"] = wp
        rec["wheat_price_min"] = min(rec["wheat_price_min"], wp)
        rec["wheat_price_end"] = wp
        m_sell_w = sum(q for it, q in _sell_events(act_m) if it == "WHEAT")
        o_sell_w = sum(q for it, q in _sell_events(act_o) if it == "WHEAT")
        my_cum += m_sell_w
        opp_cum += o_sell_w
        rec["my_sell_wheat_total"] = my_cum
        rec["opp_sell_wheat_total"] = opp_cum
        if i % 10 == 0 or i == 719:
            rec["steps"].append({
                "step": i, "wheat_price": wp,
                "mkt_inv_wheat": float(im.get("WHEAT", 10000) or 10000),
                "my_cum_sell": my_cum, "opp_cum_sell": opp_cum,
                "my_sell_delta": my_cum - opp_cum,
                "my_cash": cash_m})
    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        rec["bank_mine"], rec["bank_opp"] = b0, b1
        rec["win"] = 1 if b0 > b1 else (0 if b1 > b0 else "tie")
    else:
        rec["bank_mine"], rec["bank_opp"] = b1, b0
        rec["win"] = 1 if b1 > b0 else (0 if b0 > b1 else "tie")
    return rec


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", type=str, default="v11E")
    ap.add_argument("--opp", type=str, default="closer_cleo")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--out", type=str, default="_pm_wheat_trace.jsonl")
    args = ap.parse_args()

    out = os.path.join(BASE, args.out)
    t0 = time.time()
    n_done = 0
    for seed in range(args.seed0, args.seed0 + args.n):
        rec = run_one(args.agent, args.opp, seed)
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        n_done += 1
        if n_done % 5 == 0:
            print("[wheat-trace] %d 局 (%.0fs)" % (n_done, time.time() - t0), flush=True)
    print("[wheat-trace] DONE %d 局 → %s (%.0fs)" % (n_done, args.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
