# -*- coding: utf-8 -*-
"""P14.2 offline: animal EV + joint alloc reconstruction."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from p14_2_joint_portfolio.livestock import animal_value, ANIMALS  # noqa: E402
from p14_2_joint_portfolio.joint import joint_allocate  # noqa: E402

PRICES = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
          "EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40}


def main():
    print("=== animal marginal EV ===")
    rows = []
    for day in (0, 5, 10):
        for cash in (3000, 1000, 400):
            print(f"  day={day} cash={cash}")
            for a in ANIMALS:
                v = animal_value(a, day, cash, PRICES)
                print(f"    {a:6s} ev={v['ev']:8.1f} yields={v['n_yields']} "
                      f"gross={v['gross']:.0f} feed={v['feed_cost']:.0f} "
                      f"fert={v['fert']:.0f} ttc={v['time_to_cash']}")
                rows.append({"day": day, "cash": cash, **v})

    print("\n=== joint allocate ===")
    cases = [
        ("d0_start", 25, 3000, 0, {}, 5, 1),
        ("d0_empty20", 20, 3000, 0, {}, 6, 1),
        ("d2_after", 8, 400, 2, {"COW": 2, "SHEEP": 2}, 6, 1),
        ("d5_mid", 6, 800, 5, {"COW": 2, "SHEEP": 2}, 8, 2),
        ("d8", 4, 1500, 8, {"COW": 4, "SHEEP": 2}, 8, 2),
    ]
    jrows = []
    for name, empty, cash, day, live, farmers, land in cases:
        j = joint_allocate(empty, cash, day, PRICES, live, n_farmers=farmers, n_land=land)
        print(f"  {name}: crops={j['crops']} animals={j['animals']} wheat_tiles={j['wheat_tiles']}")
        jrows.append({"case": name, "empty": empty, "cash": cash, "day": day,
                      "crops": str(j["crops"]), "animals": str(j["animals"]),
                      "wheat_tiles": j["wheat_tiles"]})

    print("\n=== R2 obs d0-1 vs joint ===")
    print("  R2: buy melon d0, field d1 = W7 M12; animals start d1 COW2 SHEEP2")
    j = joint_allocate(25, 3000, 0, PRICES, {}, n_farmers=5)
    print(f"  joint d0: crops={j['crops']} animals={j['animals']}")
    print(f"  NOT hardcoded 8/6/3; animal targets={j['animals']}")

    out = ROOT / "p14_2_animal_value.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    out = ROOT / "p14_2_portfolio_allocations.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(jrows[0].keys()))
        w.writeheader()
        w.writerows(jrows)
    print("wrote", out.name)


if __name__ == "__main__":
    main()
