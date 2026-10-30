# -*- coding: utf-8 -*-
"""Toggle for P13.3 WATER_READY_CROP on B."""
ENABLED = False


def set_enabled(flag: bool):
    global ENABLED
    ENABLED = bool(flag)


def is_enabled() -> bool:
    return ENABLED
