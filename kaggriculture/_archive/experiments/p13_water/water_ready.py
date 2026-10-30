# -*- coding: utf-8 -*-
"""Generic WATER_READY_CROP — keep plants alive until first yield.

Engine: consecutive_unwatered >= 2 at dawn → WEED.
Not melon-specific. State-driven only.
"""
from __future__ import annotations

FIRST_YIELD = {
    "WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10,
}


def plant_at_risk(tile, day: int) -> bool:
    """True if this plant needs WATER now to survive to harvest."""
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
        return False
    if tile.get("watered_today"):
        return False
    # if already harvest-ready, prefer harvest not water
    planted = tile.get("planted_day")
    crop = tile.get("crop")
    if planted is not None and crop in FIRST_YIELD:
        if int(day) - int(planted) >= FIRST_YIELD[crop] and int(tile.get("yield_units") or 0) > 0:
            return False
    return True


def nearest_water_target(pos, tiles, day):
    """Nearest (x,y) of a plant that needs watering, or None."""
    best = None
    best_d = 10**9
    for y, row in enumerate(tiles or []):
        for x, t in enumerate(row):
            if plant_at_risk(t, day):
                d = abs(pos[0] - x) + abs(pos[1] - y)
                if d < best_d:
                    best_d = d
                    best = (x, y)
    return best


def water_ready_command(pos, tiles, day, max_walk=8):
    """Return WATER / walk / None for this worker."""
    pos = tuple(pos)
    x, y = pos
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        cur = tiles[y][x]
        if plant_at_risk(cur, day):
            return ["WATER"]
    target = nearest_water_target(pos, tiles, day)
    if target is None:
        return None
    d = abs(pos[0] - target[0]) + abs(pos[1] - target[1])
    if d > max_walk:
        return None
    tx, ty = target
    if x != tx:
        return ["EAST" if x < tx else "WEST"]
    if y != ty:
        return ["SOUTH" if y < ty else "NORTH"]
    return ["WATER"]
