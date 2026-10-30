# -*- coding: utf-8 -*-
"""P33-A: oracle hybrid — R2 market vs R2 workers value attribution.

A0 = pure R2
A1 = R2 market + our p11 workers
A2 = our market + R2 workers
A3 = pure ours (backbone)
All vs finn, pinned seed.
"""
from __future__ import annotations

import copy
import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p26_harness import load_r2, load_pool  # noqa: E402


def setup_ours():
    import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library, p18_selector
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    p18_selector.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def make_hybrid(r2_fn, our_fn, take_market_from: str, take_workers_from: str):
    """take_market_from / take_workers_from in {'r2','ours'}."""
    def agent(obs, configuration=None):
        a_r2 = r2_fn(obs, configuration)
        a_our = our_fn(obs, configuration)
        market_src = a_r2 if take_market_from == "r2" else a_our
        worker_src = a_r2 if take_workers_from == "r2" else a_our
        return {
            "farmer": copy.deepcopy(worker_src.get("farmer") or ["PASS"]),
            "hands": copy.deepcopy(worker_src.get("hands") or []),
            "market": copy.deepcopy(market_src.get("market") or []),
        }
    return agent


def run_vs_finn(own_fn, seed):
    finn = load_pool("fallow_finn")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([own_fn, finn])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"])


def main():
    rows = []
    for seed in (1, 2, 3):
        r2 = load_r2()
        our = setup_ours()
        t0 = run_vs_finn(r2, seed)

        r2b = load_r2()
        ourb = setup_ours()
        h_mkt_r2 = make_hybrid(r2b, ourb, "r2", "ours")
        t1 = run_vs_finn(h_mkt_r2, seed)

        r2c = load_r2()
        ourc = setup_ours()
        h_mkt_our = make_hybrid(r2c, ourc, "ours", "r2")
        t2 = run_vs_finn(h_mkt_our, seed)

        ourd = setup_ours()
        t3 = run_vs_finn(ourd, seed)

        rows.append({
            "seed": seed,
            "A0_R2": t0, "A1_R2mkt_ourwk": t1,
            "A2_ourmkt_R2wk": t2, "A3_ours": t3,
        })
        print(f"s{seed}: R2={t0:.0f} R2mkt+ourwk={t1:.0f} ourmkt+R2wk={t2:.0f} ours={t3:.0f}", flush=True)

    out = ROOT / "p33a_oracle_hybrid.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n=== MEANS ===")
    for k in ("A0_R2", "A1_R2mkt_ourwk", "A2_ourmkt_R2wk", "A3_ours"):
        vals = [r[k] for r in rows]
        print(f"  {k}: {sum(vals)/len(vals):.0f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
