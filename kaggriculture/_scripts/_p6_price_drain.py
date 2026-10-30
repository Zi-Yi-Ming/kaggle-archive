# -*- coding: utf-8 -*-
"""P6: price curve, marginal revenue, town-drain counterfactuals.

Uses engine market_price() directly. No agent modification.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

# import engine pricing
ENG = r"C:\Users\Lenovo\.conda\envs\kaggle\Lib\site-packages\kaggle_environments\envs\kaggriculture"
sys.path.insert(0, ENG)
import kaggriculture as kg  # noqa: E402

from kaggle_environments import make  # noqa: E402

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")


def shape(f, x, T):
    if f == "linear":
        return x
    if f == "sq":
        return x * x / T if T else x * x
    if f == "sqrt":
        return (x ** 0.5) * (T ** 0.5) if T else x ** 0.5
    if f == "log":
        return math_log1p(x) * (math_log1p(T) or 1)
    if f == "hinge":
        if not T or T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def math_log1p(x):
    import math
    return math.log1p(x)


def market_price(item, inventory, params=None):
    return kg.market_price(item, inventory, params)


def revenue_sell_q(item, inv0, q, params=None):
    """Sell q units one-by-one: quote at inv, then inv += 1 each unit."""
    inv = inv0
    prices = []
    total = 0
    for _ in range(q):
        p = market_price(item, inv, params)
        prices.append(p)
        total += p
        if p > 1:
            inv += 1
    return total, prices, inv


def marginal_series(item, inv0, qmax, params=None):
    """MR of the k-th unit (1-indexed) when selling sequentially from inv0."""
    inv = inv0
    out = []
    for k in range(1, qmax + 1):
        p = market_price(item, inv, params)
        out.append((k, inv, p))
        if p > 1:
            inv += 1
    return out


def main():
    import math
    curve_rows = []
    mr_rows = []

    print("=== Price vs inventory (selected) ===")
    for item in ("STRAWBERRY", "MILK", "WOOL", "MELON", "WHEAT"):
        print(f"\n[{item}] base={kg.MARKET_PARAMS[item]['base']} T={kg.MARKET_PARAMS[item]['T']}")
        for inv in (10000, 9900, 9800, 9500, 9000, 8500, 8000):
            p = market_price(item, inv)
            print(f"  inv={inv:5d} price={p}")
            curve_rows.append({"item": item, "inv": inv, "price": p})

    print("\n=== Sequential sell: first/mid/last unit price from I0 ===")
    for item in ("STRAWBERRY", "MILK", "WOOL", "MELON"):
        for q in (10, 50, 100, 200):
            rev, prices, end_inv = revenue_sell_q(item, 10000, q)
            mr = prices[-1] - prices[0] if prices else 0
            print(f"  {item:12s} q={q:3d} R={rev:8.0f} p_first={prices[0]:3d} p_last={prices[-1]:3d} "
                  f"avg={rev/q:.1f} end_inv={end_inv}")
            mr_rows.append({
                "item": item, "q": q, "inv0": 10000,
                "revenue": rev, "p_first": prices[0], "p_last": prices[-1],
                "avg_price": rev / q, "end_inv": end_inv,
            })
        # marginal of unit k
        ser = marginal_series(item, 10000, 100)
        print(f"  {item} MR samples: k=1 p={ser[0][2]} k=10 p={ser[9][2]} k=50 p={ser[49][2]} k=100 p={ser[99][2]}")

    # Town drain: shops consume from inventory. Typical drain per 4 steps:
    # each unlocked shop consumes 1 of each demanded product (2x if single-product)
    # + town center 1 each product except fert every 24 steps (scales after day 10/20)
    print("\n=== Drain vs sell order (analytical) ===")
    # Start inv=9800 (some player sells already), sell 100 units
    # Case A: sell 100 now at 9800
    # Case B: drain 50 first (inv=9750) then sell 100
    # Case C: sell 50, drain 50, sell 50
    for item in ("STRAWBERRY", "MILK"):
        revA, _, _ = revenue_sell_q(item, 9800, 100)
        revB, _, _ = revenue_sell_q(item, 9750, 100)  # after drain 50
        r1, _, inv1 = revenue_sell_q(item, 9800, 50)
        r2, _, _ = revenue_sell_q(item, inv1 - 50, 50)  # drain 50 restores some scarcity
        revC = r1 + r2
        print(f"  {item}: flood@9800 R={revA:.0f}  after_drain50 R={revB:.0f}  "
              f"split50+drain+50 R={revC:.0f}  B-A={revB-revA:+.0f} C-A={revC-revA:+.0f}")
        mr_rows.append({
            "item": item, "q": 100, "inv0": 9800,
            "revenue_flood": revA, "revenue_after_drain": revB, "revenue_split": revC,
            "delta_drain_minus_flood": revB - revA,
            "delta_split_minus_flood": revC - revA,
        })

    # In-engine: does town drain between two sells raise the second sell's price?
    # Agent buys wheat, sells half, waits for town drain step, sells rest.
    # shop_interval default 4; center 24.

    def wheat_agent(schedule):
        """schedule: list of market order lists by step."""
        def a(obs):
            step = int(obs.get("step") or 0)
            m = schedule[step] if step < len(schedule) else []
            return {"farmer": ["PASS"], "hands": [], "market": m}
        return a

    def run_sched(s0, s1, steps, seed=1):
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = steps
        env.configuration["seed"] = seed
        env.run([wheat_agent(s0), wheat_agent(s1)])
        f = env.steps[-1]
        return (
            float(f[0]["observation"]["farms"][0]["money"]),
            float(f[1]["observation"]["farms"][1]["money"]),
        )

    # Both buy 40 wheat over 4 steps, then:
    # F: sell 40 at step 8
    # S: sell 20 at step 8, sell 20 at step 12 (after more town drains)
    buy = [["BUY_PRODUCT", "WHEAT", 10]] * 4
    flood = buy + [[]] * 4 + [["SELL", "WHEAT", 40]] + [[]] * 20
    split = buy + [[]] * 4 + [["SELL", "WHEAT", 20]] + [[]] * 3 + [["SELL", "WHEAT", 20]] + [[]] * 16
    idle = [[]] * 30

    print("\n=== In-engine flood vs split (wheat, same total 40) ===")
    for seed in (1, 2, 3):
        b0, b1 = run_sched(flood, idle, 30, seed)
        b0s, b1s = run_sched(split, idle, 30, seed)
        print(f"  seed{seed}: flood={b0:.0f} split={b0s:.0f} split-flood={b0s-b0:+.0f}")
        mr_rows.append({
            "test": "in_engine_split_vs_flood", "seed": seed,
            "flood_money": b0, "split_money": b0s, "delta": b0s - b0,
        })

    # sell immediately after buy vs wait 4 steps (town drain window)
    early = [["BUY_PRODUCT", "WHEAT", 20]] * 2 + [["SELL", "WHEAT", 40]] + [[]] * 10
    late = [["BUY_PRODUCT", "WHEAT", 20]] * 2 + [[]] * 4 + [["SELL", "WHEAT", 40]] + [[]] * 6
    print("\n=== In-engine sell now vs wait 4 steps (drain) ===")
    for seed in (1, 2, 3):
        be, _ = run_sched(early, idle, 20, seed)
        bl, _ = run_sched(late, idle, 20, seed)
        print(f"  seed{seed}: early={be:.0f} late={bl:.0f} late-early={bl-be:+.0f}")
        mr_rows.append({
            "test": "in_engine_late_vs_early", "seed": seed,
            "early_money": be, "late_money": bl, "delta": bl - be,
        })

    with open(ROOT / "p6_price_curve.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "inv", "price"])
        w.writeheader()
        w.writerows(curve_rows)
    with open(ROOT / "p6_marginal_revenue.csv", "w", newline="", encoding="utf-8") as f:
        # flatten mixed keys
        keys = sorted({k for r in mr_rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(mr_rows)
    print("wrote p6_price_curve.csv p6_marginal_revenue.csv")


if __name__ == "__main__":
    main()
