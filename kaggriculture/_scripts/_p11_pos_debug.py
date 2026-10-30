# -*- coding: utf-8 -*-
"""Dump worker positions vs tile kinds around plant attempts."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p11_planner.planner import StrategicPlanner  # noqa: E402
from _pm_pool import load_agent  # noqa: E402

LOG = ROOT / "_p11_pos_log.txt"


def main():
    planner = StrategicPlanner()
    finn = load_agent("fallow_finn")
    fh = LOG.open("w", encoding="utf-8")

    def agent(obs, configuration=None):
        a = planner.act(obs)
        step = int(obs.get("step") or 0)
        if step <= 20:
            farm = obs["farms"][obs["player"]]
            tiles = farm["tiles"]
            pos_list = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
            cmds = [a.get("farmer")] + list(a.get("hands") or [])
            seeds = obs["private"]["seeds"]
            parts = []
            for i, (p, c) in enumerate(zip(pos_list, cmds)):
                x, y = p
                tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else "?"
                tdesc = "None" if tile is None else ("LOCKED" if tile == "LOCKED" else str(tile)[:80])
                parts.append(f"w{i}@{p}{c}->{tdesc}")
            fh.write(f"s{step} seeds={ {k:v for k,v in seeds.items() if v} } | " + " || ".join(parts) + "\n")
            fh.flush()
        return a

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 48
    env.configuration["seed"] = 1
    env.run([agent, finn])
    fh.close()
    print("wrote", LOG)


if __name__ == "__main__":
    main()
