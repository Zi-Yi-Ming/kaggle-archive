# -*- coding: utf-8 -*-
"""P40: complete coupled open-loop programs.

Each program is ONE atomic generator that decides market AND workers.
NOT market-grammar + p11. NOT elite tape splice.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")

ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
ANIMAL_STRUCT = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
HOME = ((4, 4), (5, 4), (4, 5), (5, 5))
FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}


def _fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def program_hash(prog: dict) -> str:
    return hashlib.md5(json.dumps(prog, sort_keys=True).encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Discrete coupled-program parameters (affect market AND workers together)
# ---------------------------------------------------------------------------

# Opening pack — seeds + animals bought on d0h0
OPENING = {
    "melon12w7_c2s2": {"seeds": (("MELON", 12), ("WHEAT", 7)), "animals": (("COW", 2), ("SHEEP", 2))},
    "melon10w8_c2s2": {"seeds": (("MELON", 10), ("WHEAT", 8)), "animals": (("COW", 2), ("SHEEP", 2))},
    "melon8w10_c1s3": {"seeds": (("MELON", 8), ("WHEAT", 10)), "animals": (("COW", 1), ("SHEEP", 3))},
    "mixed6w8_c3s2": {"seeds": (("MELON", 6), ("STRAWBERRY", 2), ("WHEAT", 8)), "animals": (("COW", 3), ("SHEEP", 2))},
}

# Mid production: replant priority after long-crop window
MID = {
    "straw_wheat": ("STRAWBERRY", "WHEAT", "CARROT", "TOMATO"),
    "tomato_straw": ("TOMATO", "STRAWBERRY", "WHEAT", "CARROT"),
    "wheat_carrot": ("WHEAT", "CARROT", "STRAWBERRY", "TOMATO"),
}

ANIMAL_MIX = {
    "cw16": {"COW": 8, "SHEEP": 8},
    "cow12": {"COW": 12, "SHEEP": 4},
    "sheep12": {"COW": 4, "SHEEP": 12},
}

LAND = {
    "e6_11_18": (6, 11, 18),
    "e6_11": (6, 11),
    "m10_16": (10, 16),
}

SELL = {
    "dusk": {"hours": (18, 20, 21), "hold_wheat": 6},
    "freq": {"hours": (6, 12, 18, 21), "hold_wheat": 4},
    "dawn_dusk": {"hours": (6, 18), "hold_wheat": 6},
}

HIRE = {
    "ramp": "ramp",      # 5,5,6,6,7,7,8,8,9,9,10...
    "max": "max",        # 10 every day
}

LONG_CUT = {"d10": 10, "d12": 12}

# Worker routing style (coupled with market — not a free layer)
ROUTE = {
    "cluster": "plant_nearest_weeds_then_plant",
    "swarm": "all_plant_until_full_then_care",
}


def compile_program(prog: dict):
    """Self-contained coupled agent. No p11. No elite tape."""
    opening = OPENING[prog["opening"]]
    mid_order = MID[prog["mid"]]
    mix = ANIMAL_MIX[prog["animal_mix"]]
    land_days = LAND[prog["land"]]
    sell = SELL[prog["sell"]]
    hire_mode = HIRE[prog["hire"]]
    long_cut = LONG_CUT[prog.get("long_cut", "d10")]
    route = ROUTE[prog.get("route", "cluster")]

    state = {"day": -1, "tasks": {}}

    def beside_shed(pos):
        return (pos[0], pos[1]) in HOME

    def nearest_home(pos):
        return min(HOME, key=lambda p: (abs(pos[0] - p[0]) + abs(pos[1] - p[1]), p))

    def walk(pos, target):
        x, y = pos
        tx, ty = target
        tx = max(0, min(9, int(tx)))
        ty = max(0, min(9, int(ty)))
        if x != tx:
            return ["EAST" if x < tx else "WEST"]
        if y != ty:
            return ["SOUTH" if y < ty else "NORTH"]
        return None

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def crop_ready(tile, day):
        if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
            return False
        crop = tile.get("crop")
        planted = tile.get("planted_day")
        planted = -99 if planted is None else int(planted)
        need = FIRST_YIELD.get(crop, 2)
        if planted >= 0 and day - planted >= need:
            return True
        yu = tile.get("yield_units")
        if yu is not None:
            try:
                return int(yu) > 0 and (planted < 0 or day - planted >= need)
            except Exception:
                return False
        return False

    def hire_target(day):
        if hire_mode == "max":
            return 10
        # ramp
        if day <= 1:
            return 5
        if day <= 4:
            return 6
        if day <= 7:
            return 8
        if day <= 10:
            return 9
        return 10

    def market_orders(shed, seeds, money, prices, day, hour, hires_today, live, n_land, empty):
        market = []
        cash = float(money)

        def add(o):
            if len(market) >= 10:
                return False
            market.append(o)
            return True

        # 1) d0 opening
        if day == 0 and hour == 0:
            for crop, q in opening["seeds"]:
                cost = SEED_COST[crop] * q
                if cash >= cost + 15 and add(["BUY_SEED", crop, q]):
                    cash -= cost
            for a, q in opening["animals"]:
                cost = ANIMAL_COST[a] * q
                if cash >= cost + 15 and add(["BUY_ANIMAL", a, q]):
                    cash -= cost

        # 2) land
        if hour == 0 and day in land_days and n_land < 4 and cash >= 1400:
            if add(["BUY_LAND"]):
                cash -= 1000

        # 3) animals
        if hour == 0 and day >= 1:
            for a, target in mix.items():
                have = live[a] + int(shed.get(a) or 0)
                gap = target - have
                can = min(max(0, gap), 2, int(max(0.0, cash - 80) // ANIMAL_COST[a]))
                for _ in range(can):
                    if not add(["BUY_ANIMAL", a, 1]):
                        break
                    cash -= ANIMAL_COST[a]

        # 4) seed top-up for empty tiles
        if hour in (0, 6, 12) and empty > 1 and cash >= 50:
            bought = 0
            for crop in mid_order:
                if day < long_cut and crop in ("WHEAT", "CARROT"):
                    # early: keep planting cash crop if any left; wheat for feed
                    pass
                cost = SEED_COST[crop]
                if cash < cost + 25:
                    continue
                qmax = 2 if cost >= 50 else 4
                q = min(empty - bought, qmax, int((cash - 25) // cost))
                if q <= 0:
                    continue
                if add(["BUY_SEED", crop, q]):
                    cash -= cost * q
                    bought += q
                if bought >= empty - 1 or len(market) >= 8:
                    break
            # long crop early
            if day < long_cut and empty > bought and cash >= 80 + 40:
                q = min(empty - bought, 3, int((cash - 40) // 80))
                if q > 0 and add(["BUY_SEED", "MELON", q]):
                    cash -= 80 * q

        # 5) hire (leave room for sells)
        if hour == 0:
            room = max(0, 9 - len(market))
            target = hire_target(day)
            n = 0
            while n < target and n < room:
                cost = _fib(hires_today + n)
                if cash < cost + 4 or not add(["HIRE"]):
                    break
                cash -= cost
                n += 1

        # 6) sell
        if hour in sell["hours"] or day >= 29:
            hold = 0 if day >= 29 else sell["hold_wheat"]
            items = []
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q <= 0:
                    continue
                if item == "WHEAT":
                    q = max(0, q - hold)
                    if q <= 0:
                        continue
                px = int(prices.get(item) or 1)
                items.append((px * q, item, q))
            items.sort(reverse=True)
            for _, item, q in items:
                if not add(["SELL", item, q]):
                    break

        if day >= 29:
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q > 0:
                    add(["SELL", item, q])

        return market

    def tile_at(tiles, x, y):
        try:
            return tiles[y][x]
        except Exception:
            return "OOB"

    def tile_kind(tiles, x, y):
        t = tile_at(tiles, x, y)
        if t is None:
            return "EMPTY"
        if isinstance(t, dict):
            k = t.get("kind")
            if k == "PLANT":
                return "PLANT"
            if k == "WEED":
                return "WEED"
            if t.get("animal"):
                return "ANIMAL"
            return k or "DICT"
        return "OTHER"

    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        day = step // 24
        hour = step % 24
        player = int(obs.get("player") or 0)
        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        private = obs.get("private") or {}
        shed = dict(private.get("shed") or {})
        seeds = dict(private.get("seeds") or {})
        inventories = list(private.get("inventories") or [])
        prices = dict((obs.get("market") or {}).get("prices") or {})
        money = float(farm.get("money") or 0)
        tiles = farm.get("tiles") or []
        positions = [tuple(farm.get("farmer") or (4, 4))]
        for h in farm.get("hands") or []:
            positions.append(tuple(h))
        hires_today = int(farm.get("hires_today") or 0)
        n_land = len(farm.get("unlocked_quadrants") or [])

        live = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
        empty = 0
        for row in tiles:
            for t in row:
                if t is None:
                    empty += 1
                elif isinstance(t, dict) and t.get("animal") in live:
                    live[t["animal"]] += 1

        market = market_orders(
            shed, seeds, money, prices, day, hour, hires_today, live, n_land, empty,
        )

        # --- coupled worker program ---
        if day != state["day"]:
            state["day"] = day
            state["tasks"] = {}

        # plant order
        if day < long_cut:
            plant_order = ("MELON",) + tuple(c for c in mid_order if c != "MELON")
        else:
            plant_order = tuple(mid_order)

        seed_budget = {c: int(seeds.get(c) or 0) for c in CROPS}
        claimed = set()
        for task in state["tasks"].values():
            if task and task[0] == "PLANT":
                claimed.add(tuple(task[1]))

        weeds = []
        empties = []
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "WEED":
                    weeds.append((x, y))
                elif t is None and (x, y) not in claimed:
                    empties.append((x, y))
        weeds.sort(key=lambda p: (manhattan(p, (4, 4)), p))
        empties.sort(key=lambda p: (manhattan(p, (4, 4)), p))

        plant_queue = []
        for x, y in empties:
            chosen = None
            for crop in plant_order:
                if crop == "MELON" and day >= long_cut:
                    continue
                if seed_budget.get(crop, 0) > 0:
                    chosen = crop
                    seed_budget[crop] -= 1
                    break
            if chosen is None:
                break
            plant_queue.append(((x, y), chosen))
        dig_queue = weeds[:]

        # animal need snapshot
        need_animal = False
        n_waiting = sum(int(shed.get(a) or 0) for a in ANIMAL_COST)
        n_empty_struct = 0
        for row in tiles:
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get("kind") in ("COOP", "PASTURE") and not t.get("animal"):
                    n_empty_struct += 1
                if t.get("animal") and (
                    not t.get("fed_today")
                    or (t.get("fed_today") and not t.get("cared_today"))
                    or int(t.get("yield_units") or 0) > 0
                    or t.get("fertilizer_available")
                ):
                    need_animal = True

        def keep_or_assign(actor, pos):
            task = state["tasks"].get(actor)
            if task:
                op = task[0]
                tx, ty = task[1]
                k = tile_kind(tiles, tx, ty)
                if op == "PLANT" and k == "EMPTY" and int(seeds.get(task[2]) or 0) > 0:
                    if (tx, ty) == pos:
                        return ["PLANT", task[2]]
                    w = walk(pos, (tx, ty))
                    return w if w else ["PLANT", task[2]]
                if op == "DIG" and k == "WEED":
                    if (tx, ty) == pos:
                        return ["DIG"]
                    w = walk(pos, (tx, ty))
                    return w if w else ["DIG"]
                if op == "HARVEST" and crop_ready(tile_at(tiles, tx, ty), day):
                    if (tx, ty) == pos:
                        return ["HARVEST"]
                    w = walk(pos, (tx, ty))
                    return w if w else ["HARVEST"]
                if op == "WATER" and isinstance(tile_at(tiles, tx, ty), dict):
                    t = tile_at(tiles, tx, ty)
                    if t.get("kind") == "PLANT" and not t.get("watered_today") and hour < 20:
                        if (tx, ty) == pos:
                            return ["WATER"]
                        w = walk(pos, (tx, ty))
                        return w if w else ["WATER"]
                state["tasks"].pop(actor, None)

            # new assignment — priority: harvest > dig > water > plant > build > place > care
            # harvest
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and crop_ready(t, day):
                        state["tasks"][actor] = ("HARVEST", (x, y))
                        if (x, y) == pos:
                            return ["HARVEST"]
                        w = walk(pos, (x, y))
                        return w if w else ["HARVEST"]

            # dig (spare workers / swarm early)
            if dig_queue and (route == "swarm" or actor >= 1 or not plant_queue):
                tx, ty = dig_queue.pop(0)
                state["tasks"][actor] = ("DIG", (tx, ty))
                if (tx, ty) == pos:
                    return ["DIG"]
                w = walk(pos, (tx, ty))
                return w if w else ["DIG"]

            # water
            if hour < 20:
                for y, row in enumerate(tiles):
                    for x, t in enumerate(row):
                        if isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today"):
                            state["tasks"][actor] = ("WATER", (x, y))
                            if (x, y) == pos:
                                return ["WATER"]
                            w = walk(pos, (x, y))
                            return w if w else ["WATER"]

            # plant
            if plant_queue:
                if route == "swarm" or actor >= 2 or not need_animal or len(positions) <= 3:
                    (tx, ty), crop = plant_queue.pop(0)
                    state["tasks"][actor] = ("PLANT", (tx, ty), crop)
                    if (tx, ty) == pos:
                        return ["PLANT", crop]
                    w = walk(pos, (tx, ty))
                    return w if w else ["PLANT", crop]

            # build structures for waiting animals (only if no plantable seeds)
            has_seed = any(int(v or 0) > 0 for v in seeds.values())
            if n_waiting > n_empty_struct and not has_seed:
                for y, row in enumerate(tiles):
                    for x, t in enumerate(row):
                        if t is None:
                            op = "BUILD_COOP" if int(shed.get("GOOSE") or 0) > 0 else "BUILD_PASTURE"
                            if (x, y) == pos:
                                return [op]
                            w = walk(pos, (x, y))
                            return w if w else [op]

            # place animal from inventory
            inv = dict(inventories[actor] or {}) if actor < len(inventories) else {}
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal"):
                        for a, st in ANIMAL_STRUCT.items():
                            if st == t.get("kind") and int(inv.get(a) or 0) > 0:
                                if (x, y) == pos:
                                    return ["PLACE", a]
                                w = walk(pos, (x, y))
                                return w if w else ["PLACE", a]

            # animal micro for shepherds
            if actor <= 2 or need_animal:
                for y, row in enumerate(tiles):
                    for x, t in enumerate(row):
                        if not isinstance(t, dict) or not t.get("animal"):
                            continue
                        if not t.get("fed_today") and int(inv.get("WHEAT") or 0) > 0:
                            if (x, y) == pos:
                                return ["FEED"]
                            w = walk(pos, (x, y))
                            return w if w else ["FEED"]
                        if t.get("fed_today") and not t.get("cared_today"):
                            if (x, y) == pos:
                                return ["CARE"]
                            w = walk(pos, (x, y))
                            return w if w else ["CARE"]
                        if int(t.get("yield_units") or 0) > 0:
                            if (x, y) == pos:
                                return ["HARVEST"]
                            w = walk(pos, (x, y))
                            return w if w else ["HARVEST"]
                        if t.get("fertilizer_available"):
                            if (x, y) == pos:
                                return ["COLLECT_FERTILIZER"]
                            w = walk(pos, (x, y))
                            return w if w else ["COLLECT_FERTILIZER"]

            # pickup wheat / animals at shed
            if beside_shed(pos):
                hungry = sum(
                    1 for row in tiles for t in row
                    if isinstance(t, dict) and t.get("animal") and not t.get("fed_today")
                )
                if hungry and not inv.get("WHEAT") and int(shed.get("WHEAT") or 0) > 0:
                    return ["PICKUP", "WHEAT", min(hungry, int(shed["WHEAT"]), 8)]
                for a in ANIMAL_COST:
                    if int(shed.get(a) or 0) > 0:
                        return ["PICKUP", a, 1]

            # end-of-day cargo return
            has_cargo = any(int(v or 0) > 0 for v in inv.values())
            if has_cargo and hour >= 19:
                w = walk(pos, nearest_home(pos))
                return w if w else ["DROP"]

            # idle home
            if not beside_shed(pos) and hour < 22:
                w = walk(pos, nearest_home(pos))
                if w:
                    return w
            return ["PASS"]

        farmer = keep_or_assign(0, positions[0])
        hands = []
        for i in range(1, len(positions)):
            hands.append(keep_or_assign(i, positions[i]))

        # sanitize
        from p10_executor.validators import sanitize_action
        return sanitize_action(
            {"farmer": farmer, "hands": hands, "market": market},
            shed=shed, money=money, prices=prices,
        )

    return agent


def enumerate_programs(limit=500):
    """Coupled program grid. Cap at limit."""
    progs = []
    for opening in OPENING:
        for mid in MID:
            for mix in ANIMAL_MIX:
                for land in LAND:
                    for sell in SELL:
                        for hire in HIRE:
                            for long_cut in LONG_CUT:
                                for route in ROUTE:
                                    progs.append({
                                        "opening": opening,
                                        "mid": mid,
                                        "animal_mix": mix,
                                        "land": land,
                                        "sell": sell,
                                        "hire": hire,
                                        "long_cut": long_cut,
                                        "route": route,
                                    })
    # unique by hash, cap
    seen = set()
    uniq = []
    for p in progs:
        h = program_hash(p)
        if h in seen:
            continue
        seen.add(h)
        uniq.append(p)
        if len(uniq) >= limit:
            break
    return uniq
