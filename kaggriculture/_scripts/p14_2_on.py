# -*- coding: utf-8 -*-
ENABLED = False


def set_enabled(flag: bool):
    global ENABLED
    ENABLED = bool(flag)


def is_enabled() -> bool:
    return ENABLED
