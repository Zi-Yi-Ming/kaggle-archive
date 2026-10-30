# -*- coding: utf-8 -*-
"""P6.1: inventory_before large SELL events in R2 live + local replays."""
from __future__ import annotations

import csv
import importlib.util
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "replays"
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

# dump threshold: requested sell qty >= 100 (tape uses 1000 caps)
DUMP_Q = 100
PREMIUM = ("STRAWBERRY", "MILK", "WOOL", "MELON", "EGG", "WHEAT", "FERTILIZER", "CARROT", "TOMATO")


def audit_steps(steps, seat, source):
    """For each large SELL by `seat`, record shed before that turn's actions."""
    rows = []
    for idx, snap in enumerate(steps):
        if seat >= len(snap):
            continue
        rec = snap[seat] or {}
        obs = rec.get("observation") or {}
        act = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        if int(obs.get("player") or seat) != seat:
            continue
        shed = ((obs.get("private") or {}).get("shed")) or {}
        prices = ((obs.get("market") or {}).get("prices")) or {}
        for o in act.get("market") or []:
            if not o or o[0] != "SELL" or len(o) < 3:
                continue
            item, q = o[1], int(o[2] or 0)
            if q < DUMP_Q:
                continue
            inv = int(shed.get(item) or 0)
            rows.append({
                "source": source,
                "step": step,
                "day": step // 24,
                "item": item,
                "requested_q": q,
                "inv_before": inv,
                # actual sell cannot exceed inv; cap is hollow if inv << q
                "actual_cap": min(q, inv),
                "price": int(prices.get(item) or 0),
                "hollow": q > inv,
            })
    return rows


def local_r2_trace(seeds=(1, 2, 3)):
    """Run R2 vs fallow_finn and dump large SELL events with inv_before."""
    rows = []
    for seed in seeds:
        spec = importlib.util.spec_from_file_location(f"r2_{seed}", str(ROOT / "_push_medal" / "main.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        from _pm_pool import load_agent as load_pool
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.configuration["seed"] = seed
        env.run([m.agent, load_pool("fallow_finn")])
        rows.extend(audit_steps(env.steps, 0, f"local_finn_s{seed}"))
    return rows


def main():
    all_rows = []

    # live replays: seat of ZiYiMing
    for p in sorted(REP.glob("episode-*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        teams = (data.get("info") or {}).get("TeamNames") or []
        if "ZiYiMing" not in teams:
            continue
        seat = teams.index("ZiYiMing")
        rows = audit_steps(data.get("steps") or [], seat, f"live:{p.name}")
        all_rows.extend(rows)

    print(f"live dump events: {len(all_rows)}")

    # local
    try:
        local_rows = local_r2_trace()
        print(f"local dump events: {len(local_rows)}")
        all_rows.extend(local_rows)
    except Exception as e:
        import traceback
        print("local trace fail", e)
        traceback.print_exc()

    if not all_rows:
        print("NO dump events found — STOP")
        return

    # stats by item for premium + all
    print("\n=== inventory_before large SELL (q>=100) ===")
    by_item = defaultdict(list)
    for r in all_rows:
        by_item[r["item"]].append(r["inv_before"])
    for item in sorted(by_item, key=lambda k: -len(by_item[k])):
        vals = by_item[item]
        vals_s = sorted(vals)
        n = len(vals)
        med = st.median(vals_s)
        p25 = vals_s[n // 4]
        p75 = vals_s[(3 * n) // 4]
        p90 = vals_s[int(0.9 * (n - 1))]
        print(f"  {item:12s} n={n:4d} mean={st.mean(vals):6.1f} med={med:5.1f} "
              f"p25={p25:5.1f} p75={p75:5.1f} p90={p90:5.1f} max={max(vals)}")

    # Gate A: premium focus
    prem_vals = []
    for item in ("STRAWBERRY", "MILK", "WOOL", "MELON"):
        prem_vals.extend(by_item.get(item, []))
    if prem_vals:
        prem_s = sorted(prem_vals)
        med = st.median(prem_s)
        p75 = prem_s[(3 * len(prem_s)) // 4]
        n_ge50 = sum(1 for v in prem_s if v >= 50)
        n_ge40 = sum(1 for v in prem_s if v >= 40)
        print(f"\n=== PREMIUM combined n={len(prem_s)} med={med} p75={p75} "
              f">=40:{n_ge40} >=50:{n_ge50}")
        print(f"  hollow dumps (q>inv): {sum(1 for r in all_rows if r['hollow'])}/{len(all_rows)}")

    # sample largest requested vs inv
    print("\n=== sample events ===")
    for r in all_rows[:8]:
        print(f"  {r['source'][:30]:30s} d{r['day']:02d} {r['item']:10s} q={r['requested_q']:5d} inv={r['inv_before']:4d} hollow={r['hollow']}")

    # CSV
    path = ROOT / "p6_1_dump_inventory.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    print("wrote", path)

    # Gate decision print
    if prem_vals:
        if med <= 20 and p75 <= 30:
            print("\nGATE_A_PASS: STOP_PRICE_CURVE")
        elif med >= 40 or n_ge50 >= max(3, 0.2 * len(prem_s)):
            print("\nGATE_B_PASS: RUN_SPLIT_DUMP_COUNTERFACTUAL")
        else:
            print(f"\nGATE_BORDERLINE med={med} p75={p75} — lean STOP_PRICE_CURVE")


if __name__ == "__main__":
    main()
