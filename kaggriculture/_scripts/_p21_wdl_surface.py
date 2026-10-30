# -*- coding: utf-8 -*-
"""P21: W/D/L counterfactual surface vs mid-tier opponent (rancher_rita).

Same force-tail protocol as P19/P20; outcome = W/D/L vs one fixed opponent family.
Primary label: P(W)+0.5*P(D) over seeds. Also record bank and cash@5.
No NN. No submit.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

OPP_KEY = "broker_bea"  # tier 6 — mid; seek ~50% W/L knife-edge


def load_opp():
    from _pm_pool import load_agent
    return load_agent(OPP_KEY)


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p21_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


FORCE = {"enabled": False, "day": 10, "tail": "MAIN"}


def count_tiles(tiles):
    melon = plant = animals = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plant += 1
                    if t.get("crop") == "MELON":
                        melon += 1
                if t.get("animal"):
                    animals += 1
    return melon, plant, animals


def run(force_day, tail, seed, seat=0, opponent="pool"):
    FORCE.update(enabled=True, day=force_day, tail=tail)
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p16_branch
    import p17_1_library
    import p18_selector as sel
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    sel.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_opp()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    day_cash = {}
    state_at = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            shed = dict(private.get("shed") or {})
            tiles = farm.get("tiles") or []
            melon, plant, animals = count_tiles(tiles)
            if step % 24 == 0:
                day_cash[day] = float(farm.get("money") or 0)
                state_at[day] = {
                    "money": float(farm.get("money") or 0),
                    "melon": melon, "plant": plant, "animals": animals,
                    "shed_total": sum(int(v or 0) for v in shed.values()),
                }
            return action
        return agent

    import p18_selector as selmod
    orig = selmod.decide

    def forced_decide(day, state):
        if FORCE["enabled"] and FORCE["day"] <= day <= FORCE["day"] + 10:
            return FORCE["tail"]
        return "MAIN"

    selmod.decide = forced_decide
    selmod.ENABLED = True

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    selmod.decide = orig
    selmod.ENABLED = False
    FORCE["enabled"] = False

    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    if my > op:
        outcome = "W"
    elif my == op:
        outcome = "D"
    else:
        outcome = "L"
    st = state_at.get(force_day, {})
    margin = my - op
    rec = {
        "opponent": opponent, "seed": seed, "seat": seat,
        "force_day": force_day, "tail": tail,
        "my": my, "opp": op, "outcome": outcome, "margin": margin,
        "cash_d5": day_cash.get(min(force_day + 5, 29)),
        "cash_force": st.get("money"),
        "melon_force": st.get("melon"),
        "animals_force": st.get("animals"),
    }
    print(f"{opponent} d{force_day} {tail:12s} s{seed}: {outcome} "
          f"my={my:.0f} opp={op:.0f} m={margin:+.0f} mel={st.get('melon')} c5={rec['cash_d5']}", flush=True)
    return rec


def main():
    rows = []
    for seed in (1, 2):
        for day in (9, 10):
            for tail in ("MAIN", "CASH_WINDOW", "HERD_SCALE"):
                rows.append(run(day, tail, seed, seat=0, opponent="pool"))

    out = ROOT / "p21_wdl_surface.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # aggregate P(W/D/L) per (day, tail) across seeds
    print("\n=== W/D/L by (day, tail) over seeds ===")
    groups = defaultdict(list)
    for r in rows:
        groups[(r["force_day"], r["tail"])].append(r)
    summary = []
    for key, g in sorted(groups.items()):
        n = len(g)
        nw = sum(1 for x in g if x["outcome"] == "W")
        nd = sum(1 for x in g if x["outcome"] == "D")
        nl = sum(1 for x in g if x["outcome"] == "L")
        pw, pd, pl = nw / n, nd / n, nl / n
        score = pw + 0.5 * pd
        print(f"  d{key[0]} {key[1]:12s}: W{nw}/D{nd}/L{nl}  P(W)+.5P(D)={score:.2f}  "
              f"bank_mean={sum(x['my'] for x in g)/n:.0f}")
        summary.append({
            "day": key[0], "tail": key[1], "n": n,
            "pw": pw, "pd": pd, "pl": pl, "score": score,
            "bank_mean": sum(x["my"] for x in g) / n,
        })

    # best tail by WDL score per day
    print("\n=== BEST tail by W/D/L score ===")
    best_rules = []
    by_day = defaultdict(list)
    for s in summary:
        by_day[s["day"]].append(s)
    for day, g in sorted(by_day.items()):
        best = max(g, key=lambda x: x["score"])
        print(f"  d{day}: best={best['tail']} score={best['score']:.2f} "
              + ", ".join(f"{x['tail']}={x['score']:.2f}" for x in g))
        best_rules.append({"day": day, "best_tail": best["tail"], "score": best["score"]})

    out2 = ROOT / "p21_wdl_summary.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    # selector comparison on these states
    # A: fixed MAIN
    # B: melon>=3 -> CASH (P20 rule)
    # C: W/D/L score argmax (use mean score by day from this table)
    print("\n=== SELECTOR COMPARISON (held same rollouts) ===")
    # For each (seed,day) we have 3 tails; pick according to rule and take that outcome
    by_sd = defaultdict(dict)
    for r in rows:
        by_sd[(r["seed"], r["force_day"])][r["tail"]] = r

    def eval_selector(name, pick_fn):
        nw = nd = nl = 0
        banks = []
        picks = []
        for (seed, day), tails in sorted(by_sd.items()):
            mel = tails["MAIN"].get("melon_force") or 0
            tail = pick_fn(day, mel, tails)
            picks.append(tail)
            r = tails[tail]
            if r["outcome"] == "W":
                nw += 1
            elif r["outcome"] == "D":
                nd += 1
            else:
                nl += 1
            banks.append(r["my"])
        n = nw + nd + nl
        score = (nw + 0.5 * nd) / n if n else 0
        print(f"  {name}: W{nw}/D{nd}/L{nl} score={score:.2f} bank={sum(banks)/len(banks):.0f} "
              f"picks={Counter_picks(picks)}")
        return score, sum(banks) / len(banks)

    def Counter_picks(picks):
        from collections import Counter
        return dict(Counter(picks))

    eval_selector("fixed MAIN", lambda d, m, t: "MAIN")
    eval_selector("P20 melon>=3 CASH", lambda d, m, t: "CASH_WINDOW" if m >= 3 else "MAIN")
    # C: use day-level best from this experiment (in-sample — note overfit risk)
    day_best = {x["day"]: x["best_tail"] for x in best_rules}
    eval_selector("P21 day-argmax WDL", lambda d, m, t: day_best.get(d, "MAIN"))
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
