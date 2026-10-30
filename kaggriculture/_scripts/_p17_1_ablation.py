# -*- coding: utf-8 -*-
"""P17.1 strict gate: backbone vs continuation library. 8 games vs R2.

Rule: if library not stably >= backbone, STOP branch paradigm.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p171_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(label, library_on, seed, seat):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p16_branch
    import p17_1_library as lib
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)   # backbone lifecycle
    p14_1_on.set_enabled(True)      # backbone portfolio
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    lib.set_enabled(library_on)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    tail_hits = []

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            try:
                st = pmod.debug_state() or {}
            except Exception:
                st = {}
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
        "label": label, "library": int(library_on), "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op, "win": int(my > op),
        "bankrupt": int(my < 1000),
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20), "d29": day_cash.get(29),
        "tail": lib.active_tail() if library_on else "MAIN",
    }
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} "
          f"d10={rec['d10']} d15={rec['d15']} d29={my:.0f} tail={rec['tail']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            rows.append(run("BACKBONE", False, seed, seat))
            rows.append(run("LIB", True, seed, seat))

    out = ROOT / "p17_1_local_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(lab, k):
        v = [r[k] for r in rows if r["label"] == lab and r.get(k) is not None]
        return sum(v) / len(v) if v else 0

    print("\n=== SUMMARY ===")
    for lab in ("BACKBONE", "LIB"):
        wins = sum(r["win"] for r in rows if r["label"] == lab)
        print(f"{lab}: {wins}/8 bank={mean(lab,'my'):.0f} d15={mean(lab,'d15'):.0f} "
              f"d29={mean(lab,'my'):.0f} bankrupt={sum(r['bankrupt'] for r in rows if r['label']==lab)}")
    print("\n=== PAIRED LIB-BACKBONE ===")
    n_pos = 0
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            b = next(r for r in rows if r["label"]=="BACKBONE" and r["seed"]==seed and r["seat"]==seat)
            l = next(r for r in rows if r["label"]=="LIB" and r["seed"]==seed and r["seat"]==seat)
            d = l["my"] - b["my"]
            if d > 0:
                n_pos += 1
            print(f"  s{seed} seat{seat}: B={b['my']:.0f} L={l['my']:.0f} Δ={d:+.0f} tail={l['tail']}")
    print(f"LIB better: {n_pos}/8")

    ab = ROOT / "p17_1_ablation.csv"
    with open(ab, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arm", "wins", "bank", "d15", "d29", "lib_better_pairs", "bankrupt"])
        for lab in ("BACKBONE", "LIB"):
            wins = sum(r["win"] for r in rows if r["label"] == lab)
            w.writerow([lab, wins, round(mean(lab, "my")), round(mean(lab, "d15")),
                        round(mean(lab, "my")), n_pos if lab=="LIB" else "",
                        sum(r["bankrupt"] for r in rows if r["label"]==lab)])
    print("wrote", out.name, ab.name)


if __name__ == "__main__":
    main()
