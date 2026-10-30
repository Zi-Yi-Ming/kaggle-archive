# -*- coding: utf-8 -*-
"""P15: 2x2 interaction Base / Melon / Sheep / Melon+Sheep vs finn (cleaner own cash).

Use finn as opponent so own-side cash curve is less noisy than vs R2.
2 seeds × both seats × 4 arms = 16 games.
Interaction I(t) = V(A+B) - V(A) - V(B) + V(base)  at each checkpoint day.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_finn():
    from _pm_pool import load_agent
    return load_agent("fallow_finn")


def run(arm, seed, seat):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p15_force_sheep
    melon = arm in ("A", "AB")
    sheep = arm in ("B", "AB")
    # water ON whenever melon is on (lifecycle); also ON for sheep-only and base
    # to keep water factor constant across arms
    p13_1_melon.set_enabled(melon)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(False)
    p14_2_on.set_enabled(False)
    p15_force_sheep.set_enabled(sheep, 2)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_finn()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    n_sheep = {}
    n_melon = {}
    rev = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            sh = m = 0
            for row in farm.get("tiles") or []:
                for t in row:
                    if isinstance(t, dict):
                        if t.get("animal") == "SHEEP":
                            sh += 1
                        if t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                            m += 1
            n_sheep[day] = sh
            n_melon[day] = m
            prices = dict((obs.get("market") or {}).get("prices") or {})
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    rev[day] = rev.get(day, 0) + int(o[2] or 0) * int(prices.get(o[1]) or 0)
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    rec = {
        "arm": arm, "seed": seed, "seat": seat, "my": my,
        "sheep_2": n_sheep.get(2, 0), "sheep_10": n_sheep.get(10, 0),
        "melon_5": n_melon.get(5, 0), "melon_10": n_melon.get(10, 0),
        "rev_total": sum(rev.values()),
    }
    for d in (5, 10, 15, 20, 25, 29):
        rec[f"d{d}"] = day_cash.get(d)
    print(f"{arm} s{seed} seat{seat}: d29={my:.0f} d10={rec['d10']} d15={rec['d15']} "
          f"sh2={rec['sheep_2']} sh10={rec['sheep_10']} m5={rec['melon_5']} m10={rec['melon_10']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            for arm in ("0", "A", "B", "AB"):
                rows.append(run(arm, seed, seat))

    out = ROOT / "p15_interaction_effect.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # interaction by day: I = AB - A - B + 0
    def mean_arm(arm, k):
        v = [r[k] for r in rows if r["arm"] == arm and r.get(k) is not None]
        return sum(v) / len(v) if v else 0.0

    print("\n=== CASH CURVES (mean) ===")
    print(f"{'d':>4} {'0':>10} {'A_melon':>10} {'B_sheep':>10} {'AB':>10} {'I=AB-A-B+0':>12}")
    inter_rows = []
    for d in (5, 10, 15, 20, 25, 29):
        k = f"d{d}"
        v0, va, vb, vab = mean_arm("0", k), mean_arm("A", k), mean_arm("B", k), mean_arm("AB", k)
        inter = vab - va - vb + v0
        print(f"{d:4d} {v0:10.0f} {va:10.0f} {vb:10.0f} {vab:10.0f} {inter:12.0f}")
        inter_rows.append({"day": d, "base": v0, "A_melon": va, "B_sheep": vb, "AB": vab,
                           "interaction": inter})
    k = "my"
    v0, va, vb, vab = mean_arm("0", k), mean_arm("A", k), mean_arm("B", k), mean_arm("AB", k)
    inter = vab - va - vb + v0
    print(f"{'fin':>4} {v0:10.0f} {va:10.0f} {vb:10.0f} {vab:10.0f} {inter:12.0f}")
    inter_rows.append({"day": 29, "base": v0, "A_melon": va, "B_sheep": vb, "AB": vab,
                       "interaction": inter, "note": "final"})

    out2 = ROOT / "p15_unit_marginal_value.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day", "dA", "dB", "dAB", "interaction"])
        for r in inter_rows:
            w.writerow([r["day"], r["A_melon"] - r["base"], r["B_sheep"] - r["base"],
                        r["AB"] - r["base"], r["interaction"]])
    print("wrote", out.name, out2.name)

    # save full for research
    out3 = ROOT / "p15_cash_curves.csv"
    with open(out3, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arm", "seed", "seat", "d5", "d10", "d15", "d20", "d25", "d29",
                    "sheep_2", "sheep_10", "melon_5", "melon_10", "rev_total"])
        for r in rows:
            w.writerow([r["arm"], r["seed"], r["seat"], r.get("d5"), r.get("d10"),
                        r.get("d15"), r.get("d20"), r.get("d25"), r.get("d29"),
                        r.get("sheep_2"), r.get("sheep_10"), r.get("melon_5"),
                        r.get("melon_10"), r.get("rev_total")])
    print("wrote", out3.name)


if __name__ == "__main__":
    main()
