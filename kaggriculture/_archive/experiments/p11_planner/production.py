# -*- coding: utf-8 -*-
"""Production program: market orders + worker micro-policy. No 720-tape."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from p12_primitives.animal_care import animal_care_command  # noqa: E402

from .economics import (
    ANIMALS, ANIMAL_STRUCTURE, PRODUCTS, MAX_ORDERS,
    ANIMAL_COST, SEED_COST, CROPS,
)

HOME = ((4, 4), (5, 4), (4, 5), (5, 5))
CROP_FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}


def beside_shed(pos, board=10):
    c = board // 2
    return (pos[0], pos[1]) in ((c - 1, c - 1), (c, c - 1), (c - 1, c), (c, c))


def walk(pos, target):
    x, y = pos
    tx, ty = target
    if x != tx:
        return ["EAST" if x < tx else "WEST"]
    if y != ty:
        return ["SOUTH" if y < ty else "NORTH"]
    return None


def nearest_home(pos):
    return min(HOME, key=lambda p: (abs(pos[0] - p[0]) + abs(pos[1] - p[1]), p))


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def build_market(targets, shed, seeds, money, prices, day, hour, step, hires_today, hands_n):
    market = []
    cash = float(money)

    def add(order):
        if len(market) >= MAX_ORDERS:
            return False
        market.append(order)
        return True

    # Hire once at dawn only (workers wiped overnight)
    if targets.hire_n > 0 and hour == 0:
        already = 0
        for _ in range(targets.hire_n):
            cost = _fib(hires_today + already)
            if cash < cost + 5:
                break
            if not add(["HIRE"]):
                break
            cash -= cost
            already += 1

    if targets.buy_land and cash >= 1000:
        if add(["BUY_LAND"]):
            cash -= 1000

    for a, q in (targets.buy_animals or {}).items():
        q = int(q)
        cost = ANIMAL_COST.get(a, 999)
        can = min(q, int(max(0, cash - 40) // cost))
        for _ in range(max(0, can)):
            if not add(["BUY_ANIMAL", a, 1]):
                break
            cash -= cost

    for item, q in (targets.buy_product or {}).items():
        q = int(q)
        px = int(prices.get(item) or (25 if item == "WHEAT" else 40))
        can = min(q, int(max(0, cash) // max(1, px)))
        if can > 0 and add(["BUY_PRODUCT", item, can]):
            cash -= px * can

    for crop, q in (targets.buy_seed or {}).items():
        q = int(q)
        cost = SEED_COST.get(crop, 20)
        can = min(q, int(max(0, cash) // cost))
        if can > 0 and add(["BUY_SEED", crop, can]):
            cash -= cost * can

    if targets.sell_all or targets.priority in ("MONETIZE", "LIQUIDATE", "RECOVER"):
        hold_wheat = 0 if targets.priority == "LIQUIDATE" else targets.sell_hold_wheat
        items = []
        for item in PRODUCTS:
            q = int((shed or {}).get(item) or 0)
            if q <= 0:
                continue
            if item == "WHEAT":
                q = max(0, q - hold_wheat)
                if q <= 0:
                    continue
            px = int(prices.get(item) or 1)
            items.append((px * q, item, q))
        items.sort(reverse=True)
        for _, item, q in items:
            if not add(["SELL", item, q]):
                break
    elif hour >= 18:
        # B6: monetize any product in shed (fert was skipped; R2 sells huge fert)
        hold_wheat = targets.sell_hold_wheat
        for item in PRODUCTS:
            q = int((shed or {}).get(item) or 0)
            if q <= 0:
                continue
            if item == "WHEAT":
                q = max(0, q - hold_wheat)
                if q <= 0:
                    continue
            elif item == "FERTILIZER":
                pass  # sell all fert — pure product
            elif q < 1:
                continue
            if not add(["SELL", item, q]):
                break
    return market[:MAX_ORDERS]


def _crop_ready(tile, day):
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
        return False
    crop = tile.get("crop")
    planted = int(tile.get("planted_day") if tile.get("planted_day") is not None else -99)
    need = CROP_FIRST_YIELD.get(crop, 2)
    if planted >= 0 and day - planted >= need:
        return True
    yu = tile.get("yield_units")
    if yu is not None:
        try:
            return int(yu) > 0 and (planted < 0 or day - planted >= need)
        except Exception:
            return False
    return False


def worker_command(obs, actor, tiles, positions, inventories, shed, seeds, day, step, actor_index_hint=0):
    pos = tuple(positions[actor]) if actor < len(positions) else (4, 4)
    inv = dict(inventories[actor] or {}) if actor < len(inventories) else {}

    hour = step % 24
    home = nearest_home(pos)
    dist_home = manhattan(pos, home)

    # P12.1 B1: sticky shepherd (single pickup owner + sticky wheat)
    if actor <= 2:
        try:
            from p12_1_routing.sticky_shepherd import sticky_animal_care
            care = sticky_animal_care(pos, inv, shed, tiles, hour, day,
                                      actor=actor, pickup_owner=0)
        except Exception:
            care = animal_care_command(pos, inv, shed, tiles, hour, day)
        if care is not None:
            return care

    # P13.3 WATER_READY_CROP — farmers keep plants alive (not melon-specific)
    if actor >= 3 and hour < 20:
        try:
            import p13_3_water
            if p13_3_water.is_enabled():
                from p13_water.water_ready import water_ready_command
                wc = water_ready_command(pos, tiles, day, max_walk=6)
                if wc is not None:
                    return wc
        except Exception:
            pass

    # End-of-day cargo return — DROP dumps ALL stacks (engine); inventory wipes at dawn
    has_cargo = any(int(v or 0) > 0 for v in inv.values())
    if has_cargo and hour >= max(19, 22 - dist_home):
        w = walk(pos, home)
        if w:
            return w
        return ["DROP"]

    # Shed pickups — owner only (kill multi-worker stampede)
    if actor == 0 and beside_shed(pos):
        hungry = 0
        for row in tiles:
            for t in row:
                if isinstance(t, dict) and t.get("animal") and not t.get("fed_today"):
                    hungry += 1
        if hungry and not inv.get("WHEAT") and int(shed.get("WHEAT") or 0) > 0:
            return ["PICKUP", "WHEAT", min(hungry, int(shed["WHEAT"]), 6)]
        for a in ANIMALS:
            if int(shed.get(a) or 0) <= 0:
                continue
            struct = ANIMAL_STRUCTURE[a]
            for row in tiles:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == struct and not t.get("animal"):
                        return ["PICKUP", a, 1]

    # Count inventory/structures for build decisions
    n_empty_struct = 0
    n_need_struct = 0
    for a in ANIMALS:
        in_shed = int(shed.get(a) or 0)
        in_inv = int(inv.get(a) or 0)
        struct = ANIMAL_STRUCTURE[a]
        empty_s = 0
        for row in tiles:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == struct and not t.get("animal"):
                    empty_s += 1
        if in_shed + in_inv > empty_s:
            n_need_struct += (in_shed + in_inv) - empty_s
        n_empty_struct += empty_s

    # Task list with worker diversification via actor hint
    tasks = []

    def add_task(pri, target, cmd):
        tasks.append((pri, manhattan(pos, target), target, cmd))

    has_seed = any(int(v or 0) > 0 for v in (seeds or {}).values())

    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t == "LOCKED":
                continue
            if t is None:
                animals_waiting = any(int(shed.get(a) or 0) > 0 for a in ANIMALS)
                if animals_waiting or n_need_struct > 0:
                    if int(shed.get("GOOSE") or 0) > 0:
                        add_task(55, (x, y), ["BUILD_COOP"])
                    else:
                        add_task(55, (x, y), ["BUILD_PASTURE"])
                if has_seed:
                    crop_order = ("WHEAT", "CARROT", "STRAWBERRY", "MELON", "TOMATO")
                    try:
                        from p13_1_melon import prefer_melon_plant
                        if prefer_melon_plant(day, seeds or {}):
                            crop_order = ("MELON",) + crop_order
                    except Exception:
                        pass
                    try:
                        import p14_1_on
                        if p14_1_on.is_enabled():
                            # portfolio: plant high-EV long/medium seeds before wheat flood
                            crop_order = ("MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT")
                    except Exception:
                        pass
                    for crop in crop_order:
                        if int((seeds or {}).get(crop) or 0) > 0:
                            add_task(48 if animals_waiting else 45, (x, y), ["PLANT", crop])
                            break
                continue
            if not isinstance(t, dict):
                continue
            kind = t.get("kind")
            if kind == "WEED":
                add_task(25, (x, y), ["DIG"])
            elif kind == "PLANT":
                if _crop_ready(t, day):
                    add_task(92, (x, y), ["HARVEST"])
                elif day < 29 and not t.get("watered_today"):
                    add_task(70, (x, y), ["WATER"])
                elif int(inv.get("FERTILIZER") or 0) > 0 and t.get("fertilized_until_day", -1) < day + 2:
                    add_task(60, (x, y), ["FERTILIZE"])
            elif kind in ("COOP", "PASTURE"):
                animal = t.get("animal")
                if not animal:
                    for a in ANIMALS:
                        if ANIMAL_STRUCTURE[a] == kind and int(inv.get(a) or 0) > 0:
                            add_task(88, (x, y), ["PLACE", a])
                            break
                else:
                    if not t.get("fed_today") and int(inv.get("WHEAT") or 0) > 0:
                        add_task(95, (x, y), ["FEED"])
                    elif t.get("fed_today") and not t.get("cared_today"):
                        add_task(82, (x, y), ["CARE"])
                    elif int(t.get("yield_units") or 0) > 0:
                        add_task(86, (x, y), ["HARVEST"])
                    elif t.get("fertilizer_available"):
                        add_task(78, (x, y), ["COLLECT_FERTILIZER"])

    # Prefer work on current tile if valid
    cx, cy = pos
    animals_waiting = any(int(shed.get(a) or 0) > 0 for a in ANIMALS)
    if 0 <= cy < len(tiles) and 0 <= cx < len(tiles[cy]):
        cur = tiles[cy][cx]
        if cur is None and (animals_waiting or n_need_struct > 0):
            return ["BUILD_COOP"] if int(shed.get("GOOSE") or 0) > 0 else ["BUILD_PASTURE"]
        if cur is None and has_seed:
            crop_order = ("WHEAT", "CARROT", "STRAWBERRY", "MELON", "TOMATO")
            try:
                from p13_1_melon import prefer_melon_plant
                if prefer_melon_plant(day, seeds or {}):
                    crop_order = ("MELON",) + crop_order
            except Exception:
                pass
            try:
                import p14_1_on
                if p14_1_on.is_enabled():
                    crop_order = ("MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT")
            except Exception:
                pass
            for crop in crop_order:
                if int((seeds or {}).get(crop) or 0) > 0:
                    return ["PLANT", crop]
        elif isinstance(cur, dict):
            kind = cur.get("kind")
            if kind == "WEED":
                return ["DIG"]
            if kind == "PLANT":
                if _crop_ready(cur, day):
                    return ["HARVEST"]
                if day < 29 and not cur.get("watered_today"):
                    return ["WATER"]
            if kind in ("COOP", "PASTURE"):
                animal = cur.get("animal")
                if not animal:
                    for a in ANIMALS:
                        if ANIMAL_STRUCTURE[a] == kind and int(inv.get(a) or 0) > 0:
                            return ["PLACE", a]
                else:
                    if not cur.get("fed_today") and int(inv.get("WHEAT") or 0) > 0:
                        return ["FEED"]
                    if cur.get("fed_today") and not cur.get("cared_today"):
                        return ["CARE"]
                    if int(cur.get("yield_units") or 0) > 0:
                        return ["HARVEST"]
                    if cur.get("fertilizer_available"):
                        return ["COLLECT_FERTILIZER"]

    if tasks:
        # diversify by actor so workers spread across tiles
        tasks.sort(key=lambda z: (-z[0], z[1], (z[2][0] * 17 + z[2][1] * 31 + actor * 13) % 7))
        # take the best among a shortlist, offset by actor
        shortlist = tasks[: min(8, len(tasks))]
        _, _, target, cmd = shortlist[actor % len(shortlist)]
        w = walk(pos, target)
        if w:
            return w
        return cmd

    if any(int(v or 0) > 0 for v in inv.values()):
        w = walk(pos, home)
        if w:
            return w
        return ["DROP"]
    return ["PASS"]
