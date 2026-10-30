# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Normalization and legal structured actions for Kaggriculture 1.32.7."""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping, Sequence
from typing import Any


CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
CROP_RULES = {
    "WHEAT": {"seed": 10, "first_yield_day": 2, "ongoing": False},
    "CARROT": {"seed": 20, "first_yield_day": 2, "ongoing": False},
    "TOMATO": {"seed": 50, "first_yield_day": 8, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "ongoing": True},
    "MELON": {"seed": 80, "first_yield_day": 10, "ongoing": False},
}
ANIMALS = ("GOOSE", "COW", "SHEEP")
ANIMAL_RULES = {
    "GOOSE": {"cost": 300, "structure": "COOP", "product": "EGG"},
    "COW": {"cost": 400, "structure": "PASTURE", "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "product": "WOOL"},
}
PRODUCTS = (
    "WHEAT",
    "CARROT",
    "TOMATO",
    "STRAWBERRY",
    "MELON",
    "EGG",
    "MILK",
    "WOOL",
    "FERTILIZER",
)
STORAGE_ITEMS = PRODUCTS + ANIMALS
BUYABLE_PRODUCTS = ("WHEAT", "FERTILIZER")
SHOP_NAMES = (
    "BAKERY",
    "PIZZA_SHOP",
    "BRUNCH_SPOT",
    "YARN_STORE",
    "ICE_CREAM_SHOP",
    "PET_CAFE",
    "SMOOTHIE_SHOP",
    "FARMERS_MARKET",
)

UNIT_OPS = (
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST",
    "PASS",
    "PICKUP",
    "DROP",
    "PLANT",
    "WATER",
    "HARVEST",
    "FERTILIZE",
    "BUILD_COOP",
    "BUILD_PASTURE",
    "DIG",
    "PLACE",
    "FEED",
    "COLLECT_FERTILIZER",
    "CARE",
)
MARKET_OPS = ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL", "HIRE", "BUY_LAND")
MOVES = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST": (1, 0),
    "WEST": (-1, 0),
}
LAND_PRICES = (1000, 2000, 4000)

MARKET_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.80, "above_func": "log", "above_target": 0.20},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

DEFAULT_CONFIGURATION = {
    "episodeSteps": 720,
    "boardSize": 10,
    "startingMoney": 3000,
    "maxMarketOrdersPerTurn": 10,
    "turnsPerDay": 24,
    "shedCapacity": 100,
    "farmHandCostMult": 1,
    "marketParams": {},
}
DEFAULT_ACTION = {"farmer": ["PASS"], "hands": [], "market": []}


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _config(configuration: Any | None) -> dict[str, Any]:
    result = dict(DEFAULT_CONFIGURATION)
    if configuration is None:
        return result
    if isinstance(configuration, Mapping):
        source = configuration
    else:
        source = vars(configuration)
    for key in result:
        if key in source and source[key] is not None:
            result[key] = source[key]
    return result


def _quadrant(x: int, y: int, board_size: int) -> str:
    half = board_size // 2
    return ("N" if y < half else "S") + ("W" if x < half else "E")


def _spawn(board_size: int) -> list[int]:
    half = board_size // 2
    return [max(0, half - 1), max(0, half - 1)]


def _empty_tiles(board_size: int, unlocked: set[str] | None = None) -> list[list[Any]]:
    unlocked = unlocked or {"NW"}
    return [
        [None if _quadrant(x, y, board_size) in unlocked else "LOCKED" for x in range(board_size)]
        for y in range(board_size)
    ]


def _normalize_position(value: Any, default: list[int]) -> list[int]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) >= 2:
        return [int(value[0]), int(value[1])]
    return list(default)


