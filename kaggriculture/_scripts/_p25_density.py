# -*- coding: utf-8 -*-
"""P25: local action-bundle perturbation density around R2.

Mutate only 1–2 steps at a chosen day. Keep R2 elsewhere.
Compare bank vs T0 pure R2 (same seed, vs fallow_finn).
No NN. No PPO. No submit.
"""
from __future__ import annotations

import copy
import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p25_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_finn():
    from _pm_pool import load_agent
    return load_agent("fallow_finn")


def mutate_action(action, kind):
    a = copy.deepcopy(action) if action else {"farmer": ["PASS"], "hands": [], "market": []}
    market = [o for o in (a.get("market") or []) if o]
    if kind == "DROP_SELL":
        a["market"] = [o for o in market if o[0] != "SELL"]
    elif kind == "SKIP_HIRE":
        a["market"] = [o for o in market if o[0] != "HIRE"]
    elif kind == "NO_WORK":
        a["farmer"] = ["PASS"]
        a["hands"] = []
    elif kind == "DROP_BUY":
        a["market"] = [o for o in market if o[0] not in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "BUY_LAND")]
    return a


def make_perturbed(r2_agent, day, n_steps, kind):
    state = {"left": n_steps}

    def agent(obs, configuration=None):
        action = r2_agent(obs, configuration)
        step = int(obs.get("step") or 0)
        d = step // 24
        if d == day and state["left"] > 0:
            state["left"] -= 1
            return mutate_action(action, kind)
        return action

    return agent


def run_vs_finn(own, seed, seat=0):
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = load_finn()
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    return my, op


def main():
    rows = []
    kinds = ("DROP_SELL", "SKIP_HIRE", "NO_WORK", "DROP_BUY")
    days = (4, 7, 10, 14, 20, 25)
    n_steps = 2
    for seed in (1, 2, 3):
        t0, _ = run_vs_finn(load_r2(), seed)
        print(f"\n=== seed {seed} T0 R2 bank={t0:.0f} ===", flush=True)
        for day in days:
            for kind in kinds:
                own = make_perturbed(load_r2(), day, n_steps, kind)
                my, op = run_vs_finn(own, seed)
                delta = my - t0
                rec = {
                    "seed": seed, "day": day, "kind": kind, "n_steps": n_steps,
                    "bank": my, "t0": t0, "delta": delta, "positive": int(delta > 0),
                }
                rows.append(rec)
                print(f"  d{day:02d} {kind:10s} bank={my:.0f} Δ={delta:+.0f}", flush=True)

    out = ROOT / "p25_mutation_density.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    deltas = [r["delta"] for r in rows]
    pos = sum(1 for d in deltas if d > 0)
    n = len(deltas)
    print("\n=== DENSITY ALL SEEDS ===")
    print(f"  n={n} positive={pos}/{n} ({100*pos/n:.0f}%)")
    print(f"  meanΔ={sum(deltas)/n:+.0f} medianΔ={sorted(deltas)[n//2]:+.0f}")
    print(f"  best={max(deltas):+.0f} worst={min(deltas):+.0f}")
    print("  by kind:")
    for kind in kinds:
        ds = [r["delta"] for r in rows if r["kind"] == kind]
        p = sum(1 for d in ds if d > 0)
        print(f"    {kind:10s} pos={p}/{len(ds)} mean={sum(ds)/len(ds):+.0f}")
    print("  by day:")
    for day in days:
        ds = [r["delta"] for r in rows if r["day"] == day]
        p = sum(1 for d in ds if d > 0)
        print(f"    d{day:02d} pos={p}/{len(ds)} mean={sum(ds)/len(ds):+.0f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
