# -*- coding: utf-8 -*-
"""Heterogeneous opponent pool for v13 research (TEMP, NOT production).

Pool 构成(标注可还原性):
  精确还原: v11E(cleo_v11_E_backup.py), v12(cleo_v10.py 当前), D/B(flag 组合)
  v10 近似: cleo_v11_E_backup.py 全 _V11_* 关(rollback 设计:全关 ≈ v10 行为)
  社区对手: reference_agents/ 全 10 个(tier 0-9,天然策略异构)
  不可用:   我们自己的 v7/v8/v9 提交代码(清理时已删文件,无备份)
            → 用 reference_agents/broker_bea.py(≈v7 对标)、closer_cleo.py(≈v9 对标)

用法:
    from _pm_pool import POOL, load_agent
    mod = load_agent('v11E')          # 返回可调用 agent(obs)->action
"""
import os
import importlib.util
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RA = os.path.join(BASE, "reference_agents")

# ---------------- v11 E / v12 / D / B / v10-approx(全部源于 cleo_v10.py 家族) ----------------
V10_BACKUP = os.path.join(BASE, "cleo_v11_E_backup.py")   # 载入后按 flags 覆盖
V12_CURRENT = os.path.join(BASE, "cleo_v10.py")           # 当前 = v12(sequential False)

# 已知 flag 组合(与 _pm_ablation.py 一致)
_F = {
    "E":  dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
               _V11_MARKET_MODEL=True, _V11_BELIEF=True,
               _V11_HAZARD=True, _V11_SEQUENTIAL=True),
    "D":  dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
               _V11_MARKET_MODEL=True, _V11_BELIEF=True,
               _V11_HAZARD=True, _V11_SEQUENTIAL=False),
    "B":  dict(_V11_TRANSITION_FIX=True, _V11_SHOP_COUNTER=True,
               _V11_MARKET_MODEL=True, _V11_BELIEF=False,
               _V11_HAZARD=False, _V11_SEQUENTIAL=False),
    "A":  dict(_V11_TRANSITION_FIX=False, _V11_SHOP_COUNTER=False,
               _V11_MARKET_MODEL=False, _V11_BELIEF=False,
               _V11_HAZARD=False, _V11_SEQUENTIAL=False),  # ≈ v10 rollback
}


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_v_family(key):
    """载入 v11E/v12/D/B/v10approx。返回可调用 agent。"""
    key = key.lower()
    if key == "v11e":
        m = _load_module(V10_BACKUP, "v11E")
        return m.agent
    if key == "v12":
        m = _load_module(V12_CURRENT, "v12")
        return m.agent
    if key in ("d", "b", "a"):
        m = _load_module(V10_BACKUP, key)
        for k, v in _F[key.upper()].items():
            setattr(m, k, v)
        return m.agent
    raise KeyError(key)


# ---------------- 社区对手(tier 0-9) ----------------
COMMUNITY = {  # slug -> (文件名, tier, 策略指纹)
    "fallow_finn":    ("fallow_finn.py", 0, "no-op,reward floor"),
    "wheat_walter":   ("wheat_walter.py", 1, "wheat-only,harvests early"),
    "rotation_rosa":  ("rotation_rosa.py", 2, "3-crop rotation,hires 4 hands"),
    "homestead_hana": ("homestead_hana.py", 3, "1 quadrant,8 hands,carrot-led"),
    "melon_mateo":    ("melon_mateo.py", 4, "MELON-led,holds floor"),
    "rancher_rita":   ("rancher_rita.py", 5, "COW/SHEEP ranching"),
    "broker_bea":     ("broker_bea.py", 6, "meta plan,market controller(≈v7)"),
    "ledger_lena":    ("ledger_lena.py", 7, "ledger-driven sells"),
    "slotter_silas":  ("slotter_silas.py", 8, "slot-timed sells"),
    "closer_cleo":    ("closer_cleo.py", 9, "in-place selling(≈v9)"),
}
_comm_cache = {}


def load_community(slug):
    if slug not in COMMUNITY:
        raise KeyError(slug)
    if slug not in _comm_cache:
        fn = COMMUNITY[slug][0]
        _comm_cache[slug] = _load_module(os.path.join(RA, fn), "comm_" + slug)
    return _comm_cache[slug].agent


# ---------------- Pool 定义 ----------------
# key: (loader, 描述, 类型)
POOL = {
    "v11E": (lambda: load_v_family("v11E"), "v11 E 全功能(当前线上最强,949.9)", "self"),
    "v12":  (lambda: load_v_family("v12"),  "v12 E-minus-beam(873.7)", "self"),
    "D":    (lambda: load_v_family("d"),    "D no-sequential(belief+hazard)", "self"),
    "B":    (lambda: load_v_family("b"),    "B P0-only", "self"),
    "A":    (lambda: load_v_family("a"),
             "A all-off — APPROXIMATE historical policy(≈v10 rollback,非 v10 字节级复刻)", "self"),
    "fallow_finn": (lambda: load_community("fallow_finn"), "no-op", "comm"),
    "wheat_walter": (lambda: load_community("wheat_walter"), "wheat early", "comm"),
    "rotation_rosa": (lambda: load_community("rotation_rosa"), "rotation+hires", "comm"),
    "homestead_hana": (lambda: load_community("homestead_hana"), "quadrant+hands", "comm"),
    "melon_mateo": (lambda: load_community("melon_mateo"), "melon-led", "comm"),
    "rancher_rita": (lambda: load_community("rancher_rita"), "ranching", "comm"),
    "broker_bea": (lambda: load_community("broker_bea"),
                   "community tier6 meta plan — APPROXIMATE historical policy(≈v7,非 v7 字节级复刻)", "comm"),
    "ledger_lena": (lambda: load_community("ledger_lena"), "ledger sells", "comm"),
    "slotter_silas": (lambda: load_community("slotter_silas"), "slot sells", "comm"),
    "closer_cleo": (lambda: load_community("closer_cleo"),
                    "community tier9 in-place — APPROXIMATE historical policy(≈v9,非 v9 字节级复刻)", "comm"),
}


def load_agent(key):
    """按 key 加载 agent(每次调用返回新模块实例 = 干净状态)。"""
    if key not in POOL:
        raise KeyError(key)
    return POOL[key][0]()


def pool_fingerprints():
    """返回 pool 描述(供报告)。"""
    rows = []
    for key, (_, desc, typ) in POOL.items():
        rows.append((key, typ, desc))
    return rows


if __name__ == "__main__":
    print("=== Heterogeneous Opponent Pool ===")
    for key, typ, desc in pool_fingerprints():
        print("  %-14s [%s] %s" % (key, typ, desc))
