# -*- coding: utf-8 -*-
"""Kaggriculture 本地模拟器(验证 agent 用,非提交物)。

obs/action 契约与真实环境一致 —— 2026-08-28 从 kaggle-environments 1.32.7
的 kaggriculture 引擎源码(kaggriculture.py / kaggriculture.json)逐项校准,
数值不再是社区假设:
    obs    = {"player","day","hour","step",
              "farms":[{farmer,hands,money,tiles,unlocked_quadrants,hires_today}],
              "private":{seeds,shed,inventories},
              "market":{inventory,prices},"town":{unlocked_shops}}
    action = {"farmer":[op,...],"hands":[[op,...],...],"market":[[op,...],...]}
    tile   = None | {"kind":"PLANT","crop","planted_day","watered_today",...}
                  | {"kind":"WEED"}
    tiles[y][x],farmer 坐标为 (x,y);board 10x10,farmer 初始 [4,4]

真实常量(已校准):
    CROPS/ANIMALS 见下方表;起始资金 3000;初始种子全 0(必须先从市场买);
    weedSpawnChance 0.005/瓦片/天;turnsPerDay 24;episodeSteps 720;
    shedCapacity 100;maxMarketOrdersPerTurn 10;卖价为动态(本模拟器暂用 base 价)。

尚未建模(只影响离线分数的绝对值,不影响提交正确性):
    动态价格曲线、肥料、动物、镇需求、持续型作物的精确收获调度。
"""
import random

NORTH, SOUTH, EAST, WEST = "NORTH", "SOUTH", "EAST", "WEST"
MOVES = (NORTH, SOUTH, EAST, WEST)
WATER, HARVEST, DIG, PLANT, PASS = "WATER", "HARVEST", "DIG", "PLANT", "PASS"
KIND_PLANT, KIND_WEED = "PLANT", "WEED"
BUY_SEED, SELL = "BUY_SEED", "SELL"

FARM_SIZE = 10          # 10x10 = 4 个 5x5 象限
TURNS_PER_DAY = 24      # 30 天 = 720 回合
MAX_DAYS = 30
START_MONEY = 3000.0
START_SEEDS = {"WHEAT": 0, "CARROT": 0, "TOMATO": 0, "STRAWBERRY": 0, "MELON": 0}
WEED_PROB_PER_DAY = 0.005
DRY_YIELD_FACTOR = 0.5  # 没浇水的地减产到 0.5x(简化;真实公式略复杂)

# 真实引擎常量(kaggle_environments kaggriculture.CROPS;price 为基准卖价)
CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False, "price": 25.0},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False, "price": 35.0},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True,  "price": 60.0},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True,  "price": 120.0},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False, "price": 250.0},
}
# 真实引擎常量(ANIMALS;本地模拟器暂不实现动物机制,仅保留常量供后续)
ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
# 真实引擎常量: 初始解锁 NW,依次买 NE/SW/SE,价格 1000/2000/4000
LAND_ORDER = ["NE", "SW", "SE"]
LAND_PRICES = [1000, 2000, 4000]
HIRE, BUY_LAND = "HIRE", "BUY_LAND"
DEFAULT_SPAWN = [4, 4]  # 引擎 _default_spawn: NW 象限 shed 可达格第一个


def _fib(n):
    """雇工成本序列(引擎 _fib): _fib(0)=1, _fib(1)=1, _fib(2)=2, _fib(3)=3..."""
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _quadrant_of(x, y):
    half = FARM_SIZE // 2
    return ("N" if y < half else "S") + ("W" if x < half else "E")


