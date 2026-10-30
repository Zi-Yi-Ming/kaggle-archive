# -*- coding: utf-8 -*-
"""Dump R2 mid-game farm snapshots + action market lists for grammar design."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_agent(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def main():
    r2 = load_agent(ROOT / "_push_medal" / "main.py", "r2dump")
    finn = load_agent(ROOT / "reference_agents" / "fallow_finn.py", "finndump")
    markets = []

    def wrap(inner, bag):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            bag.append({
                "step": int(obs.get("step") or 0),
                "market": a.get("market"),
                "n_hands": len(a.get("hands") or []),
                "n_farmer": 1,
            })
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = 1
    env.run([wrap(r2, markets), finn])

    out = []
    for si in (24, 48, 144, 216, 288, 360, 432, 504, 576, 648, 719):
        f = env.steps[si][0]["observation"]
        farm = f["farms"][0]
        tiles = farm.get("tiles") or []
        empty = plants = animals = 0
        crops = {}
        for row in tiles:
            for t in row:
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        plants += 1
                        c = t.get("crop")
                        crops[c] = crops.get(c, 0) + 1
                    if t.get("animal"):
                        animals += 1
        private = f.get("private") or {}
        shed = private.get("shed")
        seeds = private.get("seeds")
        # market actions this step
        mk = markets[si]["market"] if si < len(markets) else None
        out.append({
            "step": si,
            "money": farm.get("money"),
            "hands": len(farm.get("hands") or []),
            "hires_today": farm.get("hires_today"),
            "land": len(farm.get("unlocked_quadrants") or []),
            "grid": [len(tiles), len(tiles[0]) if tiles else 0],
            "empty": empty, "plants": plants, "animals": animals, "crops": crops,
            "shed": shed, "seeds": seeds,
            "market": mk,
            "shops": (f.get("town") or {}).get("unlocked_shops"),
            "prices": (f.get("market") or {}).get("prices"),
        })

    # also aggregate hire counts by day
    hire_by_day = {}
    for m in markets:
        d = m["step"] // 24
        n = sum(1 for o in (m["market"] or []) if o and o[0] == "HIRE")
        hire_by_day[d] = hire_by_day.get(d, 0) + n

    Path(ROOT / "p38_r2_snapshots.json").write_text(
        json.dumps({"snapshots": out, "hire_by_day": hire_by_day}, indent=2, default=str),
        encoding="utf-8",
    )
    for o in out:
        print("step", o["step"], "money", o["money"], "hands", o["hands"],
              "plants", o["plants"], "crops", o["crops"], "animals", o["animals"],
              "land", o["land"], "market", o["market"])
    print("hire_by_day", hire_by_day)


if __name__ == "__main__":
    main()
