# -*- coding: utf-8 -*-
"""P13.1 single-variable early MELON intervention.

Toggle ENABLED:
  False = B0 (control, current B stack)
  True  = B1 = B0 + d0-d2 MELON seed buy + plant-first

No other policy changes.
"""
from __future__ import annotations

ENABLED = False
WANT_MELON_SEEDS = 6
MELON_COST = 80


def set_enabled(flag: bool):
    global ENABLED
    ENABLED = bool(flag)


def early_melon_seed_qty(day: int, free_cash: float, seeds) -> int:
    """Melon seeds to buy on d0-d2 only."""
    if not ENABLED or day > 2:
        return 0
    have = int((seeds or {}).get("MELON") or 0)
    if have >= WANT_MELON_SEEDS:
        return 0
    if free_cash < MELON_COST * 2:
        return 0
    return min(WANT_MELON_SEEDS - have, int(free_cash // MELON_COST), 4)


def prefer_melon_plant(day: int, seeds) -> bool:
    """Plant MELON first while seeds remain (d0-d10 window for first-yield)."""
    if not ENABLED:
        return False
    return int((seeds or {}).get("MELON") or 0) > 0
