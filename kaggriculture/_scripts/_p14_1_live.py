# -*- coding: utf-8 -*-
"""P14.1 live gate: portfolio ON + water ON vs R2, 8 games both seats."""
from __future__ import annotations

import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_pf_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(seed, seat, portfolio, water):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(water)
    p14_1_on.set_enabled(portfolio)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    field = defaultdict(lambda: defaultdict(int))
    melon_rev = defaultdict(float)
    wheat_rev = defaultdict(float)
    straw_rev = defaultdict(float)
    milk_rev = defaultdict(float)
    plant_c = defaultdict(int)

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            for row in farm.get("tiles") or []:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT":
                        field[day][t.get("crop")] += 1
            prices = dict((obs.get("market") or {}).get("prices") or {})
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    item, q = o[1], int(o[2] or 0)
                    rev = q * int(prices.get(item) or 0)
                    if item == "MELON":
                        melon_rev[day] += rev
                    elif item == "WHEAT":
                        wheat_rev[day] += rev
                    elif item == "STRAWBERRY":
                        straw_rev[day] += rev
                    elif item == "MILK":
                        milk_rev[day] += rev
                if o and o[0] == "BUY_SEED" and len(o) >= 3:
                    plant_c[o[1]] += int(o[2] or 0)
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    label = "PF+wat" if portfolio and water else ("PF" if portfolio else "B0")
    rec = {
        "label": label, "portfolio": int(portfolio), "water": int(water),
        "seed": seed, "seat": seat, "my": my, "opp": op, "margin": my - op,
        "win": int(my > op), "bankrupt": int(my < 1000),
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20), "d29": day_cash.get(29),
        "melon_field_d5": field.get(5, {}).get("MELON", 0),
        "melon_field_d10": field.get(10, {}).get("MELON", 0),
        "wheat_field_d5": field.get(5, {}).get("WHEAT", 0),
        "straw_field_d10": field.get(10, {}).get("STRAWBERRY", 0),
        "melon_rev": sum(melon_rev.values()),
        "wheat_rev": sum(wheat_rev.values()),
        "straw_rev": sum(straw_rev.values()),
        "milk_rev": sum(milk_rev.values()),
        "seeds_bought": str(dict(plant_c)),
    }
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} "
          f"d10={rec['d10']} d15={rec['d15']} d29={my:.0f} "
          f"M5/M10={rec['melon_field_d5']}/{rec['melon_field_d10']} "
          f"mrev={rec['melon_rev']:.0f} srev={rec['straw_rev']:.0f} "
          f"wrev={rec['wheat_rev']:.0f} seeds={rec['seeds_bought']}", flush=True)
    return rec


def main():
    rows = []
    # B0 control
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            rows.append(run(seed, seat, False, False))
    # Treatment: portfolio + water (lifecycle dep from P13.3)
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            rows.append(run(seed, seat, True, True))

    out = ROOT / "p14_1_local_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(label, k):
        v = [r[k] for r in rows if r["label"] == label and r.get(k) is not None]
        return sum(v) / len(v) if v else None

    print("\n=== SUMMARY ===")
    for lab in ("B0", "PF+wat"):
        print(f"{lab}: wins={sum(r['win'] for r in rows if r['label']==lab)}/8 "
              f"bank={mean(lab,'my')} d10={mean(lab,'d10')} d15={mean(lab,'d15')} "
              f"d29={mean(lab,'my')} melon_rev={mean(lab,'melon_rev')} "
              f"straw_rev={mean(lab,'straw_rev')} M10={mean(lab,'melon_field_d10')} "
              f"bankrupt={sum(r['bankrupt'] for r in rows if r['label']==lab)}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
