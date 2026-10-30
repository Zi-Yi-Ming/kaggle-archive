# -*- coding: utf-8 -*-
"""Safety validators — never emit known-illegal actions."""
from __future__ import annotations

PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
ANIMALS = ("GOOSE", "COW", "SHEEP")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
MAX_ORDERS = 10
SHED_CAP = 100


def clamp_market(market, shed, money, prices=None):
    """Drop/trim illegal SELL and BUY orders. Preserve relative order."""
    if not market:
        return []
    stock = dict(shed or {})
    cash = float(money or 0)
    out = []
    for o in market:
        if not o or not isinstance(o, list):
            continue
        op = o[0]
        if op == "SELL" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            if item not in PRODUCTS or q <= 0:
                continue
            have = int(stock.get(item) or 0)
            q = min(q, have)
            if q <= 0:
                continue
            stock[item] = have - q
            out.append(["SELL", item, q])
        elif op == "BUY_PRODUCT" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            if item not in ("WHEAT", "FERTILIZER") or q <= 0:
                continue
            px = int((prices or {}).get(item) or 0) or 1
            # approximate: cannot spend more than cash
            afford = int(cash // max(1, px))
            q = min(q, afford)
            total = sum(stock.values())
            room = max(0, SHED_CAP - total)
            q = min(q, room)
            if q <= 0:
                continue
            cash -= q * px
            stock[item] = stock.get(item, 0) + q
            out.append(["BUY_PRODUCT", item, q])
        elif op == "BUY_ANIMAL" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            if item not in ANIMALS or q <= 0:
                continue
            cost = {"GOOSE": 300, "COW": 400, "SHEEP": 500}[item]
            afford = int(cash // cost)
            q = min(q, afford)
            total = sum(stock.values())
            room = max(0, SHED_CAP - total)
            q = min(q, room)
            if q <= 0:
                continue
            cash -= q * cost
            stock[item] = stock.get(item, 0) + q
            out.append(["BUY_ANIMAL", item, q])
        elif op == "BUY_SEED" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            if item not in CROPS or q <= 0:
                continue
            cost = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}[item]
            afford = int(cash // cost)
            q = min(q, afford)
            if q <= 0:
                continue
            cash -= q * cost
            out.append(["BUY_SEED", item, q])
        elif op in ("HIRE", "BUY_LAND"):
            out.append([op])
        if len(out) >= MAX_ORDERS:
            break
    return out[:MAX_ORDERS]


def validate_farmer(cmd):
    """Return sanitized farmer command or PASS."""
    if not cmd or not isinstance(cmd, list) or not cmd:
        return ["PASS"]
    op = cmd[0]
    if op in ("NORTH", "SOUTH", "EAST", "WEST", "PASS", "WATER", "HARVEST", "FEED", "CARE",
              "DIG", "COLLECT_FERTILIZER", "FERTILIZE", "BUILD_COOP", "BUILD_PASTURE", "DROP"):
        return list(cmd)
    if op == "PLANT" and len(cmd) >= 2 and cmd[1] in CROPS:
        return list(cmd)
    if op in ("PICKUP", "PLACE") and len(cmd) >= 2:
        return list(cmd)
    return ["PASS"]


def sanitize_action(action, shed=None, money=0, prices=None):
    """Full safety pass: clamp market + farmer + hands."""
    if not isinstance(action, dict):
        action = dict()
    market = clamp_market(action.get("market"), shed, money, prices)
    farmer = validate_farmer(action.get("farmer"))
    hands = []
    for h in action.get("hands") or []:
        hands.append(validate_farmer(h))
    return {"farmer": farmer, "hands": hands, "market": market}
