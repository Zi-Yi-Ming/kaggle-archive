# -*- coding: utf-8 -*-
"""Benchmark untested local external agents vs Medal R2."""
from __future__ import annotations

import importlib.util
import json
import os
import sys

ROOT = r"D:\桌面\Kaggle\kaggriculture"
sys.path.insert(0, ROOT)
from kaggle_environments import make

EXT = os.path.join(ROOT, "_external")


def load_file(path, tag):
    spec = importlib.util.spec_from_file_location(f"ag_{tag}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_named(name, tag):
    if name == "R2":
        return load_file(os.path.join(ROOT, "_push_medal", "main.py"), f"r2_{tag}")
    table = {
        "lonespear": os.path.join(EXT, "lonespear", "main.py"),
        "gzmcr": os.path.join(EXT, "gzmcr", "main.py"),
        "asajjadi": os.path.join(EXT, "asajjadi", "main.py"),
        "sey_v21": os.path.join(EXT, "sey_v21", "main.py"),
        "cok_v10": os.path.join(EXT, "cok_v10", "main.py"),
        "gytdrop": os.path.join(EXT, "gytdrop_v5", "main.py"),
        "pomagrenate": os.path.join(EXT, "pomagrenate", "main.py"),
        "grigorii": os.path.join(EXT, "grigorii", "main.py"),
        "smartex": os.path.join(EXT, "smartex-dan_kaggriculture", "main.py"),
    }
    # wrappers for some
    wrap = {
        "lonespear": os.path.join(EXT, "lonespear", "wrapper.py"),
        "gzmcr": os.path.join(EXT, "gzmcr", "wrapper.py"),
        "asajjadi": os.path.join(EXT, "asajjadi", "wrapper.py"),
        "sey_v21": os.path.join(EXT, "sey_v21", "wrapper.py"),
        "cok_v10": os.path.join(EXT, "cok_v10", "wrapper.py"),
        "gytdrop": os.path.join(EXT, "gytdrop_v5", "wrapper.py"),
    }
    path = wrap.get(name) or table[name]
    # packages may need sibling path
    pkg = os.path.dirname(path)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    if name == "smartex":
        old = os.getcwd()
        os.chdir(pkg)
        try:
            return load_file(path, f"{name}_{tag}")
        finally:
            os.chdir(old)
    return load_file(path, f"{name}_{tag}")


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


def play_pair(cand, seeds=(1, 2)):
    """cand seat0 / R2 seat1 and swapped. Return cand W-L-T and mean margin."""
    ms = []
    for seat in (0, 1):
        for seed in seeds:
            tag = f"{cand}_{seat}_{seed}_{id(object())}"
            a = load_named(cand if seat == 0 else "R2", tag + "a")
            b = load_named("R2" if seat == 0 else cand, tag + "b")
            if seat == 0:
                b0, b1, err = game(seed, a, b)
                m = b0 - b1
                bankA, bankB = b0, b1
            else:
                b0, b1, err = game(seed, b, a)
                m = b1 - b0
                bankA, bankB = b1, b0
            ms.append(m)
            print(f"    {cand} vs R2 s{seed} seat{seat}: {bankA:.0f} vs {bankB:.0f} m={m:+.0f} err={err}", flush=True)
    w = sum(1 for m in ms if m > 0)
    l = sum(1 for m in ms if m < 0)
    t = sum(1 for m in ms if m == 0)
    mean = sum(ms) / len(ms)
    print(f"  SUMMARY {cand}-R2: {w}-{l}-{t} mean={mean:+.0f}", flush=True)
    return {"w": w, "l": l, "t": t, "mean": mean, "margins": ms}


def main():
    cands = [
        "lonespear", "gzmcr", "asajjadi", "sey_v21", "cok_v10",
        "gytdrop", "pomagrenate", "grigorii", "smartex",
    ]
    out = {}
    for c in cands:
        print(f">> {c} vs R2", flush=True)
        try:
            out[c] = play_pair(c)
        except Exception as e:
            import traceback
            print(f"  FAIL {c}: {e}")
            traceback.print_exc()
            out[c] = {"error": str(e)}
    path = os.path.join(ROOT, "_calib_untested_vs_r2.json")
    json.dump(out, open(path, "w"), indent=2)
    print("wrote", path)
    print("\n=== BOARD ===")
    for k, v in out.items():
        if "error" in v:
            print(f"  {k:12s} ERROR")
        else:
            print(f"  {k:12s} {v['w']}-{v['l']}-{v['t']} mean={v['mean']:+.0f}")


if __name__ == "__main__":
    main()
