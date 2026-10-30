# -*- coding: utf-8 -*-
"""P22 probe: find knife-edge opponents (mixed W/L or small |margin|)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

CANDIDATES = [
    "ledger_lena", "slotter_silas", "homestead_hana", "melon_mateo",
    "rotation_rosa", "wheat_walter", "broker_bea",
]


def setup_backbone():
    import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library
    import p18_selector as sel
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    sel.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def run(opp_key, seed, seat=0):
    from _pm_pool import load_agent
    own = setup_backbone()
    opp = load_agent(opp_key)
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    outcome = "W" if my > op else ("D" if my == op else "L")
    print(f"  {opp_key:16s} s{seed}: {outcome} my={my:.0f} opp={op:.0f} m={my-op:+.0f}", flush=True)
    return outcome, my - op


def main():
    print("=== knife-edge probe (backbone MAIN vs pool) ===")
    results = {}
    for key in CANDIDATES:
        o1, m1 = run(key, 1)
        o2, m2 = run(key, 2)
        mixed = o1 != o2
        mean_abs = (abs(m1) + abs(m2)) / 2
        results[key] = {"o1": o1, "o2": o2, "m1": m1, "m2": m2, "mixed": mixed, "mean_abs": mean_abs}
        print(f"  >> {key}: mixed={mixed} mean|margin|={mean_abs:.0f}", flush=True)
    print("\n=== ranking by knife-edge-ness ===")
    for k, v in sorted(results.items(), key=lambda kv: (not kv[1]["mixed"], kv[1]["mean_abs"])):
        print(f"  {k}: mixed={v['mixed']} |m|={v['mean_abs']:.0f} {v['o1']}/{v['o2']} "
              f"m={v['m1']:+.0f}/{v['m2']:+.0f}")


if __name__ == "__main__":
    main()
