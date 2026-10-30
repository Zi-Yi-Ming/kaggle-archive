# -*- coding: utf-8 -*-
"""P12.1: worker action accounting R2 vs B-stack. Measure first, no routing change."""
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
# WATER/FERTILIZE count as useful crop work; DIG is maintenance
MAINT = {"DIG", "COLLECT_FERTILIZER"}
CARGO = {"PICKUP", "DROP", "PLACE"}
SELL_OPS = {"SELL"}
BUY_OPS = {"BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "BUY_LAND", "HIRE"}


def classify(cmd):
    if not cmd:
        return "NOOP"
    op = cmd[0]
    if op in MOVE:
        return "MOVE"
    if op in USEFUL:
        return op
    if op in MAINT:
        return op
    if op in CARGO:
        return op
    if op == "PASS":
        return "NOOP"
    return op


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_acct_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_b():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def run_accounting(own_factory, opp_factory, seed, own_seat, label):
    own = own_factory()
    opp = opp_factory()
    agents = [None, None]
    agents[own_seat] = own
    agents[1 - own_seat] = opp

    # per-day counters for own seat only
    day_ops = defaultdict(Counter)
    day_cash = {}
    day_hands = {}
    day_useful = defaultdict(int)
    day_move = defaultdict(int)
    day_pickup = defaultdict(int)
    day_noop = defaultdict(int)
    day_total = defaultdict(int)

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            day_hands[day] = len(farm.get("hands") or [])
            cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            for c in cmds:
                k = classify(c)
                day_ops[day][k] += 1
                day_total[day] += 1
                if k in USEFUL or k in ("DIG", "COLLECT_FERTILIZER"):
                    day_useful[day] += 1
                if k == "MOVE":
                    day_move[day] += 1
                if k == "PICKUP":
                    day_pickup[day] += 1
                if k == "NOOP":
                    day_noop[day] += 1
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([
        wrap(agents[0], own_seat == 0),
        wrap(agents[1], own_seat == 1),
    ])
    f = env.steps[-1]
    final = float(f[own_seat]["observation"]["farms"][own_seat]["money"])

    rows = []
    for day in range(30):
        tot = day_total[day] or 1
        useful = day_useful[day]
        move = day_move[day]
        pickup = day_pickup[day]
        noop = day_noop[day]
        rows.append({
            "label": label, "seed": seed, "seat": own_seat, "day": day,
            "cash": day_cash.get(day),
            "hands": day_hands.get(day),
            "total_worker_cmds": day_total[day],
            "useful": useful,
            "move": move,
            "pickup": pickup,
            "noop": noop,
            "feed": day_ops[day].get("FEED", 0),
            "plant": day_ops[day].get("PLANT", 0),
            "harvest": day_ops[day].get("HARVEST", 0),
            "water": day_ops[day].get("WATER", 0),
            "care": day_ops[day].get("CARE", 0),
            "build": day_ops[day].get("BUILD_COOP", 0) + day_ops[day].get("BUILD_PASTURE", 0),
            "drop": day_ops[day].get("DROP", 0),
            "place": day_ops[day].get("PLACE", 0),
            "collect_fert": day_ops[day].get("COLLECT_FERTILIZER", 0),
            "useful_ratio": useful / tot,
            "pickup_ratio": pickup / tot,
            "move_ratio": move / tot,
            "noop_ratio": noop / tot,
            "move_per_useful": (move / useful) if useful else None,
        })
    meta = {"label": label, "seed": seed, "seat": own_seat, "final": final}
    return rows, meta


def main():
    all_rows = []
    metas = []
    for seat in (0, 1):
        for seed in (1, 2):
            rows, meta = run_accounting(load_b, load_r2, seed, seat, "B")
            all_rows.extend(rows)
            metas.append(meta)
            print(f"B  s{seed} seat{seat} final={meta['final']:.0f}", flush=True)
            rows, meta = run_accounting(load_r2, load_b, seed, seat, "R2")
            all_rows.extend(rows)
            metas.append(meta)
            print(f"R2 s{seed} seat{seat} final={meta['final']:.0f}", flush=True)

    out = ROOT / "p12_1_worker_accounting.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    # daywise summary
    out2 = ROOT / "p12_1_daywise_productivity.csv"
    sum_rows = []
    for day in range(30):
        for label in ("R2", "B"):
            sub = [r for r in all_rows if r["label"] == label and r["day"] == day]
            if not sub:
                continue
            def m(k):
                v = [r[k] for r in sub if r.get(k) is not None]
                return sum(v) / len(v) if v else None
            sum_rows.append({
                "day": day, "label": label,
                "cash": m("cash"), "hands": m("hands"),
                "total": m("total_worker_cmds"), "useful": m("useful"),
                "move": m("move"), "pickup": m("pickup"), "noop": m("noop"),
                "feed": m("feed"), "plant": m("plant"), "harvest": m("harvest"),
                "water": m("water"), "care": m("care"),
                "useful_ratio": m("useful_ratio"), "pickup_ratio": m("pickup_ratio"),
                "move_ratio": m("move_ratio"), "move_per_useful": m("move_per_useful"),
            })
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sum_rows[0].keys()))
        w.writeheader()
        w.writerows(sum_rows)

    print("\n=== d0-d10 mean productivity ===")
    print(f"{'d':>3} {'lab':>3} {'cash':>8} {'hands':>5} {'useful':>7} {'move':>6} {'pickup':>6} "
          f"{'feed':>5} {'plant':>5} {'harv':>5} {'use%':>5} {'pku%':>5} {'mv/u':>5}")
    for day in range(11):
        for label in ("R2", "B"):
            r = next((x for x in sum_rows if x["day"] == day and x["label"] == label), None)
            if not r:
                continue
            mu = r["move_per_useful"]
            print(f"{day:3d} {label:>3} {r['cash'] or 0:8.0f} {r['hands'] or 0:5.1f} "
                  f"{r['useful'] or 0:7.1f} {r['move'] or 0:6.1f} {r['pickup'] or 0:6.1f} "
                  f"{r['feed'] or 0:5.1f} {r['plant'] or 0:5.1f} {r['harvest'] or 0:5.1f} "
                  f"{(r['useful_ratio'] or 0):5.2f} {(r['pickup_ratio'] or 0):5.2f} "
                  f"{(mu if mu is not None else -1):5.2f}")

    # early windows
    print("\n=== windows mean useful / pickup / cash ===")
    for lo, hi, name in ((0, 3, "d0-3"), (4, 6, "d4-6"), (7, 10, "d7-10"), (11, 15, "d11-15")):
        for label in ("R2", "B"):
            sub = [r for r in all_rows if r["label"] == label and lo <= r["day"] <= hi]
            def m(k):
                v = [r[k] for r in sub if r.get(k) is not None]
                return sum(v) / len(v) if v else 0
            print(f"  {name} {label}: useful={m('useful'):.1f} pickup={m('pickup'):.1f} "
                  f"move={m('move'):.1f} feed={m('feed'):.1f} plant={m('plant'):.1f} "
                  f"cash_end={m('cash'):.0f} use%={m('useful_ratio'):.2f} pku%={m('pickup_ratio'):.2f}")

    # route gap table
    out3 = ROOT / "p12_1_route_gap.csv"
    with open(out3, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day", "r2_useful", "b_useful", "useful_gap",
                    "r2_pickup", "b_pickup", "pickup_gap",
                    "r2_move", "b_move", "move_gap",
                    "r2_use_ratio", "b_use_ratio",
                    "r2_cash", "b_cash", "cash_gap"])
        for day in range(30):
            rr = next((x for x in sum_rows if x["day"] == day and x["label"] == "R2"), None)
            bb = next((x for x in sum_rows if x["day"] == day and x["label"] == "B"), None)
            if not rr or not bb:
                continue
            w.writerow([
                day, rr["useful"], bb["useful"], (rr["useful"] or 0) - (bb["useful"] or 0),
                rr["pickup"], bb["pickup"], (rr["pickup"] or 0) - (bb["pickup"] or 0),
                rr["move"], bb["move"], (rr["move"] or 0) - (bb["move"] or 0),
                rr["useful_ratio"], bb["useful_ratio"],
                rr["cash"], bb["cash"], (rr["cash"] or 0) - (bb["cash"] or 0),
            ])
    print("\nwrote", out.name, out2.name, out3.name)


if __name__ == "__main__":
    main()
