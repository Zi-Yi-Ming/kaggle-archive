# -*- coding: utf-8 -*-
"""P35-B: phase-skeleton trajectory compiler (not a tape).

Phases from P34 landmarks. Goals per phase; executor realizes actions.
Falsification: random landmark timing control.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))

from p10_executor.validators import sanitize_action  # noqa: E402

ANIMALS = ("COW", "SHEEP", "GOOSE")
ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)


def _fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


class SkeletonAgent:
    """Phase goals → market orders; workers via p11 stack.

    mode:
      'normal'  — P34 landmark schedule
      'random'  — shuffle landmark days (falsification)
      'landmark_only' — same as normal but no extra sell boost
    """

    def __init__(self, mode="normal", shift=0):
        self.mode = mode
        self.shift = shift  # random landmark offset
        from p11_planner import planner as pmod
        self._pmod = pmod
        self._planner = None
        # landmark days (P34); shift for falsification
        self.LM = {
            "animals8": 6 + shift,
            "sell2k": 6 + shift,
            "cash5k": 10 + shift,
            "melon10": 10 + shift,
            "cash20k": 12 + shift,
            "end": 29,
        }

    def phase(self, day, money, animals, melon):
        lm = self.LM
        if day < 1:
            return "BOOT"
        if animals < 8 and day <= lm["animals8"] + 2:
            return "EXPAND"
        if money < 5000 and day <= lm["cash5k"] + 3:
            return "CONVERT"
        if money < 20000 and day <= lm["cash20k"] + 5:
            return "SCALE"
        if day < 26:
            return "MONETIZE"
        return "END"

    def act(self, observation, configuration=None):
        obs = observation or {}
        if self._planner is None:
            self._planner = self._pmod.StrategicPlanner()
        base = self._planner.act(obs)
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

        animals = 0
        melon = 0
        empty = 0
        plants = 0
        live = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
        for row in tiles:
            for t in row:
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        plants += 1
                        if t.get("crop") == "MELON":
                            melon += 1
                    if t.get("animal"):
                        animals += 1
                        if t.get("animal") in live:
                            live[t["animal"]] += 1

        ph = self.phase(day, money, animals, melon)
        market = []

        def add(o):
            if len(market) < 10:
                market.append(o)

        cash = money
        # HIRE at dawn always (R2-like structural constraint)
        if hour == 0:
            n_hire = 0
            while n_hire < 10:
                cost = _fib(hires_today + n_hire)
                if cash < cost + 10:
                    break
                add(["HIRE"])
                cash -= cost
                n_hire += 1

        if ph == "BOOT" and day == 0:
            # long crop + initial livestock
            if hour == 0:
                if cash >= 80:
                    add(["BUY_SEED", "MELON", 8])
                    cash -= 640
                if cash >= 100:
                    add(["BUY_SEED", "WHEAT", 6])
                    cash -= 60
                for a in ("COW", "SHEEP"):
                    if cash >= ANIMAL_COST[a] + 50:
                        add(["BUY_ANIMAL", a, 2])
                        cash -= ANIMAL_COST[a] * 2
        elif ph == "EXPAND":
            if hour == 0:
                # animals toward 8
                for a in ("COW", "SHEEP", "GOOSE"):
                    gap = {"COW": 8, "SHEEP": 6, "GOOSE": 3}[a] - live[a] - int(shed.get(a) or 0)
                    can = min(gap, 2, int(max(0.0, cash - 80) // ANIMAL_COST[a]))
                    for _ in range(can):
                        add(["BUY_ANIMAL", a, 1])
                        cash -= ANIMAL_COST[a]
                if empty > 2 and cash >= 40:
                    add(["BUY_SEED", "WHEAT", 4])
                    cash -= 40
        elif ph in ("CONVERT", "SCALE", "MONETIZE"):
            if hour == 0 or (self.mode != "landmark_only" and hour == 12 and day >= self.LM["cash5k"]):
                # sell products
                for item in PRODUCTS:
                    q = int(shed.get(item) or 0)
                    if q <= 0:
                        continue
                    if item == "WHEAT" and q <= 4:
                        continue
                    add(["SELL", item, q])
                # more animals if rich
                if money > 3000 and hour == 0:
                    for a in ("COW", "SHEEP", "GOOSE"):
                        gap = {"COW": 8, "SHEEP": 6, "GOOSE": 3}[a] - live[a] - int(shed.get(a) or 0)
                        can = min(gap, 1, int(max(0.0, cash - 100) // ANIMAL_COST[a]))
                        for _ in range(can):
                            add(["BUY_ANIMAL", a, 1])
                            cash -= ANIMAL_COST[a]
        elif ph == "END":
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q > 0:
                    add(["SELL", item, q])

        action = dict(base or {})
        # put skeleton market first
        action["market"] = (market + list(action.get("market") or []))[:10]
        return sanitize_action(
            action, shed=shed, money=money, prices=prices,
        )


_SKELETON = None


def make_agent(mode="normal", shift=0):
    global _SKELETON
    _SKELETON = SkeletonAgent(mode=mode, shift=shift)
    return _SKELETON.act


def reset():
    global _SKELETON
    _SKELETON = None
