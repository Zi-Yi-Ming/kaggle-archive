# -*- coding: utf-8 -*-
"""Debug one P38 program: dump farm state every day."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p38_program.compiler import compile_program, enumerate_programs  # noqa: E402


def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def main():
    finn = load(ROOT / "reference_agents" / "fallow_finn.py", "finndbg")
    progs = enumerate_programs()
    p = progs[0]
    print("prog", p)
    agent = compile_program(p)
    actions = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            actions.append({"step": obs.get("step"), "market": a.get("market"),
                            "farmer": a.get("farmer"), "n_hands": len(a.get("hands") or [])})
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = 1
    env.run([wrap(agent), finn])

    for si in (0, 1, 24, 48, 72, 144, 216, 288, 432, 719):
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
                        crops[t.get("crop")] = crops.get(t.get("crop"), 0) + 1
                    if t.get("animal"):
                        animals += 1
        private = f.get("private") or {}
        print(
            "step", si, "money", farm.get("money"),
            "hands", len(farm.get("hands") or []),
            "plants", plants, "crops", crops, "animals", animals,
            "empty", empty, "land", len(farm.get("unlocked_quadrants") or []),
            "shed", private.get("shed"), "seeds", private.get("seeds"),
            "action", actions[si] if si < len(actions) else None,
        )
    print("final bank", env.steps[-1][0]["observation"]["farms"][0]["money"])


if __name__ == "__main__":
    main()
