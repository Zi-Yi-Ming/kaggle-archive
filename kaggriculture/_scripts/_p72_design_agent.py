# -*- coding: utf-8 -*-
"""P72: design new live agent from LB-winner eco profile; eval vs alperen."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p10_executor.validators import sanitize_action  # noqa: E402

FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3, 4, 5)

# LB-winner schedule (P63/P68): animals 6@d5 → 13@d10 → 17@d15; plants 27@d10
ANIMAL_TARGETS = {0: 4, 1: 5, 2: 6, 3: 7, 4: 8, 5: 6, 6: 8, 7: 9, 8: 10,
                  9: 12, 10: 13, 11: 14, 12: 15, 13: 16, 14: 16, 15: 17}
LAND_DAYS = {6, 11, 18}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
HOME = ((4, 4), (5, 4), (4, 5), (5, 5))
FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}


def _fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def build_agent():
    state = {"day": -1, "tasks": {}}

    def beside_shed(p):
        return p in HOME

    def nearest_home(pos):
        return min(HOME, key=lambda q: (abs(pos[0]-q[0])+abs(pos[1]-q[1]), q))

    def walk(pos, target):
        x, y = pos
        tx, ty = max(0, min(9, int(target[0]))), max(0, min(9, int(target[1])))
        if x != tx:
            return ["EAST" if x < tx else "WEST"]
        if y != ty:
            return ["SOUTH" if y < ty else "NORTH"]
        return None

    def manhattan(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def crop_ready(tile, day):
        if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
            return False
        crop = tile.get("crop")
        planted = tile.get("planted_day")
        planted = -99 if planted is None else int(planted)
        need = FIRST_YIELD.get(crop, 2)
        if planted >= 0 and day - planted >= need:
            return True
        yu = tile.get("yield_units")
        try:
            return int(yu or 0) > 0 and (planted < 0 or day - planted >= need)
        except Exception:
            return False

    def tile_kind(tiles, x, y):
        try:
            t = tiles[y][x]
        except Exception:
            return "OOB"
        if t is None:
            return "EMPTY"
        if isinstance(t, dict):
            k = t.get("kind")
            if k == "PLANT":
                return "PLANT"
            if k == "WEED":
                return "WEED"
            if t.get("animal"):
                return "ANIMAL"
            return k or "DICT"
        return "OTHER"

    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        day, hour = step // 24, step % 24
        player = int(obs.get("player") or 0)
        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        private = obs.get("private") or {}
        shed = dict(private.get("shed") or {})
        seeds = dict(private.get("seeds") or {})
        inventories = list(private.get("inventories") or [])
        prices = dict((obs.get("market") or {}).get("prices") or {})
        money = float(farm.get("money") or 0)
        tiles = farm.get("tiles") or []
        positions = [tuple(farm.get("farmer") or (4, 4))]
        for h in farm.get("hands") or []:
            positions.append(tuple(h))
        hires_today = int(farm.get("hires_today") or 0)
        n_land = len(farm.get("unlocked_quadrants") or [])

        live = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
        empty = plants = 0
        for row in tiles:
            for t in row:
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        plants += 1
                    if t.get("animal") in live:
                        live[t["animal"]] += 1
        n_animals = sum(live[a] + int(shed.get(a) or 0) for a in live)

        # ---------- MARKET ----------
        market = []
        cash = money

        def add(o):
            if len(market) >= 10:
                return False
            market.append(o)
            return True

        # 1) d0 opening — LB-like plant-heavy + modest animals
        if day == 0 and hour == 0:
            if cash >= 80 * 12 + 30 and add(["BUY_SEED", "MELON", 12]):
                cash -= 80 * 12
            if cash >= 10 * 7 + 30 and add(["BUY_SEED", "WHEAT", 7]):
                cash -= 10 * 7
            if cash >= 400 * 2 + 30 and add(["BUY_ANIMAL", "COW", 2]):
                cash -= 800
            if cash >= 500 * 2 + 30 and add(["BUY_ANIMAL", "SHEEP", 2]):
                cash -= 1000

        # 2) land
        if hour == 0 and day in LAND_DAYS and n_land < 4 and cash >= 1300:
            if add(["BUY_LAND"]):
                cash -= 1000

        # 3) animals toward LB ramp
        target = ANIMAL_TARGETS.get(day, 17)
        if hour == 0 and day >= 1:
            gap = target - n_animals
            can = min(max(0, gap), 2, int(max(0.0, cash - 80) // 400))
            for _ in range(can):
                if cash >= 420 and add(["BUY_ANIMAL", "COW", 1]):
                    cash -= 400
                elif cash >= 520 and add(["BUY_ANIMAL", "SHEEP", 1]):
                    cash -= 500

        # 4) seeds — keep planting
        if hour in (0, 6, 12) and empty > 1 and cash >= 50:
            bought = 0
            for crop, cost in (("MELON", 80), ("STRAWBERRY", 100), ("WHEAT", 10), ("CARROT", 20)):
                if day < 10 and crop in ("STRAWBERRY",) and bought > 2:
                    continue
                if day >= 10 and crop == "MELON":
                    continue
                q = min(empty - bought, 3 if cost >= 50 else 5, int(max(0, cash - 30) // cost))
                if q <= 0:
                    continue
                if add(["BUY_SEED", crop, q]):
                    cash -= cost * q
                    bought += q
                if bought >= empty - 1:
                    break

        # 5) hire
        if hour == 0:
            room = max(0, 9 - len(market))
            hire_tgt = 5 if day <= 2 else (7 if day <= 6 else 10)
            n = 0
            while n < hire_tgt and n < room:
                cost = _fib(hires_today + n)
                if cash < cost + 4 or not add(["HIRE"]):
                    break
                cash -= cost
                n += 1

        # 6) sell — early wheat/fert, later premium
        sell_hours = (6, 12, 18, 21) if day >= 5 else (18, 21)
        if hour in sell_hours or day >= 29:
            hold = 0 if day >= 29 else (6 if day < 10 else 3)
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

        # ---------- WORKERS ----------
        if day != state["day"]:
            state["day"] = day
            state["tasks"] = {}

        if day < 10:
            plant_order = ("MELON", "WHEAT", "STRAWBERRY", "CARROT", "TOMATO")
        else:
            plant_order = ("STRAWBERRY", "WHEAT", "TOMATO", "CARROT")

        seed_budget = {c: int(seeds.get(c) or 0) for c in SEED_COST}
        claimed = set()
        for task in state["tasks"].values():
            if task and task[0] == "PLANT":
                claimed.add(tuple(task[1]))

        weeds = []
        empties = []
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "WEED":
                    weeds.append((x, y))
                elif t is None and (x, y) not in claimed:
                    empties.append((x, y))
        weeds.sort(key=lambda p: manhattan(p, (4, 4)))
        empties.sort(key=lambda p: manhattan(p, (4, 4)))

        plant_queue = []
        for x, y in empties:
            chosen = None
            for crop in plant_order:
                if crop == "MELON" and day >= 10:
                    continue
                if seed_budget.get(crop, 0) > 0:
                    chosen = crop
                    seed_budget[crop] -= 1
                    break
            if chosen is None:
                break
            plant_queue.append(((x, y), chosen))
        dig_queue = weeds[:]

        def eco_worker(actor):
            task = state["tasks"].get(actor)
            pos = positions[actor] if actor < len(positions) else (4, 4)
            if task:
                op = task[0]
                tx, ty = task[1]
                k = tile_kind(tiles, tx, ty)
                if op == "PLANT" and k == "EMPTY" and int(seeds.get(task[2]) or 0) > 0:
                    if (tx, ty) == pos:
                        return ["PLANT", task[2]]
                    w = walk(pos, (tx, ty))
                    return w or ["PLANT", task[2]]
                if op == "DIG" and k == "WEED":
                    if (tx, ty) == pos:
                        return ["DIG"]
                    w = walk(pos, (tx, ty))
                    return w or ["DIG"]
                state["tasks"].pop(actor, None)

            # harvest
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and crop_ready(t, day):
                        if (x, y) == pos:
                            return ["HARVEST"]
                        w = walk(pos, (x, y))
                        return w or ["HARVEST"]
            # dig
            if dig_queue:
                tx, ty = dig_queue.pop(0)
                state["tasks"][actor] = ("DIG", (tx, ty))
                if (tx, ty) == pos:
                    return ["DIG"]
                w = walk(pos, (tx, ty))
                return w or ["DIG"]
            # water
            if hour < 20:
                for y, row in enumerate(tiles):
                    for x, t in enumerate(row):
                        if isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today"):
                            if (x, y) == pos:
                                return ["WATER"]
                            w = walk(pos, (x, y))
                            return w or ["WATER"]
            # plant
            if plant_queue:
                (tx, ty), crop = plant_queue.pop(0)
                state["tasks"][actor] = ("PLANT", (tx, ty), crop)
                if (tx, ty) == pos:
                    return ["PLANT", crop]
                w = walk(pos, (tx, ty))
                return w or ["PLANT", crop]
            # animal micro
            inv = dict(inventories[actor] or {}) if actor < len(inventories) else {}
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if not isinstance(t, dict) or not t.get("animal"):
                        continue
                    if not t.get("fed_today") and int(inv.get("WHEAT") or 0) > 0:
                        if (x, y) == pos:
                            return ["FEED"]
                        w = walk(pos, (x, y))
                        return w or ["FEED"]
                    if t.get("fed_today") and not t.get("cared_today"):
                        if (x, y) == pos:
                            return ["CARE"]
                        w = walk(pos, (x, y))
                        return w or ["CARE"]
                    if int(t.get("yield_units") or 0) > 0:
                        if (x, y) == pos:
                            return ["HARVEST"]
                        w = walk(pos, (x, y))
                        return w or ["HARVEST"]
            # place animal
            for y, row in enumerate(tiles):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal"):
                        for a in ANIMAL_COST:
                            if int(inv.get(a) or 0) > 0:
                                if (x, y) == pos:
                                    return ["PLACE", a]
                                w = walk(pos, (x, y))
                                return w or ["PLACE", a]
            # build if waiting and no seeds
            if n_animals > sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal")):
                if not any(int(v or 0) > 0 for v in seeds.values()):
                    for y, row in enumerate(tiles):
                        for x, t in enumerate(row):
                            if t is None:
                                op = "BUILD_COOP" if int(shed.get("GOOSE") or 0) > 0 else "BUILD_PASTURE"
                                if (x, y) == pos:
                                    return [op]
                                w = walk(pos, (x, y))
                                return w or [op]
            # pickup
            if beside_shed(pos):
                if int(shed.get("WHEAT") or 0) > 0 and not inv.get("WHEAT"):
                    return ["PICKUP", "WHEAT", min(8, int(shed["WHEAT"]))]
                for a in ANIMAL_COST:
                    if int(shed.get(a) or 0) > 0:
                        return ["PICKUP", a, 1]
            # cargo home
            if any(int(v or 0) > 0 for v in inv.values()) and hour >= 19:
                w = walk(pos, nearest_home(pos))
                return w or ["DROP"]
            if not beside_shed(pos) and hour < 22:
                w = walk(pos, nearest_home(pos))
                if w:
                    return w
            return ["PASS"]

        farmer = eco_worker(0)
        hands = [eco_worker(i) for i in range(1, len(positions))]
        return sanitize_action(
            {"farmer": farmer, "hands": hands, "market": market},
            shed=shed, money=money, prices=prices,
        )

    return agent


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def play(inner):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            return inner(obs)
    else:
        def agent(obs, configuration=None):
            return inner(obs, configuration)
    return agent


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play(a0), play(a1)])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def main():
    t0 = time.time()
    agent = build_agent()
    print("=== P72 designed agent vs finn ===", flush=True)
    banks = []
    for seed in SEEDS:
        b0, _ = run(agent, load_quiet(FINN, f"f{seed}"), seed)
        banks.append(b0)
        print(f"  finn s{seed}: {b0:.0f}", flush=True)
    print(f"finn mean={sum(banks)/len(banks):.0f}", flush=True)

    print("\n=== vs alperen ===", flush=True)
    w = d = l = 0
    for seed in SEEDS:
        a0, a1 = run(agent, load_quiet(ALPEREN, f"a{seed}"), seed)
        b0, b1 = run(load_quiet(ALPEREN, f"a{seed}b"), agent, seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        if our > theirs + 1:
            w += 1
            res = "W"
        elif theirs > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        print(f"  s{seed}: us={our:.0f} alp={theirs:.0f} {res}", flush=True)
    print(f"vs alperen {w}-{d}-{l}", flush=True)

    print("\n=== vs R2 ===", flush=True)
    w2 = d2 = l2 = 0
    for seed in SEEDS:
        a0, a1 = run(agent, load_quiet(R2, f"r{seed}"), seed)
        b0, b1 = run(load_quiet(R2, f"r{seed}b"), agent, seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        if our > theirs + 1:
            w2 += 1
        elif theirs > our + 1:
            l2 += 1
        else:
            d2 += 1
        print(f"  s{seed}: us={our:.0f} r2={theirs:.0f}", flush=True)
    print(f"vs R2 {w2}-{d2}-{l2}", flush=True)
    print(f"dt={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
