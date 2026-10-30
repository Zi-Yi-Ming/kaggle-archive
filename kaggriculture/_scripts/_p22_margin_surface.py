# -*- coding: utf-8 -*-
"""P22: paired Δmargin surface vs knife-edge opponent melon_mateo.

Δmargin(tail) = margin(tail) - margin(MAIN)  same seed, same day, same opponent.
No NN. No submit.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

OPP = "melon_mateo"
FORCE = {"enabled": False, "day": 10, "tail": "MAIN"}


def load_opp():
    from _pm_pool import load_agent
    return load_agent(OPP)


def count_melon_animals(tiles):
    melon = animals = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                    melon += 1
                if t.get("animal"):
                    animals += 1
    return melon, animals


def run(force_day, tail, seed, seat=0):
    FORCE.update(enabled=True, day=force_day, tail=tail)
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
    own = pmod.agent
    opp = load_opp()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    state_at = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            tiles = farm.get("tiles") or []
            melon, animals = count_melon_animals(tiles)
            if step % 24 == 0:
                day_cash[day] = float(farm.get("money") or 0)
                state_at[day] = {
                    "money": float(farm.get("money") or 0),
                    "melon": melon, "animals": animals,
                }
            return action
        return agent

    import p18_selector as selmod
    orig = selmod.decide

    def forced_decide(day, state):
        if FORCE["enabled"] and FORCE["day"] <= day <= FORCE["day"] + 10:
            return FORCE["tail"]
        return "MAIN"

    selmod.decide = forced_decide
    selmod.ENABLED = True
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    selmod.decide = orig
    selmod.ENABLED = False
    FORCE["enabled"] = False

    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    outcome = "W" if my > op else ("D" if my == op else "L")
    st = state_at.get(force_day, {})
    rec = {
        "opp": OPP, "seed": seed, "seat": seat, "day": force_day, "tail": tail,
        "my": my, "opp_bank": op, "margin": my - op, "outcome": outcome,
        "cash_d5": day_cash.get(min(force_day + 5, 29)),
        "melon0": st.get("melon"), "animals0": st.get("animals"),
        "cash0": st.get("money"),
    }
    print(f"d{force_day} {tail:12s} s{seed}: {outcome} my={my:.0f} opp={op:.0f} "
          f"m={my-op:+.0f} mel={st.get('melon')} c5={rec['cash_d5']}", flush=True)
    return rec


def main():
    rows = []
    for seed in (1, 2, 3, 4):
        for day in (9, 10):
            for tail in ("MAIN", "CASH_WINDOW", "HERD_SCALE"):
                rows.append(run(day, tail, seed, seat=0))

    out = ROOT / "p22_margin_surface.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # paired Δmargin vs MAIN
    print("\n=== PAIRED Δmargin (tail - MAIN) ===")
    groups = defaultdict(dict)
    for r in rows:
        groups[(r["seed"], r["day"])][r["tail"]] = r
    pair_rows = []
    n_cash_pos = n_herd_pos = 0
    cash_deltas = []
    for key, g in sorted(groups.items()):
        base = g["MAIN"]["margin"]
        dc = g["CASH_WINDOW"]["margin"] - base
        dh = g["HERD_SCALE"]["margin"] - base
        cash_deltas.append(dc)
        if dc > 0:
            n_cash_pos += 1
        if dh > 0:
            n_herd_pos += 1
        print(f"  s{key[0]} d{key[1]}: MAIN={base:+.0f} "
              f"CASH={g['CASH_WINDOW']['margin']:+.0f} (Δ={dc:+.0f}) "
              f"HERD={g['HERD_SCALE']['margin']:+.0f} (Δ={dh:+.0f})")
        pair_rows.append({
            "seed": key[0], "day": key[1],
            "melon0": g["MAIN"].get("melon0"),
            "margin_MAIN": base,
            "margin_CASH": g["CASH_WINDOW"]["margin"],
            "margin_HERD": g["HERD_SCALE"]["margin"],
            "delta_CASH": dc, "delta_HERD": dh,
            "outcome_CASH": g["CASH_WINDOW"]["outcome"],
            "outcome_MAIN": g["MAIN"]["outcome"],
        })

    n = len(pair_rows)
    print(f"\nCASH Δmargin>0: {n_cash_pos}/{n}  mean ΔCASH={sum(cash_deltas)/n:+.0f}")
    print(f"HERD Δmargin>0: {n_herd_pos}/{n}")

    # outcome flips
    flips = sum(1 for p in pair_rows if p["outcome_MAIN"] != p["outcome_CASH"])
    print(f"outcome flips MAIN vs CASH: {flips}/{n}")

    out2 = ROOT / "p22_paired_delta.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pair_rows[0].keys()))
        w.writeheader()
        w.writerows(pair_rows)
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
