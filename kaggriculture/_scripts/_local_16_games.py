# -*- coding: utf-8 -*-
"""本机轻量验证：v11E vs closer_cleo，seeds 1-8，双 seat，串行跑 16 局。

输出：
  _local_16_games.csv  （agent,opp,seed,seat,bank_agent,bank_opp,steps,sec）
"""
import csv
import os
import sys
import time
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "_kaggle_nb", "code"))


def load_agent(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def main():
    cand = load_agent("v11e", "_kaggle_nb/code/v11e_agent.py")
    opp = load_agent("cleo", "_kaggle_nb/code/closer_cleo.py")

    from kaggle_environments import make

    out_path = os.path.join(BASE, "_local_16_games.csv")
    rows = []
    tasks = [(s, seat) for s in range(1, 9) for seat in (0, 1)]
    print(f"total={len(tasks)} tasks (seeds 1-8, seats 0/1)")
    for seed, seat in tasks:
        a0, a1 = (cand, opp) if seat == 0 else (opp, cand)
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.configuration["seed"] = seed
        t0 = time.time()
        env.run([a0, a1])
        dt = time.time() - t0
        last = env.steps[-1]
        b0 = last[0]["observation"]["farms"][0]["money"]
        b1 = last[1]["observation"]["farms"][1]["money"]
        rows.append({
            "agent": "v11e",
            "opp": "closer_cleo",
            "seed": seed,
            "seat": seat,
            "bank_agent": b0 if seat == 0 else b1,
            "bank_opp": b1 if seat == 0 else b0,
            "steps": len(env.steps),
            "sec": round(dt, 2),
        })
        print(rows[-1])

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("saved:", out_path)


if __name__ == "__main__":
    main()
