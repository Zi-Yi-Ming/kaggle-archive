# -*- coding: utf-8 -*-
"""Debug P11 first days via file log."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p11_planner.planner import StrategicPlanner  # noqa: E402
from _pm_pool import load_agent  # noqa: E402

LOG = ROOT / "_p11_debug_lines.txt"


def main():
    planner = StrategicPlanner()
    finn = load_agent("fallow_finn")
    fh = LOG.open("w", encoding="utf-8")

    def agent(obs, configuration=None):
        a = planner.act(obs)
        step = int(obs.get("step") or 0)
        if step < 72 or step % 24 == 0:
            farm = obs["farms"][obs["player"]]
            private = obs["private"]
            tiles = farm.get("tiles") or []
            n_empty = sum(1 for row in tiles for t in row if t is None)
            n_plant = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT")
            n_weed = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "WEED")
            n_struct = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"))
            fh.write(
                f"s{step:3d} d{step//24}h{step%24:02d} $={float(farm['money']):.0f} "
                f"hands={len(farm['hands'])} hires={farm['hires_today']} "
                f"empty={n_empty} plant={n_plant} weed={n_weed} struct={n_struct} "
                f"shed={ {k:v for k,v in private['shed'].items() if v} } "
                f"seeds={ {k:v for k,v in private['seeds'].items() if v} } "
                f"mkt={a.get('market')} "
                f"f={a.get('farmer')} h={a.get('hands')}\n"
            )
            fh.flush()
        return a

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 200
    env.configuration["seed"] = 1
    env.run([agent, finn])
    f = env.steps[-1]
    fh.write(f"FINAL p11={f[0]['observation']['farms'][0]['money']} finn={f[0]['observation']['farms'][1]['money']}\n")
    fh.close()
    print("wrote", LOG)


if __name__ == "__main__":
    main()
