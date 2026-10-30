# -*- coding: utf-8 -*-
"""P11 full-game smoke vs finn and R2."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location("r2_gate", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_p11(tag):
    # unique module per game to reset singleton
    spec = importlib.util.spec_from_file_location(f"p11_{tag}", str(ROOT / "p11_planner" / "planner.py"))
    # easier: use package agent but reset
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def load_finn():
    from _pm_pool import load_agent
    return load_agent("fallow_finn")


def run_pair(p11_agent, opp, seed, seat, label):
    agents = [p11_agent, opp] if seat == 0 else [opp, p11_agent]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    # day snapshots
    snaps = {}
    for idx, s in enumerate(env.steps):
        rec = s[seat]
        if not rec:
            continue
        obs = rec.get("observation") or {}
        step = int(obs.get("step") or idx)
        if step % 24 == 0 and step // 24 in (5, 10, 15, 20, 25, 29):
            farms = obs.get("farms") or []
            if len(farms) >= 2:
                snaps[step // 24] = float(farms[seat].get("money") or 0)
    rec = {
        "label": label, "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op, "win": my > op, "tie": my == op,
        "errors": str(err),
        "d5": snaps.get(5), "d10": snaps.get(10), "d15": snaps.get(15),
        "d20": snaps.get(20), "d25": snaps.get(25), "d29": snaps.get(29),
    }
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} m={my-op:+.0f} W={my>op} "
          f"d10={snaps.get(10)} d20={snaps.get(20)} d29={snaps.get(29)} err={err}", flush=True)
    return rec


def main():
    rows = []
    # Phase 1: vs finn 2 seeds both seats
    for seat in (0, 1):
        for seed in (1, 2):
            from p11_planner import planner as pmod
            pmod._PLANNER = None
            rows.append(run_pair(pmod.agent, load_finn(), seed, seat, "finn"))

    # Phase 2: vs R2 2 seeds both seats
    for seat in (0, 1):
        for seed in (1, 2):
            from p11_planner import planner as pmod
            pmod._PLANNER = None
            rows.append(run_pair(pmod.agent, load_r2(), seed, seat, "R2"))

    out = ROOT / "p11_smoke_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for label in ("finn", "R2"):
        sub = [r for r in rows if r["label"] == label]
        wins = sum(1 for r in sub if r["win"])
        print(f"\n{label}: {wins}/{len(sub)} wins  mean_margin={sum(r['margin'] for r in sub)/len(sub):+.0f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
