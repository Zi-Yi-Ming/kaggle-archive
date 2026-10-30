# -*- coding: utf-8 -*-
"""P9 local gate: mode machine vs R2, 8 games, both seats."""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make


def load_mode(tag):
    # reset state each load
    spec = importlib.util.spec_from_file_location(f"mode_{tag}", str(ROOT / "_p9_mode_machine.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_r2(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def snap_gaps(env, seat):
    out = {}
    for idx, s in enumerate(env.steps):
        rec = s[seat] if seat < len(s) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        if step % 24 != 0:
            continue
        day = step // 24
        farms = obs.get("farms") or []
        if len(farms) < 2:
            continue
        my = float((farms[seat] or {}).get("money") or 0)
        op = float((farms[1 - seat] or {}).get("money") or 0)
        out[day] = my - op
    return out


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            tag = f"{seat}{seed}"
            mod = load_mode(tag)
            r2 = load_r2(tag)
            # wrap to reset mode machine state per game via unique module — already unique
            agents = [mod.agent, r2] if seat == 0 else [r2, mod.agent]
            env = make("kaggriculture", debug=False)
            env.configuration["episodeSteps"] = 720
            env.configuration["seed"] = seed
            env.run(agents)
            f = env.steps[-1]
            my = float(f[seat]["observation"]["farms"][seat]["money"])
            op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
            err = [s.get("error") for s in f if s.get("error")]
            gaps = snap_gaps(env, seat)
            st = mod.debug_state()
            seat_state = st.get(seat) or {}
            rec = {
                "seed": seed, "seat": seat,
                "my": my, "opp": op, "margin": my - op,
                "win": my > op, "tie": my == op,
                "gap10": gaps.get(10), "gap20": gaps.get(20), "gap25": gaps.get(25),
                "mode": seat_state.get("mode"),
                "switches": seat_state.get("switches"),
                "mode_log": str(seat_state.get("mode_log")),
                "errors": err,
            }
            rows.append(rec)
            print(f"MODE vs R2 s{seed} seat{seat}: {my:.0f} vs {op:.0f} m={my-op:+.0f} "
                  f"W={my>op} mode={rec['mode']} sw={rec['switches']} "
                  f"g10={rec['gap10']} g20={rec['gap20']} g25={rec['gap25']} err={err}", flush=True)

    w = sum(1 for r in rows if r["win"])
    l = sum(1 for r in rows if not r["win"] and not r["tie"])
    t = sum(1 for r in rows if r["tie"])
    print(f"\nSUMMARY MODE-R2: {w}-{l}-{t}")
    s0 = [r for r in rows if r["seat"] == 0]
    s1 = [r for r in rows if r["seat"] == 1]
    print(f"  seat0: {sum(1 for r in s0 if r['win'])}-{sum(1 for r in s0 if not r['win'])}")
    print(f"  seat1: {sum(1 for r in s1 if r['win'])}-{sum(1 for r in s1 if not r['win'])}")
    print(f"  mean margin={sum(r['margin'] for r in rows)/len(rows):+.0f}")
    print(f"  mean switches={sum(r['switches'] or 0 for r in rows)/len(rows):.1f}")

    with open(ROOT / "p9_local_results.csv", "w", newline="", encoding="utf-8") as f:
        keys = list(rows[0].keys())
        wcsv = csv.DictWriter(f, fieldnames=keys)
        wcsv.writeheader()
        wcsv.writerows(rows)
    with open(ROOT / "p9_behavior_diff.csv", "w", newline="", encoding="utf-8") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["seed", "seat", "final_mode", "switches", "mode_log", "margin"])
        for r in rows:
            wcsv.writerow([r["seed"], r["seat"], r["mode"], r["switches"], r["mode_log"], r["margin"]])
    print("wrote p9_local_results.csv p9_behavior_diff.csv")


if __name__ == "__main__":
    main()
