# -*- coding: utf-8 -*-
"""Tactical primitives extracted from R2 (no 720-tape)."""
from __future__ import annotations

from collections import deque

from .intents import Intent, Status, ExecutorResult, PASS_ACTION
from .validators import PRODUCTS, sanitize_action, MAX_ORDERS

WEED_BLOCKED = {"PLANT", "BUILD_COOP", "BUILD_PASTURE"}


class DayState:
    def __init__(self):
        self.day = -1
        self.queues = {}
        self.sale_due_step = -1
        self.advanced_sales = {}


def repair_weeds(action, positions, tiles, state, step):
    """P1: DIG if standing on WEED and command blocked; queue original."""
    day = step // 24
    if day != state.day:
        state.day = day
        state.queues.clear()
    workers = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    for w in range(min(len(workers), len(positions))):
        queue = state.queues.setdefault(w, deque())
        queue.append(list(workers[w]))
        x, y = positions[w]
        try:
            tile = tiles[y][x]
        except Exception:
            tile = None
        blocked = (queue[0][0] in WEED_BLOCKED and isinstance(tile, dict) and tile.get("kind") == "WEED")
        workers[w] = ["DIG"] if blocked else queue.popleft()
    action = dict(action)
    action["farmer"] = workers[0]
    action["hands"] = workers[1:]
    return action


def projected_shed(action, positions, tiles, shed, inventories, beside_shed):
    """P2: stock after nearby PICKUP/DROP/PLACE."""
    stock = dict(shed or {})
    total = sum(stock.values())
    workers = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    for w in range(min(len(workers), len(positions))):
        if not beside_shed(positions[w]):
            continue
        work = workers[w]
        op = work[0] if work else "PASS"
        inv = inventories[w] if w < len(inventories) else {}
        if op == "PICKUP" and len(work) >= 2 and work[1] in stock:
            q = max(0, int(work[2]) if len(work) >= 3 else 1)
            take = min(stock[work[1]], q)
            stock[work[1]] -= take
            total -= take
        elif op == "DROP":
            for item, held in (inv or {}).items():
                add = min(max(0, int(held)), max(0, 100 - total))
                if add > 0:
                    stock[item] = stock.get(item, 0) + add
                    total += add
        elif op == "PLACE" and len(work) >= 2 and work[1] not in ("GOOSE", "COW", "SHEEP"):
            item = work[1]
            q = max(0, int(work[2]) if len(work) >= 3 else 1)
            add = min(q, max(0, int((inv or {}).get(item, 0))), max(0, 100 - total))
            if add > 0:
                stock[item] = stock.get(item, 0) + add
                total += add
    return stock


def advance_sales(action, stock, prices, planned_next_sells, state, step):
    """P3: pull next-turn sells forward (skip WHEAT/FERT; price>=2)."""
    if step >= 718 or step % 72 == 0 or (step % 4 == 0 and step < 144):
        return action
    already = {o[1] for o in action.get("market") or []
               if o and o[0] == "SELL" and len(o) > 1}
    market = [list(o) for o in action.get("market") or []]
    for item in PRODUCTS:
        if item in ("WHEAT", "FERTILIZER") or item in already:
            continue
        planned = int((planned_next_sells or {}).get(item) or 0)
        have = int(stock.get(item) or 0)
        q = min(have, planned)
        if q <= 0 or int((prices or {}).get(item) or 0) < 2:
            continue
        if len(market) >= MAX_ORDERS:
            break
        market.append(["SELL", item, q])
        state.advanced_sales[item] = q
    if state.advanced_sales:
        state.sale_due_step = step + 1
    action = dict(action)
    action["market"] = market
    return action


def subtract_advanced_sales(action, state, step):
    if state.sale_due_step == step:
        remaining = dict(state.advanced_sales)
        market = []
        for o in action.get("market") or []:
            o = list(o)
            if o and o[0] == "SELL" and len(o) >= 3:
                item = o[1]
                rem = min(max(0, int(o[2])), remaining.get(item, 0))
                if rem > 0:
                    o[2] = int(o[2]) - rem
                    remaining[item] -= rem
            market.append(o)
        action = dict(action)
        action["market"] = market
    state.advanced_sales = {}
    state.sale_due_step = -1
    return action


def liquidate(positions, shed, inventories, prices, beside_shed):
    """P4: DROP + sell projected stock, premium value first."""
    workers = [["DROP"] if beside_shed(p) else ["PASS"] for p in positions]
    action = {"farmer": workers[0], "hands": workers[1:], "market": []}
    stock = projected_shed(action, positions, None, shed, inventories, beside_shed)
    sells = []
    for item in PRODUCTS:
        q = int(stock.get(item) or 0)
        if q > 0:
            sells.append(["SELL", item, q])
    sells.sort(key=lambda o: -int((prices or {}).get(o[1]) or 1) * o[2])
    action["market"] = sells[:MAX_ORDERS]
    return action


def classify_failure(action, shed, money):
    """P5: classify why an action might fail."""
    issues = []
    for o in action.get("market") or []:
        if not o:
            continue
        if o[0] == "SELL" and len(o) >= 3:
            if int(shed.get(o[1]) or 0) < int(o[2] or 0):
                issues.append(("EMPTY_STOCK", o[1]))
        if o[0] == "BUY_PRODUCT" and len(o) >= 3:
            # unknown price → flag as CASH_RISK if money tiny
            if money < 50:
                issues.append(("LOW_CASH", o[1]))
    return issues


def recover_action(action, shed, money, prices):
    """P5: drop illegal market legs; keep valid prefix."""
    return sanitize_action(action, shed=shed, money=money, prices=prices)
