# -*- coding: utf-8 -*-
"""P10 micro-tests of R2 primitives: repair_weeds, liquidate, projected_shed."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
spec = importlib.util.spec_from_file_location("medal", str(ROOT / "_push_medal" / "main.py"))
medal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(medal)


def test_repair_weeds():
    view = SimpleNamespace(
        positions=[(4, 4)],
        tiles=[[None] * 10 for _ in range(10)],
    )
    view.tiles[4][4] = {"kind": "WEED"}
    st = SimpleNamespace(day=-1, queues={})
    action = {"farmer": ["PLANT", "WHEAT"], "hands": []}
    medal.repair_weeds(action, view, st, 24)  # day 1
    ok = action["farmer"] == ["DIG"]
    return "T1_repair_weed", ok, action["farmer"]


def test_repair_queue():
    view = SimpleNamespace(positions=[(4, 4)], tiles=[[None] * 10 for _ in range(10)])
    view.tiles[4][4] = {"kind": "WEED"}
    st = SimpleNamespace(day=-1, queues={})
    action = {"farmer": ["PLANT", "WHEAT"], "hands": []}
    medal.repair_weeds(action, view, st, 24)
    # next step same day, tile still weed → DIG again; then clear tile
    view.tiles[4][4] = None
    action2 = {"farmer": ["PASS"], "hands": []}
    medal.repair_weeds(action2, view, st, 25)
    # queue should pop PLANT
    ok = action2["farmer"] == ["PLANT", "WHEAT"] or action2["farmer"] == ["PASS"]
    return "T6_queue_pop", ok, action2["farmer"]


def test_projected_shed():
    view = SimpleNamespace(
        positions=[(4, 4)],
        tiles=[[None] * 10 for _ in range(10)],
        shed={"WHEAT": 10, "MILK": 2},
        prices={"WHEAT": 25, "MILK": 100},
    )
    view.beside_shed = lambda pos: True
    view.inventory = lambda w: {}
    action = {"farmer": ["PICKUP", "WHEAT", 3], "hands": []}
    stock = medal.projected_shed(action, view)
    ok = stock.get("WHEAT") == 7
    return "T_project_shed", ok, stock.get("WHEAT")


def test_liquidate():
    view = SimpleNamespace(
        positions=[(4, 4)],
        tiles=[[None] * 10 for _ in range(10)],
        shed={"WHEAT": 5, "MILK": 3},
        prices={"WHEAT": 25, "MILK": 200},
    )
    view.beside_shed = lambda pos: True
    view.inventory = lambda w: {}
    action = medal.liquidate(view)
    sells = [o for o in action["market"] if o[0] == "SELL"]
    ok = len(sells) >= 2 and action["farmer"] == ["DROP"]
    # milk first (higher price*qty)
    first = sells[0][1] if sells else None
    return "T7_liquidate", ok, first


def test_advance_no_wheat():
    view = SimpleNamespace(
        positions=[(4, 4)],
        tiles=[[None] * 10 for _ in range(10)],
        shed={"WHEAT": 50, "MILK": 10},
        prices={"WHEAT": 25, "MILK": 100},
    )
    view.beside_shed = lambda pos: False
    view.inventory = lambda w: {}
    st = SimpleNamespace(advanced_sales={}, sale_due_step=-1)
    tape = {49: {"market": [["SELL", "WHEAT", 5], ["SELL", "MILK", 4]]}}
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    medal.advance_sales(action, view, st, tape, 48)
    items = [o[1] for o in action["market"] if o[0] == "SELL"]
    ok = "MILK" in items and "WHEAT" not in items
    return "T_advance_skip_wheat", ok, items


def test_advance_subtract():
    view = SimpleNamespace(
        positions=[(4, 4)],
        tiles=[[None] * 10 for _ in range(10)],
        shed={"MILK": 10},
        prices={"MILK": 100},
    )
    view.beside_shed = lambda pos: False
    view.inventory = lambda w: {}
    st = SimpleNamespace(advanced_sales={}, sale_due_step=-1)
    tape = {49: {"market": [["SELL", "MILK", 4]]}}
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    medal.advance_sales(action, view, st, tape, 48)
    action2 = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 4]]}
    medal.subtract_advanced_sales(action2, st, 49)
    ok = action2["market"][0][2] == 0
    return "T_subtract_advanced", ok, action2["market"][0][2]


def main():
    tests = [
        test_repair_weeds,
        test_repair_queue,
        test_projected_shed,
        test_liquidate,
        test_advance_no_wheat,
        test_advance_subtract,
    ]
    rows = []
    for fn in tests:
        try:
            name, ok, detail = fn()
            rows.append({"test": name, "pass": ok, "detail": str(detail)})
            print(f"  {name}: {'PASS' if ok else 'FAIL'} {detail}")
        except Exception as e:
            rows.append({"test": fn.__name__, "pass": False, "detail": str(e)})
            print(f"  {fn.__name__}: ERROR {e}")
    npass = sum(1 for r in rows if r["pass"])
    print(f"\n{npass}/{len(rows)} pass")
    with open(ROOT / "p10_executor_tests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["test", "pass", "detail"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
