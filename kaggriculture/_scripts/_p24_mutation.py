# -*- coding: utf-8 -*-
"""P24: mutate a day-window of R2 trajectory; compare bank vs pure R2.

T0 = pure R2
T_mut = R2 except steps in [day_lo, day_hi] replaced by our production action
        (backbone portfolio+water, optional forced tail).

Not selector. Offline trajectory improvement probe.
No submit.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

FORCE = {"enabled": False, "day": 10, "tail": "MAIN"}
MUT = {"day_lo": 9, "day_hi": 12, "tail": "CASH_WINDOW"}


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p24_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def setup_our_backbone(tail_from=None, tail=None):
    import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library
    import p18_selector as sel
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    if tail_from is not None:
        FORCE.update(enabled=True, day=tail_from, tail=tail or "MAIN")
        sel.set_selector("S1")  # enable p18 path; decide overridden below
    else:
        FORCE["enabled"] = False
        sel.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None

    import p18_selector as selmod
    orig = selmod.decide

    def forced_decide(day, state):
        if FORCE["enabled"] and FORCE["day"] <= day <= FORCE["day"] + 10:
            return FORCE["tail"]
        return "MAIN"

    selmod.decide = forced_decide
    selmod.ENABLED = True
    return pmod.agent


def make_mutant(r2_agent, our_agent, day_lo, day_hi):
    """Return agent: our actions in [day_lo, day_hi), else R2."""
    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        day = step // 24
        if day_lo <= day < day_hi:
            return our_agent(obs, configuration)
        return r2_agent(obs, configuration)
    return agent


def run(label, seed, seat=0, mutate=None):
    """mutate=None → pure R2; else dict(day_lo,day_hi,tail)."""
    r2 = load_r2()
    if mutate is None:
        own = r2
        from _pm_pool import load_agent
        opp = load_agent("fallow_finn")
    else:
        our = setup_our_backbone(tail_from=mutate["day_lo"], tail=mutate.get("tail", "MAIN"))
        own = make_mutant(r2, our, mutate["day_lo"], mutate["day_hi"])
        from _pm_pool import load_agent
        opp = load_agent("fallow_finn")
    # both arms vs finn so we measure OUR/R2 bank cleanly
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
    rec = {
        "label": label, "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op,
        "mutate": str(mutate),
    }
    print(f"{label:20s} s{seed}: bank={my:.0f} vs finn={op:.0f}", flush=True)
    return rec


def main():
    rows = []
    for seed in (1, 2, 3):
        rows.append(run("T0_R2", seed, seat=0, mutate=None))
        # mutate mid-game cash window into our CASH production
        rows.append(run("T1_R2+d9_12_CASH", seed, seat=0,
                        mutate={"day_lo": 9, "day_hi": 12, "tail": "CASH_WINDOW"}))
        # mutate early setup into our MAIN portfolio
        rows.append(run("T2_R2+d0_5_MAIN", seed, seat=0,
                        mutate={"day_lo": 0, "day_hi": 5, "tail": "MAIN"}))

    out = ROOT / "p24_trajectory_mutation.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n=== SUMMARY ===")
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        by[r["label"]].append(r["my"])
    for lab, vals in by.items():
        print(f"  {lab}: mean={sum(vals)/len(vals):.0f}  vals={[round(v) for v in vals]}")
    # paired vs T0
    t0 = {r["seed"]: r["my"] for r in rows if r["label"] == "T0_R2"}
    for lab in ("T1_R2+d9_12_CASH", "T2_R2+d0_5_MAIN"):
        deltas = []
        for r in rows:
            if r["label"] == lab:
                deltas.append(r["my"] - t0[r["seed"]])
        print(f"  {lab} vs T0: meanΔ={sum(deltas)/len(deltas):+.0f} "
              f"pos={sum(1 for d in deltas if d>0)}/{len(deltas)}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
