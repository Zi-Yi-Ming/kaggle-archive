# -*- coding: utf-8 -*-
"""B3 smoke vs finn + 4 games vs R2."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_b3_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def fresh_p11():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def run(opp_factory, seed, seat, label):
    own = fresh_p11()
    opp = opp_factory()
    agents = [own, opp] if seat == 0 else [opp, own]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    snaps = {}
    for idx, s in enumerate(env.steps):
        rec = s[seat]
        if not rec:
            continue
        obs = rec.get("observation") or {}
        step = int(obs.get("step") or idx)
        farms = obs.get("farms") or []
        if len(farms) >= 2 and step // 24 in (10, 15, 20, 25, 29):
            snaps[step // 24] = float(farms[seat].get("money") or 0)
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} m={my-op:+.0f} "
          f"d10={snaps.get(10)} d20={snaps.get(20)} d29={snaps.get(29)} err={err}", flush=True)
    return {
        "label": label, "seed": seed, "seat": seat, "my": my, "opp": op,
        "margin": my - op, "win": int(my > op), "errors": str(err),
        "d10": snaps.get(10), "d20": snaps.get(20), "d29": snaps.get(29),
    }


def main():
    from _pm_pool import load_agent
    rows = []
    # smoke vs finn
    for seed in (1, 2):
        rows.append(run(lambda: load_agent("fallow_finn"), seed, 0, "finn"))
    # vs R2
    for seat in (0, 1):
        for seed in (1, 2):
            rows.append(run(load_r2, seed, seat, "R2"))

    out = ROOT / "p12_b3_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for label in ("finn", "R2"):
        sub = [r for r in rows if r["label"] == label]
        print(f"\n{label}: wins={sum(r['win'] for r in sub)}/{len(sub)} "
              f"mean_bank={sum(r['my'] for r in sub)/len(sub):.0f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
