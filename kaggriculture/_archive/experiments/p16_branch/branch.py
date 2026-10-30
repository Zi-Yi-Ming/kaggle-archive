# -*- coding: utf-8 -*-
"""P16 one branch point — evidence-based, observable only.

P13: long crop dies if unwatered; waiting for d10 without plants is waste.
P14: B wheat-only has no cash window; melon window needs surviving plants.

Branch (single):
  Evaluate once per day in d4-d8.
  If long-crop commitment FAILED (melon field < min_live AND cash still low),
  switch continuation family to SHORT_HEAL (wheat+animals, stop long lock).
  Else stay on skeleton FIRST_CASH path.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BranchState:
    evaluated: bool = False
    triggered: bool = False
    branch_name: str = "NONE"  # NONE | SHORT_HEAL
    trigger_day: int | None = None
    trigger_reason: str = ""
    melon_at_trigger: int | None = None
    cash_at_trigger: float | None = None


# thresholds from evidence, not from R2 tape numbers
MIN_LIVE_LONG = 4
CASH_POOR = 350.0
BRANCH_DAYS = (4, 5, 6, 7, 8)


def long_crop_count(tiles) -> int:
    n = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") in ("MELON", "STRAWBERRY", "TOMATO"):
                # only count true long/medium window crops
                if t.get("crop") == "MELON" or t.get("crop") == "STRAWBERRY":
                    n += 1
    return n


def maybe_branch(state: BranchState, day: int, cash: float, tiles, enabled: bool) -> BranchState:
    if not enabled:
        return state
    if state.evaluated and day != state.trigger_day:
        # once triggered, stay on branch family (no thrash)
        return state
    if day not in BRANCH_DAYS:
        return state
    # evaluate once per day; lock after first true trigger
    if state.triggered:
        return state
    melon = long_crop_count(tiles)
    if melon < MIN_LIVE_LONG and cash < CASH_POOR:
        state.evaluated = True
        state.triggered = True
        state.branch_name = "SHORT_HEAL"
        state.trigger_day = day
        state.trigger_reason = f"long_crop<{MIN_LIVE_LONG} and cash<{CASH_POOR}"
        state.melon_at_trigger = melon
        state.cash_at_trigger = cash
    elif day == BRANCH_DAYS[-1]:
        # end of branch window without trigger — remain skeleton
        state.evaluated = True
        state.branch_name = "NONE"
    return state


def branch_modifies_portfolio(branch_name: str) -> bool:
    return branch_name == "SHORT_HEAL"


def short_heal_alloc(empty_tiles: int, cash: float, day: int, prices: dict) -> dict:
    """Continuation family B: stop long lock; wheat + cheap short crops + animals later."""
    # wheat-heavy, no melon lock
    w = min(empty_tiles, 8)
    alloc = {}
    if w > 0:
        alloc["WHEAT"] = w
    if empty_tiles > w and cash > 200:
        alloc["CARROT"] = min(3, empty_tiles - w)
    return alloc
