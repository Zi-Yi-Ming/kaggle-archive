# -*- coding: utf-8 -*-
"""Plant-fill primitive.

Evidence: d15 P11 empty≈21 plants≈12 vs R2 empty≈1 plants≈57.
Crop revenue never comes online; animals alone cannot close a $120k gap.

State-driven:
  seed_buy_orders(empty_n, seeds, prices, money, day) -> BUY_SEED mix
  plant is already first in worker tile walk; this only funds + prioritizes harvest sell.
"""
from __future__ import annotations

SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
# cheap→valuable backbone; wheat first for feed+early cash
MIX = ("WHEAT", "CARROT", "STRAWBERRY", "MELON", "TOMATO")


def seed_buy_orders(empty_n, seeds, prices, money, day, labor_reserve=120):
    """Buy seeds to fill empty tiles. Cap spend so hire/animals still work."""
    if empty_n <= 0 or day > 27:
        return []
    # early: mostly wheat/carrot; mid: add strawberry
    if day < 8:
        plan = [("WHEAT", 0.6), ("CARROT", 0.4)]
    elif day < 16:
        plan = [("WHEAT", 0.3), ("CARROT", 0.3), ("STRAWBERRY", 0.4)]
    else:
        plan = [("STRAWBERRY", 0.5), ("CARROT", 0.3), ("WHEAT", 0.2)]

    spendable = max(0.0, money - labor_reserve)
    # don't block expansion entirely
    budget = min(spendable * 0.35, 400 if day < 15 else 800)
    if budget < 15:
        return []

    orders = []
    # how many seeds we already hold
    for crop, frac in plan:
        have = int(seeds.get(crop) or 0)
        want = max(1, int(empty_n * frac))
        gap = want - have
        if gap <= 0:
            continue
        cost = SEED_COST[crop]
        afford = int(budget // cost)
        q = min(gap, afford, 8)
        if q <= 0:
            continue
        orders.append(["BUY_SEED", crop, q])
        budget -= q * cost
        if budget < 15 or len(orders) >= 4:
            break
    return orders
