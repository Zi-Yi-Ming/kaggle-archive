# -*- coding: utf-8 -*-
"""Joint crop + livestock allocation (state-driven)."""
from __future__ import annotations

from .livestock import choose_animals, animal_value, ANIMALS, A_COST, feed_wheat_need
from p14_1_portfolio.allocator import (
    allocate_portfolio, crop_ev, horizon_of, CROPS, SEED_COST, FIRST_YIELD,
)


def joint_allocate(
    empty_tiles: int,
    cash: float,
    day: int,
    prices: dict,
    live_animals: dict,
    n_farmers: int = 5,
    n_land: int = 1,
) -> dict:
    """Animals-first cash reserve, then crops; wheat floor couples feed."""
    prices = prices or {}

    feed_est = max(4, int(feed_wheat_need(live_animals) + 2))
    provisional = choose_animals(
        cash, day, prices, live_animals,
        n_empty=max(6, empty_tiles // 2),
        wheat_tiles_planned=feed_est,
        reserve=200,
    )
    animal_spend = sum(A_COST.get(a, 400) * n for a, n in provisional.items())
    # early: don't dump all cash into livestock — leave room for long crops
    max_animal_frac = 0.45 if day <= 3 else 0.65
    cap = max(0.0, cash * max_animal_frac)
    if animal_spend > cap and provisional:
        # scale down highest-cost first
        while animal_spend > cap and sum(provisional.values()) > 0:
            a = max(provisional, key=lambda x: A_COST.get(x, 400))
            provisional[a] -= 1
            animal_spend -= A_COST.get(a, 400)
            if provisional[a] <= 0:
                del provisional[a]
    cash_for_crops = max(0.0, cash - animal_spend - 150)

    feed_need = feed_wheat_need(live_animals) + feed_wheat_need(provisional)
    wheat_floor = max(4, int(feed_need + 2))
    crop_alloc = allocate_portfolio(
        empty_tiles, cash_for_crops, day, prices, n_farmers=n_farmers,
        feed_tiles=wheat_floor, reserve_cash=80,
    )
    w = crop_alloc.get("WHEAT", 0)
    if w < wheat_floor:
        crop_alloc["WHEAT"] = w + max(0, min(wheat_floor - w,
                                             empty_tiles - sum(crop_alloc.values()) + w))

    crop_tiles = sum(crop_alloc.values())
    empty_left = max(0, empty_tiles - crop_tiles)
    animals = dict(provisional)
    while sum(animals.values()) > empty_left + 2 and animals:
        weakest = min(animals, key=lambda a: animal_value(a, day, cash, prices)["ev"])
        animals[weakest] -= 1
        if animals[weakest] <= 0:
            del animals[weakest]

    return {
        "crops": crop_alloc,
        "animals": animals,
        "wheat_tiles": crop_alloc.get("WHEAT", 0),
        "animal_ev": {a: animal_value(a, day, cash, prices) for a in ANIMALS},
    }
