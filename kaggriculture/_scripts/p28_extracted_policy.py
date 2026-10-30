# -*- coding: utf-8 -*-
"""P28 extracted action-bundle policy (from R2 trajectories, not tape).

Rules mined from p28_r2_trajectories.csv:
  - Every day hour==0: HIRE as many as cash allows (workers reset overnight)
  - Hour 0-2: SELL shed products (keep small wheat for feed)
  - BUY_ANIMAL when cash allows and below elite-ish cap
  - BUY_SEED when empty tiles exist
  - Workers: existing p11 production stack (water/feed/harvest/plant)

Not a 720-step tape. State-driven.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from p10_executor.validators import sanitize_action  # noqa: E402

ANIMALS = ("COW", "SHEEP", "GOOSE")
ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
# extracted targets from R2 day-boundary (not copied schedule)
ANIMAL_CAP = {"COW": 8, "SHEEP": 6, "GOOSE": 3}


def _fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


class ExtractedPolicy:
    def __init__(self):
        from p11_planner import planner as pmod
        self._pmod = pmod
        self._planner = None

    def _base_workers(self, obs):
        if self._planner is None:
            self._planner = self._pmod.StrategicPlanner()
        # reuse worker micro-policy via planner but we'll override market
        return self._planner.act(obs)

    def act(self, observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        day = step // 24
        hour = step % 24
        player = int(obs.get("player") or 0)
        farm = (obs.get("farms") or [])[player]
        private = obs.get("private") or {}
        shed = dict(private.get("shed") or {})
        prices = dict((obs.get("market") or {}).get("prices") or {})
        money = float(farm.get("money") or 0)
        tiles = farm.get("tiles") or []
        hires_today = int(farm.get("hires_today") or 0)

        # base action from B planner (workers + weeds)
        action = self._base_workers(obs)
        market = []

        if hour == 0:
            # R2 rule: HIRE burst at dawn
            cash = money
            n_hire = 0
            while n_hire < 10:
                cost = _fib(hires_today + n_hire)
                if cash < cost + 5:
                    break
                market.append(["HIRE"])
                cash -= cost
                n_hire += 1

            # SELL products except wheat buffer
            wheat_hold = 4
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q <= 0:
                    continue
                if item == "WHEAT":
                    q = max(0, q - wheat_hold)
                    if q <= 0:
                        continue
                if len(market) >= 10:
                    break
                market.append(["SELL", item, q])

            # BUY_ANIMAL if under cap and cash left
            live = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
            for row in tiles:
                for t in row:
                    if isinstance(t, dict) and t.get("animal") in live:
                        live[t["animal"]] += 1
            for a in ("COW", "SHEEP", "GOOSE"):
                gap = ANIMAL_CAP[a] - live[a] - int(shed.get(a) or 0)
                if gap <= 0 or len(market) >= 10:
                    continue
                cost = ANIMAL_COST[a]
                can = min(gap, 2, int(max(0.0, cash - 80) // cost))
                for _ in range(can):
                    if len(market) >= 10:
                        break
                    market.append(["BUY_ANIMAL", a, 1])
                    cash -= cost

            # BUY_SEED wheat if empty tiles
            empty = sum(1 for row in tiles for t in row if t is None)
            if empty > 2 and cash >= 40 and len(market) < 10:
                market.append(["BUY_SEED", "WHEAT", 4])
                cash -= 40

        # merge: extracted market first, then keep worker cmds from base
        action = dict(action or {})
        action["market"] = (market + list(action.get("market") or []))[:10]
        return sanitize_action(
            action,
            shed=shed,
            money=money,
            prices=prices,
        )


_EXTRACTED = None


def agent(observation, configuration=None):
    global _EXTRACTED
    if _EXTRACTED is None:
        _EXTRACTED = ExtractedPolicy()
    return _EXTRACTED.act(observation, configuration)


def reset():
    global _EXTRACTED
    _EXTRACTED = None
