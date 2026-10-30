# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Local v66: strict public-state routing plus the Curve q2 counter.

This combines the independently tested v65 components without touching the
current submission artifact:

* Curve q2, strict FARMERS/Daniel step-72 repairs, and the cygn clone split;
* two-stage BAKERY/FARMERS routing and five exact late threat routes;
* three exact historical-win recoveries; and
* the six-turn loaded-unit terminal return overlay.

All opponent classification uses only public observations.
"""

from __future__ import annotations

import importlib.util
import sys
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


_CURVE = _load("_v66_curve_base", "candidate_v65_curve_q2_daniel_backbone.py")
_Q2 = _CURVE._Q2
_V65 = _Q2._V65
_BASE = _CURVE._BASE

_ORIGINAL_ADVANCE = _BASE._v58_advance_extra_policies
_ORIGINAL_RECOVERY_MODE = _BASE._v58_recovery_mode
_ORIGINAL_BASE_ACTION = _BASE._v58_base_action
_ORIGINAL_ROUTE = _BASE._v59_route

_ACTION_KEYS = {
    "bakery_yarn": "bakery_yarn",
    "recovery": "recovery",
    "yarn": "base_yarn",
    "ice_minimax": "ice_minimax",
    "known_yarn": "known_yarn",
    "clone": "clone",
}
_ROUTES = {
    "bakery_yarn": _BASE._V58_BAKERY_YARN_ROUTE,
    "recovery": _BASE._V58_RECOVERY_ROUTE,
    "yarn": _BASE._V56_YARN_ROUTE,
    "ice_minimax": _BASE._V58_ICE_MINIMAX_ROUTE,
    "known_yarn": _BASE._V58_KNOWN_YARN_ROUTE,
    "clone": _BASE._V58_CLONE_ROUTE,
}


def _fresh_state(step=-1):
    return {
        "last": step,
        "branch": "",
        "route": "",
        "victor_armed": False,
        "coke_armed": False,
        "events": [],
    }


_META_STATE = {0: _fresh_state(), 1: _fresh_state()}


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


# Historical v58 wins lost only to the universal WHEAT-5 opening.
_VICTOR_STEP72 = (
    ("FARMERS_MARKET",),
    140,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    312,
    0,
    (("MELON", 7), ("SHEEP", 4), ("STRAWBERRY", 2), ("WHEAT", 8)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9964), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 31), ("WOOL", 212)),
)

_VICTOR_STEP144 = (
    ("FARMERS_MARKET", "YARN_STORE"),
    214,
    0,
    (("COW", 4), ("MELON", 12), ("SHEEP", 2), ("STRAWBERRY", 4), ("WHEAT", 3)),
    185,
    0,
    (("COW", 1), ("MELON", 7), ("SHEEP", 4), ("STRAWBERRY", 6), ("WHEAT", 6)),
    (("CARROT", 9976), ("EGG", 9994), ("FERTILIZER", 10045),
     ("MELON", 9994), ("MILK", 9994), ("STRAWBERRY", 9976),
     ("TOMATO", 9976), ("WHEAT", 9945), ("WOOL", 9994)),
    (("CARROT", 37), ("EGG", 50), ("FERTILIZER", 91), ("MELON", 267),
     ("MILK", 181), ("STRAWBERRY", 161), ("TOMATO", 63),
     ("WHEAT", 32), ("WOOL", 217)),
)

_TWOMOON_STEP72 = (
    ("BRUNCH_SPOT",),
    140,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    312,
    0,
    (("MELON", 7), ("SHEEP", 4), ("STRAWBERRY", 2), ("WHEAT", 8)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9964), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 31), ("WOOL", 212)),
)

_YAT_STEP72 = (
    ("FARMERS_MARKET",),
    141,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    588,
    0,
    (("COW", 3), ("MELON", 5), ("SHEEP", 2), ("STRAWBERRY", 2), ("WHEAT", 12)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10018),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9970), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 96), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)


# Complete public-state shop families and exact late threat signatures.
_BAKERY_STEP72 = (
    ("BAKERY",),
    148,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    191,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9975), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)

_FARMERS_STEP72 = (
    ("FARMERS_MARKET",),
    148,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    191,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9975), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)

_NEIBYR_STEP72 = (
    ("PIZZA_SHOP",),
    142,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    154,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 6)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9973), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)

_C0NRAD_STEP72 = (
    ("FARMERS_MARKET",),
    145,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    12,
    0,
    (("CARROT", 1), ("COW", 4), ("MELON", 6), ("SHEEP", 2), ("WHEAT", 7)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10014),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9971), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)

_JOHNBLAKE_STEP72 = (
    ("BRUNCH_SPOT",),
    143,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    166,
    0,
    (("MELON", 7), ("SHEEP", 4), ("WHEAT", 10)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10012),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9966), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 98), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 31), ("WOOL", 212)),
)

_STEPHEN_STEP72 = (
    ("BRUNCH_SPOT",),
    142,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    156,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 6)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9973), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)

_COKE_STEP72 = (
    ("ICE_CREAM_SHOP",),
    148,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    191,
    0,
    (("COW", 3), ("MELON", 12), ("SHEEP", 2), ("WHEAT", 7)),
    (("CARROT", 9997), ("EGG", 9997), ("FERTILIZER", 10016),
     ("MELON", 9997), ("MILK", 9997), ("STRAWBERRY", 9997),
     ("TOMATO", 9997), ("WHEAT", 9975), ("WOOL", 9997)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 97), ("MELON", 262),
     ("MILK", 175), ("STRAWBERRY", 135), ("TOMATO", 60),
     ("WHEAT", 30), ("WOOL", 212)),
)

_COKE_STEP144 = (
    ("ICE_CREAM_SHOP", "BRUNCH_SPOT"),
    216,
    0,
    (("COW", 4), ("MELON", 12), ("SHEEP", 2), ("STRAWBERRY", 4), ("WHEAT", 3)),
    839,
    0,
    (("COW", 4), ("MELON", 12), ("SHEEP", 2), ("STRAWBERRY", 4), ("WHEAT", 3)),
    (("CARROT", 9994), ("EGG", 9994), ("FERTILIZER", 10048),
     ("MELON", 9994), ("MILK", 9976), ("STRAWBERRY", 9976),
     ("TOMATO", 9994), ("WHEAT", 9955), ("WOOL", 9994)),
    (("CARROT", 35), ("EGG", 50), ("FERTILIZER", 90), ("MELON", 267),
     ("MILK", 203), ("STRAWBERRY", 161), ("TOMATO", 61),
     ("WHEAT", 32), ("WOOL", 217)),
)


def _activate(state, branch, route, step):
    state["branch"] = branch
    state["route"] = route
    state["events"].append(f"{step}:{branch}:{route}")


def _advance(obs, visible):
    actions = _ORIGINAL_ADVANCE(obs, visible)
    seat = _BASE._v58_seat(obs)
    step = _BASE._v59_step(obs)
    state = _META_STATE[seat]
    if step == 0 or step <= int(state.get("last", -1)):
        state = _fresh_state(step)
        _META_STATE[seat] = state
    else:
        state["last"] = step

    curve_active = bool(_V65._CURVE_STATE[seat].get("active"))
    if step == 72 and not curve_active:
        signature = _public_signature(obs)
        if signature == _TWOMOON_STEP72:
            _activate(state, "historical_twomoon", "yarn", step)
        elif signature == _YAT_STEP72:
            _activate(state, "historical_yat", "recovery", step)
        elif signature == _VICTOR_STEP72:
            state["victor_armed"] = True
            state["events"].append("72:historical_victor:armed")
        elif signature == _BAKERY_STEP72:
            _activate(state, "bakery", "bakery_yarn", step)
        elif signature == _FARMERS_STEP72:
            _activate(state, "farmers", "recovery", step)
        elif signature == _NEIBYR_STEP72:
            _activate(state, "neibyr", "recovery", step)
        elif signature == _C0NRAD_STEP72:
            _activate(state, "c0nrad", "ice_minimax", step)
        elif signature == _JOHNBLAKE_STEP72:
            _activate(state, "johnblake", "known_yarn", step)
        elif signature == _STEPHEN_STEP72:
            _activate(state, "stephen", "known_yarn", step)
        elif signature == _COKE_STEP72:
            state["coke_armed"] = True
            state["events"].append("72:coke:armed")

    if step == 144:
        shops = _BASE._v58_shops(obs)
        second = shops[1] if len(shops) >= 2 else ""
        if state["victor_armed"]:
            if _public_signature(obs) == _VICTOR_STEP144:
                _activate(state, "historical_victor", "clone", step)
            else:
                state["events"].append("144:historical_victor:rejected")
            state["victor_armed"] = False
        if state["branch"] == "bakery":
            route = "bakery_yarn" if second == "YARN_STORE" else "recovery"
            _activate(state, "bakery", route, step)
        elif state["branch"] == "farmers":
            route = "yarn" if second == "YARN_STORE" else "recovery"
            _activate(state, "farmers", route, step)
        if state["coke_armed"]:
            if _public_signature(obs) == _COKE_STEP144:
                _activate(state, "coke", "known_yarn", step)
            else:
                state["events"].append("144:coke:rejected")
            state["coke_armed"] = False

    route = state["route"]
    if route:
        actions["recovery"] = actions[_ACTION_KEYS[route]]
    return actions


def _recovery_mode(obs):
    if _META_STATE[_BASE._v58_seat(obs)]["route"]:
        return "recovery"
    return _ORIGINAL_RECOVERY_MODE(obs)


def _base_action(obs, step, shops, actions):
    route = _META_STATE[_BASE._v58_seat(obs)]["route"]
    if route:
        return actions[_ACTION_KEYS[route]]
    return _ORIGINAL_BASE_ACTION(obs, step, shops, actions)


def _route(obs, future_step):
    route = _META_STATE[_BASE._v58_seat(obs)]["route"]
    if route:
        return _ROUTES[route]
    return _ORIGINAL_ROUTE(obs, future_step)


_BASE._v58_advance_extra_policies = _advance
_BASE._v58_recovery_mode = _recovery_mode
_BASE._v58_base_action = _base_action
_BASE._v59_route = _route


# Terminal overlay: route a loaded actor home only on its final feasible turn.
_RESIDUAL = sys.modules[_BASE._V51ResidualConfig.__module__]
_TERMINAL_MARKET = _RESIDUAL.terminal_market
_TERMINAL_GLOBALS = _TERMINAL_MARKET.__globals__
_TERMINAL_UNITS = _TERMINAL_GLOBALS["monetizable_terminal_units"]
_MOVE_TOWARD = _TERMINAL_GLOBALS["_move_toward"]
_SHED_ACCESS = _TERMINAL_GLOBALS["_shed_access"]
_SELLABLE = frozenset(_TERMINAL_GLOBALS["SELLABLE"])


def _align(action, expected):
    action = _BASE._v60_copy_action(action)
    hands = list(action["hands"])
    hands.extend([["PASS"] for _ in range(max(0, expected - len(hands)))])
    action["hands"] = hands[:expected]
    return action


def _route_loaded_units(obs, action, step):
    if not 713 <= step <= 716:
        return action
    seat = _BASE._v58_seat(obs)
    farm = _BASE._v58_farms(obs)[seat] or {}
    tiles = farm.get("tiles") or []
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    inventories = list((((obs or {}).get("private") or {}).get("inventories") or []))
    inventories.extend({} for _ in range(max(0, len(positions) - len(inventories))))
    action = _align(action, max(0, len(positions) - 1))
    orders = [action["farmer"], *action["hands"]]
    access = _SHED_ACCESS(len(tiles) or 10)
    departure_distance = 718 - step

    for index, (position, inventory) in enumerate(zip(positions, inventories)):
        load = sum(
            max(0, int(quantity or 0))
            for item, quantity in (inventory or {}).items()
            if item in _SELLABLE
        )
        if load <= 0:
            continue
        x, y = int(position[0]), int(position[1])
        distance = min(abs(x - sx) + abs(y - sy) for sx, sy in access)
        if distance == departure_distance:
            orders[index] = _MOVE_TOWARD((x, y), access, tiles)

    action["farmer"] = orders[0]
    action["hands"] = orders[1:]
    return action


__version__ = "local-v66-public-meta-q2-terminal-h6"


def kaggle_agent_v66_meta_closed_loop(obs, configuration=None):
    action = _CURVE.kaggle_agent_v65_curve_q2_daniel_backbone(obs, configuration)
    step = _BASE._v59_step(obs)
    action = _route_loaded_units(obs, action, step)
    if step in (717, 718):
        action = _TERMINAL_UNITS(obs, action, step)
    if step == 718:
        action = _TERMINAL_MARKET(obs, action, rule="collision", replace=True)
    return action


kaggle_agent_v66_meta_closed_loop.audit_state = _META_STATE
kaggle_submission_agent = kaggle_agent_v66_meta_closed_loop
agent = kaggle_agent_v66_meta_closed_loop
