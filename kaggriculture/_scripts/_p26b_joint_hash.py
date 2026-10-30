# -*- coding: utf-8 -*-
"""P26b: joint action hash R2+opp; isolate nondeterminism source."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_j_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_finn():
    path = ROOT / "reference_agents" / "fallow_finn.py"
    spec = importlib.util.spec_from_file_location("finn_j_" + str(id(object())), str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def act_key(a):
    return json.dumps(
        {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
        sort_keys=True, default=str,
    )


def run(seed, seat, tag):
    r2 = load_r2()
    finn = load_finn()
    seq0, seq1 = [], []
    shops = []

    def wrap(inner, seat_i):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            if seat_i == 0:
                seq0.append(act_key(a))
            else:
                seq1.append(act_key(a))
            if step == 144:
                try:
                    shops.append(tuple((obs.get("town") or {}).get("unlocked_shops") or []))
                except Exception:
                    shops.append(None)
            return a
        return agent

    agents = [None, None]
    agents[seat] = r2
    agents[1 - seat] = finn
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], 0), wrap(agents[1], 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    h0 = hashlib.md5("\n".join(seq0).encode()).hexdigest()[:16]
    h1 = hashlib.md5("\n".join(seq1).encode()).hexdigest()[:16]
    print(f"  {tag}: bank={my:.0f} opp={op:.0f} h0={h0} h1={h1} shops144={shops}", flush=True)
    return h0, h1, my, op


def main():
    print("=== same-process repeats seed=1 seat=0 ===")
    for i in range(4):
        run(1, 0, f"rep{i}")
    print("=== seed=2 ===")
    run(2, 0, "s2")


if __name__ == "__main__":
    main()
