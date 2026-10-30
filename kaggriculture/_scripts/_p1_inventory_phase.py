# -*- coding: utf-8 -*-
"""P1: inventory-drain phase and listing-probability analysis.

Data: ashok elite parquet (both >=100k) + optional R2 live replays.
No agent modification. Observational only.

Outputs (under kaggriculture/):
  inventory_drain_phase.csv
  inventory_listing_probability.csv
  elite_vs_r2_phase_diff.csv
  RESEARCH_P1.md  (written separately after we see results)
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
ASHOK = ROOT / "_external" / "public_data" / "ashok_top10" / "replays_2026-08-03.parquet"
REPLAYS = ROOT / "_external" / "replays"
PRODUCTS = ("STRAWBERRY", "MILK", "WOOL", "MELON", "EGG", "WHEAT", "FERTILIZER")


def extract_series(steps, player):
    """Per-step series for one player from their own observation/actions.

    Returns lists aligned to step index:
      inv[step][item], listed[step][item]=qty, price[step][item]
    """
    inv = []
    listed = []
    price = []
    shops_n = []
    for idx, snap in enumerate(steps):
        if player >= len(snap):
            inv.append({})
            listed.append({})
            price.append({})
            shops_n.append(None)
            continue
        rec = snap[player] or {}
        obs = rec.get("observation") or {}
        action = rec.get("action") or {}
        if not isinstance(obs, dict):
            inv.append({})
            listed.append({})
            price.append({})
            shops_n.append(None)
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        # pad if needed
        while len(inv) < step:
            inv.append({})
            listed.append({})
            price.append({})
            shops_n.append(None)
        shed = ((obs.get("private") or {}).get("shed")) or {}
        inv_row = {k: int(shed.get(k) or 0) for k in PRODUCTS}
        if step < len(inv):
            inv[step] = inv_row
        else:
            inv.append(inv_row)
            listed.append({})
            price.append({})
            shops_n.append(None)
        prices = ((obs.get("market") or {}).get("prices") or {})
        price_row = {k: int(prices.get(k) or 0) for k in PRODUCTS}
        if step < len(price):
            price[step] = price_row
        else:
            price.append(price_row)
        shops = (obs.get("town") or {}).get("unlocked_shops") or []
        if step < len(shops_n):
            shops_n[step] = len(shops)
        else:
            shops_n.append(len(shops))
        list_row = {}
        if int(obs.get("player") or player) == player:
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    item = o[1]
                    q = int(o[2] or 0)
                    if q > 0:
                        list_row[item] = list_row.get(item, 0) + q
        if step < len(listed):
            listed[step] = list_row
        else:
            listed.append(list_row)
    # ensure same length
    n = max(len(inv), len(listed), len(price), len(shops_n))
    inv += [{}] * (n - len(inv))
    listed += [{}] * (n - len(listed))
    price += [{}] * (n - len(price))
    shops_n += [None] * (n - len(shops_n))
    return inv, listed, price, shops_n


def day_boundary(inv, listed, day, product):
    """Return inv at first step of day, total listed that day."""
    s0, s1 = day * 24, (day + 1) * 24
    inv_start = inv[s0].get(product, 0) if s0 < len(inv) else 0
    inv_end = inv[min(s1 - 1, len(inv) - 1)].get(product, 0) if inv else 0
    listed_day = sum(listed[s].get(product, 0) for s in range(s0, min(s1, len(listed))))
    return inv_start, inv_end, listed_day


def analyze_game(steps, player, tag):
    inv, listed, price, shops_n = extract_series(steps, player)
    rows = []
    for day in range(0, 30):
        for product in PRODUCTS:
            inv_start, inv_end, listed_day = day_boundary(inv, listed, day, product)
            # crude production proxy: inv_end - inv_start + listed_day (ignores drain/fill)
            # drain proxy cannot be isolated without engine internals; record listed & inv
            prices = [price[s].get(product, 0) for s in range(day * 24, min((day + 1) * 24, len(price))) if price[s].get(product)]
            px = sum(prices) / len(prices) if prices else None
            rows.append({
                "tag": tag,
                "day": day,
                "product": product,
                "inv_start": inv_start,
                "inv_end": inv_end,
                "listed": listed_day,
                "price_mean": px,
                "shops": shops_n[day * 24] if day * 24 < len(shops_n) else None,
            })
    # per-step listing vs inv for probability tables
    step_rows = []
    for s in range(len(listed)):
        for product in PRODUCTS:
            q = listed[s].get(product, 0)
            inv_s = inv[s].get(product, 0) if s < len(inv) else 0
            px = price[s].get(product, 0) if s < len(price) else 0
            if q > 0 or inv_s > 0:
                step_rows.append({
                    "tag": tag,
                    "step": s,
                    "day": s // 24,
                    "product": product,
                    "inv": inv_s,
                    "listed": q,
                    "listed_flag": 1 if q > 0 else 0,
                    "price": px,
                })
    return rows, step_rows


def load_ep(data, seat):
    steps = data.get("steps") or []
    return extract_series(steps, seat)


def main():
    df = pd.read_parquet(ASHOK)
    phase_rows = []
    step_rows = []
    n_elite = 0
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
        n_elite += 1
        pr, sr = analyze_game(steps, w, "elite_win")
        phase_rows.extend(pr)
        step_rows.extend(sr)
        pr, sr = analyze_game(steps, l, "elite_lose")
        phase_rows.extend(pr)
        step_rows.extend(sr)

    # R2 live samples
    n_r2 = 0
    for p in sorted(REPLAYS.glob("episode-1080*-replay.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        teams = (data.get("info") or {}).get("TeamNames") or []
        if "ZiYiMing" not in teams:
            continue
        seat = teams.index("ZiYiMing")
        steps = data.get("steps") or []
        n_r2 += 1
        pr, sr = analyze_game(steps, seat, "r2_live")
        phase_rows.extend(pr)
        step_rows.extend(sr)

    print(f"elite_games={n_elite} r2_replays={n_r2}")
    phase_df = pd.DataFrame(phase_rows)
    step_df = pd.DataFrame(step_rows)
    phase_df.to_csv(ROOT / "inventory_drain_phase.csv", index=False)
    step_df.to_csv(ROOT / "elite_vs_r2_phase_diff.csv", index=False)

    # listing probability by inv bucket
    buckets = [0, 1, 5, 10, 15, 20, 30, 50, 100, 10**9]
    labels = ["0", "1-4", "5-9", "10-14", "15-19", "20-29", "30-49", "50-99", "100+"]
    step_df["inv_bucket"] = pd.cut(step_df["inv"], bins=buckets, labels=labels, right=False)
    prob = (
        step_df.groupby(["tag", "product", "inv_bucket"], observed=True)
        .agg(n=("listed_flag", "size"), p_list=("listed_flag", "mean"),
             listed_qty=("listed", "mean"), price=("price", "mean"))
        .reset_index()
    )
    prob.to_csv(ROOT / "inventory_listing_probability.csv", index=False)

    # day-level means
    print("\n=== day-level inv_start / listed (STRAWBERRY) ===")
    for tag in ("elite_win", "elite_lose", "r2_live"):
        sub = phase_df[(phase_df.tag == tag) & (phase_df["product"] == "STRAWBERRY")]
        if sub.empty:
            continue
        g = sub.groupby("day").agg(inv=("inv_start", "mean"), listed=("listed", "mean"))
        print(f"\n[{tag}]")
        for day in range(10, 30):
            if day in g.index:
                print(f"  d{day:02d} inv={g.loc[day,'inv']:5.1f} listed={g.loc[day,'listed']:5.1f}")

    print("\n=== listing P by inv bucket (STRAWBERRY d12-27) ===")
    sub = step_df[(step_df["product"] == "STRAWBERRY") & (step_df.day >= 12) & (step_df.day <= 27)]
    for tag in ("elite_win", "elite_lose", "r2_live"):
        s2 = sub[sub.tag == tag]
        if s2.empty:
            continue
        gg = s2.groupby("inv_bucket", observed=True).agg(n=("listed_flag", "size"), p=("listed_flag", "mean"))
        print(f"\n[{tag}]")
        for b, row in gg.iterrows():
            if row["n"] >= 20:
                print(f"  inv {b}: n={int(row['n'])} P(list)={row['p']:.3f}")

    print("\n=== first day inv>10 for premium (mean over games) ===")
    for tag in ("elite_win", "r2_live"):
        sub = phase_df[phase_df.tag == tag]
        for product in ("STRAWBERRY", "MILK", "WOOL"):
            days = []
            for (t, day), grp in sub[sub["product"] == product].groupby(["tag", "day"]):
                if grp["inv_start"].mean() >= 10:
                    days.append(day)
            if days:
                print(f"  {tag} {product}: first day inv>=10 ≈ {min(days)}")


if __name__ == "__main__":
    main()
