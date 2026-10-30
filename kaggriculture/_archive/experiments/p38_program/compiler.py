# -*- coding: utf-8 -*-
"""P38 v2: discrete program compiler. Market = grammar; workers = p11 tactical."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from p10_executor.validators import sanitize_action  # noqa: E402

ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)


def _fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def program_hash(prog: dict) -> str:
    return hashlib.md5(json.dumps(prog, sort_keys=True).encode()).hexdigest()[:12]


# Discrete grammar (search vocabulary — not elite module copies)
OPENING = {
    "melon_pack": {
        "seeds": (("MELON", 12), ("WHEAT", 7)),
        "animals": (("COW", 2), ("SHEEP", 2)),
    },
    "melon_lean": {
        "seeds": (("MELON", 8), ("WHEAT", 8)),
        "animals": (("COW", 2), ("SHEEP", 1)),
    },
    "animal_pack": {
        "seeds": (("WHEAT", 12), ("MELON", 4)),
        "animals": (("COW", 3), ("SHEEP", 3)),
    },
    "straw_open": {
        "seeds": (("STRAWBERRY", 6), ("WHEAT", 8), ("MELON", 4)),
        "animals": (("COW", 2), ("SHEEP", 2)),
    },
    "wheat_flood": {
        "seeds": (("WHEAT", 16),),
        "animals": (("COW", 2), ("SHEEP", 2), ("GOOSE", 1)),
    },
}

MID_CROP = {
    "straw_heavy": ("STRAWBERRY", "WHEAT", "TOMATO", "CARROT", "MELON"),
    "tomato_heavy": ("TOMATO", "STRAWBERRY", "WHEAT", "CARROT", "MELON"),
    "wheat_animal": ("WHEAT", "CARROT", "STRAWBERRY", "TOMATO", "MELON"),
    "mixed": ("STRAWBERRY", "TOMATO", "WHEAT", "CARROT", "MELON"),
}

ANIMAL_MIX = {
    "cow_sheep16": {"COW": 8, "SHEEP": 8, "GOOSE": 0},
    "cow_heavy": {"COW": 10, "SHEEP": 5, "GOOSE": 1},
    "sheep_heavy": {"COW": 4, "SHEEP": 11, "GOOSE": 1},
}

LAND = {
    "early": {6, 11, 18},
    "two": {6, 11},
}

HIRE = {
    "max": 10,
    "high": 9,
}

SELL = {
    "dusk": {"hours": (18, 20, 21), "hold_wheat": 8},
    "frequent": {"hours": (6, 12, 18, 21), "hold_wheat": 6},
}

LONG_CUTOFF = {
    "d10": 10,
}


def compile_program(prog: dict):
    """Return agent(obs, configuration=None) implementing this discrete program."""
    opening = OPENING[prog["opening"]]
    mid_order = MID_CROP[prog["mid_crop"]]
    mix = ANIMAL_MIX[prog["animal_mix"]]
    land_days = LAND[prog["land"]]
    hire_cap = HIRE[prog["hire"]]
    sell = SELL[prog["sell"]]
    long_cut = LONG_CUTOFF[prog.get("long_cutoff", "d10")]

    def hire_target(day):
        if day <= 2:
            return min(5, hire_cap)
        if day <= 5:
            return min(6, hire_cap)
        if day <= 9:
            return min(8, hire_cap)
        return hire_cap

    def market_orders(shed, seeds, money, prices, day, hour, hires_today, live, n_land, empty):
        market = []
        cash = float(money)

        def add(o):
            if len(market) >= 10:
                return False
            market.append(o)
            return True

        # 1) day-0 opening pack FIRST
        if day == 0 and hour == 0:
            for crop, q in opening["seeds"]:
                cost = SEED_COST[crop] * q
                if cash >= cost + 20:
                    if add(["BUY_SEED", crop, q]):
                        cash -= cost
            for a, q in opening["animals"]:
                cost = ANIMAL_COST[a] * q
                if cash >= cost + 20:
                    if add(["BUY_ANIMAL", a, q]):
                        cash -= cost

        # 2) land
        if hour == 0 and day in land_days and n_land < 4 and cash >= 1300:
            if add(["BUY_LAND"]):
                cash -= 1000

        # 3) livestock expand
        if hour == 0 and day >= 1:
            for a, target in mix.items():
                have = live[a] + int(shed.get(a) or 0)
                gap = target - have
                can = min(gap, 2, int(max(0.0, cash - 100) // ANIMAL_COST[a]))
                for _ in range(max(0, can)):
                    if not add(["BUY_ANIMAL", a, 1]):
                        break
                    cash -= ANIMAL_COST[a]

        # 4) seed top-up
        if hour in (0, 6, 12) and empty > 1 and cash >= 60:
            bought = 0
            for crop in mid_order:
                if crop == "MELON" and day >= long_cut:
                    continue
                cost = SEED_COST[crop]
                if cash < cost + 30:
                    continue
                q = min(empty - bought, 3 if cost >= 50 else 5, int((cash - 30) // cost))
                if q <= 0:
                    continue
                if add(["BUY_SEED", crop, q]):
                    cash -= cost * q
                    bought += q
                if bought >= empty - 1 or len(market) >= 8:
                    break

        # 5) hire last among dawn ops
        if hour == 0:
            room = max(0, 10 - len(market) - 1)
            target = hire_target(day)
            n = 0
            while n < target and n < room:
                cost = _fib(hires_today + n)
                if cash < cost + 5:
                    break
                if not add(["HIRE"]):
                    break
                cash -= cost
                n += 1

        # 6) sell cadence
        if hour in sell["hours"] or day >= 29:
            hold = 0 if day >= 29 else sell["hold_wheat"]
            items = []
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q <= 0:
                    continue
                if item == "WHEAT":
                    q = max(0, q - hold)
                    if q <= 0:
                        continue
                px = int(prices.get(item) or 1)
                items.append((px * q, item, q))
            items.sort(reverse=True)
            for _, item, q in items:
                if not add(["SELL", item, q]):
                    break

        if day >= 29:
            for item in PRODUCTS:
                q = int(shed.get(item) or 0)
                if q > 0:
                    add(["SELL", item, q])

        return market

    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        day = step // 24
        hour = step % 24
        player = int(obs.get("player") or 0)
        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        private = obs.get("private") or {}
        shed = dict(private.get("shed") or {})
        seeds = dict(private.get("seeds") or {})
        prices = dict((obs.get("market") or {}).get("prices") or {})
        money = float(farm.get("money") or 0)
        tiles = farm.get("tiles") or []
        hires_today = int(farm.get("hires_today") or 0)
        n_land = len(farm.get("unlocked_quadrants") or [])

        live = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
        empty = 0
        for row in tiles:
            for t in row:
                if t is None:
                    empty += 1
                elif isinstance(t, dict) and t.get("animal") in live:
                    live[t["animal"]] += 1

        market = market_orders(
            shed, seeds, money, prices, day, hour, hires_today, live, n_land, empty,
        )

        # workers + residual market from p11; discrete program PREPENDS high-level orders
        # (replace-only broke market↔worker coupling — P33)
        if not hasattr(agent, "_pl"):
            from p11_planner import planner as pmod
            agent._pl = pmod.StrategicPlanner()
        base = agent._pl.act(obs)
        action = dict(base or {})
        p11_m = list(action.get("market") or [])
        action["market"] = (market + p11_m)[:10]
        return sanitize_action(action, shed=shed, money=money, prices=prices)

    return agent


def enumerate_programs():
    progs = []
    for opening in OPENING:
        for mid in MID_CROP:
            for mix in ("cow_sheep16", "cow_heavy", "sheep_heavy"):
                for land in ("early", "two"):
                    for hire in ("max", "high"):
                        for sell in ("dusk", "frequent"):
                            progs.append({
                                "opening": opening,
                                "mid_crop": mid,
                                "animal_mix": mix,
                                "land": land,
                                "hire": hire,
                                "sell": sell,
                                "long_cutoff": "d10",
                            })
    seen = set()
    uniq = []
    for p in progs:
        h = program_hash(p)
        if h not in seen:
            seen.add(h)
            uniq.append(p)
    return uniq
