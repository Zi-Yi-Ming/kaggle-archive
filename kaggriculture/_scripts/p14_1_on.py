# -*- coding: utf-8 -*-
"""Toggle for P14.1 portfolio crop allocation."""
ENABLED = False


def set_enabled(flag: bool):
    global ENABLED
    ENABLED = bool(flag)


def is_enabled() -> bool:
    return ENABLED
