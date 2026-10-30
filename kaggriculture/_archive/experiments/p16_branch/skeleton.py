# -*- coding: utf-8 -*-
"""P16 compressed economic skeleton from R2 milestones (NOT a 720-tape).

Phases are structural, not step-indexed schedules.
Intents only; actions come from existing B executor stack.
"""
from __future__ import annotations

from dataclasses import dataclass

# Compressed from P13/P14 R2 milestones (day windows are soft, state-gated):
#   d0-2  EARLY_SETUP      short+long crops, first animals, structures
#   d3-7  HOLD_AND_WATER   keep long crop alive, scale feed/animals, land
#   d8-11 FIRST_CASH       harvest long crop, sell, livestock scale
#   d12-20 LIVESTOCK_SCALE animal products + mid crops
#   d21-28 COMPOUND        keep product sell high
#   d29    TERMINAL        liquidate


PHASES = (
    "EARLY_SETUP",
    "HOLD_AND_WATER",
    "FIRST_CASH",
    "LIVESTOCK_SCALE",
    "COMPOUND",
    "TERMINAL",
)


@dataclass
class SkeletonIntent:
    phase: str
    allow_long_crops: bool
    allow_animals: bool
    water_priority: bool
    sell_aggressive: bool
    liquidate: bool
    notes: str = ""


def phase_for_day(day: int) -> str:
    if day <= 2:
        return "EARLY_SETUP"
    if day <= 7:
        return "HOLD_AND_WATER"
    if day <= 11:
        return "FIRST_CASH"
    if day <= 20:
        return "LIVESTOCK_SCALE"
    if day <= 28:
        return "COMPOUND"
    return "TERMINAL"


def skeleton_intent(day: int, cash: float, step: int) -> SkeletonIntent:
    """Open-loop backbone intent by phase. State only for gates, not per-step tape."""
    if step >= 710:
        return SkeletonIntent("TERMINAL", True, False, False, True, True, "end")
    ph = phase_for_day(day)
    if ph == "EARLY_SETUP":
        return SkeletonIntent(ph, True, True, True, False, False, "multi-horizon+animals")
    if ph == "HOLD_AND_WATER":
        return SkeletonIntent(ph, True, True, True, False, False, "survive long crop")
    if ph == "FIRST_CASH":
        return SkeletonIntent(ph, True, True, True, True, False, "harvest+sell long")
    if ph == "LIVESTOCK_SCALE":
        return SkeletonIntent(ph, True, True, True, True, False, "animal products")
    if ph == "COMPOUND":
        return SkeletonIntent(ph, False, True, True, True, False, "product sell")
    return SkeletonIntent(ph, False, False, False, True, True, "dump")


def open_loop_fraction(day: int) -> float:
    """Research metric: how much of the season we stay on skeleton by design."""
    # branch only allowed near d4-d8 window in this prototype
    if 4 <= day <= 8:
        return 0.0  # branch window
    return 1.0
