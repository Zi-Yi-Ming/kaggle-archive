# -*- coding: utf-8 -*-
"""Belief calibration collector (TEMP analysis tool, NOT production).

跑 E vs 对手 的对局,wrap expected_opponent_market_sell 采集每步预测,
对局结束后用实际 opponent SELL orders(逐帧 action)算 actual,按
  item × horizon(1/4/12) × 时段(early/mid/late)
聚合 MAE / median error / bias / over / under rate。

输出: _pm_calib_<mode>.jsonl 每局一行的聚合校准统计(全局再在分析时合并)。
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
}


def load_mod(flags, tag):
    name = "cleo_%s_%s" % (flags.get("_V11_SEQUENTIAL"), tag)
    spec = importlib.util.spec_from_file_location(name, SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k, v in flags.items():
        setattr(mod, k, v)
    return mod


def _sells(action):
    out = []
    for o in (action or {}).get("market") or []:
        if isinstance(o, list) and o and o[0] == "SELL" and len(o) >= 3:
            try:
                out.append((o[1], int(o[2])))
            except (TypeError, ValueError):
                pass
    return out


def run_calib(seed, tag):
    from kaggle_environments import make
    modE = load_mod(FLAGS["E"], tag + "_E")
    modO = load_mod(FLAGS["B"], tag + "_O")
    seat_e_first = (seed % 2 == 1)
    a0, a1 = (modE.agent, modO.agent) if seat_e_first else (modO.agent, modE.agent)
    es, os_ = (0, 1) if seat_e_first else (1, 0)

    # E 模式决策路径不调用 expected_opponent_market_sell(已验证: pred=0)。
    # 校准改为 hook observe(每步无条件执行) → observe 返回后用该步 belief
    # 状态采样预测,再与真实对手 SELL 对比。observe 内部先更新 belief,
    # 所以采样含本步推断,对 h>=1 预测略乐观,报告中注明。
    preds = []  # (step, item, horizon, pred)
    obs_hook = modE._OPP.observe
    def wrapped_observe(obs, my_sells):
        obs_hook(obs, my_sells)
        # 采样 horizon 1/4/12(引擎消费节奏的近似)
        for h in (1, 4, 12):
            try:
                p = modE._OPP.expected_opponent_market_sell("WHEAT", h)
                if p > 0:
                    preds.append((modE._LAST_STEP, "WHEAT", h, p))
            except Exception:
                pass
            try:
                p = modE._OPP.expected_opponent_market_sell("STRAWBERRY", h)
                if p > 0:
                    preds.append((modE._LAST_STEP, "STRAWBERRY", h, p))
            except Exception:
                pass
            try:
                p = modE._OPP.expected_opponent_market_sell("MELON", h)
                if p > 0:
                    preds.append((modE._LAST_STEP, "MELON", h, p))
            except Exception:
                pass
    modE._OPP.observe = wrapped_observe

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])

    # 实际对手卖出序列: step -> {item: qty}
    actual = {}  # step -> {item: qty}
    for i, s in enumerate(env.steps):
        for item, qty in _sells(s[os_].get("action") or {}):
            actual.setdefault(i, {}).setdefault(item, 0)
            actual[i][item] += qty

    cal = {"seed": seed, "n_pred": len(preds), "groups": []}
    for st, item, h, p in preds:
        # actual 卖出在 (st, st+h] 区间
        a = 0
        for t in range(st + 1, min(st + h + 1, 720)):
            a += actual.get(t, {}).get(item, 0)
        period = "early" if st <= 240 else ("mid" if st <= 480 else "late")
        cal["groups"].append([item, h, period, p, a])
    return cal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed0", type=int, default=300)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pm_calib_EB.jsonl")
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                done.add(int(json.loads(line)["seed"]))
            except Exception:
                pass
    n = 2 if args.smoke else args.n
    need = [s for s in range(args.seed0, args.seed0 + n) if s not in done]
    print("[calib] 待跑=%d (seed %d..%d)" % (len(need), args.seed0, args.seed0 + n - 1), flush=True)
    t0 = time.time()
    for i, seed in enumerate(need):
        cal = run_calib(seed, uuid.uuid4().hex[:6])
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(cal) + "\n")
        if (i + 1) % 5 == 0 or i == len(need) - 1:
            print("[calib] %d/%d seed=%d preds=%d %.0fs"
                  % (i + 1, len(need), seed, cal["n_pred"], time.time() - t0), flush=True)
    print("[calib] DONE 累计=%d" % (len(done) + len(need)), flush=True)


if __name__ == "__main__":
    main()
