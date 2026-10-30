# -*- coding: utf-8 -*-
"""P30-C: opponent archetypes vs R2 (pinned harness).

Question: do R2's losses / low margins concentrate on a few opponent archetypes?
Falsification: if margins are uniform / all wins, no archetype concentration.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p26_harness import load_r2, load_pool  # noqa: E402

OPPONENTS = [
    "fallow_finn", "wheat_walter", "rotation_rosa", "homestead_hana",
    "melon_mateo", "rancher_rita", "broker_bea", "ledger_lena",
    "slotter_silas", "closer_cleo",
]


def run_r2_vs(opp_name, seed, seat_r2=0):
    r2 = load_r2()
    opp = load_pool(opp_name)
    recs = []

    def wrap(inner, is_r2):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            day = step // 24
            if not is_r2 and day in (5, 10, 15, 20, 25) and step % 24 == 0:
                farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
                tiles = farm.get("tiles") or []
                plants = animals = 0
                for row in tiles:
                    for t in row:
                        if isinstance(t, dict):
                            if t.get("kind") == "PLANT":
                                plants += 1
                            if t.get("animal"):
                                animals += 1
                recs.append({
                    "day": day, "money": float(farm.get("money") or 0),
                    "plants": plants, "animals": animals,
                    "hands": len(farm.get("hands") or []),
                })
            return a
        return agent

    agents = [None, None]
    agents[seat_r2] = wrap(r2, True)
    agents[1 - seat_r2] = wrap(opp, False)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run(agents)
    f = env.steps[-1]
    my = float(f[seat_r2]["observation"]["farms"][seat_r2]["money"])
    op = float(f[seat_r2]["observation"]["farms"][1 - seat_r2]["money"])
    outcome = "W" if my > op else ("D" if my == op else "L")
    # opponent features: use last recorded mid snapshot or terminal
    feat = recs[-1] if recs else {}
    return {
        "opp": opp_name, "seed": seed,
        "r2_bank": my, "opp_bank": op, "margin": my - op, "outcome": outcome,
        "opp_d10_money": next((r["money"] for r in recs if r["day"] == 10), None),
        "opp_d20_money": next((r["money"] for r in recs if r["day"] == 20), None),
        "opp_d10_plants": next((r["plants"] for r in recs if r["day"] == 10), None),
        "opp_d10_animals": next((r["animals"] for r in recs if r["day"] == 10), None),
        "opp_d20_plants": next((r["plants"] for r in recs if r["day"] == 20), None),
        "opp_d20_animals": next((r["animals"] for r in recs if r["day"] == 20), None),
        "opp_d25_hands": next((r["hands"] for r in recs if r["day"] == 25), None),
    }


def main():
    rows = []
    for opp in OPPONENTS:
        for seed in (1, 2):
            r = run_r2_vs(opp, seed)
            rows.append(r)
            print(f"  {opp:16s} s{seed}: {r['outcome']} R2={r['r2_bank']:.0f} "
                  f"opp={r['opp_bank']:.0f} m={r['margin']:+.0f} "
                  f"opp_d10={r['opp_d10_money']} ani10={r['opp_d10_animals']}", flush=True)

    out = ROOT / "p30_opponent_features.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # aggregate by opponent
    print("\n=== BY OPPONENT ===")
    by = defaultdict(list)
    for r in rows:
        by[r["opp"]].append(r)
    summary = []
    for opp, g in sorted(by.items(), key=lambda kv: sum(x["margin"] for x in kv[1]) / len(kv[1])):
        margins = [x["margin"] for x in g]
        wins = sum(1 for x in g if x["outcome"] == "W")
        losses = sum(1 for x in g if x["outcome"] == "L")
        summary.append({
            "opp": opp, "n": len(g), "W": wins, "L": losses,
            "mean_margin": sum(margins) / len(margins),
            "min_margin": min(margins),
            "mean_opp_d10": sum(x["opp_d10_money"] or 0 for x in g) / len(g),
            "mean_opp_ani10": sum(x["opp_d10_animals"] or 0 for x in g) / len(g),
        })
        print(f"  {opp:16s} W{wins}/L{losses} mean_m={sum(margins)/len(margins):+.0f} "
              f"min_m={min(margins):+.0f} opp_d10={summary[-1]['mean_opp_d10']:.0f} "
              f"ani10={summary[-1]['mean_opp_ani10']:.1f}", flush=True)

    out2 = ROOT / "p30_opponent_clusters.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    n_loss = sum(1 for r in rows if r["outcome"] == "L")
    n = len(rows)
    print(f"\nR2 losses: {n_loss}/{n}")
    if n_loss == 0:
        print("OPPONENT_ARCHETYPE_CONCENTRATION = NOT_APPLICABLE_NO_LOSSES")
    else:
        # concentration among losses
        loss_by = Counter(r["opp"] for r in rows if r["outcome"] == "L")
        print("loss by opp:", dict(loss_by))
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
