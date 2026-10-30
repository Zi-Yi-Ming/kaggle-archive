# -*- coding: utf-8 -*-
"""P41: V16 (boatlee/salem) vs R2 head-to-head, both seats, multi-seed."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([a0, a1])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"]), float(f[1]["observation"]["farms"][1]["money"])


def main():
    r2 = load(ROOT / "_push_medal" / "main.py", "r2_h2h")
    v16 = load(ROOT / "_external" / "p41_extracted" / "salem_2900_main.py", "v16_h2h")
    seeds = (1, 2, 3, 4, 5, 11, 12, 13)
    rows = []
    w = t = l = 0
    print("seed  v16_as_p0  r2_as_p1  |  r2_as_p0  v16_as_p1  winner")
    for s in seeds:
        # fresh loads each game to avoid state pollution
        r2a = load(ROOT / "_push_medal" / "main.py", f"r2_{s}a")
        v16a = load(ROOT / "_external" / "p41_extracted" / "salem_2900_main.py", f"v16_{s}a")
        b0, b1 = run(v16a, r2a, s)
        r2b = load(ROOT / "_push_medal" / "main.py", f"r2_{s}b")
        v16b = load(ROOT / "_external" / "p41_extracted" / "salem_2900_main.py", f"v16_{s}b")
        c0, c1 = run(r2b, v16b, s)
        # v16 bank = b0 when seat0 + c1 when seat1
        v16_banks = (b0, c1)
        r2_banks = (b1, c0)
        v16_mean = sum(v16_banks) / 2
        r2_mean = sum(r2_banks) / 2
        if v16_mean > r2_mean + 1:
            win = "V16"
            w += 1
        elif r2_mean > v16_mean + 1:
            win = "R2"
            l += 1
        else:
            win = "TIE"
            t += 1
        print(f"{s:4d}  {b0:9.0f}  {b1:9.0f}  |  {c0:9.0f}  {c1:9.0f}  {win}")
        rows.append({
            "seed": s, "v16_s0": b0, "r2_s1": b1, "r2_s0": c0, "v16_s1": c1,
            "v16_mean": v16_mean, "r2_mean": r2_mean, "winner": win,
        })

    print(f"\nV16 W-T-L vs R2: {w}-{t}-{l}  ({w}/{w+t+l})")
    out = ROOT / "p41_v16_vs_r2.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print("wrote", out.name)


if __name__ == "__main__":
    main()
