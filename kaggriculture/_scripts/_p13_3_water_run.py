# -*- coding: utf-8 -*-
"""P13.3 paired B0 vs B1 (WATER_READY_CROP). Melon planting ON for both."""
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
        "r2_wat_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(label, water_on, seed, seat):
    import p13_1_melon
    import p13_3_water
    p13_1_melon.set_enabled(True)  # both arms have early melon
    p13_3_water.set_enabled(water_on)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    day_melon_field = {}
    day_melon_shed = {}
    melon_sold = defaultdict(float)
    melon_rev = defaultdict(float)
    water_cmds = defaultdict(int)
    plant_melon = defaultdict(int)
    harvest_cmds = defaultdict(int)
    weed_n = defaultdict(int)

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
            day_cash[day] = float(farm.get("money") or 0)
            n_m = 0
            n_w = 0
            for row in tiles:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                        n_m += 1
                    if isinstance(t, dict) and t.get("kind") == "WEED":
                        n_w += 1
            day_melon_field[day] = n_m
            day_melon_shed[day] = int(shed.get("MELON") or 0)
            weed_n[day] = n_w
            prices = dict((obs.get("market") or {}).get("prices") or {})
            cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            for c in cmds:
                if not c:
                    continue
                if c[0] == "WATER":
                    water_cmds[day] += 1
                if c[0] == "HARVEST":
                    harvest_cmds[day] += 1
                if c[0] == "PLANT" and len(c) > 1 and c[1] == "MELON":
                    plant_melon[day] += 1
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3 and o[1] == "MELON":
                    q = int(o[2] or 0)
                    px = int(prices.get("MELON") or 0)
                    melon_sold[day] += q
                    melon_rev[day] += q * px
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])

    rec = {
        "label": label, "water": int(water_on), "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op, "win": int(my > op),
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d11": day_cash.get(11),
        "d15": day_cash.get(15), "d20": day_cash.get(20), "d29": day_cash.get(29),
        "melon_field_d9": day_melon_field.get(9), "melon_field_d10": day_melon_field.get(10),
        "melon_field_d11": day_melon_field.get(11),
        "melon_shed_d11": day_melon_shed.get(11),
        "melon_rev_d7_12": sum(melon_rev[d] for d in range(7, 13)),
        "melon_rev_total": sum(melon_rev.values()),
        "water_cmds_total": sum(water_cmds.values()),
        "plant_melon_total": sum(plant_melon.values()),
        "weed_d10": weed_n.get(10),
    }
    print(f"{label} s{seed} seat{seat}: d10={rec['d10']} d15={rec['d15']} d29={my:.0f} "
          f"fieldM d9/10/11={rec['melon_field_d9']}/{rec['melon_field_d10']}/{rec['melon_field_d11']} "
          f"shed11={rec['melon_shed_d11']} rev={rec['melon_rev_d7_12']:.0f} "
          f"water={rec['water_cmds_total']} weed10={rec['weed_d10']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            rows.append(run("B0_melon", False, seed, seat))
            rows.append(run("B1_water", True, seed, seat))

    out = ROOT / "p13_3_water_counterfactual.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(label, k):
        v = [r[k] for r in rows if r["label"] == label and r.get(k) is not None]
        return sum(v) / len(v) if v else None

    print("\n=== SUMMARY ===")
    for lab in ("B0_melon", "B1_water"):
        print(f"{lab}: d10={mean(lab,'d10')} d15={mean(lab,'d15')} d29={mean(lab,'my')} "
              f"fieldM10={mean(lab,'melon_field_d10')} shed11={mean(lab,'melon_shed_d11')} "
              f"rev={mean(lab,'melon_rev_d7_12')} water={mean(lab,'water_cmds_total')}")
    print("\n=== PAIRED B1-B0 ===")
    b0 = [r for r in rows if r["label"] == "B0_melon"]
    b1 = [r for r in rows if r["label"] == "B1_water"]
    for s0, s1 in zip(b0, b1):
        print(f"  s{s0['seed']} seat{s0['seat']}: "
              f"Δd10={(s1['d10'] or 0)-(s0['d10'] or 0):+.0f} "
              f"Δd15={(s1['d15'] or 0)-(s0['d15'] or 0):+.0f} "
              f"Δd29={(s1['my'] or 0)-(s0['my'] or 0):+.0f} "
              f"Δrev={(s1['melon_rev_d7_12'] or 0)-(s0['melon_rev_d7_12'] or 0):+.0f} "
              f"B1_field11={s1['melon_field_d11']} B0_field11={s0['melon_field_d11']}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
