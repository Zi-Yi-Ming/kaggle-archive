# -*- coding: utf-8 -*-
"""Live resource-target inference. Continuous, cash-adaptive. No tape."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from .economics import (
    ELITE_ANIMALS, ELITE_LAND, ANIMAL_COST, ANIMALS,
    cash_reserve, crop_priority, animal_counts, hungry_animals,
    land_cost, structure_gaps, empty_tiles, count_kind, SEED_COST,
)


@dataclass
class ResourceTargets:
    hire_n: int = 0
    buy_land: bool = False
    buy_animals: dict = field(default_factory=dict)
    buy_seed: dict = field(default_factory=dict)
    buy_product: dict = field(default_factory=dict)
    sell_all: bool = False
    sell_hold_wheat: int = 0
    cash_reserve: float = 0
    priority: str = "PRODUCE"
    notes: list = field(default_factory=list)


def _bootstrap_animals(day, money, live, n_land):
    """Day-paced elite ladder (structure of R2, not its tape)."""
    # d0-1: 2 cow + 2 sheep bootstrap (R2-like)
    # d2-5: fill cows if cash
    # after land2 (d~6+): finish 8C/6S
    # d10+: goose 3
    want = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
    if day <= 1:
        want["COW"] = 2
        want["SHEEP"] = 2
    elif day <= 5:
        want["COW"] = 4
        want["SHEEP"] = 2
    elif day <= 9:
        want["COW"] = 6
        want["SHEEP"] = 4
    elif day <= 13:
        want["COW"] = 8
        want["SHEEP"] = 6
        if money > 4000:
            want["GOOSE"] = 2
    else:
        want = dict(ELITE_ANIMALS)
    return want


def infer_targets(obs, day: int, hour: int, step: int) -> ResourceTargets:
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    seeds = dict(private.get("seeds") or {})
    inventories = list(private.get("inventories") or [])
    prices = dict((obs.get("market") or {}).get("prices") or {})
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    money = float(farm.get("money") or 0)
    tiles = farm.get("tiles") or []
    unlocked = list(farm.get("unlocked_quadrants") or ["NW"])
    hands = farm.get("hands") or []

    t = ResourceTargets()
    t.cash_reserve = cash_reserve(day, money)

    if step >= 710:
        t.priority = "LIQUIDATE"
        t.sell_all = True
        return t

    if money < 80 and day >= 2:
        t.priority = "RECOVER"
        t.sell_all = True
        t.notes.append("cash_crisis")
        return t

    free_cash = money - t.cash_reserve

    # Daily hire: workers wiped at dawn. Early modest, later max.
    if day == 0:
        want_hire = 5
    elif day <= 3:
        want_hire = 6
    elif day <= 7:
        want_hire = 8
    else:
        want_hire = 9
    # never spend below a hard floor
    hard_floor = 80 if day < 5 else 150
    if money < hard_floor + 20:
        want_hire = 0
    elif free_cash < 30:
        want_hire = min(want_hire, 2)
    t.hire_n = want_hire

    live = animal_counts(tiles)
    n_land = len(unlocked)
    lc = land_cost(n_land)
    empty = empty_tiles(tiles)
    n_empty = len(empty)
    hungry = hungry_animals(tiles)

    # Land: elite timing d6 / d11, cash-gated (delay if poor — novel)
    if n_land < ELITE_LAND and lc is not None:
        allow_from = 5 if n_land == 1 else 10
        if day >= allow_from and free_cash >= lc + 200:
            t.buy_land = True
            t.priority = "EXPAND"
            free_cash -= lc
            t.notes.append(f"land@{day}")

    joint_on = False
    try:
        import p14_2_on
        joint_on = p14_2_on.is_enabled()
    except Exception:
        joint_on = False

    # P15 interaction probe: optional forced early sheep (not a planner)
    try:
        import p15_force_sheep
        n_fs = p15_force_sheep.forced_sheep(
            day, live.get("SHEEP", 0), int(shed.get("SHEEP") or 0), money)
        if n_fs > 0:
            t.buy_animals["SHEEP"] = t.buy_animals.get("SHEEP", 0) + n_fs
            free_cash -= 500 * n_fs
            t.notes.append(f"force_sheep={n_fs}")
    except Exception:
        pass

    if joint_on:
        # P14.2 joint crop+livestock (replaces bootstrap ladder + crop hook)
        try:
            from p14_2_joint_portfolio.joint import joint_allocate
            n_farmers = max(1, len(hands) - 2)
            j = joint_allocate(n_empty, money, day, prices, live,
                               n_farmers=n_farmers, n_land=n_land)
            t.notes.append(f"joint c={j['crops']} a={j['animals']}")
            # animals
            for a, want_n in (j.get("animals") or {}).items():
                have = live.get(a, 0) + int(shed.get(a) or 0) + sum(
                    int((i or {}).get(a) or 0) for i in inventories)
                gap = max(0, int(want_n) - have)
                cost = ANIMAL_COST.get(a, 400)
                can = min(gap, 3, int(max(0, free_cash - 80) // cost))
                if can > 0:
                    t.buy_animals[a] = can
                    free_cash -= cost * can
                    t.priority = "EXPAND"
            # seeds from crop alloc
            buys_made = {}
            for c, n in (j.get("crops") or {}).items():
                have = int(seeds.get(c) or 0)
                need = max(0, int(n) - have)
                cost = SEED_COST.get(c, 20)
                can = min(need, int(max(0.0, free_cash - 40) // cost), 8)
                if can > 0:
                    t.buy_seed[c] = t.buy_seed.get(c, 0) + can
                    free_cash -= cost * can
        except Exception:
            pass
    else:
        # Animals by paced want + live (include shed/inventory as "owned")
        need_buy, need_build, need_place = structure_gaps(tiles, shed, inventories)
        want = _bootstrap_animals(day, money, live, n_land)
        for a in ("COW", "SHEEP", "GOOSE"):
            have = live[a] + int(shed.get(a) or 0) + sum(int((i or {}).get(a) or 0) for i in inventories)
            gap = max(0, want[a] - have)
            if gap <= 0:
                continue
            cost = ANIMAL_COST[a]
            # batch of 1-2, leave cash for hires/seeds
            max_batch = 2 if day <= 2 else 3
            can = min(gap, max_batch, int(max(0, free_cash - 60) // cost))
            if can > 0:
                t.buy_animals[a] = can
                free_cash -= cost * can
                t.priority = "EXPAND"

    # P14.1 portfolio crop allocation (replaces single-window wheat bias when ON)
    portfolio_on = False
    try:
        import p14_1_on
        portfolio_on = p14_1_on.is_enabled()
    except Exception:
        portfolio_on = False

    if joint_on:
        pass  # crops already handled
    elif portfolio_on:
        try:
            from p14_1_portfolio.allocator import allocate_portfolio, seed_buy_from_alloc
            n_farmers = max(1, len(hands) - 2)  # shepherds ~2
            alloc = allocate_portfolio(n_empty, money, day, prices, n_farmers=n_farmers,
                                       reserve_cash=120)
            t.notes.append(f"port={alloc}")
            buys = seed_buy_from_alloc(alloc, seeds, free_cash)
            for c, q in buys.items():
                t.buy_seed[c] = t.buy_seed.get(c, 0) + q
                free_cash -= SEED_COST.get(c, 20) * q
            # keep a small wheat top-up for feed even if portfolio is low on wheat
            have_w = int(seeds.get("WHEAT") or 0)
            if have_w < 2 and free_cash >= 15:
                t.buy_seed["WHEAT"] = t.buy_seed.get("WHEAT", 0) + 2
                free_cash -= 20
        except Exception:
            pass
    else:
        # Seeds (B3 baseline)
        wheat_need = 4 if day < 4 else max(3, hungry + 2)
        have_w = int(seeds.get("WHEAT") or 0)
        if have_w < wheat_need and free_cash >= 15:
            q = min(wheat_need - have_w, 6)
            t.buy_seed["WHEAT"] = q
            free_cash -= 10 * q

        # P13.1 early MELON (single variable; 0 when disabled)
        try:
            from p13_1_melon import early_melon_seed_qty
            mq = early_melon_seed_qty(day, free_cash, seeds)
            if mq > 0:
                t.buy_seed["MELON"] = t.buy_seed.get("MELON", 0) + mq
                free_cash -= 80 * mq
        except Exception:
            pass

        prefs = crop_priority(day, shops)
        # B3 cash-crop seeds (B5 plant_fill seed flood REJECTED — bank 30k→17k)
        if day >= 7 and n_empty >= 4 and free_cash >= 40:
            for c in prefs:
                if c == "WHEAT":
                    continue
                cost = SEED_COST[c]
                have = int(seeds.get(c) or 0)
                want_n = min(n_empty, 10)
                if have < want_n and free_cash >= cost * 2:
                    q = min(want_n - have, 6, int(free_cash // cost))
                    if q > 0:
                        t.buy_seed[c] = q
                        free_cash -= cost * q
                    break

    # Feed wheat product only when already hungry (B3)
    wheat_stock = int(shed.get("WHEAT") or 0) + sum(int((i or {}).get("WHEAT") or 0) for i in inventories)
    if hungry > wheat_stock and free_cash >= 25:
        q = min(hungry - wheat_stock, 5)
        t.buy_product["WHEAT"] = q
        free_cash -= 20 * q

    fert_px = int(prices.get("FERTILIZER") or 0)
    if 14 <= day <= 28 and 1 <= fert_px <= 30 and free_cash > 500:
        t.buy_product["FERTILIZER"] = 2

    # Sells — B6: monetize sooner (stock>=2 not 6); fert is product not feed
    stock = sum(int(v or 0) for v in shed.values())
    t.sell_hold_wheat = max(2, hungry + 1)
    if stock >= 2 or day >= 26:
        t.sell_all = True
        if t.priority not in ("EXPAND",):
            t.priority = "MONETIZE"
    if stock >= 40:
        t.sell_all = True
        t.priority = "MONETIZE"

    # P18 trajectory-library selector (S0/S1/S2) → tail overlay
    try:
        import p18_selector as sel
        if sel.is_enabled() if hasattr(sel, "is_enabled") else sel.ENABLED:
            # only active when harness set selector; S0 still MAIN
            field_melon = 0
            ready_melon = 0
            for _row in tiles:
                for _tile in _row:
                    if isinstance(_tile, dict) and _tile.get("kind") == "PLANT" and _tile.get("crop") == "MELON":
                        field_melon += 1
                        planted = _tile.get("planted_day")
                        if planted is not None and day - int(planted) >= 10:
                            ready_melon += 1
            shed_melon = int(shed.get("MELON") or 0)
            n_animals = live["COW"] + live["SHEEP"] + live["GOOSE"]
            state = {
                "money": money, "melon": field_melon, "shed_melon": shed_melon,
                "animals": n_animals, "plant": count_kind(tiles, lambda x: x.get("kind") == "PLANT"),
                "shed_total": sum(int(v or 0) for v in shed.values()),
                "n_shops": len(shops), "wheat": count_kind(tiles, lambda x: x.get("crop") == "WHEAT"),
            }
            mode = sel.decide(day, state)
            t.notes.append(f"p18={sel.SELECTOR}:{mode}")
            if mode == "CASH_WINDOW":
                t.sell_all = True
                t.sell_hold_wheat = 0
                t.priority = "LIQUIDATE"
                t.buy_seed = {k: v for k, v in (t.buy_seed or {}).items() if k == "WHEAT"}
                t.buy_animals = {}
                t.buy_land = False
            elif mode == "HERD_SCALE":
                t.buy_seed = {k: v for k, v in (t.buy_seed or {}).items() if k == "WHEAT"}
    except Exception:
        pass
    return t
