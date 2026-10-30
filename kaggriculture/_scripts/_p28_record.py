# -*- coding: utf-8 -*-
"""P28a: record R2 state-action trajectories under pinned seed."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from p26_harness import load_r2, load_pool, run_game  # noqa: E402


def record_trajectory(seed: int):
    """Run R2 vs finn; dump day-boundary states + all market ops + worker op counts."""
    r2 = load_r2()
    finn = load_pool("fallow_finn")
    steps = []

    def wrap_r2(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            market = a.get("market") or []
            farmer = a.get("farmer") or []
            hands = a.get("hands") or []
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            shed = dict(private.get("shed") or {})
            seeds = dict(private.get("seeds") or {})
            tiles = farm.get("tiles") or []
            plants = melon = animals = empty = 0
            for row in tiles:
                for t in row:
                    if t is None:
                        empty += 1
                    elif isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            plants += 1
                            if t.get("crop") == "MELON":
                                melon += 1
                        if t.get("animal"):
                            animals += 1
            steps.append({
                "step": step, "day": step // 24, "hour": step % 24,
                "money": float(farm.get("money") or 0),
                "hands": len(hands), "hires_today": int(farm.get("hires_today") or 0),
                "n_land": len(farm.get("unlocked_quadrants") or []),
                "plants": plants, "melon": melon, "animals": animals, "empty": empty,
                "shed": shed, "seeds": seeds, "shops": shops,
                "market": market, "farmer": farmer, "n_hands_cmd": len(hands),
                "worker_ops": [c[0] if c else "PASS" for c in [farmer] + list(hands)],
            })
            return a
        return agent

    env_hack = None
    # use kaggle make directly for full trajectory
    from kaggle_environments import make
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap_r2(r2), finn])
    f = env.steps[-1]
    bank0 = float(f[0]["observation"]["farms"][0]["money"])
    bank1 = float(f[1]["observation"]["farms"][1]["money"])
    return steps, bank0, bank1


def main():
    all_steps = []
    banks = []
    for seed in (1, 2, 3, 4, 5):
        steps, b0, b1 = record_trajectory(seed)
        for s in steps:
            s["seed"] = seed
            s["bank_end"] = b0
            all_steps.append(s)
        banks.append({"seed": seed, "bank_r2": b0, "bank_finn": b1})
        print(f"seed{seed}: R2={b0:.0f} finn={b1:.0f} n_steps={len(steps)}", flush=True)

    out = ROOT / "p28_r2_trajectories.csv"
    # flatten json fields
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "step", "day", "hour", "money", "hands", "hires_today",
                    "n_land", "plants", "melon", "animals", "empty",
                    "shed_total", "n_shops", "market_ops", "worker_ops", "bank_end"])
        for s in all_steps:
            mops = "|".join(o[0] for o in (s["market"] or []) if o)
            wops = "|".join(s["worker_ops"])
            w.writerow([
                s["seed"], s["step"], s["day"], s["hour"], s["money"], s["hands"],
                s["hires_today"], s["n_land"], s["plants"], s["melon"], s["animals"],
                s["empty"], sum(int(v or 0) for v in s["shed"].values()),
                len(s["shops"]), mops, wops, s["bank_end"],
            ])
    out2 = ROOT / "p28_r2_banks.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(banks[0].keys()))
        w.writeheader()
        w.writerows(banks)
    print("wrote", out.name, "rows", len(all_steps))


if __name__ == "__main__":
    main()
