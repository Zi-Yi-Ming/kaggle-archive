# -*- coding: utf-8 -*-
"""E-mode failure trace collector (TEMP analysis tool, NOT production).

从 env.steps 逐帧提取 E vs B 对局的 opponent/market/policy/temporal 特征。
通过"内存 wrap"(只改加载后的模块实例属性,不碰 cleo_v10.py 源文件)采集:
  - _v11_beam_order 调用: 输入顺序 vs 输出顺序是否变化(beam changed decision)
  - _OPP.expected_opponent_market_sell: 每步预测值(用于 belief 校准)

输出: _pm_trace_<mode>.jsonl   每行一个 episode 的聚合特征 dict。
"""
import os
import sys
import json
import time
import uuid
import argparse
import importlib.util

os.environ.setdefault("NO_PROXY", "*")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleo_v10.py")

FLAGS = {
    "E": dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
              _V11_MARKET_MODEL=True, _V11_BELIEF=True,
              _V11_HAZARD=True, _V11_SEQUENTIAL=True),
    "B": dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
              _V11_MARKET_MODEL=True, _V11_BELIEF=False,
              _V11_HAZARD=False, _V11_SEQUENTIAL=False),
    "D": dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
              _V11_MARKET_MODEL=True, _V11_BELIEF=True,
              _V11_HAZARD=True, _V11_SEQUENTIAL=False),
}

# 阶段分桶 (steps)
BUCKETS = [(0, 120), (121, 240), (241, 360), (361, 480), (481, 600), (601, 720)]
ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]


