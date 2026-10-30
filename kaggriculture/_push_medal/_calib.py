# -*- coding: utf-8 -*-
"""Smoke + short calibration for medal submission (_push_medal/main.py)."""
import os
import sys
import importlib.util
import json

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, ROOT)

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent


def load_medal(tag="m"):
    path = os.path.join(BASE, "main.py")
    spec = importlib.util.spec_from_file_location(f"medal_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def load_named(name, tag):
    if name == "v11E":
        return load_pool_agent("v11E")
    if name == "closer_cleo":
        path = os.path.join(ROOT, "reference_agents", "closer_cleo.py")
        spec = importlib.util.spec_from_file_location(f"cleo_{tag}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.agent
    if name == "tetsu2131":
        path = os.path.join(ROOT, "_external", "top5_notebooks", "tetsu2131", "wrapper.py")
        spec = importlib.util.spec_from_file_location(f"tetsu_{tag}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.agent
    if name == "fallow_finn":
        return load_pool_agent("fallow_finn")
    raise KeyError(name)


def run_game(seed, a0, a1):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    final = env.steps[-1]
    bank0 = float(final[0]["observation"]["farms"][0]["money"])
    bank1 = float(final[1]["observation"]["farms"][1]["money"])
    err = [s.get("error") for s in final if s.get("error")]
    return bank0, bank1, err


def play(A, B, seeds=(1, 2, 3), seats=(0, 1)):
    games = []
    for seat in seats:
        for seed in seeds:
            a = load_medal(f"{A}_{B}_{seat}_{seed}") if A == "MEDAL" else load_named(A, f"{A}_{seat}_{seed}")
            b = load_medal(f"{A}_{B}_{seat}_{seed}b") if B == "MEDAL" else load_named(B, f"{B}_{seat}_{seed}")
            if seat == 0:
                bank0, bank1, err = run_game(seed, a, b)
                margin_A = bank0 - bank1
                bank_A, bank_B = bank0, bank1
            else:
                bank0, bank1, err = run_game(seed, b, a)
                margin_A = bank1 - bank0
                bank_A, bank_B = bank1, bank0
            games.append({"seed": seed, "seat": seat, "bank_A": bank_A, "bank_B": bank_B,
                          "margin_A": margin_A, "errors": err})
            print(f"  {A} vs {B} seed{seed} seat{seat}: A={bank_A:.0f} B={bank_B:.0f} m={margin_A:+.0f} err={err}", flush=True)
    wins = sum(1 for g in games if g["margin_A"] > 0)
    losses = sum(1 for g in games if g["margin_A"] < 0)
    ties = sum(1 for g in games if g["margin_A"] == 0)
    mean_m = sum(g["margin_A"] for g in games) / len(games)
    return {"n": len(games), "wins_A": wins, "losses_A": losses, "ties": ties,
            "mean_margin_A": mean_m, "games": games}


def main():
    print("=== SMOKE ===", flush=True)
    agent = load_medal("smoke")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 8
    env.configuration["seed"] = 1
    env.run([agent, load_pool_agent("fallow_finn")])
    print("smoke steps", len(env.steps), "ok", flush=True)

    results = {}
    pairs = [
        ("MEDAL", "v11E"),
        ("MEDAL", "closer_cleo"),
        ("MEDAL", "tetsu2131"),
        ("MEDAL", "fallow_finn"),
    ]
    for A, B in pairs:
        print(f"\n>> {A} vs {B}", flush=True)
        results[f"{A}__vs__{B}"] = play(A, B)

    print("\n=== SUMMARY ===", flush=True)
    for k, r in results.items():
        print(f"  {k}: {r['wins_A']}-{r['losses_A']}-{r['ties']} mean_m_A={r['mean_margin_A']:+.0f}", flush=True)

    out = os.path.join(BASE, "calib_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
