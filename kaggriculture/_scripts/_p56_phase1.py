# -*- coding: utf-8 -*-
"""P56 Phase1: d9 gate-front state vs later-branch divergence. Read-only."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import statistics
import sys
from collections import defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
R2 = ROOT / "_push_medal" / "main.py"
GURU = ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)
GATE_DAY = 9  # d9 is the peak mid landmark


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def money_bucket(m):
    if m < 500:
        return "0-500"
    if m < 2000:
        return "500-2k"
    if m < 8000:
        return "2k-8k"
    if m < 30000:
        return "8k-30k"
    return "30k+"


def plant_bucket(p):
    if p <= 10:
        return "0-10"
    if p <= 30:
        return "11-30"
    if p <= 50:
        return "31-50"
    return "51+"


def cat_mask(shops):
    """Semantic product categories from shop names — not shop ID string."""
    cats = set()
    for s in shops:
        if s == "FARMERS_MARKET":
            cats.update({"CROP", "SEED"})
        elif s == "BAKERY":
            cats.update({"CROP", "WHEAT"})
        elif s == "ICE_CREAM_SHOP":
            cats.add("DAIRY")
        elif s == "BRUNCH_SPOT":
            cats.update({"EGG", "DAIRY", "WHEAT"})
        elif s == "PET_CAFE":
            cats.add("EGG")
        elif s == "YARN_STORE":
            cats.add("WOOL")
        elif s == "SMOOTHIE_SHOP":
            cats.update({"FRUIT", "MELON"})
        elif s == "PIZZA_SHOP":
            cats.update({"CROP", "TOMATO"})
    return tuple(sorted(cats)) if cats else ("NONE",)


def state_at(obs):
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    tiles = farm.get("tiles") or []
    plants = animals = empty = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants += 1
                if t.get("animal"):
                    animals += 1
    money = float(farm.get("money") or 0)
    inv_val = 0
    px = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80,
          "EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40}
    for k, q in shed.items():
        inv_val += int(q or 0) * px.get(k, 1)
    return {
        "money": money,
        "money_b": money_bucket(money),
        "hands": len(farm.get("hands") or []),
        "n_land": len(farm.get("unlocked_quadrants") or []),
        "plants": plants, "plants_b": plant_bucket(plants),
        "animals": animals, "empty": empty,
        "shed_total": sum(int(v or 0) for v in shed.values()),
        "inv_val": inv_val,
        "n_shops": len(shops),
        "cats": cat_mask(shops),
        "has_farmers": int("FARMERS_MARKET" in shops),
        "has_yarn": int("YARN_STORE" in shops),
        "px_wheat": int(prices.get("WHEAT") or 0),
        "px_melon": int(prices.get("MELON") or 0),
        "px_milk": int(prices.get("MILK") or 0),
    }


def run_pair(a_fn, b_fn, seed):
    sa, sb = [], []
    acts_a, acts_b = [], []

    def wa(obs, configuration=None):
        act = a_fn(obs, configuration)
        sa.append(state_at(obs))
        acts_a.append(act)
        return act

    def wb(obs, configuration=None):
        act = b_fn(obs, configuration)
        sb.append(state_at(obs))
        acts_b.append(act)
        return act

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wa, wb])
    f = env.steps[-1]
    return (sa, sb, acts_a, acts_b,
            float(f[0]["observation"]["farms"][0]["money"]),
            float(f[1]["observation"]["farms"][1]["money"]))


def main():
    alp = load_quiet(ALPEREN, "p56_alp")
    r2 = load_quiet(R2, "p56_r2")
    guru = load_quiet(GURU, "p56_guru")

    gate_t = GATE_DAY * 24  # start of day 9
    late_lo, late_hi = 20 * 24, 29 * 24  # d20–28

    print(f"=== Phase1: d{GATE_DAY} gate-front vs d20+ branch (vs R2) ===", flush=True)
    rows = []
    for seed in SEEDS:
        a2 = load_quiet(ALPEREN, f"p56a_{seed}")
        r2b = load_quiet(R2, f"p56r_{seed}")
        sa, sb, aa, ab, ba, br = run_pair(a2, r2b, seed)

        # gate-front: last state before gate day (step 215 = d8 h23)
        front = sa[gate_t - 1] if gate_t - 1 < len(sa) else sa[-1]
        # late branch: fraction of divergent steps in d20–28
        n = min(len(aa), len(ab), late_hi)
        late_div = sum(1 for t in range(late_lo, n) if akey(aa[t]) != akey(ab[t]))
        late_tot = max(1, n - late_lo)
        # also early similarity d2–5
        e_div = sum(1 for t in range(48, 120) if akey(aa[t]) != akey(ab[t]))

        rec = {
            "seed": seed,
            "alp_bank": ba, "r2_bank": br,
            "front_money": front["money"], "front_money_b": front["money_b"],
            "front_hands": front["hands"], "front_land": front["n_land"],
            "front_plants": front["plants"], "front_plants_b": front["plants_b"],
            "front_animals": front["animals"],
            "front_inv_val": front["inv_val"],
            "front_n_shops": front["n_shops"],
            "front_cats": "|".join(front["cats"]),
            "front_has_farmers": front["has_farmers"],
            "front_px_wheat": front["px_wheat"],
            "front_px_melon": front["px_melon"],
            "early_div_d2_5": e_div,
            "late_div_d20_28": late_div,
            "late_frac": round(late_div / late_tot, 4),
        }
        rows.append(rec)
        print(f"  s{seed}: money={front['money']:.0f} plants={front['plants']} "
              f"cats={front['cats']} early_div={e_div} late_div={late_div} "
              f"late_frac={rec['late_frac']}", flush=True)

    # does front state separate "high late divergence" vs "low"?
    print("\n=== front-state vs late_frac (vs R2) ===", flush=True)
    fracs = [r["late_frac"] for r in rows]
    print(f"late_frac range={min(fracs):.3f}–{max(fracs):.3f} "
          f"mean={statistics.mean(fracs):.3f}", flush=True)

    # group by money_b / plants_b / cats
    for key in ("front_money_b", "front_plants_b", "front_cats", "front_n_shops"):
        groups = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r["late_frac"])
        print(f"  by {key}:", flush=True)
        for k, v in sorted(groups.items(), key=lambda x: -statistics.mean(x[1])):
            print(f"    {k}: n={len(v)} mean_late={statistics.mean(v):.3f}", flush=True)

    # alperen vs guru (different opening family)
    print("\n=== alperen vs guru d9 front ===", flush=True)
    for seed in SEEDS[:4]:
        a2 = load_quiet(ALPEREN, f"p56g_{seed}")
        g2 = load_quiet(GURU, f"p56gu_{seed}")
        sa, sb, aa, ab, ba, bg = run_pair(a2, g2, seed)
        front_a = sa[gate_t - 1]
        late_div = sum(1 for t in range(late_lo, min(len(aa), len(ab), late_hi))
                       if akey(aa[t]) != akey(ab[t]))
        print(f"  s{seed}: alp_money={front_a['money']:.0f} "
              f"guru_bank={bg:.0f} late_div={late_div}/216", flush=True)

    with open(ROOT / "p56_gate_front.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p56_gate_front.csv", flush=True)

    # Phase1 gate
    # If late_frac always ~1 and front states don't cluster → no simple branch selector
    if max(fracs) - min(fracs) < 0.15:
        print("P56_PHASE1=NO_BRANCH_SEPARATION_IN_FRONT_STATE", flush=True)
    else:
        print("P56_PHASE1=FRONT_STATE_VARIES_WITH_LATE_BRANCH", flush=True)


if __name__ == "__main__":
    main()
