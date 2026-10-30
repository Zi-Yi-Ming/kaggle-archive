# -*- coding: utf-8 -*-
"""Sticky shepherd routing — single pickup owner + sticky wheat cargo."""
from __future__ import annotations

from p12_primitives.animal_care import (
    animal_care_command, scan_animals, nearest_home, walk, manhattan,
)

PRODUCTS_DROP = (
    "MILK", "WOOL", "EGG", "FERTILIZER", "MELON", "CARROT", "STRAWBERRY", "TOMATO",
)


def sticky_animal_care(pos, inv, shed, tiles, hour, day, actor=0, pickup_owner=0):
    pos = tuple(pos)
    inv = dict(inv or {})
    wheat_inv = int(inv.get("WHEAT") or 0)
    hungry, uncared, ready, fert = scan_animals(tiles)

    if wheat_inv > 0:
        home = nearest_home(pos)
        dist_home = manhattan(pos, home)
        has_products = any(int(inv.get(k) or 0) > 0 for k in PRODUCTS_DROP)
        if has_products and hour >= max(19, 22 - dist_home):
            w = walk(pos, home)
            return w if w else ["DROP"]
        if hungry:
            target = min(hungry, key=lambda p: manhattan(pos, p))
            w = walk(pos, target)
            return w if w else ["FEED"]
        if uncared:
            target = min(uncared, key=lambda p: manhattan(pos, p))
            w = walk(pos, target)
            return w if w else ["CARE"]
        if ready:
            target = min(ready, key=lambda p: manhattan(pos, p))
            w = walk(pos, target)
            return w if w else ["HARVEST"]
        if has_products:
            w = walk(pos, home)
            return w if w else ["DROP"]
        return None

    if actor != pickup_owner:
        if wheat_inv <= 0:
            x, y = pos
            tile = None
            if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
                tile = tiles[y][x]
            if isinstance(tile, dict) and tile.get("animal"):
                if tile.get("fed_today") and not tile.get("cared_today"):
                    return ["CARE"]
                if int(tile.get("yield_units") or 0) > 0:
                    return ["HARVEST"]
                if tile.get("fertilizer_available"):
                    return ["COLLECT_FERTILIZER"]
            return None
        care = animal_care_command(pos, inv, shed, tiles, hour, day)
        if care is not None and care[0] != "PICKUP":
            return care
        return None

    return animal_care_command(pos, inv, shed, tiles, hour, day)
