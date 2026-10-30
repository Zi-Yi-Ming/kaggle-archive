# -*- coding: utf-8 -*-
"""P12 B2 = B1 labor + EOD DROP fix. Quick 4-game check vs R2."""
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
        "r2_b2_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def main():
    from _p12_b1_agent import make_b1_agent
    rows = []
    for seat in (0, 1):
        for seed in (1, 2):
            own = make_b1_agent()
            opp = load_r2()
            agents = [own, opp] if seat == 0 else [opp, own]
            env = make("kaggriculture", debug=False)
            env.configuration["episodeSteps"] = 720
            env.configuration["seed"] = seed
            env.run(agents)
            f = env.steps[-1]
            my = float(f[seat]["observation"]["farms"][seat]["money"])
            op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
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
            rec = {
                "label": "B2", "seed": seed, "seat": seat,
                "my": my, "opp": op, "margin": my - op, "win": int(my > op),
                "d10": snaps.get(10), "d15": snaps.get(15), "d20": snaps.get(20),
                "d25": snaps.get(25), "d29": snaps.get(29),
            }
            rows.append(rec)
            print(f"B2 s{seed} seat{seat}: {my:.0f} vs {op:.0f} m={my-op:+.0f} "
                  f"d10={rec['d10']} d20={rec['d20']} d29={rec['d29']}", flush=True)

    out = ROOT / "p12_b2_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bank = sum(r["my"] for r in rows) / len(rows)
    d20 = [r["d20"] for r in rows if r["d20"] is not None]
    print(f"\nB2 mean bank={bank:.0f}  mean d20={sum(d20)/len(d20):.0f}  wins={sum(r['win'] for r in rows)}/{len(rows)}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