class LocalKaggricultureEnv:
    """确定性(按种子)的本地 Kaggriculture,支持 N 玩家(默认 2)。"""

    def __init__(self, seed=0, n_players=2):
        self._rng = random.Random(seed)
        self.n_players = n_players
        self.reset()

    # ---- 生命周期 ----------------------------------------------------------
    def reset(self):
        self.turn = 0
        self.day = 0
        self.hour = 0
        self.farms = []
        for _ in range(self.n_players):
            farm = {
                "farmer": list(DEFAULT_SPAWN),  # 真实初始位置(首个 5x5 象限中心)
                "money": START_MONEY,
                # 真实初始只解锁首个 5x5 象限,其余为 "LOCKED" 字符串
                "tiles": [["LOCKED"] * FARM_SIZE for _ in range(FARM_SIZE)],
                "seeds": dict(START_SEEDS),
                "shed": {k: 0 for k in list(CROPS) + ["EGG", "MILK", "WOOL", "FERTILIZER"]},
                "inventories": [{}],
                "hands": [],
                "hires_today": 0,
                "unlocked_quadrants": ["NW"],
            }
            for y in range(5):
                for x in range(5):
                    farm["tiles"][y][x] = None
            self.farms.append(farm)

    @property
    def done(self):
        return self.turn >= TURNS_PER_DAY * MAX_DAYS

    # ---- 观测(与真实 obs 形状一致)------------------------------------------
    def observe(self, player):
        return {
            "player": player,
            "day": self.day,
            "hour": self.hour,
            "step": self.turn,
            "farms": [self._public_farm(f) for f in self.farms],
            "private": {
                "seeds": dict(self.farms[player]["seeds"]),
                "shed": dict(self.farms[player]["shed"]),
                "inventories": [dict(i) for i in self.farms[player]["inventories"]],
            },
            "market": {
                "inventory": {k: 10000 for k in CROPS},
                "prices": {k: v["price"] for k, v in CROPS.items()},
            },
            "town": {"unlocked_shops": []},
        }

    def _public_farm(self, farm):
        return {
            "farmer": list(farm["farmer"]),
            "hands": [list(h) for h in farm["hands"]],
            "money": farm["money"],
            "tiles": [[self._public_tile(t) for t in row] for row in farm["tiles"]],
            "unlocked_quadrants": list(farm["unlocked_quadrants"]),
            "hires_today": farm["hires_today"],
        }

    @staticmethod
    def _public_tile(tile):
        if not isinstance(tile, dict):
            return tile  # None(空地)或 "LOCKED"(未购象限)原样返回
        if tile["kind"] == KIND_PLANT:
            return {"kind": KIND_PLANT, "crop": tile["crop"],
                    "planted_day": tile["planted_day"],
                    "watered_today": tile["watered_today"]}
        return {"kind": KIND_WEED}

    # ---- 推进 ----------------------------------------------------------------
    def step(self, actions):
        if self.done:
            return
        for player, action in enumerate(actions):
            if action is None:
                continue
            farm = self.farms[player]
            self._apply_market(player, action.get("market") or [])
            self._apply_unit(farm, action.get("farmer") or [PASS], farm["farmer"])
            for i, hcmd in enumerate(action.get("hands") or []):
                if i < len(farm["hands"]):
                    self._apply_unit(farm, hcmd, farm["hands"][i])
        self.turn += 1
        self.hour = self.turn % TURNS_PER_DAY
        if self.turn % TURNS_PER_DAY == 0:
            self._end_of_day()

    def _apply_market(self, player, ops):
        farm = self.farms[player]
        for op in ops:
            if not op:
                continue
            kind = op[0]
            if kind == HIRE:
                cost = _fib(farm["hires_today"])
                if farm["money"] >= cost:
                    farm["money"] -= cost
                    farm["hires_today"] += 1
                    farm["hands"].append(list(DEFAULT_SPAWN))
            elif kind == BUY_LAND:
                n = len(farm["unlocked_quadrants"]) - 1
                if n < len(LAND_ORDER):
                    cost = LAND_PRICES[n]
                    if farm["money"] >= cost:
                        farm["money"] -= cost
                        q = LAND_ORDER[n]
                        farm["unlocked_quadrants"].append(q)
                        for y in range(FARM_SIZE):
                            for x in range(FARM_SIZE):
                                if _quadrant_of(x, y) == q and farm["tiles"][y][x] == "LOCKED":
                                    farm["tiles"][y][x] = None
            elif kind == BUY_SEED and len(op) >= 3:
                crop, qty = op[1], int(op[2])
                spec = CROPS.get(crop)
                if spec is None or qty <= 0:
                    continue
                cost = qty * spec["seed"]
                if farm["money"] >= cost:
                    farm["money"] -= cost
                    farm["seeds"][crop] = farm["seeds"].get(crop, 0) + qty
            elif kind == SELL and len(op) >= 3:
                crop, qty = op[1], int(op[2])
                spec = CROPS.get(crop)
                have = farm["shed"].get(crop, 0)
                q = min(int(qty), have)
                if spec is None or q <= 0:
                    continue
                farm["shed"][crop] = have - q
                farm["money"] += q * spec["price"]

    def _apply_unit(self, farm, cmd, pos):
        """应用 farmer/hand 的单位动作;pos 为位置列表引用(原地修改)。"""
        if not cmd:
            return
        fx, fy = pos
        verb = cmd[0]

        if verb in MOVES:
            if verb == EAST:
                fx = min(FARM_SIZE - 1, fx + 1)
            elif verb == WEST:
                fx = max(0, fx - 1)
            elif verb == SOUTH:
                fy = min(FARM_SIZE - 1, fy + 1)
            elif verb == NORTH:
                fy = max(0, fy - 1)
            pos[0], pos[1] = fx, fy
            return

        tile = farm["tiles"][fy][fx]

        if tile == "LOCKED":
            return  # 未购象限不可执行地块动作(真实引擎 no-op)

        if verb == WATER:
            if tile and tile["kind"] == KIND_PLANT and not tile["watered_today"]:
                tile["watered_today"] = True
                tile["_waterings"] = tile.get("_waterings", 0) + 1
        elif verb == HARVEST:
            if tile and tile["kind"] == KIND_PLANT:
                crop = tile["crop"]
                spec = CROPS[crop]
                if self.day - tile["planted_day"] >= spec["first_yield_day"]:
                    if spec["ongoing"]:
                        # 持续型:每次收获 +1,累计到 max_yield 后移除
                        if tile.get("_harvested", 0) < spec["max_yield"]:
                            tile["_harvested"] = tile.get("_harvested", 0) + 1
                            farm["shed"][crop] = farm["shed"].get(crop, 0) + 1
                            if tile["_harvested"] >= spec["max_yield"]:
                                farm["tiles"][fy][fx] = None
                    else:
                        ratio = min(1.0, tile.get("_waterings", 0) / spec["first_yield_day"])
                        amount = spec["max_yield"] * (DRY_YIELD_FACTOR
                                                      + (1 - DRY_YIELD_FACTOR) * ratio)
                        farm["shed"][crop] = farm["shed"].get(crop, 0) + amount
                        farm["tiles"][fy][fx] = None
        elif verb == DIG:
            if tile and tile["kind"] == KIND_WEED:
                farm["tiles"][fy][fx] = None
        elif verb == PLANT and len(cmd) >= 2:
            crop = cmd[1]
            if tile is None and farm["seeds"].get(crop, 0) > 0:
                farm["seeds"][crop] -= 1
                farm["tiles"][fy][fx] = {
                    "kind": KIND_PLANT, "crop": crop,
                    "planted_day": self.day, "watered_today": False,
                    "_waterings": 0, "_harvested": 0,
                }
        # PASS / 未知命令: 无操作

    def _end_of_day(self):
        self.day += 1
        for farm in self.farms:
            for row in farm["tiles"]:
                for tile in row:
                    if isinstance(tile, dict) and tile["kind"] == KIND_PLANT:
                        tile["watered_today"] = False
            # 杂草: 每瓦片每天 weedSpawnChance 概率(真实引擎为逐瓦片独立概率)
            for y in range(FARM_SIZE):
                for x in range(FARM_SIZE):
                    if farm["tiles"][y][x] is None and self._rng.random() < WEED_PROB_PER_DAY:
                        farm["tiles"][y][x] = {"kind": KIND_WEED}
            # 对齐真实引擎: 每天结束重置 farmer 位置、清空 hands(次日需重新雇)、
            # 重置雇工计数与背包(引擎 _end_of_day)
            farm["farmer"] = list(DEFAULT_SPAWN)
            farm["hands"] = []
            farm["hires_today"] = 0
            farm["inventories"] = [{}]

    # ---- 计分(真实规则: 结束时 money,含已收获未售的仓库价值按 base 价估算)----
    def score(self, player):
        farm = self.farms[player]
        shed_value = sum(amt * CROPS[c]["price"]
                         for c, amt in farm["shed"].items() if c in CROPS)
        return round(farm["money"] + shed_value, 2)
