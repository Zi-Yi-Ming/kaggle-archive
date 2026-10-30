# -*- coding: utf-8 -*-
"""Diagnose why wrapping the opponent changes the candidate bank."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(r2, finn, mode, seed=1):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    shops_trace = []
    money_trace = []

    def wrap(inner, tag, only_obs=False):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            try:
                shops_trace.append((tag, int(obs.get("step") or 0),
                                    tuple((obs.get("town") or {}).get("unlocked_shops") or [])))
            except Exception:
                pass
            return a
        return agent

    if mode == "plain":
        env.run([r2, finn])
    elif mode == "wrap_r2":
        env.run([wrap(r2, "r2"), finn])
    elif mode == "wrap_finn":
        env.run([r2, wrap(finn, "finn")])
    elif mode == "wrap_both":
        env.run([wrap(r2, "r2"), wrap(finn, "finn")])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    # shops at day 6 hour 0 (step 144)
    shops144 = None
    for tag, step, shops in shops_trace:
        if tag == "r2" and step == 144:
            shops144 = shops
            break
    return b0, b1, shops144, len(shops_trace)


def main():
    r2 = load(ROOT / "_push_medal" / "main.py", "r2diag")
    finn = load(ROOT / "reference_agents" / "fallow_finn.py", "finndiag")
    for mode in ("plain", "wrap_r2", "wrap_finn", "wrap_both"):
        b0, b1, shops, n = run(r2, finn, mode)
        print(f"{mode:12s} bank0={b0:.0f} bank1={b1:.0f} shops144={shops} n_obs={n}")


if __name__ == "__main__":
    main()
