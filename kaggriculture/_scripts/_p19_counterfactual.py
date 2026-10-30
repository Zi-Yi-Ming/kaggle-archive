# -*- coding: utf-8 -*-
"""P19: force a tail from day D and score short-horizon outcomes.

Not a selector. Produces (state_at_D, tail, cash@+5/+10, bank) rows
for later rule/tree/learned selector work.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

# module-level force for the run
FORCE = {"enabled": False, "day": 10, "tail": "MAIN"}


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p19_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def count_tiles(tiles):
    melon = plant = animals = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plant += 1
                    if t.get("crop") == "MELON":
                        melon += 1
                if t.get("animal"):
                    animals += 1
    return melon, plant, animals


def run(force_day, tail, seed, seat=0):
    FORCE.update(enabled=True, day=force_day, tail=tail)
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
    sel.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    state_at = {}
    day_sell = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            shed = dict(private.get("shed") or {})
            tiles = farm.get("tiles") or []
            melon, plant, animals = count_tiles(tiles)
            prices = dict((obs.get("market") or {}).get("prices") or {})
            sells = 0.0
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    sells += int(o[2] or 0) * int(prices.get(o[1]) or 0)
            day_sell[day] = day_sell.get(day, 0) + sells
            if step % 24 == 0:
                day_cash[day] = float(farm.get("money") or 0)
                state_at[day] = {
                    "day": day,
                    "money": float(farm.get("money") or 0),
                    "melon": melon, "plant": plant, "animals": animals,
                    "shed_total": sum(int(v or 0) for v in shed.values()),
                    "shed_melon": int(shed.get("MELON") or 0),
                    "n_land": len(farm.get("unlocked_quadrants") or []),
                    "hands": len(farm.get("hands") or []),
                }
            return action
        return agent

    # inject force via p18_selector-style overlay by monkeypatching decide
    import p18_selector as selmod
    orig_decide = selmod.decide

    def forced_decide(day, state):
        if FORCE["enabled"] and day >= FORCE["day"] and day <= FORCE["day"] + 10:
            return FORCE["tail"]
        return "MAIN"

    selmod.decide = forced_decide
    selmod.ENABLED = True

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    selmod.decide = orig_decide
    selmod.ENABLED = False
    FORCE["enabled"] = False

    f = env.steps[-1]
    final = float(f[seat]["observation"]["farms"][seat]["money"])
    st = state_at.get(force_day, {})
    d5 = force_day + 5
    d10 = force_day + 10
    rec = {
        "seed": seed, "seat": seat, "force_day": force_day, "tail": tail,
        "final": final,
        "cash_d5": day_cash.get(min(d5, 29)),
        "cash_d10": day_cash.get(min(d10, 29)),
        "cash_force": st.get("money"),
        "melon_force": st.get("melon"),
        "animals_force": st.get("animals"),
        "plant_force": st.get("plant"),
        "shed_force": st.get("shed_total"),
        "sell_d5": sum(day_sell.get(d, 0) for d in range(force_day, min(force_day + 5, 30))),
        "sell_d10": sum(day_sell.get(d, 0) for d in range(force_day, min(force_day + 10, 30))),
    }
    print(f"d{force_day} {tail:12s} s{seed} seat{seat}: "
          f"c0={rec['cash_force']:.0f} c5={rec['cash_d5']} c10={rec['cash_d10']} "
          f"fin={final:.0f} mel={rec['melon_force']} ani={rec['animals_force']}", flush=True)
    return rec


def main():
    rows = []
    for seed in (1, 2):
        for day in (9, 10):
            for tail in ("MAIN", "CASH_WINDOW", "HERD_SCALE"):
                rows.append(run(day, tail, seed, seat=0))

    out = ROOT / "p19_counterfactual.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # best tail per (seed, day) by cash_d10
    print("\n=== BEST tail by cash_d10 ===")
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        groups[(r["seed"], r["force_day"])].append(r)
    for key, g in sorted(groups.items()):
        best = max(g, key=lambda r: r["cash_d10"] or 0)
        print(f"  seed{key[0]} d{key[1]}: best={best['tail']} c10={best['cash_d10']} "
              f"fin={best['final']:.0f} | " +
              ", ".join(f"{x['tail']}={x['cash_d10']}" for x in g))
    print("wrote", out.name)


if __name__ == "__main__":
    main()