def _normalize_farm(value: Any, cfg: Mapping[str, Any]) -> dict[str, Any]:
    source = _plain(value) if isinstance(value, Mapping) else {}
    board_size = int(cfg["boardSize"])
    unlocked = [str(q) for q in source.get("unlocked_quadrants", ["NW"])]
    if "NW" not in unlocked:
        unlocked.insert(0, "NW")
    default_tiles = _empty_tiles(board_size, set(unlocked))
    raw_tiles = source.get("tiles", [])
    tiles: list[list[Any]] = []
    for y in range(board_size):
        raw_row = raw_tiles[y] if isinstance(raw_tiles, list) and y < len(raw_tiles) and isinstance(raw_tiles[y], list) else []
        tiles.append(
            [copy.deepcopy(raw_row[x]) if x < len(raw_row) else default_tiles[y][x] for x in range(board_size)]
        )
    spawn = _spawn(board_size)
    hands = source.get("hands", [])
    return {
        **source,
        "money": float(source.get("money", cfg["startingMoney"])),
        "tiles": tiles,
        "farmer": _normalize_position(source.get("farmer"), spawn),
        "hands": [
            _normalize_position(position, spawn)
            for position in hands
        ] if isinstance(hands, list) else [],
        "unlocked_quadrants": unlocked,
        "hires_today": int(source.get("hires_today", 0)),
    }


