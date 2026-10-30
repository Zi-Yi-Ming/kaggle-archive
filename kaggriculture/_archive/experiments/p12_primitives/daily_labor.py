# -*- coding: utf-8 -*-
"""Daily labor primitive.

Evidence (P12 traces): after d5-d8 P11 cash collapses, hour-0 HIRE fails,
hands=0 at d10, no production/sales, death spiral to ~$0 while R2 compounds
+$6-10k/day.

Mechanism (state-driven, not a tape):
1. Compute cost to hire `target_hands` this morning (fib ladder).
2. If cash < reserve, SELL shed products (premium first) to fund labor.
3. Emit HIRE up to target while cash covers next fib cost.
4. Never allow other purchases to break the labor reserve.

Planner independence: caller passes target_hands; may pass 0 to disable.
"""
from __future__ import annotations

PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
MAX_ORDERS = 10


def fib(n: int) -> int:
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def labor_reserve(hires_today: int, want: int) -> int:
    """Cash needed to hire `want` more hands given hires already done today."""
    return sum(fib(hires_today + i) for i in range(max(0, want)))


def target_hands_for_day(day: int, money: float, n_land: int) -> int:
    """State-driven daily crew size. Not a fixed schedule — scales with land/cash."""
    if money < 50:
        return 0
    base = 6 if day <= 3 else (8 if day <= 8 else 9)
    if n_land >= 3 and day >= 12:
        base = 10
    # if chronically poor, keep a skeleton crew only
    if money < 200:
        return min(base, 3)
    if money < 400:
        return min(base, 5)
    return base


def daily_labor_orders(obs, target_hands: int | None = None, hold_wheat: int = 2):
    """Return market orders for dawn labor: optional SELL to fund + HIRE.

    Caller merges these into the action market list (before other buys).
    Only intended for hour==0 (or when hires_today==0 and hands are gone).
    """
    player = int(obs.get("player") or 0)
    step = int(obs.get("step") or 0)
    hour = step % 24
    day = step // 24
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    money = float(farm.get("money") or 0)
    hires_today = int(farm.get("hires_today") or 0)
    hands = farm.get("hands") or []
    unlocked = list(farm.get("unlocked_quadrants") or ["NW"])

    if hour != 0:
        return [], target_hands_for_day(day, money, len(unlocked))

    if target_hands is None:
        target_hands = target_hands_for_day(day, money, len(unlocked))
    # already have crew from earlier hour-0 hires this morning
    already = hires_today
    want = max(0, target_hands - already)
    if want <= 0:
        return [], target_hands

    need = labor_reserve(hires_today, want)
    # Also keep a tiny operating cushion
    cushion = 30 if day < 8 else 80
    shortfall = max(0.0, (need + cushion) - money)

    orders = []
    # Sell products (not wheat feed buffer) to fund labor — premium first
    if shortfall > 0:
        items = []
        for item in PRODUCTS:
            q = int(shed.get(item) or 0)
            if q <= 0:
                continue
            if item == "WHEAT":
                q = max(0, q - hold_wheat)
                if q <= 0:
                    continue
            px = int(prices.get(item) or 1)
            items.append((px * q, item, q, px))
        items.sort(reverse=True)
        raised = 0.0
        for _, item, q, px in items:
            if raised >= shortfall:
                break
            orders.append(["SELL", item, q])
            raised += q * px
            if len(orders) >= MAX_ORDERS - 1:
                break

    # HIRE while affordable (after planned sells — optimistic; engine clamps)
    projected_cash = money
    # estimate sell proceeds
    for o in orders:
        if o and o[0] == "SELL" and len(o) >= 3:
            projected_cash += int(o[2]) * int(prices.get(o[1]) or 1)

    hired = 0
    for i in range(want):
        cost = fib(hires_today + hired)
        if projected_cash < cost + (cushion if hired == 0 else 5):
            break
        if len(orders) >= MAX_ORDERS:
            break
        orders.append(["HIRE"])
        projected_cash -= cost
        hired += 1

    return orders, target_hands
