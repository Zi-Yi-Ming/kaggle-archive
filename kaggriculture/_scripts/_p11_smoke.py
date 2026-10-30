# -*- coding: utf-8 -*-
"""P11 smoke: planner+executor vs finn, 1 seed. Check bank & errors."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

from p11_planner.planner import agent as p11_agent, debug_state  # noqa: E402


def load_finn():
    from _pm_pool import load_agent
    return load_agent("fallow_finn")


def main():
    finn = load_finn()
    for seed in (1, 2):
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.configuration["seed"] = seed
        env.run([p11_agent, finn])
        f = env.steps[-1]
        bank = float(f[0]["observation"]["farms"][0]["money"])
        opp = float(f[0]["observation"]["farms"][1]["money"])
        err = [s.get("error") for s in f if s.get("error")]
        st = debug_state()
        # track money at days
        gaps = {}
        for idx, s in enumerate(env.steps):
            rec = s[0]
            if not rec:
                continue
            obs = rec.get("observation") or {}
            step = int(obs.get("step") or idx)
            if step % 24 == 0 and step // 24 in (5, 10, 15, 20, 25, 29):
                farms = obs.get("farms") or []
                if len(farms) >= 2:
                    gaps[step // 24] = float(farms[0].get("money") or 0)
        print(f"seed{seed}: p11={bank:.0f} finn={opp:.0f} margin={bank-opp:+.0f} "
              f"err={err} state={st} day_money={gaps}", flush=True)


if __name__ == "__main__":
    main()
