# -*- coding: utf-8 -*-
"""Eval new public agents vs finn and vs R2. finn never wrapped."""
from __future__ import annotations

import csv
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

EXT = ROOT / "_external" / "p51_extracted"
CANDS = {
    "kaito_v48": EXT / "40_40_early_floor_39_46_top_10_v48_fast_routes.py",
    "state_router": EXT / "kaggriculture_public_state_router_74_5_win_rate.py",
    "yhay_shop_0913": EXT / "shop_router_0913.py",
}
FINN = ROOT / "reference_agents" / "fallow_finn.py"
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3)


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


def vs_finn(make_fn, seeds):
    banks = []
    w = d = l = 0
    for seed in seeds:
        b0, b1 = run(make_fn(), load(FINN, f"finn51_{seed}a"), seed)
        c0, c1 = run(load(FINN, f"finn51_{seed}b"), make_fn(), seed)
        our = (b0 + c1) / 2
        opp = (b1 + c0) / 2
        banks.append(our)
        if our > opp + 1:
            w += 1
        elif opp > our + 1:
            l += 1
        else:
            d += 1
        print(f"    vs finn s{seed}: {our:.0f}", flush=True)
    return w, d, l, statistics.mean(banks), statistics.pstdev(banks) if len(banks) > 1 else 0


def vs_r2(make_fn, seeds):
    w = d = l = 0
    banks = []
    for seed in seeds:
        b0, b1 = run(make_fn(), load(R2, f"r2_51_{seed}a"), seed)
        c0, c1 = run(load(R2, f"r2_51_{seed}b"), make_fn(), seed)
        our = (b0 + c1) / 2
        theirs = (b1 + c0) / 2
        banks.append(our)
        if our > theirs + 1:
            w += 1
            res = "W"
        elif theirs > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        print(f"    vs R2 s{seed}: us={our:.0f} r2={theirs:.0f} {res}", flush=True)
    return w, d, l, statistics.mean(banks)


def main():
    t0 = time.time()
    rows = []
    print("=== R2 vs finn ref ===", flush=True)
    w, d, l, bm, bs = vs_finn(lambda: load(R2, f"r2ref_{id(object())}"), SEEDS)
    print(f"R2 W-D-L {w}-{d}-{l} bank={bm:.0f}±{bs:.0f}", flush=True)
    rows.append({"name": "R2", "finn_WL": w - l, "finn_bank": bm, "vs_R2_WL": None, "vs_R2_bank": None})

    for name, path in CANDS.items():
        print(f"\n=== {name} ===", flush=True)
        try:
            def make(path=path, name=name):
                return load(path, f"c51_{name}_{id(object())}")
            w, d, l, bm, bs = vs_finn(make, SEEDS)
            print(f"  finn W-D-L {w}-{d}-{l} bank={bm:.0f}±{bs:.0f}", flush=True)
            rw, rd, rl, rb = vs_r2(make, SEEDS)
            print(f"  vs R2 W-D-L {rw}-{rd}-{rl} our_mean={rb:.0f}", flush=True)
            rows.append({
                "name": name, "finn_WL": w - l, "finn_bank": bm,
                "vs_R2_WL": rw - rl, "vs_R2_bank": rb,
            })
        except Exception as e:
            print(f"  FAIL {e}", flush=True)
            rows.append({"name": name, "error": str(e)[:160]})

    with open(ROOT / "p51_new_agents.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["name", "finn_WL", "finn_bank", "vs_R2_WL", "vs_R2_bank", "error"]
        wri = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p51_new_agents.csv", f"dt={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
