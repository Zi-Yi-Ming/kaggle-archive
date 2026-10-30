# -*- coding: utf-8 -*-
"""B0 = P11 as-is. B1 = P11 + daily_labor primitive (single intervention)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from p12_primitives.daily_labor import daily_labor_orders, labor_reserve  # noqa: E402

EXPENSIVE = {"BUY_LAND", "BUY_ANIMAL"}


def make_b1_agent():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    base = pmod.agent

    def agent(obs, configuration=None):
        action = base(obs, configuration) or {"farmer": ["PASS"], "hands": [], "market": []}
        step = int(obs.get("step") or 0)
        hour = step % 24
        if hour != 0:
            return action
        player = int(obs.get("player") or 0)
        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        money = float(farm.get("money") or 0)
        hires_today = int(farm.get("hires_today") or 0)
        unlocked = list(farm.get("unlocked_quadrants") or ["NW"])

        labor, target = daily_labor_orders(obs)
        market = list(action.get("market") or [])

        # Drop expensive buys that would break today's labor reserve
        want_hire = max(0, target - hires_today)
        reserve = labor_reserve(hires_today, want_hire) + 40
        # keep labor orders; strip land/animal if money tight after labor
        kept = []
        spent_est = 0
        for o in market:
            if o and o[0] in EXPENSIVE:
                continue  # B1 single-variable: labor wins over expansion at dawn
            if o and o[0] == "HIRE":
                continue  # replaced by primitive
            kept.append(o)

        # put labor first (sells then hires), then other non-hire orders
        new_market = list(labor)
        for o in kept:
            if len(new_market) >= 10:
                break
            new_market.append(o)
        action = dict(action)
        action["market"] = new_market[:10]
        return action

    return agent


def make_b0_agent():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent
