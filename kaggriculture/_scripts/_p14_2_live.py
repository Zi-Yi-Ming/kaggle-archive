# -*- coding: utf-8 -*-
"""P14.2 live: joint portfolio+water vs R2. 8 games. Compare to P14.1 crop-only."""
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
        "r2_jp_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(label, seed, seat, joint, crop_pf, water):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(water)
    p14_1_on.set_enabled(crop_pf)
    p14_2_on.set_enabled(joint)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    animals = defaultdict(lambda: defaultdict(int))
    plants = defaultdict(lambda: defaultdict(int))
    rev = defaultdict(lambda: defaultdict(float))
    notes = []

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            ca = cs = cg = 0
            for row in farm.get("tiles") or []:
                for t in row:
                    if isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            plants[day][t.get("crop")] += 1
                        a = t.get("animal")
                        if a == "COW":
                            ca += 1
                        elif a == "SHEEP":
                            cs += 1
                        elif a == "GOOSE":
                            cg += 1
            animals[day]["COW"] = ca
            animals[day]["SHEEP"] = cs
            animals[day]["GOOSE"] = cg
            prices = dict((obs.get("market") or {}).get("prices") or {})
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    item, q = o[1], int(o[2] or 0)
                    rev[day][item] += q * int(prices.get(item) or 0)
            if step == 0:
                # grab planner notes if any
                try:
                    st = pmod.debug_state()
                    notes.append(str(st))
                except Exception:
                    pass
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])

    def a_at(d, k):
        return animals.get(d, {}).get(k, 0)

    rec = {
        "label": label, "joint": int(joint), "crop_pf": int(crop_pf), "water": int(water),
        "seed": seed, "seat": seat, "my": my, "opp": op, "margin": my - op,
        "win": int(my > op), "bankrupt": int(my < 1000),
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20), "d29": day_cash.get(29),
        "COW_d10": a_at(10, "COW"), "SHEEP_d10": a_at(10, "SHEEP"), "GOOSE_d10": a_at(10, "GOOSE"),
        "COW_d20": a_at(20, "COW"), "SHEEP_d20": a_at(20, "SHEEP"),
        "MELON_d10": plants.get(10, {}).get("MELON", 0),
        "WHEAT_d5": plants.get(5, {}).get("WHEAT", 0),
        "rev_MELON": sum(rev[d].get("MELON", 0) for d in rev),
        "rev_MILK": sum(rev[d].get("MILK", 0) for d in rev),
        "rev_WOOL": sum(rev[d].get("WOOL", 0) for d in rev),
        "rev_EGG": sum(rev[d].get("EGG", 0) for d in rev),
        "rev_FERT": sum(rev[d].get("FERTILIZER", 0) for d in rev),
        "rev_WHEAT": sum(rev[d].get("WHEAT", 0) for d in rev),
    }
    rec["rev_animal"] = rec["rev_MILK"] + rec["rev_WOOL"] + rec["rev_EGG"]
    rec["rev_total"] = sum(sum(rev[d].values()) for d in rev)
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} d15={rec['d15']} d29={my:.0f} "
          f"an10={rec['COW_d10']}C/{rec['SHEEP_d10']}S/{rec['GOOSE_d10']}G "
          f"M10={rec['MELON_d10']} mrev={rec['rev_MELON']:.0f} arev={rec['rev_animal']:.0f}", flush=True)
    return rec


def main():
    rows = []
    # Ablation arms
    # B0: no joint, no crop pf, no water
    # PF: crop portfolio + water (P14.1)
    # JOINT: joint + water
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            rows.append(run("B0", seed, seat, False, False, False))
            rows.append(run("PF14.1", seed, seat, False, True, True))
            rows.append(run("JOINT", seed, seat, True, False, True))

    out = ROOT / "p14_2_local_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(lab, k):
        v = [r[k] for r in rows if r["label"] == lab and r.get(k) is not None]
        return sum(v) / len(v) if v else 0

    print("\n=== SUMMARY ===")
    for lab in ("B0", "PF14.1", "JOINT"):
        wins = sum(r["win"] for r in rows if r["label"] == lab)
        print(f"{lab}: {wins}/8 bank={mean(lab,'my'):.0f} d15={mean(lab,'d15'):.0f} "
              f"d29={mean(lab,'my'):.0f} C10={mean(lab,'COW_d10'):.1f} S10={mean(lab,'SHEEP_d10'):.1f} "
              f"M10={mean(lab,'MELON_d10'):.1f} mrev={mean(lab,'rev_MELON'):.0f} "
              f"arev={mean(lab,'rev_animal'):.0f} bankrupt={sum(r['bankrupt'] for r in rows if r['label']==lab)}")
    # ablation
    ab = ROOT / "p14_2_ablation.csv"
    with open(ab, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arm", "wins", "bank", "d15", "d29", "COW_d10", "SHEEP_d10", "MELON_d10",
                    "melon_rev", "animal_rev", "bankrupt"])
        for lab in ("B0", "PF14.1", "JOINT"):
            wins = sum(r["win"] for r in rows if r["label"] == lab)
            w.writerow([lab, wins, round(mean(lab, "my")), round(mean(lab, "d15")),
                        round(mean(lab, "my")), round(mean(lab, "COW_d10"), 1),
                        round(mean(lab, "SHEEP_d10"), 1), round(mean(lab, "MELON_d10"), 1),
                        round(mean(lab, "rev_MELON")), round(mean(lab, "rev_animal")),
                        sum(r["bankrupt"] for r in rows if r["label"] == lab)])
    print("wrote", out.name, ab.name)


if __name__ == "__main__":
    main()
