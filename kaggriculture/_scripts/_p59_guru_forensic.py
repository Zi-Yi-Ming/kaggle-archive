# -*- coding: utf-8 -*-
"""P59: d15–20 alperen vs guru forensic. Read-only. No candidate policy."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
GURU = ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)
WIN0, WIN1 = 15, 21  # d15–20 inclusive


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def classify(a, b):
    ma = json.dumps(a.get("market"), sort_keys=True, default=str)
    mb = json.dumps(b.get("market"), sort_keys=True, default=str)
    if ma != mb:
        if any(o and o[0] == "SELL" for o in (a.get("market") or []) + (b.get("market") or [])):
            return "SELL"
        return "MARKET_OTHER"
    return "WORKER"


def eco(obs, act):
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    tiles = farm.get("tiles") or []
    plants = animals = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants += 1
                if t.get("animal"):
                    animals += 1
    money = float(farm.get("money") or 0)
    inv = sum(int(v or 0) for v in shed.values())
    px = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80,
          "EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40}
    inv_val = sum(int(v or 0) * px.get(k, 1) for k, v in shed.items())
    sell_q = sum(int(o[2]) for o in (act.get("market") or []) if o and o[0] == "SELL" and len(o) >= 3)
    buy_q = sum(1 for o in (act.get("market") or []) if o and o[0] and str(o[0]).startswith("BUY"))
    hire_n = sum(1 for o in (act.get("market") or []) if o and o[0] == "HIRE")
    return {
        "money": money,
        "plants": plants,
        "animals": animals,
        "hands": len(farm.get("hands") or []),
        "land": len(farm.get("unlocked_quadrants") or []),
        "inv": inv,
        "inv_val": inv_val,
        "asset": money + inv_val,
        "sell_q": sell_q,
        "buy_n": buy_q,
        "hire_n": hire_n,
    }


def run_pair(a_fn, b_fn, seed):
    sa, sb, aa, ab = [], [], [], []

    def wa(obs, configuration=None):
        act = a_fn(obs, configuration)
        sa.append(eco(obs, act))
        aa.append(act)
        return act

    def wb(obs, configuration=None):
        act = b_fn(obs, configuration)
        sb.append(eco(obs, act))
        ab.append(act)
        return act

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wa, wb])
    f = env.steps[-1]
    return sa, sb, aa, ab, (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def main():
    print("=== P59 d15–20 alperen vs guru ===", flush=True)
    # per-seed daily eco gap
    daily_gaps = []  # list of dict seed, day, gap_asset, gap_money, ...
    type_by_day = Counter()
    persistent_notes = []

    for seed in SEEDS:
        alp = load_quiet(ALPEREN, f"p59a_{seed}")
        guru = load_quiet(GURU, f"p59g_{seed}")
        sa, sb, aa, ab, banks = run_pair(alp, guru, seed)
        ba, bg = banks
        print(f"\nseed {seed}: alp={ba:.0f} guru={bg:.0f} {'GURU' if bg>ba+1 else ('ALP' if ba>bg+1 else 'TIE')}", flush=True)

        print(f"  {'d':>3} {'a_money':>8} {'g_money':>8} {'d_money':>8} "
              f"{'a_asset':>8} {'g_asset':>8} {'d_asset':>8} "
              f"{'a_pl':>4} {'g_pl':>4} {'a_an':>4} {'g_an':>4} "
              f"{'a_hd':>4} {'g_hd':>4} {'div':>4} {'types'}", flush=True)

        for day in range(WIN0, WIN1):
            t = day * 24
            if t >= min(len(sa), len(sb)):
                continue
            ea, eb = sa[t], sb[t]  # dawn snapshot
            # midday snapshot too
            t2 = min(t + 12, len(sa) - 1, len(sb) - 1)
            ea2, eb2 = sa[t2], sb[t2]
            # use midday for money/asset
            gap_m = eb2["money"] - ea2["money"]
            gap_a = eb2["asset"] - ea2["asset"]
            n_div = 0
            types = Counter()
            for u in range(t, min(t + 24, len(aa), len(ab))):
                if akey(aa[u]) != akey(ab[u]):
                    n_div += 1
                    types[classify(aa[u], ab[u])] += 1
                    type_by_day[(day, classify(aa[u], ab[u]))] += 1
            print(f"  {day:3d} {ea2['money']:8.0f} {eb2['money']:8.0f} {gap_m:8.0f} "
                  f"{ea2['asset']:8.0f} {eb2['asset']:8.0f} {gap_a:8.0f} "
                  f"{ea2['plants']:4d} {eb2['plants']:4d} {ea2['animals']:4d} {eb2['animals']:4d} "
                  f"{ea2['hands']:4d} {eb2['hands']:4d} {n_div:4d} {dict(types)}", flush=True)
            daily_gaps.append({
                "seed": seed, "day": day,
                "alp_money": ea2["money"], "guru_money": eb2["money"], "gap_money": gap_m,
                "alp_asset": ea2["asset"], "guru_asset": eb2["asset"], "gap_asset": gap_a,
                "alp_plants": ea2["plants"], "guru_plants": eb2["plants"],
                "alp_animals": ea2["animals"], "guru_animals": eb2["animals"],
                "alp_hands": ea2["hands"], "guru_hands": eb2["hands"],
                "alp_sell_q": ea2["sell_q"], "guru_sell_q": eb2["sell_q"],
                "n_div": n_div, "types": json.dumps(dict(types)),
            })

        # first day in window where |gap_asset| > 2000
        first_big = None
        for day in range(WIN0, WIN1):
            row = next((g for g in daily_gaps if g["seed"] == seed and g["day"] == day), None)
            if row and abs(row["gap_asset"]) > 2000:
                first_big = day
                break
        print(f"  first |gap_asset|>2k at d{first_big}", flush=True)
        if first_big is not None:
            persistent_notes.append((seed, first_big))

    # summarize gap_asset trend mean across seeds
    print("\n=== mean gap_asset (guru−alperen) by day ===", flush=True)
    by_day = defaultdict(list)
    for g in daily_gaps:
        by_day[g["day"]].append(g["gap_asset"])
    for day in range(WIN0, WIN1):
        vals = by_day.get(day) or []
        if vals:
            print(f"  d{day}: mean={sum(vals)/len(vals):+.0f} "
                  f"min={min(vals):+.0f} max={max(vals):+.0f}", flush=True)

    print("\n=== div types in window ===", flush=True)
    type_tot = Counter()
    for (day, typ), n in type_by_day.items():
        type_tot[typ] += n
    print(type_tot.most_common(), flush=True)

    # persistent mechanism check: same first_big day across ≥2 seeds?
    print("\nfirst_big days", persistent_notes, flush=True)
    cnt = Counter(d for _, d in persistent_notes)
    print("histogram", cnt.most_common(), flush=True)

    with open(ROOT / "p59_guru_forensic.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(daily_gaps[0].keys()))
        wri.writeheader()
        wri.writerows(daily_gaps)

    # decision
    if len(cnt) >= 1 and cnt.most_common(1)[0][1] >= 3:
        print("P59_PASS_WINDOW_LOCATED", flush=True)
    else:
        print("P59_STOP NO_GURU_COUNTER_RULE", flush=True)
    print("wrote p59_guru_forensic.csv", flush=True)


if __name__ == "__main__":
    main()
