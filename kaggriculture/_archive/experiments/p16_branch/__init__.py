# -*- coding: utf-8 -*-
"""P16.1 branch triggers.

fixed:  day==10, melon present, money<1800
state:  once-per-game; day>=10; true_harvest_ready>=3 or shed_melon>=3;
        money < 1000  (thin cash while convertible inventory exists)
"""
from __future__ import annotations

SKELETON_ON = False
BRANCH_MODE = "off"  # off | fixed | state
_fired = False


def reset():
    global _fired
    _fired = False


def set_skeleton(flag: bool):
    global SKELETON_ON
    SKELETON_ON = bool(flag)


def set_branch_mode(mode: str):
    global BRANCH_MODE, _fired
    assert mode in ("off", "fixed", "state")
    BRANCH_MODE = mode
    _fired = False


def set_branch(flag: bool):
    set_branch_mode("fixed" if flag else "off")


def is_skeleton() -> bool:
    return SKELETON_ON


def is_branch() -> bool:
    return BRANCH_MODE != "off"


def branch_force_sell(
    day: int,
    money: float,
    field_melon: int,
    shed_melon: int,
    ready_melon: int = 0,
) -> bool:
    global _fired
    if BRANCH_MODE == "off":
        return False
    if BRANCH_MODE == "fixed":
        if day != 10:
            return False
        if field_melon <= 0 and shed_melon <= 0:
            return False
        return money < 1800
    # state-derived: once only, stricter
    if _fired:
        return False
    if day < 10:
        return False
    convertible = ready_melon + shed_melon
    if convertible < 3:
        return False
    if money >= 1000:
        return False
    _fired = True
    return True
