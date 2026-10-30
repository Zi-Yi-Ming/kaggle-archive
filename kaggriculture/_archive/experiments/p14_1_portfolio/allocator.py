# -*- coding: utf-8 -*-
"""Multi-horizon crop portfolio — state-driven, no R2 tape, no MELON=12 hardcode.

Horizons by first_yield_day (engine):
  short  <= 3 days
  medium 4-9 days
  long   >= 10 days

EV per tile (proxy):
  units * quote - seed - water_cost * fy_days - tile_lock * fy_days

Portfolio: allocate limited tiles/cash/water-labor across horizons
so short cash + long spike can coexist (R2 structure, not R2 numbers).
"""
from __future__ import annotations

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
# expected harvested units if watered through first yield (engine max_yield ballpark)
EXPECTED_UNITS = {"WHEAT": 5, "CARROT": 3, "TOMATO": 3, "STRAWBERRY": 3, "MELON": 5}
WATER_COST_PER_DAY = 2.0   # opportunity $ proxy per watering action-day
TILE_LOCK_PER_DAY = 1.5    # proxy for occupying a tile
ENDING_DAY = 29


def horizon_of(crop: str) -> str:
    fy = FIRST_YIELD[crop]
    if fy <= 3:
        return "short"
    if fy <= 9:
        return "medium"
    return "long"


def crop_ev(crop: str, quote: float, day: int, cash: float) -> float:
    """State-dependent expected value per tile through first yield."""
    fy = FIRST_YIELD[crop]
    if day + fy > ENDING_DAY:
        return -1e9  # cannot cash out
    px = quote if quote and quote > 0 else 1.0
    units = EXPECTED_UNITS[crop]
    gross = units * px
    cost = SEED_COST[crop] + WATER_COST_PER_DAY * fy + TILE_LOCK_PER_DAY * fy
    # cash urgency: prefer sooner cash when poor
    urgency = 1.0 + max(0.0, (400.0 - cash) / 400.0) * 0.35
    horizon_bonus = {"short": urgency, "medium": 1.0, "long": 1.15}[horizon_of(crop)]
    return (gross - cost) * horizon_bonus


def water_capacity(n_workers_farmers: int) -> int:
    """Rough tiles a farmer crew can keep watered daily."""
    return max(4, min(20, n_workers_farmers * 3))


def allocate_portfolio(
    empty_tiles: int,
    cash: float,
    day: int,
    prices: dict,
    n_farmers: int = 5,
    feed_tiles: int = 6,
    reserve_cash: float = 200.0,
) -> dict:
    """Return {crop: n_tiles} target. Greedy multi-horizon fill with floors."""
    if empty_tiles <= 0 or day > 20:
        return {}

    ev = {}
    for c in CROPS:
        q = float(prices.get(c) or 0)
        ev[c] = crop_ev(c, q, day, cash)

    # horizon floors so we never collapse to single-window wheat-only
    # short floor: feed/early cash
    short_c = max((c for c in CROPS if horizon_of(c) == "short"), key=lambda c: ev[c], default="WHEAT")
    long_c = max((c for c in CROPS if horizon_of(c) == "long"), key=lambda c: ev[c], default="MELON")
    med_c = max((c for c in CROPS if horizon_of(c) == "medium"), key=lambda c: ev[c], default="STRAWBERRY")

    alloc = {}
    left = empty_tiles
    budget = max(0.0, cash - reserve_cash)
    wcap = water_capacity(n_farmers)

    def try_add(crop, n):
        nonlocal left, budget
        n = min(n, left)
        if n <= 0:
            return
        cost = SEED_COST[crop] * n
        # water burden of this batch
        if cost > budget:
            n = int(budget // SEED_COST[crop])
            cost = SEED_COST[crop] * n
        if n <= 0:
            return
        alloc[crop] = alloc.get(crop, 0) + n
        left -= n
        budget -= cost

    # 1) short floor — always some wheat-like
    try_add(short_c, min(6, max(3, empty_tiles // 5)))

    # 2) long window if we can still cash out and have water slack
    if day + FIRST_YIELD[long_c] <= ENDING_DAY - 1 and ev[long_c] > 0:
        # scale with cash: more free cash → more long tiles
        cash_frac = min(1.0, max(0.0, (cash - 400) / 2500))
        want_long = int(round(4 + 10 * cash_frac))  # 4..14, economic not tape
        want_long = min(want_long, left, wcap - alloc.get(short_c, 0))
        try_add(long_c, want_long)

    # 3) medium if day allows full medium window
    if day + FIRST_YIELD[med_c] <= ENDING_DAY - 2 and ev[med_c] > 0 and left > 0:
        try_add(med_c, min(4, left))

    # 4) fill rest with best remaining EV
    while left > 0 and budget >= SEED_COST["WHEAT"]:
        ranked = sorted(CROPS, key=lambda c: -ev[c])
        placed = False
        for c in ranked:
            if day + FIRST_YIELD[c] > ENDING_DAY:
                continue
            if SEED_COST[c] > budget:
                continue
            try_add(c, 1)
            placed = True
            break
        if not placed:
            break

    return alloc


def seed_buy_from_alloc(alloc: dict, seeds: dict, cash: float) -> dict:
    """BUY_SEED to reach portfolio targets."""
    buys = {}
    budget = max(0.0, cash - 150.0)
    for crop, target in alloc.items():
        have = int(seeds.get(crop) or 0)
        need = max(0, int(target) - have)
        if need <= 0:
            continue
        can = min(need, int(budget // SEED_COST[crop]))
        if can > 0:
            buys[crop] = can
            budget -= can * SEED_COST[crop]
    return buys
