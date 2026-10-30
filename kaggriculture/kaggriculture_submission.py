# -*- coding: utf-8 -*-
"""
Kaggriculture v2 策略 agent —— 自包含单文件(纯 stdlib,零依赖),可直接提交。

比赛: https://www.kaggle.com/competitions/kaggriculture
规则: 30 天 = 720 回合的双人对战农场模拟,按"资金 + 仓库价值"计分;
      每回合返回 {"farmer": [命令...], "hands": [[命令...]...], "market": [[操作...]...]}
      市场操作不消耗 farmer 行动,每回合都能做。

v3.4 策略(2026-08-28,基于真实引擎校准与验证):
1. 市场(每回合免费): 卖出(非 MELON 清仓;MELON 限量卖保价,day 28 清仓);
   day>=2 买 2 个肥料(BUY_PRODUCT);day>=3 保证 1 个 MELON 种子;
   WHEAT 按 WHEAT_CAP=13 限量(24 回合/天劳动力硬墙,限种植量让浇水更充分);
2. farmer 按优先级就近行动: 收获(0) > 浇水(1) > 施肥/取肥(2) > 除草(3) > 播种(4);
   MELON 窗口期(age 6-8)施肥:浇水加成翻倍,age 9 达 cap 6 提前收获;
3. 移动规则: 已站在目标地块则执行动作,否则朝目标走一步(先 x 轴后 y 轴)。
   雇工/买地经真实引擎验证为负收益,默认关闭。
作物价格/产量/成熟天数与 kaggle-environments 的 kaggriculture 一致(2026-08-28 校准)。
"""
# 作物成熟天数(真实引擎 CROPS.first_yield_day;obs 的 PLANT tile 带 crop 字段)
MATURE_DAYS_BY_CROP = {
    "WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10,
}
DEFAULT_MATURE_DAYS = 2

# 真实引擎常量(kaggle_environments kaggriculture,2026-08-28 校准):
# 种子价/基准卖价/最大产量。注意引擎没有 "CORN" —— 用不存在的作物名会让
# BUY_SEED 订单被环境静默丢弃(v1 曾因此 720 回合全程无效)。
CROPS = {
    "WHEAT":      {"seed_cost": 10.0, "sell_price": 25.0, "base_yield": 6.0},
    "CARROT":     {"seed_cost": 20.0, "sell_price": 35.0, "base_yield": 4.0},
    "TOMATO":     {"seed_cost": 50.0, "sell_price": 60.0, "base_yield": 4.0},
    "STRAWBERRY": {"seed_cost": 100.0, "sell_price": 120.0, "base_yield": 4.0},
    "MELON":      {"seed_cost": 80.0, "sell_price": 250.0, "base_yield": 6.0},
}
BEST_CROP = "WHEAT"  # 2 天成熟快周转:6×25=150 收入 / 10 种子,ROI 15x

# v3.5 激进变体(第 5 次提交,2026-08-28 多 seed 验证):day>=2 起种 MELON。
# 与 v3.4 唯一差异 = MELON_SWITCH_DAY 3→2:平均 23256 vs 22633(+623,3/4 seed 领先),
# 种子 123 微降 -67(噪声级)。肥料补上了 s2 的时序短板(seed 7: -1548 → +1501)。
MELON_SWITCH_DAY = 2
MELON_QTY = 1
WHEAT_CAP = 18  # 劳动力硬墙:限种植量让浇水更充分;s2c13m1 平均更高但方差大,弃用

# v3.4 肥料产线 + MELON 限卖(2026-08-28 多 seed 验证,4/4 seed 全胜 +1133):
# MELON 窗口期(age 6-8)施肥 → 浇水加成翻倍,age 9 达 cap 6(提前收获);
# MELON 每回合限量卖 1 个(镇消费消化库存,价格维持高位),day 28 起清仓。
FERT_QTY = 2             # 赛季需 2 个肥料(每轮 MELON 施 1 次)
FERT_WINDOW = (6, 8)     # 施肥窗口(MELON age 6-8)
SHED_ACCESS = [(4, 4), (5, 4), (4, 5), (5, 5)]  # 仓库旁格(引擎 _shed_access_tiles)
MELON_SELL_LIMIT = 1     # 每回合 MELON 最多卖 N 个(限量保价)
END_DUMP_DAY = 28        # 赛季末清仓日(此后不限量卖)

