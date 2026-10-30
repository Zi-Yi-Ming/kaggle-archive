# -*- coding: utf-8 -*-
"""P17.1 Type-E continuation library (architecture only, no external tapes).

Backbone = MAIN (our open-loop multi-horizon skeleton via p14_1+p13_3).
Tails    = pre-defined future target overlays (not full 720-step tapes).
Checkpoints: sparse, observable, once each.

Prefix-compatible: a tail only changes FUTURE strategic targets; no rewind.
"""
from __future__ import annotations

ENABLED = False

# selected tail after checkpoint; None = MAIN backbone
ACTIVE_TAIL = None
_FIRED = set()

TAILS = ("MAIN", "CASH_WINDOW", "HERD_SCALE")

# sparse checkpoints: (name, day_lo, day_hi)
CHECKPOINTS = (
    ("CP_CASH_WINDOW", 9, 12),
    ("CP_HERD_SCALE", 11, 16),
)


def set_enabled(flag: bool):
    global ENABLED, ACTIVE_TAIL, _FIRED
    ENABLED = bool(flag)
    ACTIVE_TAIL = None
    _FIRED = set()


def is_enabled() -> bool:
    return ENABLED


def active_tail() -> str:
    return ACTIVE_TAIL or "MAIN"


def observe_checkpoint(
    day: int,
    money: float,
    ready_melon: int,
    shed_melon: int,
    n_animals: int,
) -> str | None:
    """Return tail name if a checkpoint fires; else None. Once per checkpoint."""
    if not ENABLED:
        return None
    # CP1: convertible long-crop inventory but thin cash → CASH_WINDOW tail
    if "CP_CASH_WINDOW" not in _FIRED and 9 <= day <= 12:
        convertible = ready_melon + shed_melon
        if convertible >= 2 and money < 1200:
            _FIRED.add("CP_CASH_WINDOW")
            return "CASH_WINDOW"
    # CP2: no livestock yet but cash allows → HERD_SCALE tail
    if "CP_HERD_SCALE" not in _FIRED and 11 <= day <= 16:
        if n_animals < 2 and money >= 900:
            _FIRED.add("CP_HERD_SCALE")
            return "HERD_SCALE"
    return None


def commit_tail(tail: str):
    global ACTIVE_TAIL
    if tail in TAILS:
        ACTIVE_TAIL = tail


def apply_tail_to_targets(t):
    """Overlay strategic targets for the active tail. Mutates ResourceTargets."""
    tail = active_tail()
    if tail == "CASH_WINDOW":
        t.sell_all = True
        t.sell_hold_wheat = 0
        t.priority = "LIQUIDATE"
        # stop expanding long horizon; allow short cash only
        t.buy_seed = {k: v for k, v in (t.buy_seed or {}).items() if k == "WHEAT"}
        t.buy_animals = {}
        t.buy_land = False
        t.notes.append("tail=CASH_WINDOW")
    elif tail == "HERD_SCALE":
        # prioritize animals; keep wheat for feed; drop extra long seeds
        t.buy_seed = {k: v for k, v in (t.buy_seed or {}).items() if k == "WHEAT"}
        t.notes.append("tail=HERD_SCALE")
        # leave existing buy_animals; planner already set them
    return t
