# -*- coding: utf-8 -*-
"""E-mode Postmortem ablation harness (TEMP analysis tool, NOT production).

设计要点:
1. 每局重新 exec cleo_v10.py 成独立模块实例 —— 模拟 Kaggle 每局新进程,
   避免 _OPP / _CLONE_CONFIDENCE / _LAST_STEP 等模块级状态跨局泄漏。
2. E/B/D 由 flags 覆盖(setattr 在 exec 后,agent 函数体运行时读全局,有效)。
3. seat 交替:seed 奇数 -> [E,B]; seed 偶数 -> [B,E],消除 seat bias。
4. 断点续跑:结果追加写 CSV,已完成的 seed 自动跳过,便于分批跑防超时。

用法:
  python _pm_ablation.py --mode EB --total 220     # E vs B, seeds 1..220
  python _pm_ablation.py --mode ED --total 220     # E vs D
  python _pm_ablation.py --mode EB --total 4       # 冒烟
输出: _pm_results_<mode>.csv  每行: seed,seat,w0,w1,winner(0/1/tie)
"""
import os
import sys
import time
import json
import uuid
import argparse
import importlib.util

os.environ.setdefault("NO_PROXY", "*")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleo_v10.py")

FLAGS = {
    # 生产默认(E 模式全开)
    "E": dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
              _V11_MARKET_MODEL=True, _V11_BELIEF=True,
              _V11_HAZARD=True, _V11_SEQUENTIAL=True),
    # B = P0-only
    "B": dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
              _V11_MARKET_MODEL=True, _V11_BELIEF=False,
              _V11_HAZARD=False, _V11_SEQUENTIAL=False),
    # D = 去掉 sequential
    "D": dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
              _V11_MARKET_MODEL=True, _V11_BELIEF=True,
              _V11_HAZARD=True, _V11_SEQUENTIAL=False),
}


def load_mod(flags):
    """exec cleo_v10.py 成新模块实例并覆盖 flags(干净状态)。"""
    name = "cleo_%s_%s" % (flags.get("_V11_SEQUENTIAL"), uuid.uuid4().hex[:6])
    spec = importlib.util.spec_from_file_location(name, SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k, v in flags.items():
        setattr(mod, k, v)
    return mod


def run_episode(seed, modA, modB):
    """跑一局: seat0=modA, seat1=modB; 返回 (bank0, bank1, winner)。"""
    from kaggle_environments import make
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([modA.agent, modB.agent])
    fin = env.steps[-1]
    b0 = fin[0]["observation"]["farms"][0]["money"]
    b1 = fin[1]["observation"]["farms"][1]["money"]
    winner = 0 if b0 > b1 else (1 if b1 > b0 else "tie")
    return b0, b1, winner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["EB", "ED"], required=True)
    ap.add_argument("--total", type=int, default=220)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--smoke", action="store_true", help="只跑 2 局快速验证")
    args = ap.parse_args()

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_pm_results_%s.csv" % args.mode)
    done = set()
    if os.path.exists(out):
        with open(out, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 5 and parts[0].isdigit():
                    done.add(int(parts[0]))
    n_todo = 2 if args.smoke else args.total
    need = [s for s in range(args.seed0, args.seed0 + n_todo) if s not in done]
    print("[harness] mode=%s 已完成=%d 待跑=%d" % (args.mode, len(done), len(need)),
          flush=True)

    t0 = time.time()
    for i, seed in enumerate(need):
        seat = "AB" if seed % 2 == 1 else "BA"   # 交替 seat
        modA = load_mod(FLAGS[args.mode[0]])     # 每局重载,干净状态
        modB = load_mod(FLAGS[args.mode[1]])
        if args.mode == "EB":
            if seat == "AB":
                m0, m1 = modA, modB
            else:
                m0, m1 = modB, modA
        else:  # ED
            if seat == "AB":
                m0, m1 = modA, modB
            else:
                m0, m1 = modB, modA
        b0, b1, winner = run_episode(seed, m0, m1)
        # seat0=第1个参数,seat1=第2个参数;winner 归 seat
        row = "%d,%s,%.2f,%.2f,%s" % (seed, seat, b0, b1, winner)
        with open(out, "a", encoding="utf-8") as f:
            f.write(row + "\n")
        if (i + 1) % 10 == 0 or i == len(need) - 1:
            dt = time.time() - t0
            print("[harness] %d/%d seed=%d %s %.1fs/局累计%.0fs"
                  % (i + 1, len(need), seed, winner, dt / (i + 1), dt), flush=True)
    print("[harness] DONE mode=%s 新跑=%d 总结果=%d" % (args.mode, len(need),
          len(done) + len(need)), flush=True)


if __name__ == "__main__":
    main()
