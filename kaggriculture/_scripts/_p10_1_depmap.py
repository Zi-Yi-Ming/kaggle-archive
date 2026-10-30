# -*- coding: utf-8 -*-
"""P10.1 dependency map: R2 modules tactical vs strategic vs tape-bound."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")

ROWS = [
    # module, purpose, class, inputs, outputs, repair_dep, tape_dep
    ("FarmView", "obs adapter", "TACTICAL", "observation", "tiles/pos/shed/prices", "", "no"),
    ("repair_weeds", "DIG + queue blocked plant/build", "TACTICAL", "action,view,state,step", "action", "self", "no"),
    ("projected_shed", "stock after pickup/drop/place", "TACTICAL", "action,view", "stock dict", "", "no"),
    ("subtract_advanced_sales", "undo pre-sold qty next turn", "TACTICAL", "action,state,step", "action", "R3", "needs sale_due_step"),
    ("advance_sales", "pull next-turn sells forward", "HYBRID", "action,view,state,tape,step", "action", "R3,R4", "yes — tape[next_step]"),
    ("liquidate", "terminal dump @718", "TACTICAL", "view", "action", "R4", "step-bound 718"),
    ("Policy.act", "tape + repairs", "TAPE_BOUND", "obs", "action", "R1,R3,R4,R5", "yes — 13 tapes"),
    ("V217/V218 routes", "path/route planning", "STRATEGIC/TACTICAL", "obs,action", "action", "walk", "partial"),
    ("V219 walk/worker", "move/feed/care", "TACTICAL", "obs,state", "command", "R6", "no"),
    ("V224 sales_first", "reorder sells", "TACTICAL", "action", "action", "", "no"),
    ("V226 topup", "cash/input recovery", "TACTICAL", "obs,action,state", "action", "R10", "no"),
    ("V231 controller", "capacity/cash adjust", "HYBRID", "obs,action,state", "action", "R11", "partial"),
    ("V233 sheep layer", "wool/fert credit + worker override", "HYBRID", "obs,action,state", "action", "R7,R8", "day>=12 commit"),
    ("V234 feed rescue", "BUY WHEAT if hungry sheep", "TACTICAL", "obs,action,state", "action", "R9", "no"),
    ("SHOP_PLANS", "first-2 shops → plan id", "TAPE_BOUND", "shops", "plan index", "", "yes"),
    ("_INLINE_TAPES", "719-step action library", "TAPE_BOUND", "plan,step", "action", "", "yes — full season"),
]


def main():
    path = ROOT / "p10_1_dependency_map.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["module", "purpose", "class", "inputs", "outputs", "repair_dep", "tape_dep"])
        for r in ROWS:
            w.writerow(r)
    tact = sum(1 for r in ROWS if r[2] == "TACTICAL")
    print(f"modules={len(ROWS)} TACTICAL={tact} written {path}")


if __name__ == "__main__":
    main()
