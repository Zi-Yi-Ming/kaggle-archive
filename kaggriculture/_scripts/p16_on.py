# -*- coding: utf-8 -*-
"""P16 toggles + per-player branch memory."""
BRANCH_ON = False
SKELETON_ON = False
_BRANCH = {}


def set_skeleton(flag: bool):
    global SKELETON_ON
    SKELETON_ON = bool(flag)


def set_branch(flag: bool):
    global BRANCH_ON
    BRANCH_ON = bool(flag)


def skeleton_enabled() -> bool:
    return SKELETON_ON


def branch_enabled() -> bool:
    return BRANCH_ON


def get_branch(player: int):
    from p16_branch.branch import BranchState
    if player not in _BRANCH:
        _BRANCH[player] = BranchState()
    return _BRANCH[player]


def reset_memory():
    _BRANCH.clear()
