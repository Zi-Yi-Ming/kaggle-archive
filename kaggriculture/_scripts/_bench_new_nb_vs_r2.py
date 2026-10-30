# -*- coding: utf-8 -*-
"""Benchmark newly downloaded public notebooks vs Medal R2."""
from __future__ import annotations

import importlib.util
import json
import os
import sys

ROOT = r"D:\桌面\Kaggle\kaggriculture"
PUB = os.path.join(ROOT, "_external", "public_nb")
sys.path.insert(0, ROOT)
from kaggle_environments import make


def load_file(path, tag):
    spec = importlib.util.spec_from_file_location(f"ag_{tag}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_named(name, tag):
    if name == "R2":
        return load_file(os.path.join(ROOT, "_push_medal", "main.py"), f"r2_{tag}")
    table = {
        "boatlee": os.path.join(PUB, "boatlee_v20", "main.py"),
        "kaito48": os.path.join(PUB, "kaito_v48", "main.py"),
        "kaito43": os.path.join(PUB, "kaito_v43", "main.py"),
        "kaito21": os.path.join(PUB, "kaito_v21", "main.py"),
        "kaito58": os.path.join(PUB, "kaito_v58", "main.py"),
    }
    return load_file(table[name], f"{name}_{tag}")


def game(seed, a0, a1):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    return b0, b1, err


def play_pair(cand, seeds=(1, 2, 3)):
    ms = []
    for seat in (0, 1):
        for seed in seeds:
            tag = f"{cand}_{seat}_{seed}_{id(object())}"
            a = load_named(cand if seat == 0 else "R2", tag + "a")
            b = load_named("R2" if seat == 0 else cand, tag + "b")
            if seat == 0:
                b0, b1, err = game(seed, a, b)
                m, bankA, bankB = b0 - b1, b0, b1
            else:
                b0, b1, err = game(seed, b, a)
                m, bankA, bankB = b1 - b0, b1, b0
            ms.append(m)
            print(f"    {cand} vs R2 s{seed} seat{seat}: {bankA:.0f} vs {bankB:.0f} m={m:+.0f} err={err}", flush=True)
    w = sum(1 for m in ms if m > 0)
    l = sum(1 for m in ms if m < 0)
    t = sum(1 for m in ms if m == 0)
    mean = sum(ms) / len(ms)
    s0, s1 = ms[: len(seeds)], ms[len(seeds):]
    print(f"  SUMMARY {cand}-R2: {w}-{l}-{t} mean={mean:+.0f} seat0={sum(s0)/len(s0):+.0f} seat1={sum(s1)/len(s1):+.0f}", flush=True)
    return {"w": w, "l": l, "t": t, "mean": mean, "margins": ms}


def main():
    out = {}
    for c in ["boatlee", "kaito48", "kaito43"]:
        print(f">> {c} vs R2", flush=True)
        try:
            out[c] = play_pair(c)
        except Exception as e:
            import traceback
            print("FAIL", c, e)
            traceback.print_exc()
            out[c] = {"error": str(e)}
    json.dump(out, open(os.path.join(ROOT, "_calib_new_nb_vs_r2.json"), "w"), indent=2)
    print("\n=== BOARD ===")
    for k, v in out.items():
        if "error" in v:
            print(f"  {k:10s} ERROR {v['error'][:80]}")
        else:
            print(f"  {k:10s} {v['w']}-{v['l']}-{v['t']} mean={v['mean']:+.0f}")


if __name__ == "__main__":
    main()
