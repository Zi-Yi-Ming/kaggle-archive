# -*- coding: utf-8 -*-
"""P16.1 three-arm: S0 skeleton / S1 fixed d10 branch / S2 state-derived branch."""
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
        "r2_p161a_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run(arm, seed, seat):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p16_branch
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_skeleton(True)
    p16_branch.set_branch_mode(arm)  # off | fixed | state
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    fires = 0
    fire_days = []

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            nonlocal fires
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            day_cash[day] = float(farm.get("money") or 0)
            # detect fire from planner notes
            try:
                if pmod._PLANNER and pmod._PLANNER.last_targets:
                    notes = getattr(pmod._PLANNER.last_targets, "notes", []) or []
                    if any("branch_force_sell" in str(n) for n in notes):
                        if not fire_days or fire_days[-1] != day:
                            fire_days.append(day)
                            fires += 1
            except Exception:
                pass
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    rec = {
        "arm": arm, "seed": seed, "seat": seat, "my": my,
        "d5": day_cash.get(5), "d10": day_cash.get(10), "d15": day_cash.get(15),
        "d20": day_cash.get(20), "d29": day_cash.get(29),
        "fires": fires, "fire_days": "|".join(str(d) for d in fire_days),
        "bankrupt": int(my < 1000),
    }
    print(f"{arm:5s} s{seed} seat{seat}: d29={my:.0f} d15={rec['d15']} fires={fires} {rec['fire_days']}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            for arm in ("off", "fixed", "state"):
                rows.append(run(arm, seed, seat))

    out = ROOT / "p16_1_ablation.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def mean(arm, k):
        v = [r[k] for r in rows if r["arm"] == arm and r.get(k) is not None]
        return sum(v) / len(v) if v else 0

    print("\n=== SUMMARY ===")
    for arm in ("off", "fixed", "state"):
        fires = sum(r["fires"] for r in rows if r["arm"] == arm)
        print(f"{arm:5s}: bank={mean(arm,'my'):.0f} d15={mean(arm,'d15'):.0f} "
              f"fires={fires}/8 bankrupt={sum(r['bankrupt'] for r in rows if r['arm']==arm)}")

    print("\n=== PAIRED state-fixed ===")
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            st = next(r for r in rows if r["arm"]=="state" and r["seed"]==seed and r["seat"]==seat)
            fx = next(r for r in rows if r["arm"]=="fixed" and r["seed"]==seed and r["seat"]==seat)
            of = next(r for r in rows if r["arm"]=="off" and r["seed"]==seed and r["seat"]==seat)
            print(f"  s{seed} seat{seat}: off={of['my']:.0f} fixed={fx['my']:.0f} state={st['my']:.0f} "
                  f"Δstate-fixed={st['my']-fx['my']:+.0f} fires={fx['fires']}/{st['fires']}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
