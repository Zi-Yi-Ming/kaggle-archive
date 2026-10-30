# -*- coding: utf-8 -*-
"""Early feed-wheat buffer primitive.

Evidence: R2 d10 shed WHEAT≈53 vs P11≈2. B3 shepherds close FEED→yield→DROP
but d10 cash still ~$90 because animals are not fed on time and wheat is not
stocked. Cows need wheat daily from placement; without a buffer shepherds
walk to shed, find nothing, and the yield clock never starts.

State-driven targets (not a tape):
  feed_reserve(day, n_animals) -> wheat units to hold in shed/inventory
  wheat_buy_orders(...)        -> BUY_PRODUCT to top up reserve
  plant_bias(...)              -> keep planting wheat until reserve met
"""
from __future__ import annotations


def feed_reserve(day: int, n_animals: int, money: float) -> int:
    """Wheat units to keep on hand for FEED (shed + inventory)."""
    if n_animals <= 0 and day < 2:
        return 4  # bootstrap before first animals arrive
    # one feed per animal per day + walk slack; scale with herd
    base = n_animals + 4
    if day <= 8:
        # early: animals are being placed — keep a fat buffer
        return max(base, 8)
    if day <= 18:
        return max(base, 10)
    return max(base, 6)


def wheat_buy_orders(shed, inventories, prices, money, day, n_animals, labor_reserve=80):
    """BUY_PRODUCT WHEAT to restore feed reserve. Ignores already-carried inv."""
    target = feed_reserve(day, n_animals, money)
    have = int(shed.get("WHEAT") or 0)
    # inventory wheat is in-transit for FEED; count half conservatively
    inv_w = sum(int((i or {}).get("WHEAT") or 0) for i in (inventories or []))
    stock = have + inv_w // 2
    need = target - stock
    if need <= 0:
        return []
    px = int(prices.get("WHEAT") or 25)
    if px <= 0:
        return []
    spendable = max(0.0, money - labor_reserve)
    # don't drain cash needed for dawn hire; allow modest overdraw early
    if day <= 5:
        spendable = max(spendable, money * 0.25)
    afford = int(spendable // px)
    q = min(need, afford, 8)
    if q <= 0:
        return []
    return [["BUY_PRODUCT", "WHEAT", q]]


def wheat_seed_bias(day: int, n_animals: int, wheat_seeds: int, wheat_plants: int) -> int:
    """Extra WHEAT seeds to buy so plants refill the feed reserve."""
    target_plants = min(16, max(6, n_animals + 4)) if day <= 12 else min(10, n_animals)
    planted_gap = max(0, target_plants - wheat_plants)
    seed_gap = max(0, planted_gap - wheat_seeds)
    if day > 20:
        seed_gap = min(seed_gap, 2)
    return min(seed_gap, 6)
