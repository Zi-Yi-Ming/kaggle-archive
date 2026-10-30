# -*- coding: utf-8 -*-
"""Level 4: minimal planner + executor, full 720 steps vs finn. Not a strategy."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p10_executor.core import TacticalExecutor  # noqa: E402
from p10_executor.intents import Intent  # noqa: E402


def plan(obs):
    """Extremely simple planner — architecture harness only."""
    step = int(obs.get("step") or 0)
    day = step // 24
    me = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[me] if me < len(farms) else {}
    money = float(farm.get("money") or 0)
    shed = ((obs.get("private") or {}).get("shed")) or {}
    stock = sum(int(v or 0) for v in shed.values())
    if step >= 710:
        return Intent.LIQUIDATE
    if money < 200 and day >= 5:
        return Intent.RECOVER
    if stock >= 8:
        return Intent.SELL_AVAILABLE
    return Intent.MAINTAIN_PRODUCTION


def run(seed=1, opponent="fallow_finn"):
    ex = TacticalExecutor()
    from _pm_pool import load_agent as load_pool
    def agent(obs, configuration=None):
        intent = plan(obs)
        return ex.step(obs, intent).action
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([agent, load_pool(opponent)])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    return bank, err


def main():
    rows = []
    for seed in (1, 2, 3):
        try:
            bank, err = run(seed)
            rows.append({"seed": seed, "bank": bank, "errors": err, "bankrupt": bank < 1000})
            print(f"  seed{seed}: bank={bank:.0f} err={err} bankrupt={bank<1000}", flush=True)
        except Exception as e:
            print("FAIL", seed, e)
            rows.append({"seed": seed, "bank": None, "errors": str(e), "bankrupt": True})
    n_ok = sum(1 for r in rows if r["bank"] and not r["bankrupt"] and not r["errors"])
    print(f"\nLevel4: {n_ok}/{len(rows)} complete without crash/bankrupt")
    path = ROOT / "p10_1_level4_planner.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["seed", "bank", "errors", "bankrupt"])
        w.writeheader()
        w.writerows(rows)
    print("wrote", path)


if __name__ == "__main__":
    main()
