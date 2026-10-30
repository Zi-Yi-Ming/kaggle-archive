# -*- coding: utf-8 -*-
"""P2-E1: outlier / near-quantity execution analysis on elite mirrors.

Observation: P0/P1 show similar list counts and (locally) similar phase.
Hypothesis H2: same qty, different realized conversion (timing x price).
Experiment: among elite games, pair by similar total STRAWBERRY listed d15-29
and compare revenue proxy (sum qty*price at list time), inv phase, margin.
Also: winner vs loser list-price CDF when inv in mid buckets.

Falsifier: if high/low revenue is uncorrelated with timing/price features
beyond noise, drop H2 for strawberry.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
ASHOK = ROOT / "_external" / "public_data" / "ashok_top10" / "replays_2026-08-03.parquet"
PROD = "STRAWBERRY"


def extract_player(steps, player):
    listed = []  # (step, qty, price, inv_before)
    inv_day = {}
    for idx, snap in enumerate(steps):
        if player >= len(snap):
            continue
        rec = snap[player] or {}
        obs = rec.get("observation") or {}
        action = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        shed = ((obs.get("private") or {}).get("shed")) or {}
        inv = int(shed.get(PROD) or 0)
        if step % 24 == 0:
            inv_day[step // 24] = inv
        if int(obs.get("player") or player) != player:
            continue
        prices = ((obs.get("market") or {}).get("prices") or {})
        px = int(prices.get(PROD) or 0)
        for o in action.get("market") or []:
            if o and o[0] == "SELL" and o[1] == PROD and len(o) >= 3:
                q = int(o[2] or 0)
                if q > 0 and 15 <= step // 24 <= 29:
                    listed.append((step, q, px, inv))
    tot_q = sum(q for _, q, _, _ in listed)
    rev = sum(q * p for _, q, p, _ in listed)
    # first list in window, mean price, share listed when inv>=15
    first = min((s for s, _, _, _ in listed), default=None)
    mean_px = rev / tot_q if tot_q else None
    inv15_q = sum(q for _, q, _, inv in listed if inv >= 15)
    # day of max inv
    max_day = max(inv_day, key=lambda d: inv_day[d]) if inv_day else None
    return {
        "tot_q": tot_q,
        "rev": rev,
        "mean_px": mean_px,
        "first_list": first,
        "first_list_day": (first // 24) if first is not None else None,
        "inv15_share": (inv15_q / tot_q) if tot_q else None,
        "max_inv": inv_day.get(max_day, 0) if max_day is not None else 0,
        "max_inv_day": max_day,
        "inv_d20": inv_day.get(20),
        "inv_d25": inv_day.get(25),
        "n_events": len(listed),
    }


def main():
    df = pd.read_parquet(ASHOK)
    rows = []
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
        l = 1 - w
        steps = data.get("steps") or []
        fw = extract_player(steps, w)
        fl = extract_player(steps, l)
        rows.append({
            "episode_id": int(df.iloc[i]["episode_id"]),
            "margin": abs(r0 - r1),
            "w_tot_q": fw["tot_q"], "w_rev": fw["rev"], "w_mean_px": fw["mean_px"],
            "w_first_day": fw["first_list_day"], "w_inv15_share": fw["inv15_share"],
            "w_max_inv": fw["max_inv"], "w_max_inv_day": fw["max_inv_day"],
            "w_n_events": fw["n_events"],
            "l_tot_q": fl["tot_q"], "l_rev": fl["rev"], "l_mean_px": fl["mean_px"],
            "l_first_day": fl["first_list_day"],
        })
    d = pd.DataFrame(rows)
    print("n", len(d))
    # correlation of margin with w-l rev and w-l first_day
    d["d_rev"] = d.w_rev - d.l_rev
    d["d_q"] = d.w_tot_q - d.l_tot_q
    d["d_first"] = d.w_first_day - d.l_first_day
    d["d_px"] = d.w_mean_px - d.l_mean_px
    print("\n=== margin vs deltas (spearman-like via rank corr) ===")
    for col in ("d_rev", "d_q", "d_first", "d_px"):
        if d[col].notna().sum() > 10:
            print(f"  corr(margin, {col}) = {d['margin'].corr(d[col], method='spearman'):.3f}")
    print("\n=== winner vs loser means ===")
    for col in ("tot_q", "rev", "mean_px", "first_day"):
        print(f"  {col}: win={d['w_'+col].mean():.2f} lose={d['l_'+col].mean():.2f}")

    # near-quantity pairs: bucket tot_q and compare rev spread
    print("\n=== near-quantity: win rev vs lose rev within q-bin ===")
    d["qbin"] = pd.cut(d.w_tot_q, bins=[0, 80, 120, 160, 200, 10**9])
    for b, g in d.groupby("qbin", observed=True):
        if len(g) < 8:
            continue
        print(f"  qbin {b}: n={len(g)} win_rev={g.w_rev.mean():.0f} lose_rev={g.l_rev.mean():.0f} "
              f"win_px={g.w_mean_px.mean():.1f} lose_px={g.l_mean_px.mean():.1f} "
              f"win_first={g.w_first_day.mean():.1f} margin={g.margin.mean():.0f}")

    # top vs bottom margin quartile
    d = d.sort_values("margin")
    lo, hi = d.head(len(d)//4), d.tail(len(d)//4)
    print("\n=== bottom vs top margin quartile ===")
    for name, g in (("low_margin", lo), ("high_margin", hi)):
        print(f"  {name}: margin={g.margin.mean():.0f} d_rev={g.d_rev.mean():.0f} "
              f"d_q={g.d_q.mean():.1f} d_first={g.d_first.mean():.2f} d_px={g.d_px.mean():.1f} "
              f"w_first={g.w_first_day.mean():.1f} l_first={g.l_first_day.mean():.1f}")

    # outliers: high win rev low lose rev
    d["rev_gap"] = d.w_rev - d.l_rev
    top = d.nlargest(8, "rev_gap")
    print("\n=== top 8 rev_gap games ===")
    print(top[["episode_id", "margin", "w_tot_q", "w_rev", "w_mean_px", "w_first_day",
               "l_tot_q", "l_rev", "l_mean_px", "l_first_day"]].to_string(index=False))
    d.to_csv(ROOT / "p2_straw_execution.csv", index=False)
    print("wrote p2_straw_execution.csv")


if __name__ == "__main__":
    main()
