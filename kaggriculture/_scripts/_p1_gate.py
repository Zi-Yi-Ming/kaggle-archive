# -*- coding: utf-8 -*-
"""P1 Gate: local R2 phase vs Elite envelope. Diagnostic only."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make

R2 = ROOT / "_push_medal" / "main.py"
ASHOK = ROOT / "_external" / "public_data" / "ashok_top10" / "replays_2026-08-03.parquet"
PRODUCTS = ("STRAWBERRY", "MILK", "WOOL", "MELON", "EGG")


def load_r2(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", str(R2))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_and_trace(seed, seat=0):
    """Run R2 vs fallow_finn (no-op) so R2's own inventory/listing is uncontested-ish.

    Finn doesn't sell into the market much, so drain is mostly town/shop.
    Also run R2 vs R2 for a second condition.
    """
    from _pm_pool import load_agent as load_pool
    a = load_r2(f"s{seed}a")
    b = load_pool("fallow_finn")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a, b] if seat == 0 else [b, a])
    steps = env.steps
    # trace seat of R2
    r2_seat = seat
    inv = defaultdict(lambda: defaultdict(int))  # step -> item
    listed = defaultdict(lambda: defaultdict(int))
    first10 = {}
    n_inv15 = defaultdict(int)
    n_list_inv15 = defaultdict(int)
    for idx, snap in enumerate(steps):
        if r2_seat >= len(snap):
            continue
        rec = snap[r2_seat] or {}
        obs = rec.get("observation") or {}
        action = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        shed = ((obs.get("private") or {}).get("shed")) or {}
        for item in PRODUCTS:
            q = int(shed.get(item) or 0)
            inv[step][item] = q
            if q >= 10 and item not in first10:
                first10[item] = step
            if q >= 15:
                n_inv15[item] += 1
        if int(obs.get("player") or r2_seat) == r2_seat:
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    item = o[1]
                    q = int(o[2] or 0)
                    if q > 0 and item in PRODUCTS:
                        listed[step][item] += q
                        if inv[step].get(item, 0) >= 15:
                            n_list_inv15[item] += 1
    return {
        "seed": seed,
        "seat": seat,
        "first10": first10,
        "n_inv15": dict(n_inv15),
        "n_list_inv15": dict(n_list_inv15),
        "bank": float(steps[-1][r2_seat]["observation"]["farms"][r2_seat]["money"]) if steps else None,
    }


def elite_envelope():
    """Recompute elite first-day inv>=10 medians and P(list|inv>=15) from parquet."""
    import pandas as pd
    df = pd.read_parquet(ASHOK)
    first_days = defaultdict(list)
    n15 = defaultdict(int)
    nlist15 = defaultdict(int)
    for i in range(len(df)):
        try:
            data = json.loads(df.iloc[i]["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            r0, r1 = float(rew[0]), float(rew[1])
        except Exception:
            continue
        if min(r0, r1) < 100000:
            continue
        w = 0 if r0 >= r1 else 1
        steps = data.get("steps") or []
        first10 = {}
        for idx, snap in enumerate(steps):
            if w >= len(snap):
                continue
            rec = snap[w] or {}
            obs = rec.get("observation") or {}
            action = rec.get("action") or {}
            if not isinstance(obs, dict):
                continue
            step = obs.get("step")
            step = int(step) if step is not None else idx
            shed = ((obs.get("private") or {}).get("shed")) or {}
            listed_items = set()
            if int(obs.get("player") or w) == w:
                for o in action.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) > 0:
                        listed_items.add(o[1])
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q >= 10 and item not in first10:
                    first10[item] = step
                if q >= 15:
                    n15[item] += 1
                    if item in listed_items:
                        nlist15[item] += 1
        for item, st in first10.items():
            first_days[item].append(st)
    out = {}
    for item in PRODUCTS:
        days = sorted(s // 24 for s in first_days.get(item, []))
        med = days[len(days) // 2] if days else None
        p = (nlist15[item] / n15[item]) if n15[item] else None
        out[item] = {
            "n_games_first10": len(days),
            "median_first10_day": med,
            "q25": days[len(days) // 4] if days else None,
            "q75": days[(3 * len(days)) // 4] if days else None,
            "n_inv15": n15[item],
            "p_sell_inv15": p,
        }
    return out


def main():
    print("=== Elite envelope ===", flush=True)
    envl = elite_envelope()
    for item, row in envl.items():
        print(f"  {item}: first10 med={row['median_first10_day']} "
              f"[{row['q25']},{row['q75']}] P(SELL|inv>=15)={row['p_sell_inv15']}", flush=True)

    print("\n=== Local R2 vs fallow_finn ===", flush=True)
    local = []
    for seed in range(1, 9):
        try:
            r = run_and_trace(seed, seat=0)
            local.append(r)
            print(f"  seed{seed}: first10={r['first10']} bank={r['bank']:.0f}", flush=True)
        except Exception as e:
            import traceback
            print("FAIL", seed, e)
            traceback.print_exc()

    # also 4 seeds seat1
    print("\n=== Local R2 vs fallow_finn seat1 ===", flush=True)
    for seed in range(1, 5):
        try:
            r = run_and_trace(seed, seat=1)
            local.append(r)
            print(f"  seed{seed}: first10={r['first10']} bank={r['bank']:.0f}", flush=True)
        except Exception as e:
            print("FAIL seat1", seed, e)

    # aggregate local
    print("\n=== LOCAL R2 aggregate ===", flush=True)
    rows_csv = []
    for item in PRODUCTS:
        days = sorted(r["first10"][item] // 24 for r in local if item in r["first10"])
        med = days[len(days) // 2] if days else None
        n15 = sum(r["n_inv15"].get(item, 0) for r in local)
        nl = sum(r["n_list_inv15"].get(item, 0) for r in local)
        p = (nl / n15) if n15 else None
        e = envl.get(item) or {}
        delta = None
        if med is not None and e.get("median_first10_day") is not None:
            delta = med - e["median_first10_day"]
        ratio = None
        if p is not None and e.get("p_sell_inv15"):
            ratio = p / e["p_sell_inv15"]
        print(f"  {item}: local_first10_med={med} elite={e.get('median_first10_day')} "
              f"delta_days={delta}  local_P={p} elite_P={e.get('p_sell_inv15')} ratio={ratio}", flush=True)
        rows_csv.append({
            "product": item,
            "local_R2_first_day_inv10_median": med,
            "elite_median_first_day_inv10": e.get("median_first10_day"),
            "delta_days": delta,
            "local_R2_P_sell_given_inv15": p,
            "elite_P_sell_given_inv15": e.get("p_sell_inv15"),
            "ratio_local_over_elite": ratio,
            "local_n_inv15": n15,
            "local_n_list_inv15": nl,
            "elite_n_inv15": e.get("n_inv15"),
            "n_local_games": len(local),
        })

    import csv
    outp = ROOT / "p1_gate_metrics.csv"
    with open(outp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_csv[0].keys()))
        w.writeheader()
        w.writerows(rows_csv)
    print("wrote", outp)
    json.dump({"elite": envl, "local": local}, open(ROOT / "p1_gate_raw.json", "w"), indent=2)


if __name__ == "__main__":
    main()
