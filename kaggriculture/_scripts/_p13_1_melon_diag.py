# -*- coding: utf-8 -*-
"""Quick: are melon plants on tiles? harvested? at d8-d12 for B1."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
import p13_1_melon  # noqa: E402


def main():
    p13_1_melon.set_enabled(True)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    from _pm_pool import load_agent
    finn = load_agent("fallow_finn")
    log = []

    def agent(obs, configuration=None):
        a = pmod.agent(obs, configuration)
        step = int(obs.get("step") or 0)
        day = step // 24
        if step % 24 == 0 and 0 <= day <= 16:
            farm = obs["farms"][obs["player"]]
            tiles = farm["tiles"]
            melon_plants = 0
            any_plants = 0
            empty = 0
            for row in tiles:
                for t in row:
                    if t is None:
                        empty += 1
                    elif isinstance(t, dict) and t.get("kind") == "PLANT":
                        any_plants += 1
                        if t.get("crop") == "MELON":
                            melon_plants += 1
            shed = obs["private"]["shed"]
            seeds = obs["private"]["seeds"]
            log.append((day, float(farm["money"]), melon_plants, any_plants, empty,
                        int(seeds.get("MELON") or 0), int(shed.get("MELON") or 0),
                        int(shed.get("WHEAT") or 0)))
        return a

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 400
    env.configuration["seed"] = 1
    env.run([agent, finn])
    print("day money melon_plants all_plants empty melon_seeds shed_melon shed_wheat")
    for r in log:
        print(f"d{r[0]:02d} {r[1]:7.0f} melon={r[2]:2d} plants={r[3]:2d} empty={r[4]:2d} "
              f"seedsM={r[5]} shedM={r[6]} shedW={r[7]}")


if __name__ == "__main__":
    main()
