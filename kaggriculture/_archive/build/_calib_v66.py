# -*- coding: utf-8 -*-
"""Quick local calib: v66 vs Medal R2 vs tetsu vs v11E."""
import os
import sys
import importlib.util
import json

ROOT = r"D:\桌面\Kaggle\kaggriculture"
V66 = os.path.join(ROOT, "_external", "git", "v66")
sys.path.insert(0, ROOT)
sys.path.insert(0, V66)

from kaggle_environments import make


def load_v66(tag):
    # ensure unique-ish load; package imports relative names
    if V66 not in sys.path:
        sys.path.insert(0, V66)
    import main as v66_main
    return v66_main.agent


def load_path(path, name, tag):
    spec = importlib.util.spec_from_file_location(f"{name}_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def load_named(name, tag):
    if name == "v66":
        return load_v66(tag)
    if name == "MEDAL":
        return load_path(os.path.join(ROOT, "_push_medal", "main.py"), "medal", tag)
    if name == "tetsu":
        return load_path(os.path.join(ROOT, "_push_tetsu_r3", "main.py"), "tetsu", tag)
    if name == "v11E":
        from _pm_pool import load_agent
        return load_agent("v11E")
    raise KeyError(name)


def run_game(seed, a0, a1):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    final = env.steps[-1]
    b0 = float(final[0]["observation"]["farms"][0]["money"])
    b1 = float(final[1]["observation"]["farms"][1]["money"])
    err = [s.get("error") for s in final if s.get("error")]
    return b0, b1, err


def play(A, B, seeds=(1, 2), seats=(0, 1)):
    games = []
    for seat in seats:
        for seed in seeds:
            tag = f"{A}_{B}_{seat}_{seed}_{id(object())}"
            a = load_named(A, tag + "a")
            b = load_named(B, tag + "b")
            if seat == 0:
                b0, b1, err = run_game(seed, a, b)
                mA, bankA, bankB = b0 - b0 + (b0 - b1), b0, b1
                mA = b0 - b1
            else:
                b0, b1, err = run_game(seed, b, a)
                mA = b1 - b0
                bankA, bankB = b1, b0
            games.append((mA, bankA, bankB, err))
            print(f"  {A} vs {B} seed{seed} seat{seat}: A={bankA:.0f} B={bankB:.0f} m={mA:+.0f} err={err}", flush=True)
    wins = sum(1 for m, *_ in games if m > 0)
    losses = sum(1 for m, *_ in games if m < 0)
    ties = sum(1 for m, *_ in games if m == 0)
    mean = sum(m for m, *_ in games) / len(games)
    return wins, losses, ties, mean


def main():
    pairs = [
        ("v66", "MEDAL"),
        ("v66", "tetsu"),
        ("v66", "v11E"),
        ("MEDAL", "tetsu"),
    ]
    out = {}
    for A, B in pairs:
        print(f"\n>> {A} vs {B}", flush=True)
        try:
            w, l, t, m = play(A, B)
            out[f"{A}__vs__{B}"] = {"w": w, "l": l, "t": t, "mean_m_A": m}
            print(f"  SUMMARY {A}-{B}: {w}-{l}-{t} mean={m:+.0f}", flush=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            out[f"{A}__vs__{B}"] = {"error": str(e)}
    path = os.path.join(ROOT, "_push_v66_calib.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\n", out)


if __name__ == "__main__":
    main()
