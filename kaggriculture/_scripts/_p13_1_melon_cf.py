# -*- coding: utf-8 -*-
"""P13.1 paired B0 vs B1 (+ early MELON) vs R2 reference."""
from __future__ import annotations

import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

import p13_1_melon as melon  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_mel_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_one(label, seed, seat, vs_r2=True):
    melon.set_enabled(label == "B1")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2() if vs_r2 else None
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    day_melon_shed = {}
    day_melon_inv = {}
    melon_sold_qty = 0
    melon_revenue = 0.0
    wheat_sold = 0
    milk_sold = 0
    plant_melon_n = 0
    harvest_n = 0

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            nonlocal melon_sold_qty, melon_revenue, wheat_sold, milk_sold, plant_melon_n, harvest_n
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if is_own:
                farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
                private = obs.get("private") or {}
                shed = dict(private.get("shed") or {})
                invs = list(private.get("inventories") or [])
                day_cash[day] = float(farm.get("money") or 0)
                day_melon_shed[day] = int(shed.get("MELON") or 0)
                day_melon_inv[day] = sum(int((i or {}).get("MELON") or 0) for i in invs)
                prices = dict((obs.get("market") or {}).get("prices") or {})
                cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
                for c in cmds:
                    if c and c[0] == "PLANT" and len(c) >= 2 and c[1] == "MELON":
                        plant_melon_n += 1
                    if c and c[0] == "HARVEST":
                        harvest_n += 1
                for o in action.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3:
                        item, q = o[1], int(o[2] or 0)
                        px = int(prices.get(item) or 0)
                        if item == "MELON":
                            melon_sold_qty += q
                            melon_revenue += q * px
                        elif item == "WHEAT":
                            wheat_sold += q
                        elif item == "MILK":
                            milk_sold += q
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    opp_m = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    rec = {
        "label": label, "seed": seed, "seat": seat,
        "my_d29": my, "opp_d29": opp_m, "margin": my - opp_m,
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20),
        "melon_sold": melon_sold_qty, "melon_rev": melon_revenue,
        "melon_shed_d10": day_melon_shed.get(10), "melon_inv_d10": day_melon_inv.get(10),
        "plant_melon_cmds": plant_melon_n, "harvest_cmds": harvest_n,
        "wheat_sold": wheat_sold, "milk_sold": milk_sold,
    }
    print(f"{label} s{seed} seat{seat}: d10={rec['d10']} d15={rec['d15']} d29={my:.0f} "
          f"melon$={melon_revenue:.0f} q={melon_sold_qty} shed10={rec['melon_shed_d10']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            rows.append(run_one("B0", seed, seat))
            rows.append(run_one("B1", seed, seat))

    out = ROOT / "p13_1_melon_counterfactual.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n=== PAIRED B1-B0 ===")
    print(f"{'seed':>4} {'seat':>4} {'B0d10':>8} {'B1d10':>8} {'Δd10':>8} "
          f"{'B0d15':>8} {'B1d15':>8} {'Δd15':>8} {'B1melon$':>10}")
    b0 = {(r["seed"], r["seat"]): r for r in rows if r["label"] == "B0"}
    b1 = {(r["seed"], r["seat"]): r for r in rows if r["label"] == "B1"}
    d10s, d15s, revs = [], [], []
    for key in sorted(b0):
        a, b = b0[key], b1[key]
        dd10 = (b.get("d10") or 0) - (a.get("d10") or 0)
        dd15 = (b.get("d15") or 0) - (a.get("d15") or 0)
        d10s.append(dd10)
        d15s.append(dd15)
        revs.append(b.get("melon_rev") or 0)
        print(f"{key[0]:4d} {key[1]:4d} {a.get('d10') or 0:8.0f} {b.get('d10') or 0:8.0f} {dd10:+8.0f} "
              f"{a.get('d15') or 0:8.0f} {b.get('d15') or 0:8.0f} {dd15:+8.0f} {b.get('melon_rev') or 0:10.0f}")
    print(f"\nmean Δd10={sum(d10s)/len(d10s):+.0f}  Δd15={sum(d15s)/len(d15s):+.0f}  "
          f"B1 melon$={sum(revs)/len(revs):.0f}")
    b0_bank = sum(r["my_d29"] for r in rows if r["label"]=="B0")/4
    b1_bank = sum(r["my_d29"] for r in rows if r["label"]=="B1")/4
    print(f"mean bank B0={b0_bank:.0f} B1={b1_bank:.0f}")

    # cash trajectory dump
    out2 = ROOT / "p13_1_cash_trajectory.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "seed", "seat", "d5", "d10", "d15", "d20", "d29",
                    "melon_sold", "melon_rev", "plant_melon_cmds", "wheat_sold", "milk_sold"])
        for r in rows:
            w.writerow([r["label"], r["seed"], r["seat"], r["d5"], r["d10"], r["d15"],
                        r["d20"], r["my_d29"], r["melon_sold"], r["melon_rev"],
                        r["plant_melon_cmds"], r["wheat_sold"], r["milk_sold"]])
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
