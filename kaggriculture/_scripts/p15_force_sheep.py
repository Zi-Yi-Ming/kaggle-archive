# -*- coding: utf-8 -*-
"""P15: force early SHEEP×N for interaction tests. Not a full planner."""
ENABLED = False
N_SHEEP = 2
BUY_UNTIL_DAY = 2


def set_enabled(flag: bool, n: int = 2):
    global ENABLED, N_SHEEP
    ENABLED = bool(flag)
    N_SHEEP = int(n)


def is_enabled() -> bool:
    return ENABLED


def forced_sheep(day: int, live_sheep: int, shed_sheep: int, cash: float) -> int:
    """How many sheep to buy this dawn. 0 when disabled."""
    if not ENABLED or day > BUY_UNTIL_DAY:
        return 0
    have = live_sheep + shed_sheep
    gap = max(0, N_SHEEP - have)
    if gap <= 0 or cash < 600:
        return 0
    return min(gap, int((cash - 200) // 500), 2)