def load_mod(flags, ep_id):
    name = "cleo_%s_%s" % (flags.get("_V11_SEQUENTIAL"), ep_id)
    spec = importlib.util.spec_from_file_location(name, SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k, v in flags.items():
        setattr(mod, k, v)
    return mod


def _sell_orders(action):
    """从 action.market 提取 SELL 订单 [(item, qty), ...]"""
    out = []
    for o in (action or {}).get("market") or []:
        if isinstance(o, list) and o and o[0] == "SELL" and len(o) >= 3:
            try:
                out.append((o[1], int(o[2])))
            except (TypeError, ValueError):
                pass
    return out


def _buy_orders(action):
    out = []
    for o in (action or {}).get("market") or []:
        if isinstance(o, list) and o and o[0] == "BUY_SEED" and len(o) >= 3:
            try:
                out.append((o[1], int(o[2])))
            except (TypeError, ValueError):
                pass
    return out


def trace_episode(seed, mode, ep_id):
    """跑一局并返回聚合特征 dict。seat 交替: seed 奇 E 先手, 偶 E 后手。"""
    from kaggle_environments import make
    modE = load_mod(FLAGS["E"], ep_id + "_E")
    modO = load_mod(FLAGS[mode[1]], ep_id + "_O")  # mode='EB'/'ED' -> O=B/D
    seat_e_first = (seed % 2 == 1)
    a0, a1 = (modE.agent, modO.agent) if seat_e_first else (modO.agent, modE.agent)

    # --- 内存 wrap: beam 调用统计(E 模块实例) ---
    stats = {"beam_calls": 0, "beam_changed": 0, "beam_same": 0,
             "beam_orders_in": 0, "pred_events": []}
    orig_beam = modE._v11_beam_order
    def wrapped_beam(orders, obs, money, short):
        stats["beam_calls"] += 1
        stats["beam_orders_in"] += len(orders)
        out = orig_beam(orders, obs, money, short)
        if [id(o) for o in out] != [id(o) for o in orders]:
            stats["beam_changed"] += 1
        else:
            stats["beam_same"] += 1
        return out
    modE._v11_beam_order = wrapped_beam

    # --- 内存 wrap: belief 预测(E 模块) ---
    # 模块全局 _LAST_STEP 由 agent 每步更新,wrap 里直接读它拿当前 step
    orig_pred = modE._OPP.expected_opponent_market_sell
    def wrapped_pred(item, steps_ahead):
        v = orig_pred(item, steps_ahead)
        stats["pred_events"].append((modE._LAST_STEP, item, steps_ahead, v))
        return v
    modE._OPP.expected_opponent_market_sell = wrapped_pred

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])

    steps = env.steps
    # E 所在 seat 与 O 所在 seat
    es, os_ = (0, 1) if seat_e_first else (1, 0)
    feats = {"seed": seed, "mode": mode, "seat_e": es,
             "beam_calls": stats["beam_calls"],
             "beam_changed": stats["beam_changed"],
             "beam_same": stats["beam_same"]}

    # 逐帧扫描
    my_sell = []          # (step, item, qty)
    opp_sell = []         # (step, item, qty)
    my_buy = []
    cash_e = []
    cash_o = []
    opp_first_sell = {}
    per_bucket = {b: {"e_sell": 0, "o_sell": 0, "e_cash": [], "o_cash": []}
                  for b in range(6)}
    price_min = {}; price_end = {}
    inv_min = {}
    floor_hits = {}
    shed_e = []
    for i, s in enumerate(steps):
        oE = s[es]["observation"]
        oO = s[os_]["observation"]
        st = i
        # cash
        ce = oE["farms"][es]["money"]; co = oE["farms"][os_]["money"]
        cash_e.append(ce); cash_o.append(co)
        # sells/buys from actions
        aE = s[es].get("action") or {}
        aO = s[os_].get("action") or {}
        for item, qty in _sell_orders(aE):
            my_sell.append((st, item, qty))
        for item, qty in _sell_orders(aO):
            opp_sell.append((st, item, qty))
        for item, qty in _buy_orders(aE):
            my_buy.append((st, item, qty))
        # market
        mkt = oE["market"] or {}
        inv = mkt.get("inventory") or {}
        prc = mkt.get("prices") or {}
        for it in ITEMS:
            iv = inv.get(it, 10000); pv = prc.get(it, 0)
            inv_min[it] = min(inv_min.get(it, 1e9), iv)
            if pv == 1.0 or pv <= 2:
                floor_hits[it] = floor_hits.get(it, 0) + 1
            if i >= 700:
                price_end[it] = pv
        # bucket
        bidx = min(5, st // 121)
        per_bucket[bidx]["e_sell"] += len(_sell_orders(aE))
        per_bucket[bidx]["o_sell"] += len(_sell_orders(aO))
        per_bucket[bidx]["e_cash"].append(ce)
        per_bucket[bidx]["o_cash"].append(co)
    # opp first sell step per item
    for st, item, qty in opp_sell:
        if item not in opp_first_sell:
            opp_first_sell[item] = st
    # E first sell step & aggregates
    e_first_sell = my_sell[0][0] if my_sell else None
    o_first_any = min(opp_first_sell.values()) if opp_first_sell else None
    feats.update({
        "win_e": 1 if cash_e[-1] > cash_o[-1] else (0 if cash_o[-1] > cash_e[-1] else "tie"),
        "cash_e_end": cash_e[-1], "cash_o_end": cash_o[-1],
        "bank_diff": cash_e[-1] - cash_o[-1],
        "my_n_sell": len(my_sell), "opp_n_sell": len(opp_sell),
        "my_n_buy": len(my_buy),
        "e_first_sell_step": e_first_sell, "o_first_sell_step": o_first_any,
        "opp_sell_by_item": {it: sum(q for _, j, q in opp_sell if j == it)
                             for it in ITEMS},
        "my_sell_by_item": {it: sum(q for _, j, q in my_sell if j == it)
                            for it in ITEMS},
        "opp_first_sell_by_item": opp_first_sell,
        "cash_e_min": min(cash_e), "cash_e_max": max(cash_e),
        "cash_o_min": min(cash_o), "cash_o_max": max(cash_o),
        "price_end": price_end, "inv_min": inv_min, "floor_hits": floor_hits,
        "bucket_e_sell": [per_bucket[b]["e_sell"] for b in range(6)],
        "bucket_o_sell": [per_bucket[b]["o_sell"] for b in range(6)],
        "bucket_e_cash_avg": [round(sum(per_bucket[b]["e_cash"]) / max(1, len(per_bucket[b]["e_cash"])))
                              for b in range(6)],
        "bucket_o_cash_avg": [round(sum(per_bucket[b]["o_cash"]) / max(1, len(per_bucket[b]["o_cash"])))
                              for b in range(6)],
    })
    # beam per-sell-order outcome: 若 beam 改变且此局输/赢, 记录在聚合层即可
    return feats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["EB", "ED"], default="EB")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_pm_trace_%s.jsonl" % args.mode)
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                j = json.loads(line)
                done.add(int(j["seed"]))
            except Exception:
                pass
    n = 2 if args.smoke else args.n
    need = [s for s in range(args.seed0, args.seed0 + n) if s not in done]
    print("[trace] mode=%s 待跑=%d (seed %d..%d)" % (args.mode, len(need),
          args.seed0, args.seed0 + n - 1), flush=True)
    t0 = time.time()
    for i, seed in enumerate(need):
        ep_id = uuid.uuid4().hex[:6]
        feats = trace_episode(seed, args.mode, ep_id)
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(feats, ensure_ascii=False) + "\n")
        if (i + 1) % 10 == 0 or i == len(need) - 1:
            dt = time.time() - t0
            print("[trace] %d/%d seed=%d win_e=%s %.0fs"
                  % (i + 1, len(need), seed, feats["win_e"], dt), flush=True)
    print("[trace] DONE 新跑=%d 累计=%d" % (len(need), len(done) + len(need)), flush=True)


if __name__ == "__main__":
    main()
