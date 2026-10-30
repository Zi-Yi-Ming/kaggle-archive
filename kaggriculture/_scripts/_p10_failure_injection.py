# -*- coding: utf-8 -*-
"""P10: failure injection — corrupt R2 actions, see if recovery happens."""
from __future__ import annotations

import csv
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make


def load_r2(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def inject(action, step, kind):
    """Corrupt one action at a given step. Return (action, injected)."""
    if step != 48:  # inject once mid-early game
        return action, False
    a = dict(action)
    market = list(a.get("market") or [])
    if kind == "sell_zero":
        market = market + [["SELL", "MELON", 5]]  # likely 0 stock early
    elif kind == "buy_impossible":
        market = market + [["BUY_ANIMAL", "COW", 99]]  # no cash
    elif kind == "plant_weed_force":
        # force farmer DIG-like invalid: PLANT on current tile regardless
        a["farmer"] = ["PLANT", "MELON"]  # may no-op
    elif kind == "invalid_op":
        a["farmer"] = ["FLY"]
        market = market + [["SELL", "NOT_AN_ITEM", 3]]
    a["market"] = market[:10]
    return a, True


def run(kind, seed=1, inject_step=48):
    r2 = load_r2(f"inj_{kind}_{seed}")
    injected = {"done": False}
    bank_trace = []

    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        a = r2(obs)
        if not injected["done"]:
            a, hit = inject(a, step, kind)
            if hit:
                injected["done"] = True
        return a

    from _pm_pool import load_agent as load_pool
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([agent, load_pool("fallow_finn")])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    # recovery: bank vs baseline without injection
    return {"kind": kind, "seed": seed, "bank": bank, "errors": err, "injected": injected["done"]}


def baseline(seed=1):
    r2 = load_r2(f"base_{seed}")
    from _pm_pool import load_agent as load_pool
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([r2, load_pool("fallow_finn")])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"])


def main():
    print("=== baseline seed1 ===", flush=True)
    base = baseline(1)
    print(f"  bank={base:.0f}", flush=True)
    rows = []
    for kind in ("sell_zero", "buy_impossible", "plant_weed_force", "invalid_op"):
        try:
            r = run(kind, seed=1)
            r["baseline_bank"] = base
            r["delta"] = r["bank"] - base
            r["recovered"] = r["delta"] > -5000 and not r["errors"]
            rows.append(r)
            print(f"  {kind}: bank={r['bank']:.0f} d={r['delta']:+.0f} err={r['errors']} rec={r['recovered']}", flush=True)
        except Exception as e:
            import traceback
            print("FAIL", kind, e)
            traceback.print_exc()
            rows.append({"kind": kind, "seed": 1, "bank": None, "errors": str(e), "injected": False})

    # also uninjected control
    print(f"  control: bank={base:.0f}", flush=True)
    rows.append({"kind": "control", "seed": 1, "bank": base, "errors": [], "injected": False,
                 "baseline_bank": base, "delta": 0, "recovered": True})

    with open(ROOT / "p10_failure_injection.csv", "w", newline="", encoding="utf-8") as f:
        keys = sorted({k for r in rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("wrote p10_failure_injection.csv")


if __name__ == "__main__":
    main()