# v4 区域分工实验(2026-08-29):打破 24 回合/天劳动力硬墙。
# 引擎机制:hand 每天清空需重新 HIRE(第 1 个只花 1 金币,fib 成本),
# 每天 farmer/hand 都重置回 shed 旁格。v2 失败根因是"全局就近"——
# 两个单位抢同一目标,移动开销>劳动力收益。
# v4 解法:区域分工 —— farmer 只管 x<=2 左区(15 格),hand 只管 x=3,4 右区(10 格),
# 各自只在区域内扫描,从根上消除目标冲突;MELON 种在右区由 hand 照看。
HIRE_TARGET = 1          # 每天雇 1 个 hand(成本 1 金币)
HIRE_MONEY_GUARD = 50    # 雇工后保底资金
LAND_PRICES = [1000, 2000, 4000]  # NE / SW / SE(真实引擎 LAND_PRICES)
BUY_LAND_TRIGGER = 0     # 空地块 ≤ N 时考虑买地(0=关闭;买地后移动开销大)
BUY_LAND_GUARD = 500     # 买地后保底资金(留种子/周转)

# 区域边界:初始 5x5 象限,farmer 管 x<=2,hand 管 x=3,4
FARMER_X_MAX = 2
HAND_X_MIN = 3


def _market_ops(obs):
    """每回合市场操作: 清仓卖出 + 雇工 + 买地 + 补种子。返回 market 列表。"""
    priv = obs["private"]
    farm = obs["farms"][obs["player"]]
    money = farm["money"]
    market = []

    # 1) 卖出库存: MELON 限量卖(保价,镇消费消化库存),赛季末清仓;其余清仓
    for crop, qty in priv.get("shed", {}).items():
        if qty and qty > 0:
            if crop == "MELON" and obs["day"] < END_DUMP_DAY:
                n = min(int(qty), MELON_SELL_LIMIT)
                if n > 0:
                    market.append(["SELL", "MELON", n])
            else:
                market.append(["SELL", crop, int(qty)])

    tiles = farm["tiles"]
    empty = sum(1 for row in tiles for t in row if t is None)
    owned = sum(priv.get("seeds", {}).values())

    # 2) 雇工: 单 farmer 一天 24 回合浇不完 25 格,劳动力是瓶颈
    n_hands = len(farm.get("hands") or [])
    if n_hands < HIRE_TARGET and money > HIRE_MONEY_GUARD:
        market.append(["HIRE"])

    # 3) 买地: 现有地块快种满且资金够地价 + 保底时扩张
    n_unlocked = len(farm.get("unlocked_quadrants") or ["NW"])
    if BUY_LAND_TRIGGER > 0 and empty <= BUY_LAND_TRIGGER and n_unlocked < 4:
        next_price = LAND_PRICES[n_unlocked - 1]
        if money >= next_price + BUY_LAND_GUARD:
            market.append(["BUY_LAND"])

    # 3.5) 买肥料(BUY_PRODUCT 进 shed;MELON 每轮施肥 1 次,赛季需 FERT_QTY 个)
    day = obs["day"]
    if day >= 2:
        shed_f = priv.get("shed", {}).get("FERTILIZER", 0)
        if shed_f < FERT_QTY and money >= 260:
            market.append(["BUY_PRODUCT", "FERTILIZER", FERT_QTY - shed_f])

    # 4) 补种子: day>=切换日后保证有 MELON_QTY 个 MELON 种子(独立判断,
    #    避免 WHEAT 囤种导致 want=0 时 MELON 买不上);WHEAT 按 WHEAT_CAP
    #    限量(24 回合/天劳动力硬墙,限种植量让浇水更充分,多 seed 验证 +2455)
    if day >= MELON_SWITCH_DAY:
        have_m = priv.get("seeds", {}).get("MELON", 0)
        buy_m = max(0, MELON_QTY - have_m)
        if buy_m > 0:
            cost = buy_m * CROPS["MELON"]["seed_cost"]
            if money >= cost:
                market.append(["BUY_SEED", "MELON", buy_m])
                money -= cost
    planted_w = sum(1 for row in tiles for t in row
                    if isinstance(t, dict) and t.get("crop") == "WHEAT")
    have_w = priv.get("seeds", {}).get("WHEAT", 0)
    cap_room = max(0, WHEAT_CAP - planted_w - have_w)
    if cap_room > 0:
        cost = cap_room * CROPS["WHEAT"]["seed_cost"]
        if money >= cost:
            market.append(["BUY_SEED", "WHEAT", cap_room])
    return market