def normalize_observation(
    observation: Mapping[str, Any] | Any,
    configuration: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    """Return a detached observation with every official field and nested key."""
    cfg = _config(configuration)
    source = _plain(observation) if isinstance(observation, Mapping) else _plain(vars(observation))
    player = int(source.get("player", 0))

    farms_source = source.get("farms", [])
    if not isinstance(farms_source, list):
        farms_source = []
    farms = [
        _normalize_farm(farms_source[index] if index < len(farms_source) else {}, cfg)
        for index in range(2)
    ]

    private_source = source.get("private", {})
    private_source = _plain(private_source) if isinstance(private_source, Mapping) else {}
    shed_source = private_source.get("shed", {})
    seeds_source = private_source.get("seeds", {})
    inventory_source = private_source.get("inventories", [])
    shed_source = shed_source if isinstance(shed_source, Mapping) else {}
    seeds_source = seeds_source if isinstance(seeds_source, Mapping) else {}
    inventory_source = inventory_source if isinstance(inventory_source, list) else []
    unit_count = 1 + len(farms[player]["hands"]) if 0 <= player < len(farms) else 1
    inventories = []
    for index in range(max(unit_count, len(inventory_source), 1)):
        raw = inventory_source[index] if index < len(inventory_source) else {}
        inventories.append(
            {str(item): int(quantity) for item, quantity in raw.items()}
            if isinstance(raw, Mapping)
            else {}
        )
    private = {
        **private_source,
        "shed": {item: int(shed_source.get(item, 0)) for item in STORAGE_ITEMS},
        "seeds": {crop: int(seeds_source.get(crop, 0)) for crop in CROPS},
        "inventories": inventories,
    }

    market_source = source.get("market", {})
    market_source = _plain(market_source) if isinstance(market_source, Mapping) else {}
    market_inventory = market_source.get("inventory", {})
    market_prices = market_source.get("prices", {})
    market_inventory = market_inventory if isinstance(market_inventory, Mapping) else {}
    market_prices = market_prices if isinstance(market_prices, Mapping) else {}
    market = {
        **market_source,
        "inventory": {
            item: int(market_inventory.get(item, MARKET_PARAMS[item]["I0"])) for item in PRODUCTS
        },
        "prices": {
            item: int(market_prices.get(item, MARKET_PARAMS[item]["base"])) for item in PRODUCTS
        },
    }

    town_source = source.get("town", {})
    town_source = _plain(town_source) if isinstance(town_source, Mapping) else {}
    shops = town_source.get("unlocked_shops", [])
    town = {
        **town_source,
        "unlocked_shops": [str(shop) for shop in shops] if isinstance(shops, list) else [],
    }

    turns_per_day = max(1, int(cfg["turnsPerDay"]))
    step = int(source.get("step", int(source.get("day", 0)) * turns_per_day + int(source.get("hour", 0))))
    return {
        **source,
        "player": player,
        "step": step,
        "day": int(source.get("day", step // turns_per_day)),
        "hour": int(source.get("hour", step % turns_per_day)),
        "farms": farms,
        "private": private,
        "market": market,
        "town": town,
        "remainingOverageTime": float(source.get("remainingOverageTime", 60.0)),
    }


def _working_observation(observation: Any, cfg: Mapping[str, Any]) -> Mapping[str, Any]:
    """Use a complete live observation directly; normalize partial fixtures."""
    if isinstance(observation, Mapping):
        required = {"player", "farms", "private", "market", "town"}
        if required <= observation.keys():
            player = int(observation["player"])
            farms = observation["farms"]
            private = observation["private"]
            if (
                isinstance(farms, Sequence)
                and 0 <= player < len(farms)
                and isinstance(private, Mapping)
                and {"shed", "seeds", "inventories"} <= private.keys()
            ):
                return observation
    return normalize_observation(observation, cfg)


def _canonical_part(value: Any, fallback: list[Any] | None = None) -> list[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        return list(["PASS"] if fallback is None else fallback)
    part = [_plain(item) for item in value]
    part[0] = str(part[0]).upper()
    if len(part) >= 2 and isinstance(part[1], str):
        part[1] = part[1].upper()
    if len(part) >= 3:
        try:
            part[2] = int(part[2])
        except (TypeError, ValueError):
            pass
    return part


def canonicalize_action(action: Any) -> dict[str, Any]:
    """Canonicalize action containers and operation/item casing without judging legality."""
    source = action if isinstance(action, Mapping) else {}
    farmer = _canonical_part(source.get("farmer", ["PASS"]))
    raw_hands = source.get("hands", [])
    raw_market = source.get("market", [])
    hands = (
        [_canonical_part(part) for part in raw_hands]
        if isinstance(raw_hands, Sequence) and not isinstance(raw_hands, (str, bytes, bytearray))
        else []
    )
    market = (
        [_canonical_part(order, fallback=[]) for order in raw_market]
        if isinstance(raw_market, Sequence) and not isinstance(raw_market, (str, bytes, bytearray))
        else []
    )
    return {"farmer": farmer, "hands": hands, "market": market}


def encode_action(action: Any) -> tuple[tuple[Any, ...], tuple[tuple[Any, ...], ...], tuple[tuple[Any, ...], ...]]:
    """Encode a structured action losslessly into a hashable canonical tuple."""
    canonical = canonicalize_action(action)
    return (
        tuple(canonical["farmer"]),
        tuple(tuple(part) for part in canonical["hands"]),
        tuple(tuple(order) for order in canonical["market"]),
    )


def decode_action(encoded: Any) -> dict[str, Any]:
    """Decode the tuple returned by :func:`encode_action`."""
    if isinstance(encoded, Mapping):
        return canonicalize_action(encoded)
    if not isinstance(encoded, Sequence) or isinstance(encoded, (str, bytes)) or len(encoded) != 3:
        raise ValueError("encoded action must contain farmer, hands, and market")
    return canonicalize_action(
        {"farmer": encoded[0], "hands": encoded[1], "market": encoded[2]}
    )


def _shed_tiles(board_size: int) -> set[tuple[int, int]]:
    half = board_size // 2
    return {
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    }


def _unit_position(farm: Mapping[str, Any], unit_index: int) -> list[int] | None:
    if unit_index == 0:
        return farm["farmer"]
    hands = farm["hands"]
    return hands[unit_index - 1] if 0 <= unit_index - 1 < len(hands) else None


def legal_unit_actions(
    observation: Mapping[str, Any] | Any,
    unit_index: int = 0,
    configuration: Mapping[str, Any] | Any | None = None,
) -> list[list[Any]]:
    """Enumerate every effectful atomic action for one current farmer/hand."""
    cfg = _config(configuration)
    obs = _working_observation(observation, cfg)
    player = obs["player"]
    if not 0 <= player < len(obs["farms"]):
        return [["PASS"]]
    farm = obs["farms"][player]
    position = _unit_position(farm, int(unit_index))
    if position is None:
        return [["PASS"]]
    x, y = position
    board_size = int(cfg["boardSize"])
    if not (0 <= x < board_size and 0 <= y < board_size):
        return [["PASS"]]
    inventory = obs["private"]["inventories"][unit_index]
    shed = obs["private"]["shed"]
    shed_total = sum(max(0, int(quantity)) for quantity in shed.values())
    shed_room = max(0, int(cfg["shedCapacity"]) - shed_total)

    actions: list[list[Any]] = [["PASS"]]
    for op, (dx, dy) in MOVES.items():
        if 0 <= x + dx < board_size and 0 <= y + dy < board_size:
            actions.append([op])

    tile = farm["tiles"][y][x]
    shed_adjacent = (x, y) in _shed_tiles(board_size)
    if shed_adjacent:
        if any(int(quantity) > 0 for quantity in inventory.values()):
            actions.append(["DROP"])
        for item in STORAGE_ITEMS:
            for quantity in range(1, max(0, int(shed.get(item, 0))) + 1):
                actions.append(["PICKUP", item, quantity])
        for item in STORAGE_ITEMS:
            held = max(0, int(inventory.get(item, 0)))
            matches_structure = (
                item in ANIMAL_RULES
                and isinstance(tile, Mapping)
                and tile.get("kind") == ANIMAL_RULES[item]["structure"]
                and "animal" not in tile
            )
            if matches_structure:
                if held > 0:
                    actions.append(["PLACE", item])
                continue
            for quantity in range(1, min(held, shed_room) + 1):
                actions.append(["PLACE", item, quantity])

    if tile == "LOCKED":
        return actions

    # Animal placement is a tile operation and works on matching structures
    # anywhere on owned land, not only on the four shed-access tiles.
    if isinstance(tile, Mapping) and "animal" not in tile:
        for animal, rule in ANIMAL_RULES.items():
            candidate = ["PLACE", animal]
            if (
                tile.get("kind") == rule["structure"]
                and int(inventory.get(animal, 0)) > 0
                and candidate not in actions
            ):
                actions.append(candidate)

    if tile is None:
        for crop in CROPS:
            if obs["private"]["seeds"].get(crop, 0) > 0:
                actions.append(["PLANT", crop])
        actions.extend([["BUILD_COOP"], ["BUILD_PASTURE"]])
        return actions

    if not isinstance(tile, Mapping):
        return actions

    has_animal = "animal" in tile
    if not has_animal:
        actions.append(["DIG"])

    if tile.get("kind") == "PLANT":
        if not bool(tile.get("watered_today", False)):
            actions.append(["WATER"])
        crop = str(tile.get("crop", ""))
        if crop in CROP_RULES:
            old_enough = obs["day"] - int(tile.get("planted_day", obs["day"])) >= CROP_RULES[crop]["first_yield_day"]
            if int(tile.get("yield_units", 0)) > 0 and old_enough:
                actions.append(["HARVEST"])
        if int(inventory.get("FERTILIZER", 0)) > 0:
            actions.append(["FERTILIZE"])
    elif has_animal:
        if not bool(tile.get("fed_today", False)) and int(inventory.get("WHEAT", 0)) > 0:
            actions.append(["FEED"])
        if int(tile.get("yield_units", 0)) > 0:
            actions.append(["HARVEST"])
        if bool(tile.get("fertilizer_available", False)):
            actions.append(["COLLECT_FERTILIZER"])
        if not bool(tile.get("cared_today", False)):
            actions.append(["CARE"])
    return actions


def _shape(name: str, value: float, target: float) -> float:
    value = max(0.0, value)
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
    if name == "hinge":
        if target <= 0:
            return value
        ratio = value / target
        return ratio + 8.0 * max(0.0, ratio - 1.0) ** 2
    return value


def _resolved_market_params(configuration: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    params = {item: dict(values) for item, values in MARKET_PARAMS.items()}
    overrides = configuration.get("marketParams", {})
    if isinstance(overrides, Mapping):
        for item, patch in overrides.items():
            if item in params and isinstance(patch, Mapping):
                params[item].update(patch)
    return params


def _market_price(item: str, inventory: int, params: Mapping[str, Mapping[str, Any]]) -> int:
    rule = params[item]
    base = float(rule["base"])
    initial = int(rule["I0"])
    target = float(rule["T"])
    if inventory < initial:
        shape_name = str(rule["below_func"])
        amplitude = float(rule["below_target"]) * base / _shape(shape_name, target, target)
        result = base + amplitude * _shape(shape_name, initial - inventory, target)
    else:
        shape_name = str(rule["above_func"])
        amplitude = float(rule["above_target"]) * base / _shape(shape_name, target, target)
        result = base - amplitude * _shape(shape_name, inventory - initial, target)
    return max(1, int(round(result)))


def _fib(index: int) -> int:
    first, second = 1, 1
    for _ in range(index):
        first, second = second, first + second
    return first


def _max_affordable_product_quantity(
    item: str,
    money: float,
    room: int,
    inventory: int,
    params: Mapping[str, Mapping[str, Any]],
) -> int:
    spent = 0
    affordable = 0
    for quantity in range(1, room + 1):
        spent += _market_price(item, inventory - quantity, params)
        if spent > money:
            break
        affordable = quantity
    return affordable


def legal_market_actions(
    observation: Mapping[str, Any] | Any,
    configuration: Mapping[str, Any] | Any | None = None,
) -> list[list[Any]]:
    """Enumerate every effectful legal single market order, including quantities."""
    cfg = _config(configuration)
    obs = _working_observation(observation, cfg)
    player = obs["player"]
    if not 0 <= player < len(obs["farms"]):
        return []
    farm = obs["farms"][player]
    money = float(farm["money"])
    shed = obs["private"]["shed"]
    room = max(0, int(cfg["shedCapacity"]) - sum(max(0, int(n)) for n in shed.values()))
    orders: list[list[Any]] = []

    for crop in CROPS:
        maximum = int(money // int(CROP_RULES[crop]["seed"]))
        orders.extend([["BUY_SEED", crop, quantity] for quantity in range(1, maximum + 1)])

    params = _resolved_market_params(cfg)
    for item in BUYABLE_PRODUCTS:
        maximum = _max_affordable_product_quantity(
            item,
            money,
            room,
            int(obs["market"]["inventory"][item]),
            params,
        )
        orders.extend([["BUY_PRODUCT", item, quantity] for quantity in range(1, maximum + 1)])

    for animal in ANIMALS:
        maximum = min(room, int(money // int(ANIMAL_RULES[animal]["cost"])))
        orders.extend([["BUY_ANIMAL", animal, quantity] for quantity in range(1, maximum + 1)])

    for item in PRODUCTS:
        maximum = max(0, int(shed.get(item, 0)))
        orders.extend([["SELL", item, quantity] for quantity in range(1, maximum + 1)])

    hire_cost = int(cfg["farmHandCostMult"]) * _fib(int(farm["hires_today"]))
    if money >= hire_cost:
        orders.append(["HIRE"])
    extra_unlocked = max(0, len(farm["unlocked_quadrants"]) - 1)
    if extra_unlocked < len(LAND_PRICES) and money >= LAND_PRICES[extra_unlocked]:
        orders.append(["BUY_LAND"])
    return orders


def legal_action_factors(
    observation: Mapping[str, Any] | Any,
    configuration: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    """Return the complete factorized legal space for all current decision makers."""
    cfg = _config(configuration)
    obs = _working_observation(observation, cfg)
    player = obs["player"]
    hand_count = len(obs["farms"][player]["hands"]) if 0 <= player < 2 else 0
    return {
        "farmer": legal_unit_actions(obs, 0, cfg),
        "hands": [legal_unit_actions(obs, index + 1, cfg) for index in range(hand_count)],
        "market": legal_market_actions(obs, cfg),
    }


def legal_action_candidates(
    observation: Mapping[str, Any] | Any,
    configuration: Mapping[str, Any] | Any | None = None,
) -> list[dict[str, Any]]:
    """Build scorer-ready full actions for every atomic legal factor choice.

    The official joint space is a Cartesian product (and the market component is
    an ordered queue), so materializing every joint action is intractable. These
    candidates cover every legal atomic choice while all other factors PASS.
    Agents can compose several selected factors and call :func:`sanitize_action`.
    """
    factors = legal_action_factors(observation, configuration)
    hand_count = len(factors["hands"])
    baseline = {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(hand_count)], "market": []}
    candidates = [copy.deepcopy(baseline)]
    for action in factors["farmer"]:
        if action != ["PASS"]:
            candidate = copy.deepcopy(baseline)
            candidate["farmer"] = action
            candidates.append(candidate)
    for hand_index, choices in enumerate(factors["hands"]):
        for action in choices:
            if action != ["PASS"]:
                candidate = copy.deepcopy(baseline)
                candidate["hands"][hand_index] = action
                candidates.append(candidate)
    for order in factors["market"]:
        candidate = copy.deepcopy(baseline)
        candidate["market"] = [order]
        candidates.append(candidate)
    return candidates


def _part_key(part: Sequence[Any]) -> tuple[Any, ...]:
    result = list(part)
    if result and result[0] in {"PICKUP", "PLACE"} and len(result) == 2:
        result.append(1)
    return tuple(result)


def _sanitize_market(
    orders: list[list[Any]],
    obs: Mapping[str, Any],
    cfg: Mapping[str, Any],
) -> list[list[Any]]:
    player = obs["player"]
    farm = obs["farms"][player]
    money = float(farm["money"])
    hires = int(farm["hires_today"])
    unlocked = len(farm["unlocked_quadrants"])
    shed = dict(obs["private"]["shed"])
    seeds = dict(obs["private"]["seeds"])
    market_inventory = dict(obs["market"]["inventory"])
    params = _resolved_market_params(cfg)
    capacity = int(cfg["shedCapacity"])
    output: list[list[Any]] = []

    for raw in orders[: max(1, int(cfg["maxMarketOrdersPerTurn"]))]:
        if not raw:
            continue
        op = raw[0]
        if op == "HIRE":
            cost = int(cfg["farmHandCostMult"]) * _fib(hires)
            if money >= cost:
                money -= cost
                hires += 1
                output.append(["HIRE"])
            continue
        if op == "BUY_LAND":
            extra = unlocked - 1
            if extra < len(LAND_PRICES) and money >= LAND_PRICES[extra]:
                money -= LAND_PRICES[extra]
                unlocked += 1
                output.append(["BUY_LAND"])
            continue
        if len(raw) < 3:
            continue
        try:
            requested = int(raw[2])
        except (TypeError, ValueError):
            continue
        if requested <= 0:
            continue
        item = raw[1]
        accepted = 0
        if op == "SELL" and item in PRODUCTS:
            accepted = min(requested, max(0, int(shed.get(item, 0))))
            if accepted:
                for _ in range(accepted):
                    price = _market_price(item, market_inventory[item], params)
                    money += price
                    shed[item] -= 1
                    # The official engine does not add $1-floor sales to supply.
                    if price > 1:
                        market_inventory[item] += 1
        elif op == "BUY_SEED" and item in CROPS:
            cost = int(CROP_RULES[item]["seed"])
            accepted = min(requested, int(money // cost))
            if accepted:
                money -= accepted * cost
                seeds[item] += accepted
        elif op == "BUY_ANIMAL" and item in ANIMALS:
            cost = int(ANIMAL_RULES[item]["cost"])
            room = max(0, capacity - sum(shed.values()))
            accepted = min(requested, room, int(money // cost))
            if accepted:
                money -= accepted * cost
                shed[item] += accepted
        elif op == "BUY_PRODUCT" and item in BUYABLE_PRODUCTS:
            room = max(0, capacity - sum(shed.values()))
            for _ in range(min(requested, room)):
                price = _market_price(item, market_inventory[item] - 1, params)
                if money < price:
                    break
                money -= price
                market_inventory[item] -= 1
                shed[item] += 1
                accepted += 1
        if accepted:
            output.append([op, item, accepted])
    return output


def sanitize_action(
    action: Any,
    observation: Mapping[str, Any] | Any,
    configuration: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    """Sanitize one joint turn in the official farmer -> hands -> market order."""
    cfg = _config(configuration)
    obs = _working_observation(observation, cfg)
    canonical = canonicalize_action(action)
    player = int(obs["player"])
    hand_count = (
        len(obs["farms"][player]["hands"])
        if 0 <= player < 2
        else 0
    )

    unit_parts = [canonical["farmer"]] + canonical["hands"][:hand_count]
    unit_parts.extend([["PASS"]] * (1 + hand_count - len(unit_parts)))

    # Market-only candidates dominate the scorer's action set. They need no
    # mutable unit simulation, so retain the complete live view directly.
    if all(part == ["PASS"] for part in unit_parts):
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in range(hand_count)],
            "market": _sanitize_market(canonical["market"], obs, cfg),
        }

    simulation = normalize_observation(obs, cfg)

    # Match the interpreter's atomic pre-pass: an over-requested crop is blocked
    # for every unit before any farmer or hand action is applied.
    plant_counts: dict[str, int] = {}
    for part in unit_parts:
        if len(part) >= 2 and part[0] == "PLANT":
            plant_counts[part[1]] = plant_counts.get(part[1], 0) + 1
    blocked = {
        crop
        for crop, count in plant_counts.items()
        if count > int(simulation["private"]["seeds"].get(crop, 0))
    }

    # Reuse the exact 1.32.7 transition function after choosing each currently
    # legal factor. This matters whenever units share a tile or shed inventory.
    from kaggle_environments.envs.kaggriculture.kaggriculture import (
        _apply_unit_action,
    )

    farm = simulation["farms"][player]
    private = simulation["private"]
    sanitized_units: list[list[Any]] = []
    for index, part in enumerate(unit_parts):
        if len(part) >= 2 and part[0] == "PLANT" and part[1] in blocked:
            selected = ["PASS"]
        else:
            legal = legal_unit_actions(simulation, index, cfg)
            lookup = {_part_key(candidate): candidate for candidate in legal}
            selected = copy.deepcopy(lookup.get(_part_key(part), ["PASS"]))
        sanitized_units.append(selected)
        _apply_unit_action(
            farm,
            private,
            index,
            selected,
            int(cfg["boardSize"]),
            int(simulation["day"]),
            max(1, int(cfg["turnsPerDay"])),
            int(cfg["shedCapacity"]),
        )

    return {
        "farmer": sanitized_units[0],
        "hands": sanitized_units[1:],
        "market": _sanitize_market(canonical["market"], simulation, cfg),
    }


def is_action_legal(
    action: Any,
    observation: Mapping[str, Any] | Any,
    configuration: Mapping[str, Any] | Any | None = None,
) -> bool:
    """Return whether the structured action is canonical, effectful, and state-legal."""
    canonical = canonicalize_action(action)
    cfg = _config(configuration)
    obs = _working_observation(observation, cfg)
    player = int(obs["player"])
    hand_count = len(obs["farms"][player]["hands"]) if 0 <= player < 2 else 0
    canonical["hands"].extend(
        [["PASS"]] * max(0, hand_count - len(canonical["hands"]))
    )

    def semantic(value: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            _part_key(value["farmer"]),
            tuple(_part_key(part) for part in value["hands"]),
            tuple(_part_key(order) for order in value["market"]),
        )

    return semantic(canonical) == semantic(sanitize_action(canonical, obs, cfg))


complete_legal_candidates = legal_action_factors


__all__ = [
    "ANIMALS",
    "ANIMAL_RULES",
    "BUYABLE_PRODUCTS",
    "CROPS",
    "CROP_RULES",
    "DEFAULT_ACTION",
    "DEFAULT_CONFIGURATION",
    "MARKET_OPS",
    "PRODUCTS",
    "SHOP_NAMES",
    "STORAGE_ITEMS",
    "UNIT_OPS",
    "canonicalize_action",
    "complete_legal_candidates",
    "decode_action",
    "encode_action",
    "is_action_legal",
    "legal_action_candidates",
    "legal_action_factors",
    "legal_market_actions",
    "legal_unit_actions",
    "normalize_observation",
    "sanitize_action",
]
