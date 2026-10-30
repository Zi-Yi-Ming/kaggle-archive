# -*- coding: utf-8 -*-
"""P11 formal 8-game gate vs R2, both seats, seeds 1-4."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location("r2_p11gate", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def main():
    from p11_planner import planner as pmod
    rows = []
    intent_rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            pmod._PLANNER = None
            r2 = load_r2()
            p11 = pmod.agent
            agents = [p11, r2] if seat == 0 else [r2, p11]
            env = make("kaggriculture", debug=False)
            env.configuration["episodeSteps"] = 720
            env.configuration["seed"] = seed
            env.run(agents)
            f = env.steps[-1]
            my = float(f[seat]["observation"]["farms"][seat]["money"])
            op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
            err = [s.get("error") for s in f if s.get("error")]
            gaps = {}
            for idx, s in enumerate(env.steps):
                rec = s[seat]
                if not rec:
                    continue
                obs = rec.get("observation") or {}
                step = int(obs.get("step") or idx)
                if step % 24 == 0:
                    day = step // 24
                    if day in (10, 15, 20, 25, 29):
                        farms = obs.get("farms") or []
                        if len(farms) >= 2:
                            gaps[day] = float(farms[seat].get("money") or 0) - float(farms[1 - seat].get("money") or 0)
            st = pmod.debug_state()
            rec = {
                "seed": seed, "seat": seat, "my": my, "opp": op, "margin": my - op,
                "win": int(my > op), "tie": int(my == op),
                "gap10": gaps.get(10), "gap15": gaps.get(15), "gap20": gaps.get(20),
                "gap25": gaps.get(25), "gap29": gaps.get(29),
                "bankrupt": int(my < 1000), "errors": str(err),
                "last_priority": st.get("priority"), "n_intents": st.get("n_intents"),
            }
            rows.append(rec)
            # sample intent log
            for step, day, pri, buy, land, hire in (pmod._PLANNER.intent_log if pmod._PLANNER else [])[:0]:
                pass
            if pmod._PLANNER:
                log = pmod._PLANNER.intent_log
                # downsample every 24 steps
                for item in log:
                    if item[0] % 24 == 0:
                        intent_rows.append({
                            "seed": seed, "seat": seat, "step": item[0], "day": item[1],
                            "priority": item[2], "buy_animals": str(item[3]),
                            "buy_land": item[4], "hire_n": item[5],
                        })
            print(f"R2 s{seed} seat{seat}: {my:.0f} vs {op:.0f} m={my-op:+.0f} W={my>op} "
                  f"g10={gaps.get(10)} g20={gaps.get(20)} g29={gaps.get(29)} err={err}", flush=True)

    w = sum(r["win"] for r in rows)
    l = sum(1 for r in rows if not r["win"] and not r["tie"])
    t = sum(r["tie"] for r in rows)
    print(f"\nSUMMARY P11-R2: {w}-{l}-{t}")
    print(f"  seat0: {sum(r['win'] for r in rows if r['seat']==0)}/4")
    print(f"  seat1: {sum(r['win'] for r in rows if r['seat']==1)}/4")
    print(f"  mean margin={sum(r['margin'] for r in rows)/len(rows):+.0f}")
    print(f"  bankrupt={sum(r['bankrupt'] for r in rows)}/{len(rows)}")

    out = ROOT / "p11_local_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(rows)
    out2 = ROOT / "p11_intent_trajectory.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(intent_rows[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(intent_rows)
    print("wrote", out, out2)


if __name__ == "__main__":
    main()
