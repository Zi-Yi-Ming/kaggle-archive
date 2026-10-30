# -*- coding: utf-8 -*-
"""P10.1 snapshot parity + failure regression."""
from __future__ import annotations

import csv
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p10_executor.core import TacticalExecutor  # noqa: E402
from p10_executor.intents import Intent  # noqa: E402
from p10_executor.validators import sanitize_action  # noqa: E402


def load_r2(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def harvest_snapshots(n_games=2, seeds=(1, 2)):
    """Run R2 vs finn; collect (obs, r2_action) at day boundaries + a few mid steps."""
    snaps = []
    for seed in seeds:
        r2 = load_r2(f"harv{seed}")
        from _pm_pool import load_agent as load_pool
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.configuration["seed"] = seed
        env.run([r2, load_pool("fallow_finn")])
        for idx, step in enumerate(env.steps):
            rec = step[0] or {}
            obs = rec.get("observation")
            act = rec.get("action") or {}
            if not isinstance(obs, dict):
                continue
            st = obs.get("step")
            st = int(st) if st is not None else idx
            if st % 24 == 0 or st in (48, 100, 200, 400, 717, 718):
                snaps.append({"seed": seed, "step": st, "obs": obs, "r2_action": dict(act)})
    return snaps


def parity_one(snap):
    ex = TacticalExecutor()
    obs = snap["obs"]
    # map R2 action to a comparable sanitized form
    r2 = snap["r2_action"]
    shed = ((obs.get("private") or {}).get("shed")) or {}
    money = float(((obs.get("farms") or [{}])[0] or {}).get("money") or 0)
    prices = ((obs.get("market") or {}).get("prices")) or {}
    r2s = sanitize_action(r2, shed=shed, money=money, prices=prices)
    # choose intent by heuristic for parity of *validity*, not full action match
    step = int(obs.get("step") or 0)
    if step >= 717:
        intent = Intent.LIQUIDATE
    elif any(v > 0 for v in shed.values()) and step % 24 >= 20:
        intent = Intent.SELL_AVAILABLE
    else:
        intent = Intent.MAINTAIN_PRODUCTION
    er = ex.step(obs, intent)
    # validity: executor action must be clamped-safe
    es = er.action
    ok_sell = True
    for o in es.get("market") or []:
        if o[0] == "SELL" and int(shed.get(o[1]) or 0) < int(o[2] or 0):
            ok_sell = False
    r2_sell_ok = True
    for o in r2s.get("market") or []:
        if o[0] == "SELL" and int(shed.get(o[1]) or 0) < int(o[2] or 0):
            r2_sell_ok = False
    return {
        "step": step,
        "intent": intent.value,
        "status": er.status.value if hasattr(er.status, "value") else str(er.status),
        "r2_valid_sell": r2_sell_ok,
        "ex_valid_sell": ok_sell,
        "r2_n_orders": len(r2s.get("market") or []),
        "ex_n_orders": len(es.get("market") or []),
        "r2_farmer": r2s.get("farmer"),
        "ex_farmer": es.get("farmer"),
        "same_farmer": r2s.get("farmer") == es.get("farmer"),
    }


def main():
    print("=== harvest snapshots ===", flush=True)
    snaps = harvest_snapshots()
    print(f"n_snaps={len(snaps)}", flush=True)
    rows = [parity_one(s) for s in snaps]
    valid = sum(1 for r in rows if r["ex_valid_sell"])
    print(f"executor sell-valid: {valid}/{len(rows)}")
    print(f"R2 sell-valid: {sum(1 for r in rows if r['r2_valid_sell'])}/{len(rows)}")
    # farmer match is not required — different intents
    print(f"same farmer (not required): {sum(1 for r in rows if r['same_farmer'])}/{len(rows)}")
    for r in rows[:: max(1, len(rows)//10)]:
        print(f"  s{r['step']} intent={r['intent']} status={r['status']} "
              f"ex_ok={r['ex_valid_sell']} r2_ok={r['r2_valid_sell']} "
              f"ex_mkt={r['ex_n_orders']} r2_mkt={r['r2_n_orders']}")

    with open(ROOT / "p10_1_snapshot_parity.csv", "w", newline="", encoding="utf-8") as f:
        keys = list(rows[0].keys()) if rows else []
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("wrote p10_1_snapshot_parity.csv")

    # failure regression
    print("\n=== failure regression ===", flush=True)
    fr = []
    cases = [
        ("empty_sell", {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MELON", 5]]}, {"WHEAT": 2}, 0),
        ("no_cash_buy", {"farmer": ["PASS"], "hands": [], "market": [["BUY_ANIMAL", "COW", 9]]}, {}, 10),
        ("invalid_plant", {"farmer": ["FLY"], "hands": [], "market": []}, {}, 1000),
        ("garbage", {"farmer": ["X"], "hands": [], "market": [["SELL", "NOPE", 1], ["SELL", "WHEAT", 99]]}, {"WHEAT": 3}, 500),
    ]
    for name, action, shed, money in cases:
        out = sanitize_action(action, shed=shed, money=money, prices={"WHEAT": 25, "MELON": 250, "COW": 400})
        bad = False
        for o in out["market"]:
            if o[0] == "SELL" and int(shed.get(o[1]) or 0) < int(o[2] or 0):
                bad = True
        if out["farmer"] not in (["PASS"], ["NORTH"], ["SOUTH"], ["EAST"], ["WEST"]) and out["farmer"][0] not in (
            "WATER", "HARVEST", "FEED", "CARE", "DIG", "PLANT", "PICKUP", "PLACE", "PASS"
        ):
            bad = True
        fr.append({"case": name, "pass": not bad, "farmer": str(out["farmer"]), "market": str(out["market"])})
        print(f"  {name}: {'PASS' if not bad else 'FAIL'} {out['farmer']} {out['market']}")
    with open(ROOT / "p10_1_failure_regression.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["case", "pass", "farmer", "market"])
        w.writeheader()
        w.writerows(fr)
    print("wrote p10_1_failure_regression.csv")


if __name__ == "__main__":
    main()
