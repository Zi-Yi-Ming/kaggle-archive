# -*- coding: utf-8 -*-
"""P18 ablation: S0 fixed / S1 rules / S2 knn retrieval. 8 games vs R2."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p18a_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(selector, seed, seat):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p16_branch
    import p17_1_library
    import p18_selector as sel
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    sel.set_selector(selector)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    rec = {
        "selector": selector, "seed": seed, "seat": seat, "my": my,
        "win": 0, "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20), "d29": day_cash.get(29),
        "bankrupt": int(my < 1000),
    }
    print(f"{selector} s{seed} seat{seat}: d29={my:.0f} d15={rec['d15']} "
          f"d10={rec['d10']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            for sel in ("S0", "S1", "S2"):
                rows.append(run(sel, seed, seat))

    out = ROOT / "p18_ablation.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(s, k):
        v = [r[k] for r in rows if r["selector"] == s and r.get(k) is not None]
        return sum(v) / len(v) if v else 0

    print("\n=== SUMMARY ===")
    for s in ("S0", "S1", "S2"):
        print(f"{s}: bank={mean(s,'my'):.0f} d15={mean(s,'d15'):.0f} "
              f"bankrupt={sum(r['bankrupt'] for r in rows if r['selector']==s)}")
    print("\n=== PAIRED S2-S1 / S2-S0 ===")
    n21 = n20 = 0
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            s0 = next(r for r in rows if r["selector"]=="S0" and r["seed"]==seed and r["seat"]==seat)
            s1 = next(r for r in rows if r["selector"]=="S1" and r["seed"]==seed and r["seat"]==seat)
            s2 = next(r for r in rows if r["selector"]=="S2" and r["seed"]==seed and r["seat"]==seat)
            if s2["my"] > s1["my"]:
                n21 += 1
            if s2["my"] > s0["my"]:
                n20 += 1
            print(f"  s{seed} seat{seat}: S0={s0['my']:.0f} S1={s1['my']:.0f} S2={s2['my']:.0f} "
                  f"Δ2-1={s2['my']-s1['my']:+.0f} Δ2-0={s2['my']-s0['my']:+.0f}")
    print(f"S2>S1: {n21}/8  S2>S0: {n20}/8")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
