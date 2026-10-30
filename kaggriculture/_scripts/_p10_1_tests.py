# -*- coding: utf-8 -*-
"""P10.1 micro-tests T1–T7 on extracted executor primitives."""
from __future__ import annotations

import csv
from collections import deque
from pathlib import Path
from types import SimpleNamespace

import sys
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from p10_executor.intents import Intent, Status  # noqa: E402
from p10_executor.primitives import (  # noqa: E402
    DayState, repair_weeds, projected_shed, advance_sales,
    subtract_advanced_sales, liquidate,
)
from p10_executor.validators import sanitize_action, clamp_market  # noqa: E402
from p10_executor.core import TacticalExecutor  # noqa: E402


def T1():
    st = DayState()
    pos = [(4, 4)]
    tiles = [[None] * 10 for _ in range(10)]
    tiles[4][4] = {"kind": "WEED"}
    action = {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": []}
    out = repair_weeds(action, pos, tiles, st, 24)
    return out["farmer"] == ["DIG"]


def T2():
    st = DayState()
    pos = [(4, 4)]
    tiles = [[None] * 10 for _ in range(10)]
    tiles[4][4] = {"kind": "WEED"}
    repair_weeds({"farmer": ["PLANT", "WHEAT"], "hands": []}, pos, tiles, st, 24)
    tiles[4][4] = None
    out = repair_weeds({"farmer": ["PASS"], "hands": []}, pos, tiles, st, 25)
    return out["farmer"] == ["PLANT", "WHEAT"]


def T3():
    pos = [(4, 4)]
    shed = {"WHEAT": 10, "MILK": 2}
    action = {"farmer": ["PICKUP", "WHEAT", 3], "hands": [], "market": []}
    stock = projected_shed(action, pos, None, shed, [{}], lambda p: True)
    return stock.get("WHEAT") == 7


def T4():
    # milk 200*3 > wheat 25*5 → milk first
    pos = [(4, 4)]
    shed = {"WHEAT": 5, "MILK": 3}
    prices = {"WHEAT": 25, "MILK": 200}
    action = liquidate(pos, shed, [{}], prices, lambda p: True)
    sells = [o for o in action["market"] if o[0] == "SELL"]
    return action["farmer"] == ["DROP"] and sells and sells[0][1] == "MILK"


def T5():
    st = DayState()
    pos = [(4, 4)]
    stock = {"WHEAT": 50, "MILK": 10}
    prices = {"WHEAT": 25, "MILK": 100}
    planned = {"WHEAT": 5, "MILK": 4}
    action = advance_sales({"farmer": ["PASS"], "hands": [], "market": []}, stock, prices, planned, st, 49)
    items = [o[1] for o in action["market"] if o[0] == "SELL"]
    return "MILK" in items and "WHEAT" not in items


def T6():
    st = DayState()
    pos = [(4, 4)]
    stock = {"MILK": 10}
    prices = {"MILK": 100}
    action = advance_sales({"farmer": ["PASS"], "hands": [], "market": []}, stock, prices, {"MILK": 4}, st, 49)
    assert st.sale_due_step == 50
    action2 = subtract_advanced_sales({"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 4]]}, st, 50)
    return action2["market"][0][2] == 0


def T7():
    # invalid / empty sell must be clamped
    out = sanitize_action(
        {"farmer": ["FLY"], "hands": [], "market": [["SELL", "MELON", 5], ["SELL", "NOT", 1]]},
        shed={"WHEAT": 2}, money=0, prices={},
    )
    ok = out["farmer"] == ["PASS"] and all(o[1] == "WHEAT" or o[1] != "MELON" for o in out["market"])
    # melon stock 0 → dropped
    ok = ok and not any(o[1] == "MELON" for o in out["market"])
    return ok


def T_exec_sell():
    ex = TacticalExecutor()
    obs = {
        "step": 100, "player": 0,
        "farms": [{"money": 1000, "farmer": [4, 4], "hands": [], "tiles": [[None]*10 for _ in range(10)]}],
        "private": {"shed": {"MILK": 8}, "inventories": [{}], "seeds": {}},
        "market": {"prices": {"MILK": 100}},
        "town": {"unlocked_shops": []},
    }
    r = ex.step(obs, Intent.SELL_AVAILABLE)
    sells = [o for o in r.action["market"] if o[0] == "SELL"]
    return r.status in (Status.SUCCESS, Status.REPAIRED) and any(o[1] == "MILK" for o in sells)


def main():
    tests = [T1, T2, T3, T4, T5, T6, T7, T_exec_sell]
    rows = []
    for fn in tests:
        try:
            ok = bool(fn())
            rows.append({"test": fn.__name__, "pass": ok})
            print(f"  {fn.__name__}: {'PASS' if ok else 'FAIL'}")
        except Exception as e:
            rows.append({"test": fn.__name__, "pass": False})
            print(f"  {fn.__name__}: ERROR {e}")
    n = sum(1 for r in rows if r["pass"])
    print(f"\n{n}/{len(rows)} pass  ({100*n/len(rows):.0f}%)")
    path = ROOT / "p10_1_executor_tests.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "pass"])
        w.writeheader()
        w.writerows(rows)
    print("wrote", path)


if __name__ == "__main__":
    main()
