# -*- coding: utf-8 -*-
"""Tactical executor: intent → validated action. No 720-step tape."""
from __future__ import annotations

from .intents import Intent, Status, ExecutorResult, PASS_ACTION
from .primitives import (
    DayState,
    repair_weeds,
    projected_shed,
    advance_sales,
    subtract_advanced_sales,
    liquidate,
    recover_action,
)
from .validators import sanitize_action, PRODUCTS


def _beside_shed(pos, board=10):
    c = board // 2
    return (pos[0], pos[1]) in ((c - 1, c - 1), (c, c - 1), (c - 1, c), (c, c))


class TacticalExecutor:
    def __init__(self):
        self.state = DayState()

    def reset(self):
        self.state = DayState()

    def step(self, observation, intent, planned_next_sells=None):
        """Execute one intent against current observation.

        Returns ExecutorResult. Never emits sell>stock or invalid farmer ops.
        """
        try:
            obs = observation or {}
            step = int(obs.get("step") or 0)
            player = int(obs.get("player") or 0)
            farms = obs.get("farms") or []
            if player >= len(farms):
                return ExecutorResult(PASS_ACTION, Status.BLOCKED, reason="no_farm")
            farm = farms[player] or {}
            private = obs.get("private") or {}
            shed = dict(private.get("shed") or {})
            inventories = list(private.get("inventories") or [])
            prices = dict((obs.get("market") or {}).get("prices") or {})
            money = float(farm.get("money") or 0)
            positions = [farm.get("farmer") or [4, 4], *(farm.get("hands") or [])]
            tiles = farm.get("tiles") or []
            repairs = []

            # build base action from intent
            if intent == Intent.NOOP:
                base = dict(PASS_ACTION)
                status = Status.NOOP
                reason = "noop_intent"
            elif intent == Intent.CLEAR_WEED:
                base = {"farmer": ["DIG"], "hands": [], "market": []}
                status = Status.SUCCESS
                reason = "clear_weed"
            elif intent == Intent.LIQUIDATE:
                base = liquidate(positions, shed, inventories, prices, _beside_shed)
                status = Status.SUCCESS
                reason = "liquidate"
            elif intent == Intent.SELL_AVAILABLE:
                market = []
                for item in PRODUCTS:
                    q = int(shed.get(item) or 0)
                    if q > 0 and len(market) < 10:
                        market.append(["SELL", item, q])
                base = {"farmer": ["PASS"], "hands": [], "market": market}
                status = Status.SUCCESS
                reason = "sell_available"
            elif intent == Intent.RECOVER:
                # sell anything with stock; no buys
                market = []
                for item in PRODUCTS:
                    q = int(shed.get(item) or 0)
                    if q > 0 and len(market) < 10:
                        market.append(["SELL", item, q])
                base = {"farmer": ["PASS"], "hands": [], "market": market}
                status = Status.REPAIRED
                repairs.append("recover_sell_all")
                reason = "recover"
            else:
                # MAINTAIN_PRODUCTION: no-op units; optional wheat buy if cash
                market = []
                if money >= 50 and int((private.get("seeds") or {}).get("WHEAT") or 0) < 5:
                    market.append(["BUY_SEED", "WHEAT", 3])
                base = {"farmer": ["PASS"], "hands": [], "market": market}
                status = Status.SUCCESS
                reason = "maintain"

            # P1 weed repair
            base = repair_weeds(base, positions, tiles, self.state, step)
            if any(c == ["DIG"] for c in [base.get("farmer")] + list(base.get("hands") or [])):
                repairs.append("weed_dig")

            # P3 advance sales (if caller provides planned next sells)
            if planned_next_sells and intent not in (Intent.LIQUIDATE, Intent.RECOVER):
                stock = projected_shed(base, positions, tiles, shed, inventories, _beside_shed)
                base = advance_sales(base, stock, prices, planned_next_sells, self.state, step)
                if self.state.advanced_sales:
                    repairs.append("advance_sell")

            # subtract if due
            base = subtract_advanced_sales(base, self.state, step)

            # P5 validate / recover
            before = base
            base = sanitize_action(base, shed=shed, money=money, prices=prices)
            if before.get("market") != base.get("market"):
                repairs.append("market_clamp")
                if status == Status.SUCCESS and intent == Intent.SELL_AVAILABLE:
                    status = Status.REPAIRED

            return ExecutorResult(base, status, repairs, reason, {
                "step": step, "intent": intent.value if hasattr(intent, "value") else intent,
            })
        except Exception as e:
            return ExecutorResult(PASS_ACTION, Status.FAILED, reason=str(e))
