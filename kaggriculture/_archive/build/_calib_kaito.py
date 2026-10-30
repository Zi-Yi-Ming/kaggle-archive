# -*- coding: utf-8 -*-
"""Calibrate Kaito v58 / v27 / Rayk vs Medal R2."""
import os
import sys
import importlib.util
import json

ROOT = r"D:\桌面\Kaggle\kaggriculture"
PUB = os.path.join(ROOT, "_external", "public_nb")
sys.path.insert(0, ROOT)

from kaggle_environments import make


def load_file(path, name, tag):
    spec = importlib.util.spec_from_file_location(f"{name}_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def load_named(name, tag):
    if name == "MEDAL":
        return load_file(os.path.join(ROOT, "_push_medal", "main.py"), "medal", tag)
    if name == "kaito58":
        return load_file(os.path.join(PUB, "kaito_v58", "main.py"), "k58", tag)
    if name == "kaito27":
        return load_file(os.path.join(PUB, "kaito_v27", "main.py"), "k27", tag)
    if name == "rayk":
        return load_file(os.path.join(PUB, "rayk_rank", "main.py"), "rayk", tag)
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
                mA, bankA, bankB = b0 - b1, b0, b1
            else:
                b0, b1, err = run_game(seed, b, a)
                mA, bankA, bankB = b1 - b0, b1, b0
            games.append((mA, bankA, bankB, err))
            print(f"  {A} vs {B} s{seed} seat{seat}: A={bankA:.0f} B={bankB:.0f} m={mA:+.0f} err={err}", flush=True)
    w = sum(1 for m, *_ in games if m > 0)
    l = sum(1 for m, *_ in games if m < 0)
    t = sum(1 for m, *_ in games if m == 0)
    mean = sum(m for m, *_ in games) / len(games)
    return w, l, t, mean


def main():
    pairs = [
        ("kaito58", "MEDAL"),
        ("kaito27", "MEDAL"),
        ("rayk", "MEDAL"),
        ("kaito58", "kaito27"),
        ("kaito58", "v11E"),
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
    path = os.path.join(ROOT, "_calib_kaito_medal.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
