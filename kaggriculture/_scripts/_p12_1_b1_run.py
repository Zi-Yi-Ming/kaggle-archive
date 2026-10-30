# -*- coding: utf-8 -*-
"""P12.1 B0 vs B1 (sticky shepherd) + R2 reference. 4 games each."""
from __future__ import annotations

import csv
import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

MOVE = {"NORTH", "SOUTH", "EAST", "WEST"}
USEFUL = {"FEED", "PLANT", "HARVEST", "CARE", "BUILD_COOP", "BUILD_PASTURE", "WATER", "FERTILIZE"}


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_rt_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def fresh_b():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def run(label, seed, seat):
    own = fresh_b()
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp
    day_pickup = defaultdict(int)
    day_useful = defaultdict(int)
    day_move = defaultdict(int)
    day_total = defaultdict(int)
    day_cash = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            for c in cmds:
                op = c[0] if c else "PASS"
                day_total[day] += 1
                if op == "PICKUP":
                    day_pickup[day] += 1
                if op in MOVE:
                    day_move[day] += 1
                if op in USEFUL:
                    day_useful[day] += 1
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
        "label": label, "seed": seed, "seat": seat, "my": my, "opp": op,
        "margin": my - op, "win": int(my > op),
    }
    for d in (3, 5, 7, 10, 15, 20, 29):
        rec[f"d{d}"] = day_cash.get(d)
    rec["pickup_d7_15"] = sum(day_pickup[d] for d in range(7, 16))
    rec["useful_d7_15"] = sum(day_useful[d] for d in range(7, 16))
    rec["move_d7_15"] = sum(day_move[d] for d in range(7, 16))
    tot = sum(day_total[d] for d in range(7, 16)) or 1
    rec["pku_ratio_d7_15"] = rec["pickup_d7_15"] / tot
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} "
          f"d7={rec['d7']} d10={rec['d10']} d15={rec['d15']} "
          f"pku7_15={rec['pickup_d7_15']} pku%={rec['pku_ratio_d7_15']:.2f}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            rows.append(run("B1_sticky", seed, seat))
    out = ROOT / "p12_1_b0_b1.csv"
    # merge with prior B0 accounting summary if present
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bank = sum(r["my"] for r in rows) / len(rows)
    d10 = [r["d10"] for r in rows if r.get("d10") is not None]
    pku = [r["pku_ratio_d7_15"] for r in rows]
    print(f"\nB1_sticky mean bank={bank:.0f}  d10={sum(d10)/len(d10) if d10 else None:.0f}  "
          f"pku%={sum(pku)/len(pku):.3f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
