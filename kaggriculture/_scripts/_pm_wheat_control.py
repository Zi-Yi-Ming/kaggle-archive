# -*- coding: utf-8 -*-
"""Research-only WHEAT sell control wrapper (TEMP, NOT production).

设计(基于 WHEAT failure 再分析的发现):
  oversell 全部发生在末期(601-720),表现为单笔/单步大单(seed2: 681 步卖 26,
  697 步卖 53, 716 步卖 30),而正常局是均匀小单(总量 ~159 同步对手)。
  机制假设:末期大单砸 WHEAT 供给 → 边际价格伤害;或只是输局 cash 压力的表现
  (effect 而非 cause)——本 wrapper 用于 A/B/C 实验判定,不预设结论。

pressure-aware throttling(保守,不简单写死 cap=10):
  - 仅当: 单步 WHEAT SELL 总量 > step_cap,且 WHEAT 市价 <= price_cap(供应
    压力信号)时,把该步 WHEAT SELL 截断到 step_cap,余量留 shed 后续步自然卖。
  - 三档: none / mild / medium(敏感性实验用,不做大搜索)
  - 不改 cleo_v10.py/任何 production;仅包装 v11 E 的 agent 函数,逐局实例化。

用法:
    from _pm_wheat_control import make_wheat_controlled
    ag = make_wheat_controlled('v11E', level='mild')   # 返回可调用 agent
"""
import os
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
V11_BACKUP = os.path.join(BASE, "cleo_v11_E_backup.py")

# 三档控制参数(保守区间,非大搜索)
LEVELS = {
    # step_cap = 单步 WHEAT SELL 总量上限; price_cap = 市价<=此值时启用截断
    "none":   {"step_cap": 10 ** 9, "price_cap": 0.0},    # 无控制
    "mild":   {"step_cap": 25, "price_cap": 50.0},        # 低价(<50)且单步>25 才截
    "medium": {"step_cap": 15, "price_cap": 55.0},        # 更紧:价<55 且单步>15 截
}


def _is_wheat_sell(o):
    return (isinstance(o, list) and len(o) >= 3
            and o[0] == "SELL" and o[1] == "WHEAT")


def _wheat_price(obs):
    try:
        return float(((obs.get("market") or {}).get("prices") or {}).get("WHEAT", 1e9) or 1e9)
    except Exception:
        return 1e9


def make_wheat_controlled(agent_key="v11E", level="none"):
    """载入 v11 E 模块并包装 agent 实现 WHEAT 单步卖量截断。"""
    spec = importlib.util.spec_from_file_location("v11E_wrap", V11_BACKUP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    base_agent = mod.agent
    cfg = LEVELS.get(level, LEVELS["none"])
    step_cap = cfg["step_cap"]
    price_cap = cfg["price_cap"]

    def agent(obs, config=None):
        try:
            act = base_agent(obs, config)
        except TypeError:
            act = base_agent(obs)
        if act is None:
            act = {"farmer": ["PASS"], "hands": [], "market": []}
        mkt = act.get("market")
        if not mkt:
            return act
        wheat_orders = [o for o in mkt if _is_wheat_sell(o)]
        if not wheat_orders:
            return act
        total = sum(int(o[2]) for o in wheat_orders)
        price = _wheat_price(obs)
        # 仅当 pressure 信号(价<=price_cap)且单步卖量超限才截断
        if total > step_cap and price <= price_cap:
            keep = [o for o in mkt if not _is_wheat_sell(o)]
            keep.append(["SELL", "WHEAT", int(step_cap)])
            act["market"] = keep[:10]
        return act

    return agent


if __name__ == "__main__":
    print("levels:", LEVELS)
    ag = make_wheat_controlled("v11E", "mild")
    print("mild wrapper OK:", type(ag).__name__)
