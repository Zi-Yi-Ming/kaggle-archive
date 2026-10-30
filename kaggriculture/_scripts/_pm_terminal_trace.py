# -*- coding: utf-8 -*-
"""Terminal Conversion Postmortem trace (v14 research, TEMP, NOT production).

目标:回答 "E 输局是库存过多 / 卖太晚 / 卖错商品 / 价格不允许转换"。
对每局采集:
  - 540-720 逐步: 双方 cash / shed 各商品 / inventories 负载 / 田间 yield_units
    / 各商品市价 / 市场库存 / 双方当步 SELL 明细
  - 全局: 双方累计卖出(分商品)、首次"大单清算"时点(step>=600 且单步卖量>=10)
  - 局末分解: cash + shed 现值 + 田间未收现值(按局末价)

输出: _pm_terminal_trace.jsonl (每局一条)

用法:
    python _pm_terminal_trace.py --opp closer_cleo --n 16 --seed0 1
"""
import os
import sys
import json
import time
import argparse

os.environ.setdefault("NO_PROXY", "*")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))

import _pm_pool as P

SELLABLE = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
            "EGG", "MILK", "WOOL", "FERTILIZER"]


def _sell_events(action):
    out = []
    for o in (action or {}).get("market") or []:
        if isinstance(o, list) and o and o[0] == "SELL":
            out.append((o[1], int(o[2])))
    return out


def _yield_units(tiles):
    total = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict):
                total += int(t.get("yield_units", 0) or 0)
    return total


def _shed_list(shed):
    return [int((shed or {}).get(it, 0) or 0) for it in SELLABLE]


def _decomp(cash, shed, yield_units, prices):
    shed_val = sum(q * float(prices.get(it, 0) or 0) for it, q in zip(SELLABLE, shed))
    yield_val = yield_units  # 价值按 item 混合,粗略用均价后续在分析端算;这里只存原始
    return {"cash": cash, "shed_val": shed_val, "yield_units": yield_units}


def run_one(agent_key, opp_key, seed, snap_from=540):
    from kaggle_environments import make
    agA = P.load_agent(agent_key)
    agB = P.load_agent(opp_key)
    seat_a_first = (seed % 2 == 1)
    a0, a1 = (agA, agB) if seat_a_first else (agB, agA)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])

    my_seat = 0 if seat_a_first else 1
    opp_seat = 1 if seat_a_first else 0
    n = len(env.steps)
    cum_m = {it: 0 for it in SELLABLE}
    cum_o = {it: 0 for it in SELLABLE}
    first_big = {"m": None, "o": None}
    snap = []

    for i, s in enumerate(env.steps):
        obs_m = s[my_seat]["observation"]
        obs_o = s[opp_seat]["observation"]
        farm_m = obs_m["farms"][obs_m["player"]]
        farm_o = obs_o["farms"][obs_o["player"]]
        priv_m = obs_m.get("private") or {}
        priv_o = obs_o.get("private") or {}
        shed_m = _shed_list(priv_m.get("shed"))
        shed_o = _shed_list(priv_o.get("shed"))
        yield_m = _yield_units(farm_m.get("tiles"))
        yield_o = _yield_units(farm_o.get("tiles"))
        prices = ((obs_m.get("market") or {}).get("prices") or {})
        mkt = ((obs_m.get("market") or {}).get("inventory") or {})
        cash_m = float(farm_m.get("money", 0) or 0)
        cash_o = float(farm_o.get("money", 0) or 0)
        sells_m = _sell_events(s[my_seat].get("action"))
        sells_o = _sell_events(s[opp_seat].get("action"))
        for it, q in sells_m:
            cum_m[it] += q
        for it, q in sells_o:
            cum_o[it] += q
        if i >= 600:
            tot_m = sum(q for _, q in sells_m)
            tot_o = sum(q for _, q in sells_o)
            if first_big["m"] is None and tot_m >= 10:
                first_big["m"] = i
            if first_big["o"] is None and tot_o >= 10:
                first_big["o"] = i
        if i >= snap_from or i == n - 1:
            snap.append({
                "s": i,
                "cm": round(cash_m), "co": round(cash_o),
                "sm": shed_m, "so": shed_o,
                "ym": yield_m, "yo": yield_o,
                "pr": [float(prices.get(it, 0) or 0) for it in SELLABLE],
                "mk": [float(mkt.get(it, 10000) or 10000) for it in SELLABLE],
                "sel_m": sells_m, "sel_o": sells_o,
            })

    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    if seat_a_first:
        bank_mine, bank_opp = b0, b1
        win = 1 if b0 > b1 else (0 if b1 > b0 else "tie")
    else:
        bank_mine, bank_opp = b1, b0
        win = 1 if b1 > b0 else (0 if b0 > b1 else "tie")
    last = snap[-1]
    prices_final = [last["pr"][j] for j in range(len(SELLABLE))]
    shed_val_m = sum(q * p for q, p in zip(last["sm"], prices_final))
    shed_val_o = sum(q * p for q, p in zip(last["so"], prices_final))

    return {
        "seed": seed, "agent": agent_key, "opp": opp_key,
        "seat_a_first": seat_a_first, "win": win,
        "bank_mine": round(bank_mine), "bank_opp": round(bank_opp),
        "sellable": SELLABLE,
        "cum_m": cum_m, "cum_o": cum_o,
        "first_big": first_big,
        "hands_m": len(farm_m.get("hands") or []),
        "hands_o": len(farm_o.get("hands") or []),
        "snap": snap,
        "end": {
            "shed_val_m": round(shed_val_m), "shed_val_o": round(shed_val_o),
            "yield_m": last["ym"], "yield_o": last["yo"],
            "total_m": round(bank_mine + shed_val_m),
            "total_o": round(bank_opp + shed_val_o),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", type=str, default="v11E")
    ap.add_argument("--opp", type=str, default="closer_cleo")
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--snap-from", type=int, default=540)
    ap.add_argument("--out", type=str, default="_pm_terminal_trace.jsonl")
    args = ap.parse_args()

    out = os.path.join(BASE, args.out)
    t0 = time.time()
    for seed in range(args.seed0, args.seed0 + args.n):
        rec = run_one(args.agent, args.opp, seed, snap_from=args.snap_from)
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        if (seed - args.seed0 + 1) % 4 == 0:
            print("[term-trace] %d 局 (%.0fs)" % (seed - args.seed0 + 1, time.time() - t0), flush=True)
    print("[term-trace] DONE %d 局 -> %s (%.0fs)" % (args.n, args.out, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
