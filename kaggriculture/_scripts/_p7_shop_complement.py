# -*- coding: utf-8 -*-
"""Breakthrough probe A: is there a shop-family where a non-R2 policy beats R2?

If yes, a meta-router can exist. If no, meta-agent over existing policies is dead.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make


def load_file(path, tag, chdir=False):
    pkg = os.path.dirname(path)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    spec = importlib.util.spec_from_file_location(f"ag_{tag}", path)
    m = importlib.util.module_from_spec(spec)
    if chdir:
        old = os.getcwd()
        os.chdir(pkg)
        try:
            spec.loader.exec_module(m)
        finally:
            os.chdir(old)
    else:
        spec.loader.exec_module(m)
    return m.agent


def first_shops(env):
    for snap in env.steps:
        obs = snap[0].get("observation") or {}
        if not isinstance(obs, dict):
            continue
        shops = (obs.get("town") or {}).get("unlocked_shops") or []
        if len(shops) >= 2:
            return tuple(shops[:2])
        if len(shops) == 1:
            last = shops
    return tuple()


def run_pair(A, B, seed, a_is_r2_seat0=True):
    r2_path = str(ROOT / "_push_medal" / "main.py")
    other = {
        "v66": (str(ROOT / "_external" / "git" / "v66" / "main.py"), True),
        "shape": (str(ROOT / "_external" / "public_nb" / "tetsu_shape" / "main.py"), False),
    }
    tag = f"{A}_{B}_{seed}_{a_is_r2_seat0}"
    if A == "R2":
        a = load_file(r2_path, tag + "a")
    else:
        p, cd = other[A]
        a = load_file(p, tag + "a", chdir=cd)
    if B == "R2":
        b = load_file(r2_path, tag + "b")
    else:
        p, cd = other[B]
        b = load_file(p, tag + "b", chdir=cd)
    agents = [a, b] if a_is_r2_seat0 else [b, a]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    f = env.steps[-1]
    r2_seat = 0 if a_is_r2_seat0 else 1
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    r2m = b0 if r2_seat == 0 else b1
    oppm = b1 if r2_seat == 0 else b0
    shops = first_shops(env)
    return {"seed": seed, "R2_seat": r2_seat, "R2": r2m, "opp": oppm, "margin_R2": r2m - oppm, "shops": shops}


def main():
    rows = []
    for other in ("v66", "shape"):
        for seat in (0, 1):
            for seed in range(1, 7):
                try:
                    r = run_pair("R2", other, seed, a_is_r2_seat0=(seat == 0))
                    r["other"] = other
                    rows.append(r)
                    print(f"R2 vs {other} seat{seat} s{seed}: R2={r['R2']:.0f} opp={r['opp']:.0f} "
                          f"m={r['margin_R2']:+.0f} shops={r['shops']}", flush=True)
                except Exception as e:
                    import traceback
                    print("FAIL", other, seat, seed, e)
                    traceback.print_exc()

    # group by first-shop pair
    print("\n=== R2 margin by first-2 shops ===")
    by = defaultdict(list)
    for r in rows:
        by[(r["other"], r["shops"])].append(r["margin_R2"])
    for k, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
        other, shops = k
        wins = sum(1 for x in v if x < -500)  # R2 loses
        print(f"  {other:6s} {shops}: n={len(v)} mean_R2={sum(v)/len(v):+.0f} R2_losses={wins}/{len(v)}")

    # Does any shop family have R2 consistently losing to another policy?
    print("\n=== any (other, shops) with R2 lose in >= half games? ===")
    found = False
    for (other, shops), v in by.items():
        if len(v) >= 2 and sum(1 for x in v if x < -500) >= len(v) / 2:
            print(f"  YES {other} {shops} {v}")
            found = True
    if not found:
        print("  NO — no complementary shop family found")

    json.dump(rows, open(ROOT / "p7_meta_shop_complement.json", "w"), indent=2, default=str)
    print("wrote p7_meta_shop_complement.json")


if __name__ == "__main__":
    main()
