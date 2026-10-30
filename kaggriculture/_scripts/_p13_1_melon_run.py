# -*- coding: utf-8 -*-
"""P13.1 paired B0 vs B1 (early MELON) vs R2 reference."""
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
        "r2_mel_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(label, melon_on, seed, seat):
    import p13_1_melon
    p13_1_melon.set_enabled(melon_on)
    # force reimport of planner modules that may have cached? they call p13_1_melon at runtime — ok
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    day_melon_shed = {}
    day_shed = {}
    melon_sold = defaultdict(float)
    melon_rev = defaultdict(float)
    plant_melon = defaultdict(int)
    harvest_melon = defaultdict(int)
    buy_melon = defaultdict(int)

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
            day_cash[day] = float(farm.get("money") or 0)
            day_melon_shed[day] = int(shed.get("MELON") or 0)
            day_shed[day] = shed
            prices = dict((obs.get("market") or {}).get("prices") or {})
            cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            for c in cmds:
                if c and c[0] == "PLANT" and len(c) > 1 and c[1] == "MELON":
                    plant_melon[day] += 1
                if c and c[0] == "HARVEST":
                    harvest_melon[day] += 1
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3 and o[1] == "MELON":
                    q = int(o[2] or 0)
                    px = int(prices.get("MELON") or 0)
                    melon_sold[day] += q
                    melon_rev[day] += q * px
                if o and o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "MELON":
                    buy_melon[day] += int(o[2] or 0)
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
        "label": label, "melon": int(melon_on), "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op, "win": int(my > op),
        "d10": day_cash.get(10), "d15": day_cash.get(15), "d20": day_cash.get(20),
        "d29": day_cash.get(29),
        "d10_gap": (day_cash.get(10) - op) if day_cash.get(10) is not None else None,
        "melon_shed_d10": day_melon_shed.get(10),
        "melon_sold_d7_10": sum(melon_sold[d] for d in range(7, 11)),
        "melon_rev_d7_10": sum(melon_rev[d] for d in range(7, 11)),
        "melon_rev_total": sum(melon_rev.values()),
        "melon_bought": sum(buy_melon.values()),
        "plant_melon_cmds": sum(plant_melon.values()),
        "d5_cash": day_cash.get(5),
        "d0_cash": day_cash.get(0),
    }
    print(f"{label} s{seed} seat{seat}: d10={rec['d10']} d15={rec['d15']} d29={my:.0f} "
          f"melon_rev7_10={rec['melon_rev_d7_10']:.0f} melon_shed10={rec['melon_shed_d10']} "
          f"bought={rec['melon_bought']} plants={rec['plant_melon_cmds']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            rows.append(run("B0", False, seed, seat))
            rows.append(run("B1_melon", True, seed, seat))
            # R2 reference once per seat/seed from B1's opp already — add explicit R2 own
            rows.append(run("R2_ref", False, seed, seat) if False else
                        {"label": "R2_ref", "melon": 0, "seed": seed, "seat": seat,
                         "my": None, "opp": None, "margin": None, "win": None,
                         "d10": None, "d15": None, "d20": None, "d29": None,
                         "d10_gap": None, "melon_shed_d10": None,
                         "melon_sold_d7_10": None, "melon_rev_d7_10": None,
                         "melon_rev_total": None, "melon_bought": None,
                         "plant_melon_cmds": None, "d5_cash": None, "d0_cash": None})

    # fill R2_ref from opp column of B rows? better: run R2 as own once per seat/seed
    r2_rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            # lightweight: only need d10 money of R2 — already in B's opp at end, not d10
            pass

    out = ROOT / "p13_1_melon_counterfactual.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        keys = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    def mean(label, k):
        v = [r[k] for r in rows if r["label"] == label and r.get(k) is not None]
        return sum(v) / len(v) if v else None

    print("\n=== SUMMARY ===")
    for lab in ("B0", "B1_melon"):
        print(f"{lab}: d10={mean(lab,'d10')} d15={mean(lab,'d15')} d29={mean(lab,'my')} "
              f"melon_rev7_10={mean(lab,'melon_rev_d7_10')} melon_rev_tot={mean(lab,'melon_rev_total')}")
    b0 = [r for r in rows if r["label"] == "B0"]
    b1 = [r for r in rows if r["label"] == "B1_melon"]
    # paired deltas
    print("\n=== PAIRED B1-B0 ===")
    for (s0, s1) in zip(b0, b1):
        assert s0["seed"] == s1["seed"] and s0["seat"] == s1["seat"]
        d10 = (s1.get("d10") or 0) - (s0.get("d10") or 0)
        d15 = (s1.get("d15") or 0) - (s0.get("d15") or 0)
        d29 = (s1.get("my") or 0) - (s0.get("my") or 0)
        print(f"  s{s0['seed']} seat{s0['seat']}: Δd10={d10:+.0f} Δd15={d15:+.0f} Δd29={d29:+.0f} "
              f"B1melon_rev={s1.get('melon_rev_d7_10')}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
