# -*- coding: utf-8 -*-
"""Research-only synthetic opponents v2 (TEMP, NOT submission strategies).

方案:包装 wheat_walter(tier1 纯 WHEAT 生产,已验证可生产 bank~6000),
只拦截/改写其 market SELL 节奏,生产层(farmer 动作)完全不动。

卖货节奏(唯一差异):
  aggressive: 每步 shed 有 WHEAT 就全卖(近似 walter 原行为,更激进)
  hoarder:    现金 < 3000 才卖
  balanced:   现金 < 12000 卖 30(留库存)
  delayed:    step<480 不卖;480-600 现金<800 救急卖 10;>=600 全清
"""
import os
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
_ww_mod = None


def _wheat_walter():
    global _ww_mod
    if _ww_mod is None:
        spec = importlib.util.spec_from_file_location(
            "synth_ww", os.path.join(BASE, "reference_agents", "wheat_walter.py"))
        _ww_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_ww_mod)
    return _ww_mod


def _is_sell(o):
    return isinstance(o, list) and o and o[0] == "SELL"


def _shed_wheat(obs):
    return int(((obs.get("private") or {}).get("shed") or {}).get("WHEAT", 0) or 0)


def _cash(obs):
    p = int(obs.get("player", 0) or 0)
    farms = obs.get("farms") or []
    if p < len(farms):
        return float(farms[p].get("money", 0) or 0)
    return 0.0


def _wrap(policy):
    """policy(obs) -> 该步应卖多少(qty<=0 = 不卖)。"""
    base_mod = _wheat_walter()

    def agent(obs, config=None):
        try:
            act = base_mod.agent(obs, config)
        except TypeError:
            act = base_mod.agent(obs)
        if act is None:
            act = {"farmer": ["PASS"], "hands": [], "market": []}
        mkt = [o for o in (act.get("market") or []) if not _is_sell(o)]
        q = policy(obs)
        if q > 0:
            mkt.append(["SELL", "WHEAT", q])
        act["market"] = mkt[:10]
        return act

    return agent


def _aggressive(obs):
    return _shed_wheat(obs)          # 每步全卖


def _hoarder(obs):
    return _shed_wheat(obs) if _cash(obs) < 3000 else 0


def _balanced(obs):
    if _cash(obs) < 12000:
        return min(_shed_wheat(obs), 30)
    return 0


def _delayed(obs):
    step = int(obs.get("step", 0) or 0)
    if step >= 600:
        return _shed_wheat(obs)      # 末期全清
    if step >= 480 and _cash(obs) < 800:
        return min(_shed_wheat(obs), 10)
    return 0


SYNTHETIC = {
    "aggressive": _aggressive,
    "hoarder": _hoarder,
    "balanced": _balanced,
    "delayed": _delayed,
}
_FP = {
    "aggressive": "sell ALL WHEAT every step",
    "hoarder": "sell only when cash < 3000",
    "balanced": "sell <=30 when cash < 12000",
    "delayed": "no sell <480; dump all >=600",
}


def load_synthetic(key):
    """返回包装后的可调用 agent。"""
    if key not in SYNTHETIC:
        raise KeyError(key)
    return _wrap(SYNTHETIC[key])


def fingerprint(key):
    return _FP.get(key, "?")