def _scan_target(obs, pos, x_min=0, x_max=9, is_hand=False):
    """以 pos 为起点扫描地块,返回 (pri, dist, x, y, 动作命令)。

    pri: 0=收获 1=浇水 2=除杂草 3=播种(数字小优先级高);
    dist: 曼哈顿距离(同优先级下就近)。
    x_min/x_max: 区域边界 —— farmer 与 hand 各管一片,消除目标冲突。
    is_hand: hand 用自己的 inventory(inventories[1]),farmer 用 inventories[0]。
    """
    farm = obs["farms"][obs["player"]]
    tiles = farm["tiles"]
    fx, fy = pos
    day = obs["day"]
    seeds = obs["private"].get("seeds", {})

    best = None  # (pri, dist, x, y, action)

    def consider(pri, x, y, action):
        nonlocal best
        dist = abs(x - fx) + abs(y - fy)
        if best is None or (pri, dist) < (best[0], best[1]):
            best = (pri, dist, x, y, action)

    # 已有地块: 收获 > 浇水 > [施肥/取肥] > 除杂草(仅扫本区域)
    invs = obs["private"].get("inventories", []) or [{}]
    inv_i = 1 if is_hand else 0
    inv_f = (invs[inv_i] or {}).get("FERTILIZER", 0) if len(invs) > inv_i else 0
    shed_f = obs["private"].get("shed", {}).get("FERTILIZER", 0)
    melon_unfert = False  # 是否有 MELON 在施肥窗口(age 6-8)
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if x < x_min or x > x_max:
                continue
            if t is None or not isinstance(t, dict):
                continue  # 空地或 LOCKED(未购象限)都不可操作
            if t["kind"] == "PLANT":
                age = day - t["planted_day"]
                days = MATURE_DAYS_BY_CROP.get(t.get("crop"), DEFAULT_MATURE_DAYS)
                if age >= days:
                    consider(0, x, y, ["HARVEST"])
                elif not t.get("watered_today"):
                    consider(1, x, y, ["WATER"])
                # 肥料: MELON 窗口期施肥(浇水加成翻倍,提前达 cap)
                if t.get("crop") == "MELON" and FERT_WINDOW[0] <= age <= FERT_WINDOW[1]:
                    melon_unfert = True
                    if inv_f > 0:
                        consider(2, x, y, ["FERTILIZE"])
            elif t["kind"] == "WEED":
                consider(3, x, y, ["DIG"])

    # 取肥料: MELON 需要施肥但手里没肥、仓里有 → 去仓库旁格 PICKUP
    if melon_unfert and inv_f <= 0 and shed_f > 0:
        for sx, sy in SHED_ACCESS:
            consider(2, sx, sy, ["PICKUP", "FERTILIZER"])

    # 播种: 只在没有更高优先级目标时考虑(本区域内空地块 + 有种子)。
    # MELON 只由 hand 种(右区),集中施肥路径;farmer 左区只种 WHEAT/CARROT。
    if best is None or best[0] > 3:
        if is_hand and day >= MELON_SWITCH_DAY:
            crops = ("MELON", "WHEAT", "CARROT")
        else:
            crops = ("WHEAT", "CARROT", "WHEAT")
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if x < x_min or x > x_max:
                    continue
                if t is not None:
                    continue
                for crop in crops:
                    if seeds.get(crop, 0) > 0:
                        consider(4, x, y, ["PLANT", crop])
                        break
    return best


def _unit_cmd(obs, target, pos):
    """目标 → 本回合该单位命令: 已在目标上则执行动作,否则走一步。"""
    if target is None:
        return ["PASS"]
    pri, _, x, y, action = target
    fx, fy = pos
    if (fx, fy) == (x, y):
        return list(action)
    # 移动: 先 x 轴后 y 轴
    if fx < x:
        return ["EAST"]
    if fx > x:
        return ["WEST"]
    if fy < y:
        return ["SOUTH"]
    if fy > y:
        return ["NORTH"]
    return ["PASS"]


def agent(obs, config=None):
    """Kaggriculture 提交入口(兼容 agent(obs) 与 agent(obs, config) 两种调用)。
    返回 {"farmer", "hands", "market"}。区域分工: farmer 管左区, hand 管右区。"""
    market = _market_ops(obs)
    farm = obs["farms"][obs["player"]]
    farmer_pos = farm["farmer"]
    farmer = _unit_cmd(obs, _scan_target(obs, farmer_pos, 0, FARMER_X_MAX),
                       farmer_pos)
    hands = []
    for hpos in farm.get("hands") or []:
        hands.append(_unit_cmd(obs, _scan_target(obs, hpos, HAND_X_MIN, 9,
                                                 is_hand=True), hpos))
    return {"farmer": farmer, "hands": hands, "market": market}


if __name__ == "__main__":
    # 自检: 用最小观测验证返回结构合法
    mini_obs = {
        "player": 0,
        "day": 1,
        "farms": [
            {"farmer": [0, 0], "hands": [], "money": 100.0,
             "tiles": [[None] * 5 for _ in range(5)],
             "unlocked_quadrants": ["NW"]},
            {"farmer": [0, 0], "hands": [], "money": 100.0,
             "tiles": [[None] * 5 for _ in range(5)],
             "unlocked_quadrants": ["NW"]},
        ],
        "private": {"seeds": {"WHEAT": 4}, "shed": {}},
    }
    act = agent(mini_obs)
    assert set(act) == {"farmer", "hands", "market"}, act
    assert act["farmer"] and isinstance(act["farmer"], list)
    assert isinstance(act["hands"], list)
    assert isinstance(act["market"], list)
    print("自检通过 ✅  action =", act)
