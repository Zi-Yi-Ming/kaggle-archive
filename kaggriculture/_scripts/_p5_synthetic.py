# -*- coding: utf-8 -*-
"""P5 synthetic market tests — correct market=[[op,...],...] format."""
from __future__ import annotations

import csv
from pathlib import Path

from kaggle_environments import make

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")


def run(seq0, seq1, steps=48, seed=1):
    """seqX: list per step; each step is a list of market orders."""

    def agt(idx):
        def a(obs):
            step = int(obs.get("step") or 0)
            seq = seq0 if idx == 0 else seq1
            market = seq[step] if step < len(seq) else []
            return {"farmer": ["PASS"], "hands": [], "market": market}
        return a

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = steps
    env.configuration["seed"] = seed
    env.run([agt(0), agt(1)])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    shed0 = dict((f[0]["observation"].get("private") or {}).get("shed") or {})
    inv = ((f[0]["observation"].get("market") or {}).get("inventory") or {})
    return b0, b1, inv.get("WHEAT"), shed0.get("WHEAT")


def main():
    rows = []

    # A: both buy 5 wheat × 4 steps then both sell 1/step × 10
    buy = [["BUY_PRODUCT", "WHEAT", 5]]
    sell1 = [["SELL", "WHEAT", 1]]
    sA = buy * 4 + sell1 * 10 + [[]] * 10
    b0, b1, inv, sh = run(sA, sA, steps=30)
    rows.append({"test": "A_lockstep_sell", "bank0": b0, "bank1": b1, "inv_wheat": inv, "shed0_wheat": sh})
    print("A lockstep", b0, b1, "diff", b0 - b1, "shed0", sh)

    # B: both have stock; p0 dumps 10 in ONE order, p1 dumps 1×10
    sB0 = buy * 4 + [["SELL", "WHEAT", 10]] + [[]] * 12
    sB1 = buy * 4 + sell1 * 10 + [[]] * 2
    b0, b1, inv, sh = run(sB0, sB1, steps=30)
    rows.append({"test": "B_dump10_vs_1x10", "bank0": b0, "bank1": b1, "inv_wheat": inv, "shed0_wheat": sh})
    print("B dump10 vs 1x10", b0, b1, "diff", b0 - b1)

    # C: p0 buy then sell same turn (two orders); p1 idle after buy
    sC0 = [["BUY_PRODUCT", "WHEAT", 1]] * 3 + [["BUY_PRODUCT", "WHEAT", 1], ["SELL", "WHEAT", 1]] * 5 + [[]] * 5
    sC1 = [["BUY_PRODUCT", "WHEAT", 1]] * 3 + [["BUY_PRODUCT", "WHEAT", 1]] * 5 + [[]] * 10
    b0, b1, inv, sh = run(sC0, sC1, steps=20)
    rows.append({"test": "C_sell_then_buy_same_turn", "bank0": b0, "bank1": b1, "inv_wheat": inv, "shed0_wheat": sh})
    print("C sell-then-buy", b0, b1, "diff", b0 - b1)

    # D: same lockstep sell — player0 vs player1 price if they dump same turn
    # both buy 20, then both dump 20 in one order on step 8
    buy20 = [["BUY_PRODUCT", "WHEAT", 5]] * 4
    dump = [["SELL", "WHEAT", 20]]
    sD0 = buy20 + dump + [[]] * 8
    sD1 = buy20 + dump + [[]] * 8
    b0, b1, inv, sh = run(sD0, sD1, steps=20)
    rows.append({"test": "D_simultaneous_dump20", "bank0": b0, "bank1": b1, "inv_wheat": inv, "shed0_wheat": sh})
    print("D simultaneous dump20", b0, b1, "diff", b0 - b1)

    # E: p0 sells 1 first slot then buys; p1 buys first then sells — after equal stock
    sE0 = buy20 + [["SELL", "WHEAT", 1], ["BUY_PRODUCT", "WHEAT", 1]] * 6 + [[]] * 4
    sE1 = buy20 + [["BUY_PRODUCT", "WHEAT", 1], ["SELL", "WHEAT", 1]] * 6 + [[]] * 4
    b0, b1, inv, sh = run(sE0, sE1, steps=20)
    rows.append({"test": "E_slot_order_sell_buy", "bank0": b0, "bank1": b1, "inv_wheat": inv, "shed0_wheat": sh})
    print("E slot order", b0, b1, "diff", b0 - b1)

    path = ROOT / "p5_synthetic_market_tests.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", path)


if __name__ == "__main__":
    main()
