# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Local-only composite: v62 + attack-class yarn switch + Curve q1 counter.

This probe intentionally imports nearby research candidates.  It is not a
submission artifact; the purpose is to validate branch composition before a
standalone candidate is produced.
"""

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


_BASE = _load("_v65_v62_base", "candidate_v62_composite_bakery_yarn.py")
_CURVE_SOURCE = _load("_v65_curve_source", "candidate_v60_curve_counter.py")


# Dude/get-some-fries public route-class branch.  The first signature only arms
# the branch; no action changes until the complete public step-72 signature is
# visible.
_ATTACK_STATE = {
    0: {"last": -1, "armed": False, "active": False},
    1: {"last": -1, "armed": False, "active": False},
}
_ATTACK_ORIGINAL_ADVANCE = _BASE._v58_advance_extra_policies
_ATTACK_ORIGINAL_RECOVERY = _BASE._v58_recovery_mode
_ATTACK_ORIGINAL_ROUTE = _BASE._v59_route
_ATTACK_FIRST_SHOPS = {"BAKERY", "BRUNCH_SPOT", "FARMERS_MARKET"}


def _asset_counts(farm):
    counts = {}
    for tile in _BASE._v58_walk_tiles((farm or {}).get("tiles", []) or []):
        value = str(tile.get("animal") or tile.get("crop") or "")
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _attack_step1_signature(obs):
    seat = _BASE._v58_seat(obs)
    opponent = _BASE._v58_farms(obs)[1 - seat]
    market = (obs or {}).get("market", {}) or {}
    return (
        _BASE._v58_number(opponent.get("money")),
        len(opponent.get("hands", []) or []),
        _BASE._v58_number((market.get("inventory") or {}).get("WHEAT")),
        _BASE._v58_number((market.get("prices") or {}).get("WHEAT")),
    )


def _attack_step72_signature(obs):
    seat = _BASE._v58_seat(obs)
    mine, opponent = _BASE._v58_farms(obs)[seat], _BASE._v58_farms(obs)[1 - seat]
    market = (obs or {}).get("market", {}) or {}
    shops = _BASE._v58_shops(obs)
    return (
        bool(shops and shops[0] in _ATTACK_FIRST_SHOPS)
        and _BASE._v58_number(mine.get("money")) == 149
        and len(mine.get("hands", []) or []) == 0
        and _asset_counts(mine) == {"COW": 3, "SHEEP": 2, "WHEAT": 7, "MELON": 12}
        and _BASE._v58_number(opponent.get("money")) == 724
        and len(opponent.get("hands", []) or []) == 0
        and _asset_counts(opponent)
        == {"COW": 2, "SHEEP": 3, "WHEAT": 10, "STRAWBERRY": 3}
        and _BASE._v58_number((market.get("inventory") or {}).get("WHEAT")) == 9975
        and _BASE._v58_number((market.get("prices") or {}).get("WHEAT")) == 30
    )


def _attack_advance(obs, visible):
    actions = _ATTACK_ORIGINAL_ADVANCE(obs, visible)
    seat = _BASE._v58_seat(obs)
    step = _BASE._v59_step(obs)
    state = _ATTACK_STATE[seat]
    if step == 0 or step <= int(state.get("last", -1)):
        state = {"last": step, "armed": False, "active": False}
        _ATTACK_STATE[seat] = state
    state["last"] = step
    if step == 1 and _attack_step1_signature(obs) == (11, 5, 9942, 33):
        state["armed"] = True
    if step == 72 and state["armed"]:
        state["active"] = _attack_step72_signature(obs)
    if state["active"]:
        actions["recovery"] = actions["base_yarn"]
    return actions


def _attack_recovery_mode(obs):
    if _ATTACK_STATE[_BASE._v58_seat(obs)]["active"]:
        return "recovery"
    return _ATTACK_ORIGINAL_RECOVERY(obs)


def _attack_route(obs, future_step):
    if _ATTACK_STATE[_BASE._v58_seat(obs)]["active"]:
        return _BASE._V56_YARN_ROUTE
    return _ATTACK_ORIGINAL_ROUTE(obs, future_step)


_BASE._v58_advance_extra_policies = _attack_advance
_BASE._v58_recovery_mode = _attack_recovery_mode
_BASE._v59_route = _attack_route


# CurveCowboy public counter.  Its route remains isolated from all base-route
# state once the exact step-1 signature fires.
_CURVE_ROUTE = _CURVE_SOURCE._CURVE_COUNTER_ROUTE
_CURVE_STATE = {
    0: {"last": -1, "active": False, "pending": {}},
    1: {"last": -1, "active": False, "pending": {}},
}
_CURVE_BLOCKED = {"BUILD_PASTURE", "BUILD_COOP", "PLANT", "PLACE"}
_CURVE_SELLABLE = (
    "WOOL", "MILK", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "FERTILIZER", "WHEAT"
)


def _curve_signature(obs):
    seat = _BASE._v58_seat(obs)
    mine, rival = _BASE._v58_farms(obs)[seat], _BASE._v58_farms(obs)[1 - seat]
    inventory = (((obs or {}).get("market") or {}).get("inventory") or {})
    return (
        _BASE._v59_step(obs) == 1
        and _BASE._v58_number(mine.get("money")) == 2864
        and _BASE._v58_number(rival.get("money")) == 1390
        and len(rival.get("hands") or []) == 0
        and _BASE._v58_number(inventory.get("WHEAT")) == 9941
    )


def _curve_order(action):
    action = _BASE._v60_copy_action(action)
    indexed = {}
    hires = []
    for order in action["market"]:
        if order and order[0] == "HIRE":
            hires.append(order)
        elif len(order) >= 2:
            indexed[(order[0], order[1])] = order
    market = [["SELL", "WHEAT", 1]]
    for key in (("BUY_ANIMAL", "COW"), ("BUY_ANIMAL", "SHEEP")):
        if key in indexed:
            market.append(indexed[key])
    market.extend(hires)
    for key in (("BUY_SEED", "WHEAT"), ("BUY_SEED", "MELON")):
        if key in indexed:
            market.append(indexed[key])
    action["market"] = market[:10]
    return action


def _curve_align(obs, action):
    action = _BASE._v60_copy_action(action)
    seat = _BASE._v58_seat(obs)
    expected = len((_BASE._v58_farms(obs)[seat] or {}).get("hands") or [])
    action["hands"].extend([["PASS"] for _ in range(max(0, expected - len(action["hands"])))])
    action["hands"] = action["hands"][:expected]
    return action


def _curve_weed(tiles, position):
    try:
        x, y = int(position[0]), int(position[1])
        tile = tiles[y][x]
        return isinstance(tile, dict) and tile.get("kind") == "WEED"
    except (IndexError, TypeError, ValueError):
        return False


def _curve_repair(obs, action, state):
    seat = _BASE._v58_seat(obs)
    farm = _BASE._v58_farms(obs)[seat] or {}
    tiles = farm.get("tiles") or []
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    orders = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    orders.extend([["PASS"] for _ in range(max(0, len(positions) - len(orders)))])
    pending = state["pending"]
    for actor, position in enumerate(positions):
        scheduled = orders[actor] if orders[actor] else ["PASS"]
        queue = pending.get(actor)
        if queue:
            orders[actor] = queue.pop(0)
            if scheduled[0] != "PASS":
                queue.append(scheduled)
            if not queue:
                pending.pop(actor, None)
        elif scheduled[0] in _CURVE_BLOCKED and _curve_weed(tiles, position):
            orders[actor] = ["DIG"]
            pending[actor] = [scheduled]
    action["farmer"] = orders[0]
    action["hands"] = orders[1:len(positions)]
    return action


def _curve_liquidate(obs, action):
    action = _BASE._v60_copy_action(action)
    shed = dict((((obs or {}).get("private") or {}).get("shed") or {}))
    action["market"] = [
        ["SELL", item, int(shed.get(item, 0) or 0)]
        for item in _CURVE_SELLABLE
        if int(shed.get(item, 0) or 0) > 0
    ][:10]
    return action


__version__ = "local-v65-v62-attack-yarn-curve-q1"


def kaggle_agent_v65_local_combined(obs, configuration=None):
    base_action = _BASE.kaggle_agent_v62_composite_bakery_yarn(obs, configuration)
    step = _BASE._v59_step(obs)
    seat = _BASE._v58_seat(obs)
    state = _CURVE_STATE[seat]
    if step == 0 or step <= int(state.get("last", -1)):
        state = {"last": step, "active": False, "pending": {}}
        _CURVE_STATE[seat] = state
    else:
        state["last"] = step
    if _curve_signature(obs):
        state["active"] = True
        return _curve_order(base_action)
    if not state["active"] or step < 2:
        return base_action
    action = _curve_align(obs, _CURVE_ROUTE[min(max(0, step), 719)])
    action = _curve_repair(obs, action, state)
    if step == 2:
        action["market"].append(["BUY_PRODUCT", "WHEAT", 1])
    capacity = _BASE._v60_int((configuration or {}).get("shedCapacity", 100)) or 100
    action = _BASE._v60_shed_guard(obs, action, capacity)
    if step == 718:
        action = _curve_liquidate(obs, action)
    return action
