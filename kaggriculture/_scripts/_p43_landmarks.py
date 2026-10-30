# -*- coding: utf-8 -*-
"""P43: immutable sell/phase landmarks across 5 elites (seed1 vs finn)."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

AGENTS = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "rayk_c95": ROOT / "_external" / "p41_extracted" / "rayk_c95_main.py",
}


def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def record(name, path, seed=1):
    fn = load(path, f"p43_{name}")
    finn = load(ROOT / "reference_agents" / "fallow_finn.py", "finn_p43")
    sells = []
    hires_by_day = defaultdict(int)
    land_days = []
    animal_buy_days = []
    last_plants = None
    money_trace = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            day = step // 24
            for o in a.get("market") or []:
                if not o:
                    continue
                if o[0] == "SELL" and len(o) >= 3:
                    sells.append((step, day, o[1], int(o[2])))
                elif o[0] == "HIRE":
                    hires_by_day[day] += 1
                elif o[0] == "BUY_LAND":
                    land_days.append(day)
                elif o[0] == "BUY_ANIMAL":
                    animal_buy_days.append(day)
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            money_trace.append((step, float(farm.get("money") or 0)))
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([wrap(fn), finn])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])

    first_sell = {}
    for st, day, item, q in sells:
        if item not in first_sell:
            first_sell[item] = (st, day, q)

    # money landmarks
    def money_at(day):
        s = day * 24
        if s < len(money_trace):
            return money_trace[s][1]
        return None

    return {
        "name": name,
        "bank": bank,
        "first_sell": first_sell,
        "n_sells": len(sells),
        "hire_days": sorted(hires_by_day.keys()),
        "hire_total": sum(hires_by_day.values()),
        "land_days": sorted(set(land_days)),
        "animal_buy_days": sorted(set(animal_buy_days))[:12],
        "money_d0": money_at(0),
        "money_d5": money_at(5),
        "money_d10": money_at(10),
        "money_d12": money_at(12),
        "money_d15": money_at(15),
        "money_d20": money_at(20),
        "money_d29": money_at(29),
    }


def main():
    rows = []
    details = {}
    for name, path in AGENTS.items():
        if not path.exists():
            print("missing", name)
            continue
        r = record(name, path)
        details[name] = r
        print(f"{name:12s} bank={r['bank']:.0f} first_sells={ {k:v[0] for k,v in sorted(r['first_sell'].items())} }")
        print(f"             land={r['land_days']} money_d10={r['money_d10']} d12={r['money_d12']} d20={r['money_d20']}")
        rows.append({
            "name": name,
            "bank": r["bank"],
            "first_WHEAT": r["first_sell"].get("WHEAT", (None,))[0],
            "first_FERT": r["first_sell"].get("FERTILIZER", (None,))[0],
            "first_WOOL": r["first_sell"].get("WOOL", (None,))[0],
            "first_MILK": r["first_sell"].get("MILK", (None,))[0],
            "first_MELON": r["first_sell"].get("MELON", (None,))[0],
            "first_EGG": r["first_sell"].get("EGG", (None,))[0],
            "first_STRAW": r["first_sell"].get("STRAWBERRY", (None,))[0],
            "land_days": "|".join(map(str, r["land_days"])),
            "money_d10": r["money_d10"],
            "money_d12": r["money_d12"],
            "money_d20": r["money_d20"],
        })

    out = ROOT / "p43_landmark_skeleton.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out.name)

    # cross-elite agreement on first-sell steps
    print("\n=== first-sell agreement (unique steps across elites) ===")
    items = ["WHEAT", "FERTILIZER", "WOOL", "MILK", "MELON", "EGG", "STRAWBERRY"]
    for item in items:
        vals = [details[n]["first_sell"][item][0] for n in details if item in details[n]["first_sell"]]
        print(f"  {item:12s} n={len(vals)} unique={sorted(set(vals))}")


if __name__ == "__main__":
    main()
