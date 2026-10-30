# -*- coding: utf-8 -*-
"""Generic harvest-ready primitive (state-driven, not melon-specific).

Engine truth:
- non-ongoing crops start yield_units=1 but HARVEST no-ops until
  day - planted_day >= first_yield_day
- HARVEST puts units in worker inventory (_inv_add), removes non-ongoing plant
- plant dies to WEED if consecutive_unwatered >= 2
"""
from __future__ import annotations

# first_yield_day from engine CROPS
FIRST_YIELD = {
    "WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10,
}
ONGOING = {"TOMATO": True, "STRAWBERRY": True, "WHEAT": False, "CARROT": False, "MELON": False}


def is_harvest_ready(tile, day: int) -> bool:
    """True iff engine will accept HARVEST on this plant/animal tile."""
    if not isinstance(tile, dict):
        return False
    if tile.get("animal"):
        return int(tile.get("yield_units") or 0) > 0
    if tile.get("kind") != "PLANT":
        return False
    if int(tile.get("yield_units") or 0) <= 0:
        return False
    planted = tile.get("planted_day")
    if planted is None:
        return False
    need = FIRST_YIELD.get(tile.get("crop"), 2)
    return int(day) - int(planted) >= need


def needs_water(tile, day: int) -> bool:
    """Plant will die if unwatered again (consecutive_unwatered>=2 at dawn)."""
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
        return False
    if is_harvest_ready(tile, day):
        return False  # harvest first
    return not tile.get("watered_today")
