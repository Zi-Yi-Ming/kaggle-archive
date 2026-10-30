# -*- coding: utf-8 -*-
"""Deterministic local harness. ALWAYS use this for Δbank experiments.

Root cause (P26): env.configuration["seed"] is scrubbed by resolve_episode_seed
and does NOT control shop RNG. Must set env.info["seed"] before run.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_det_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_pool(name: str):
    path = ROOT / "reference_agents" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(
        f"pool_{name}_" + str(id(object())), str(path)
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_game(agent0, agent1, seed: int, episode_steps: int = 720):
    """Run one episode with PINNED episode seed. Returns banks + action hashes."""
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = episode_steps
    # CRITICAL: pin info seed; configuration seed is scrubbed and ignored
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    try:
        env.configuration["seed"] = int(seed)
    except Exception:
        pass

    seq = [[], []]

    def wrap(inner, seat_i):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            seq[seat_i].append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))
            return a
        return agent

    env.run([wrap(agent0, 0), wrap(agent1, 1)])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    h0 = hashlib.md5("\n".join(seq[0]).encode()).hexdigest()[:16]
    h1 = hashlib.md5("\n".join(seq[1]).encode()).hexdigest()[:16]
    shops = []
    # last observation town
    try:
        shops = list((f[0]["observation"].get("town") or {}).get("unlocked_shops") or [])
    except Exception:
        pass
    return {
        "bank0": b0, "bank1": b1,
        "hash0": h0, "hash1": h1,
        "shops": shops,
        "seed": seed,
    }
