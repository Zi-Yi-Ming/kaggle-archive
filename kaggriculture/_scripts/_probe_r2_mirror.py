# -*- coding: utf-8 -*-
"""Local R2-mirror dump-order probe.

Hypothesis: in identical shop-router mirrors, seat0's market orders commit
first and get better end-dump prices.

Method: play R2 vs R2 on fixed seeds, report seat0-seat1 margin and whether
final banks are equal (true mirror) or seat0-favored.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

ROOT = r"D:\桌面\Kaggle\kaggriculture"
sys.path.insert(0, ROOT)
from kaggle_environments import make

R2 = os.path.join(ROOT, "_push_medal", "main.py")


def load(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", R2)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(seed):
    a0, a1 = load(f"s{seed}a"), load(f"s{seed}b")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    return b0, b1, err


def main():
    rows = []
    for seed in range(1, 13):
        b0, b1, err = run(seed)
        m = b0 - b1
        rows.append((seed, b0, b1, m, err))
        print(f"seed={seed:2d} seat0={b0:8.0f} seat1={b1:8.0f} m={m:+8.0f} err={err}", flush=True)
    margins = [r[3] for r in rows]
    eq = sum(1 for m in margins if m == 0)
    s0 = sum(1 for m in margins if m > 0)
    s1 = sum(1 for m in margins if m < 0)
    mean = sum(margins) / len(margins)
    print(f"\nSUMMARY n={len(margins)} seat0_win={s0} seat1_win={s1} exact_tie={eq} mean_seat0={mean:+.1f}")
    print("  if mean>>0: seat0 dump advantage confirmed locally")
    print("  if mean~0: local engine is seat-symmetric; live gaps are opponent-specific")
    json.dump(
        {"rows": [{"seed": s, "b0": a, "b1": b, "m": m, "err": e} for s, a, b, m, e in rows],
         "s0": s0, "s1": s1, "eq": eq, "mean": mean},
        open(os.path.join(ROOT, "_calib_r2_mirror.json"), "w"),
        indent=2,
    )


if __name__ == "__main__":
    main()
