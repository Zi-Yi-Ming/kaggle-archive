# -*- coding: utf-8 -*-
"""Animal economics + joint crop/livestock portfolio.

Engine facts (not R2 targets):
  GOOSE cost300 fy4 int1 max_held4 product EGG
  COW   cost400 fy8 int2 max_held6 product MILK
  SHEEP cost500 fy6 int3 max_held6 product WOOL
  Sheep also fertilizer_available (secondary).
  Animals need FEED (wheat) daily + CARE; structures take tiles.
"""
from __future__ import annotations

ANIMALS = ("GOOSE", "COW", "SHEEP")
A_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
A_FY = {"GOOSE": 4, "COW": 8, "SHEEP": 6}
A_INT = {"GOOSE": 1, "COW": 2, "SHEEP": 3}
A_MAX = {"GOOSE": 4, "COW": 6, "SHEEP": 6}
A_PROD = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
A_STRUCT = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
# secondary: sheep fertilizer trickle
FERT_FROM_SHEEP = 0.35  # units/day proxy after care

PRICE0 = {"EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40}
# seasonal peaks from P13 R2 ledger (blended, not a day schedule)
PEAK = {"EGG": 80, "MILK": 180, "WOOL": 220, "FERTILIZER": 100}
FEED_WHEAT_PER_ANIMAL_DAY = 0.85
WHEAT_INTERNAL = 6.0  # self-grown, not market quote
ENDING_DAY = 29
STRUCT_TILE_COST = 1.0


def _blended_px(product: str, prices: dict) -> float:
    cur = float(prices.get(product) or PRICE0.get(product) or 1)
    peak = float(PEAK.get(product) or cur)
    return 0.35 * cur + 0.65 * peak


def animal_value(animal: str, day: int, cash: float, prices: dict | None = None) -> dict:
    """Marginal EV for one animal from day to end of season."""
    prices = prices or {}
    if day + A_FY[animal] > ENDING_DAY:
        return {"animal": animal, "ev": -1e9, "days_prod": 0, "n_yields": 0,
                "gross": 0, "feed_cost": 0, "acq": A_COST[animal], "fert": 0}
    days_left = ENDING_DAY - day
    days_prod = max(0, days_left - A_FY[animal])
    n_yields = 0 if days_prod <= 0 else 1 + (days_prod // A_INT[animal])
    n_yields = min(n_yields, A_MAX[animal])
    px = _blended_px(A_PROD[animal], prices)
    gross = n_yields * px
    fert = 0.0
    if animal == "SHEEP":
        fert = FERT_FROM_SHEEP * days_prod * _blended_px("FERTILIZER", prices)
    feed = FEED_WHEAT_PER_ANIMAL_DAY * days_left * WHEAT_INTERNAL
    acq = A_COST[animal]
    ev = gross + fert - acq - feed
    return {
        "animal": animal, "ev": ev, "days_prod": days_prod, "n_yields": n_yields,
        "gross": gross, "feed_cost": feed, "acq": acq, "fert": fert,
        "time_to_cash": A_FY[animal],
    }


def choose_animals(
    cash: float,
    day: int,
    prices: dict,
    live: dict,
    n_empty: int,
    existing_struct_empty: int = 0,
    reserve: float = 250.0,
    wheat_tiles_planned: int = 5,
) -> dict:
    """State-driven animal targets. Caps by cash, empty tiles, feed capacity.

    Does NOT hardcode 8/6/3. Caps come from marginal EV + resource limits.
    """
    if day > 18:
        return {}
    vals = {a: animal_value(a, day, cash, prices) for a in ANIMALS}
    # rank by EV
    ranked = sorted(ANIMALS, key=lambda a: -vals[a]["ev"])
    budget = max(0.0, cash - reserve)
    # feed capacity: wheat tiles * yield / (animals * feed rate) rough
    # assume each wheat tile yields ~5 wheat per 2-day cycle → 2.5/day; need 0.85/head/day
    feed_heads = max(0, int((wheat_tiles_planned * 2.2) / FEED_WHEAT_PER_ANIMAL_DAY))
    # also can buy wheat product — soft cap
    feed_heads = max(feed_heads, 3)

    targets = {}
    placed = existing_struct_empty
    for a in ranked:
        v = vals[a]
        if v["ev"] <= 0:
            continue
        have = int(live.get(a) or 0)
        # structure slots: empty pastures/coops count once globally
        max_by_tile = max(0, n_empty)  # need build tile if no empty struct
        max_by_cash = int(budget // A_COST[a]) if A_COST[a] else 0
        # sheep share pastures with cows — soft combined cap
        already_other_pasture = sum(targets.get(x, 0) + int(live.get(x) or 0)
                                    for x in ANIMALS if A_STRUCT[x] == "PASTURE" and x != a)
        if A_STRUCT[a] == "PASTURE":
            # leave room: total pasture animals not absurd vs empty
            max_by_pasture = max(0, n_empty - already_other_pasture)
        else:
            max_by_pasture = max(0, n_empty - already_other_pasture)
        max_by_feed = max(0, feed_heads - sum(targets.values()) - sum(int(live.get(x) or 0) for x in ANIMALS))
        want = max(0, min(max_by_cash, max_by_tile, max_by_pasture, max_by_feed, 6))
        # soft prefer positive EV animals; don't force equal split
        if v["ev"] < 50:
            want = min(want, 2)
        if want > 0:
            targets[a] = want
            budget -= A_COST[a] * want
    return targets


def feed_wheat_need(live_or_target: dict) -> float:
    n = sum(int(v or 0) for v in live_or_target.values())
    return n * FEED_WHEAT_PER_ANIMAL_DAY
