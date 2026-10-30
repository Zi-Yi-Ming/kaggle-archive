# -*- coding: utf-8 -*-
"""P16 ablation: skeleton-only vs skeleton+branch vs R2. 8 games each."""
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
        "r2_p16_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(label, seed, seat, skeleton, branch):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p16_branch
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(skeleton)  # skeleton backbone lifecycle
    p14_1_on.set_enabled(skeleton)     # skeleton backbone portfolio
    p14_2_on.set_enabled(False)
    p16_branch.set_skeleton(skeleton)
    p16_branch.set_branch(branch)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    melon_field = {}
    melon_shed = {}
    branch_hits = 0

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            nonlocal branch_hits
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            day_cash[day] = float(farm.get("money") or 0)
            n_m = 0
            for row in farm.get("tiles") or []:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                        n_m += 1
            melon_field[day] = n_m
            melon_shed[day] = int((private.get("shed") or {}).get("MELON") or 0)
            # detect branch fire from notes in debug if available
            try:
                st = pmod.debug_state()
            except Exception:
                st = {}
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])

    # infer branch fired: d10 money low with melon present would have triggered
    fired = 0
    if branch and melon_field.get(10, 0) + melon_shed.get(10, 0) > 0 and (day_cash.get(10) or 9999) < 1800:
        fired = 1

    rec = {
        "label": label, "skeleton": int(skeleton), "branch": int(branch),
        "seed": seed, "seat": seat, "my": my, "opp": op, "margin": my - op,
        "win": int(my > op), "bankrupt": int(my < 1000),
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20), "d29": day_cash.get(29),
        "melon_f10": melon_field.get(10, 0), "melon_s10": melon_shed.get(10, 0),
        "branch_fired": fired,
    }
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} "
          f"d10={rec['d10']} d15={rec['d15']} d29={my:.0f} "
          f"m10={rec['melon_f10']}/{rec['melon_s10']} fire={fired}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            rows.append(run("SKEL", seed, seat, True, False))
            rows.append(run("SKEL+BR", seed, seat, True, True))

    out = ROOT / "p16_local_results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(lab, k):
        v = [r[k] for r in rows if r["label"] == lab and r.get(k) is not None]
        return sum(v) / len(v) if v else 0

    print("\n=== SUMMARY ===")
    for lab in ("SKEL", "SKEL+BR"):
        wins = sum(r["win"] for r in rows if r["label"] == lab)
        fires = sum(r["branch_fired"] for r in rows if r["label"] == lab)
        print(f"{lab}: {wins}/8 bank={mean(lab,'my'):.0f} d15={mean(lab,'d15'):.0f} "
              f"d29={mean(lab,'my'):.0f} fires={fires}/8 "
              f"bankrupt={sum(r['bankrupt'] for r in rows if r['label']==lab)}")

    ab = ROOT / "p16_ablation.csv"
    with open(ab, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arm", "wins", "bank", "d15", "d29", "branch_fires", "bankrupt"])
        for lab in ("SKEL", "SKEL+BR"):
            wins = sum(r["win"] for r in rows if r["label"] == lab)
            fires = sum(r["branch_fired"] for r in rows if r["label"] == lab)
            w.writerow([lab, wins, round(mean(lab, "my")), round(mean(lab, "d15")),
                        round(mean(lab, "my")), fires,
                        sum(r["bankrupt"] for r in rows if r["label"] == lab)])
    print("wrote", out.name, ab.name)

    # behavior diff
    bd = ROOT / "p16_behavior_diff.csv"
    with open(bd, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "seat", "skel_d15", "br_d15", "skel_d29", "br_d29", "br_fired"])
        for seat in (0, 1):
            for seed in (1, 2, 3, 4):
                s = next(r for r in rows if r["label"]=="SKEL" and r["seed"]==seed and r["seat"]==seat)
                b = next(r for r in rows if r["label"]=="SKEL+BR" and r["seed"]==seed and r["seat"]==seat)
                w.writerow([seed, seat, s.get("d15"), b.get("d15"), s.get("d29"), b.get("d29"),
                            b.get("branch_fired")])
    print("wrote", bd.name)


if __name__ == "__main__":
    main()
