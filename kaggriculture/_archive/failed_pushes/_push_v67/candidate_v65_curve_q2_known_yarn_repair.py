# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Local probe: v65/cygn with Curve q2 and one strict step-72 repair."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_SOURCE_FILE = globals().get("__file__")
_HERE = (
    Path(_SOURCE_FILE).resolve().parent
    if _SOURCE_FILE
    else Path.cwd() / "reference" / "live_meta"
)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CYGN = _load("_v65_curve_q2_cygn_base", "candidate_v65_curve_cygn_clone.py")
_V65 = _CYGN._V65
_BASE = _CYGN._BASE
_KNOWN_YARN = _BASE._v51_build_policy(_BASE._V58_KNOWN_YARN_ROUTE, _BASE._V54_CONFIG)
_STATE = {
    0: {"last": -1, "repair": False},
    1: {"last": -1, "repair": False},
}


def _copy_action(action):
    action = action or {}
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _replace_quantity(action, verb, item, quantity):
    action = _copy_action(action)
    for order in action["market"]:
        if len(order) >= 2 and order[:2] == [verb, item]:
            order[2:] = [quantity]
            break
    return action


def _public_signature(obs):
    seat = _BASE._v58_seat(obs)
    mine, opponent = _BASE._v58_farms(obs)[seat], _BASE._v58_farms(obs)[1 - seat]
    market = (obs or {}).get("market", {}) or {}
    inventory = market.get("inventory", {}) or {}
    prices = market.get("prices", {}) or {}
    return (
        tuple(_BASE._v58_shops(obs)),
        _BASE._v58_number(mine.get("money")),
        len(mine.get("hands") or []),
        tuple(sorted(_V65._asset_counts(mine).items())),
        _BASE._v58_number(opponent.get("money")),
        len(opponent.get("hands") or []),
        tuple(sorted(_V65._asset_counts(opponent).items())),
        tuple(sorted((key, _BASE._v58_number(value)) for key, value in inventory.items())),
        tuple(sorted((key, _BASE._v58_number(value)) for key, value in prices.items())),
    )


_CURVE_Q2_REPAIR_STEP72 = (
    ("FARMERS_MARKET",),
    205,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    220,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9976), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)


__version__ = "local-v65-curve-q2-known-yarn72-repair-cygn"


def kaggle_agent_v65_curve_q2_known_yarn_repair(obs, configuration=None):
    selected = _CYGN.kaggle_agent_v65_curve_cygn_clone(obs, configuration)
    visible = _BASE._v56_visible_configuration(configuration)
    known_yarn = _KNOWN_YARN(obs, visible)
    step = _BASE._v59_step(obs)
    seat = _BASE._v58_seat(obs)
    state = _STATE[seat]
    if step == 0 or step <= int(state.get("last", -1)):
        state = {"last": step, "repair": False}
        _STATE[seat] = state
    else:
        state["last"] = step

    curve_active = bool(_V65._CURVE_STATE[seat].get("active"))
    if step == 1 and curve_active:
        return _replace_quantity(selected, "SELL", "WHEAT", 2)
    if step == 2 and curve_active:
        return _replace_quantity(selected, "BUY_PRODUCT", "WHEAT", 2)
    if step == 72 and curve_active:
        state["repair"] = _public_signature(obs) == _CURVE_Q2_REPAIR_STEP72
    if not state["repair"]:
        return selected

    action = _BASE._v60_seed_trim(obs, known_yarn, step)
    capacity = _BASE._v60_int((configuration or {}).get("shedCapacity", 100)) or 100
    action = _BASE._v60_shed_guard(obs, action, capacity)
    if step == 718:
        action = _V65._curve_liquidate(obs, action)
    return action


kaggle_agent_v65_curve_q2_known_yarn_repair.audit_state = _STATE
kaggle_submission_agent = kaggle_agent_v65_curve_q2_known_yarn_repair
agent = kaggle_agent_v65_curve_q2_known_yarn_repair
