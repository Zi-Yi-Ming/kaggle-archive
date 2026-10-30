# -*- coding: utf-8 -*-
"""Animal-care loop primitive.

Evidence (P12): P11 FEED ~15–30/day vs R2 ~15–17/game/day sustained;
P11 PICKUP 100–190/day vs FEED 14–37 (pickup-thrash); yield_units≈0 after d12
while R2 climbs 6–21. Shed almost never holds MILK/WOOL/EGG.

State-driven (no tape). One worker at a time. Planner can disable via flag.

Loop:
  hungry animal? → ensure wheat in inv (exact qty from shed) → walk → FEED
  then CARE if fed
  then HARVEST if yield_units>0
  else if cargo → walk home → DROP
"""
from __future__ import annotations

ANIMALS = ("COW", "SHEEP", "GOOSE")
MAX_ORDERS = 10


def beside_shed(pos, board=10):
    c = board // 2
    return (pos[0], pos[1]) in ((c - 1, c - 1), (c, c - 1), (c - 1, c), (c, c))


def nearest_home(pos):
    homes = ((4, 4), (5, 4), (4, 5), (5, 5))
    return min(homes, key=lambda p: (abs(pos[0] - p[0]) + abs(pos[1] - p[1]), p))


def walk(pos, target):
    x, y = pos
    tx, ty = target
    if x != tx:
        return ["EAST" if x < tx else "WEST"]
    if y != ty:
        return ["SOUTH" if y < ty else "NORTH"]
    return None


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def scan_animals(tiles):
    """Return lists of animal tile tasks."""
    hungry, uncared, ready, fert = [], [], [], []
    for y, row in enumerate(tiles or []):
        for x, t in enumerate(row):
            if not isinstance(t, dict) or not t.get("animal"):
                continue
            if not t.get("fed_today"):
                hungry.append((x, y))
            elif not t.get("cared_today"):
                uncared.append((x, y))
            elif int(t.get("yield_units") or 0) > 0:
                ready.append((x, y))
            elif t.get("fertilizer_available"):
                fert.append((x, y))
    return hungry, uncared, ready, fert


def animal_care_command(pos, inv, shed, tiles, hour, day):
    """Return next animal-care command for this worker, or None.

    Priority: EOD drop → feed → care → harvest → collect fert → pickup wheat.
    """
    pos = tuple(pos)
    inv = dict(inv or {})
    home = nearest_home(pos)
    dist_home = manhattan(pos, home)
    cargo_n = sum(int(v or 0) for v in inv.values())
    wheat_inv = int(inv.get("WHEAT") or 0)

    hungry, uncared, ready, fert = scan_animals(tiles)
    n_hungry = len(hungry)
    n_uncared = len(uncared)

    # EOD: dump cargo so dawn wipe cannot destroy milk/wool/eggs
    if cargo_n > 0 and hour >= max(19, 22 - dist_home):
        w = walk(pos, home)
        return w if w else ["DROP"]

    # Already on an animal tile?
    x, y = pos
    tile = None
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        tile = tiles[y][x]
    if isinstance(tile, dict) and tile.get("animal"):
        if not tile.get("fed_today") and wheat_inv > 0:
            return ["FEED"]
        if tile.get("fed_today") and not tile.get("cared_today"):
            return ["CARE"]
        if int(tile.get("yield_units") or 0) > 0:
            return ["HARVEST"]
        if tile.get("fertilizer_available"):
            return ["COLLECT_FERTILIZER"]

    # Need wheat for hungry animals — pickup exact shortfall once
    wheat_shed = int(shed.get("WHEAT") or 0)
    if n_hungry > 0 and wheat_inv == 0 and wheat_shed > 0:
        if beside_shed(pos):
            q = min(n_hungry, wheat_shed, 6)
            return ["PICKUP", "WHEAT", q]
        # walk home to pick up feed
        w = walk(pos, home)
        if w:
            return w
        return ["PICKUP", "WHEAT", min(n_hungry, wheat_shed, 6)]

    # If carrying wheat, go feed nearest hungry
    if wheat_inv > 0 and hungry:
        target = min(hungry, key=lambda p: manhattan(pos, p))
        w = walk(pos, target)
        return w if w else ["FEED"]

    # Feeded but uncared
    if uncared:
        target = min(uncared, key=lambda p: manhattan(pos, p))
        w = walk(pos, target)
        return w if w else ["CARE"]

    # Harvest ready animals
    if ready:
        target = min(ready, key=lambda p: manhattan(pos, p))
        w = walk(pos, target)
        return w if w else ["HARVEST"]

    # Collect fert from sheep
    if fert:
        target = min(fert, key=lambda p: manhattan(pos, p))
        w = walk(pos, target)
        return w if w else ["COLLECT_FERTILIZER"]

    return None


def wheat_topup_orders(shed, prices, money, n_hungry, hold=0):
    """BUY_PRODUCT WHEAT if animals hungry and shed/insufficient stock."""
    if n_hungry <= 0:
        return []
    have = int(shed.get("WHEAT") or 0)
    # also assume some already being carried; conservative
    need = n_hungry - have
    if need <= 0:
        return []
    px = int(prices.get("WHEAT") or 25)
    afford = int(max(0.0, money - 80) // max(1, px))
    q = min(need, afford, 5)
    if q <= 0:
        return []
    return [["BUY_PRODUCT", "WHEAT", q]]
