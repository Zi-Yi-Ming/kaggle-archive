# -*- coding: utf-8 -*-
"""P26c: print resolved episode seed + shops across repeats."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location("r2c_" + str(id(object())), str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_finn():
    path = ROOT / "reference_agents" / "fallow_finn.py"
    spec = importlib.util.spec_from_file_location("finnc_" + str(id(object())), str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(cfg_seed, info_seed=None, tag=""):
    r2 = load_r2()
    finn = load_finn()
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = cfg_seed
    if info_seed is not None:
        if env.info is None:
            env.info = {}
        env.info["seed"] = info_seed
    shops = []

    def wrap(inner):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            a = inner(obs, configuration)
            if step == 144:
                shops.append(tuple((obs.get("town") or {}).get("unlocked_shops") or []))
            return a
        return agent

    env.run([wrap(r2), wrap(finn)])
    info_seed_after = getattr(env, "info", None)
    info_seed_val = None
    if isinstance(info_seed_after, dict):
        info_seed_val = info_seed_after.get("seed")
    cfg_seed_after = env.configuration.get("seed") if isinstance(env.configuration, dict) else getattr(env.configuration, "seed", None)
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    print(f"  {tag}: cfg_in={cfg_seed} info_set={info_seed} info_after={info_seed_val} "
          f"cfg_after={cfg_seed_after} bank={bank:.0f} shops144={shops}", flush=True)
    return shops, bank


def main():
    print("=== only configuration.seed=1 ===")
    for i in range(3):
        run(1, None, f"cfg1_rep{i}")
    print("=== configuration.seed=1 AND info.seed=1 ===")
    for i in range(3):
        run(1, 1, f"both1_rep{i}")
    print("=== configuration.seed=99 AND info.seed=99 ===")
    for i in range(2):
        run(99, 99, f"both99_rep{i}")


if __name__ == "__main__":
    main()
