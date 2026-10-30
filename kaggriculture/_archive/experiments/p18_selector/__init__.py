# -*- coding: utf-8 -*-
"""P18 selectors over R2 trajectory library.

S0 fixed: always MAIN
S1 rule:  p17.1-style observable checkpoints
S2 knn:   retrieve mode from library by state similarity (day-windowed)

Modes map to p17_1 tails: MAIN / CASH_WINDOW / HERD_SCALE
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
LIB_PATH = ROOT / "p18_trajectory_library.csv"

SELECTOR = "S0"  # S0 | S1 | S2
ENABLED = False
_LIBRARY = []
_FIRED_TAIL = None


def set_enabled(flag: bool):
    global ENABLED
    ENABLED = bool(flag)


def is_enabled() -> bool:
    return ENABLED


def load_library():
    global _LIBRARY
    if _LIBRARY:
        return _LIBRARY
    if not LIB_PATH.exists():
        return []
    _LIBRARY = list(csv.DictReader(LIB_PATH.open(encoding="utf-8")))
    for r in _LIBRARY:
        for k in ("day", "money", "melon", "animals", "plant", "shed_total", "n_shops", "wheat"):
            try:
                r[k] = float(r.get(k) or 0)
            except Exception:
                r[k] = 0.0
    return _LIBRARY


def set_selector(name: str):
    global SELECTOR, _FIRED_TAIL, ENABLED
    assert name in ("S0", "S1", "S2")
    SELECTOR = name
    ENABLED = name != "S0"  # S0 is pure backbone
    _FIRED_TAIL = None


def reset():
    global _FIRED_TAIL
    _FIRED_TAIL = None


def _feat_dist(a, b):
    # scale-ish
    keys = (("money", 2000.0), ("melon", 6.0), ("animals", 8.0),
            ("plant", 20.0), ("shed_total", 30.0), ("n_shops", 3.0))
    s = 0.0
    for k, sc in keys:
        d = (a.get(k, 0) - b.get(k, 0)) / sc
        s += d * d
    return math.sqrt(s)


def knn_mode(state: dict, day: int, k: int = 3) -> str:
    lib = load_library()
    if not lib:
        return "MAIN"
    pool = [r for r in lib if abs(r["day"] - day) <= 2]
    if not pool:
        pool = lib
    pool = sorted(pool, key=lambda r: _feat_dist(state, r))[:k]
    votes = {}
    for r in pool:
        votes[r["mode"]] = votes.get(r["mode"], 0) + 1
    return max(votes, key=votes.get)


def select_mode(day: int, state: dict) -> str:
    """Return strategic mode for this day under current selector."""
    if SELECTOR == "S0":
        return "MAIN"
    if SELECTOR == "S1":
        # sparse rules (P17.1-style), once-ish by day window
        money = state.get("money", 0)
        melon = state.get("melon", 0)
        shed_m = state.get("shed_melon", 0)
        animals = state.get("animals", 0)
        if 9 <= day <= 12 and (melon + shed_m) >= 2 and money < 1200:
            return "CASH_WINDOW"
        if 11 <= day <= 16 and animals < 2 and money >= 900:
            return "HERD_SCALE"
        return "MAIN"
    # S2
    return knn_mode(state, day, k=3)


def decide(day: int, state: dict) -> str:
    """Sticky tail after first non-MAIN selection in a window (avoid thrash)."""
    global _FIRED_TAIL
    if _FIRED_TAIL and day <= 18:
        # keep conversion tail once chosen through mid game
        if _FIRED_TAIL == "CASH_WINDOW":
            return _FIRED_TAIL
    mode = select_mode(day, state)
    if mode in ("CASH_WINDOW", "HERD_SCALE"):
        _FIRED_TAIL = mode
    return mode
