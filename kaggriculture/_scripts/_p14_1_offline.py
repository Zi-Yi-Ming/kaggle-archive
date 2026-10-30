# -*- coding: utf-8 -*-
"""P14.1 offline: reconstruct portfolio on d0/d1-like states vs R2 observed."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from p14_1_portfolio.allocator import allocate_portfolio, crop_ev, horizon_of, CROPS  # noqa: E402

PRICES0 = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250}


def main():
    print("=== crop EV at d0 cash=3000 ===")
    for c in CROPS:
        print(f"  {c:12s} h={horizon_of(c):6s} ev={crop_ev(c, PRICES0[c], 0, 3000):8.1f}")

    print("\n=== allocate on typical early states ===")
    cases = [
        ("d0_start", 25, 3000, 0, 5),
        ("d0_poor", 25, 800, 0, 5),
        ("d1_after_buy", 10, 200, 1, 6),
        ("d5_mid", 8, 700, 5, 8),
        ("d8_late", 12, 1500, 8, 8),
        ("d15_too_late_long", 10, 2000, 15, 8),
    ]
    rows = []
    for name, empty, cash, day, farmers in cases:
        alloc = allocate_portfolio(empty, cash, day, PRICES0, n_farmers=farmers)
        print(f"  {name}: empty={empty} cash={cash} d{day} -> {alloc}")
        row = {"case": name, "empty": empty, "cash": cash, "day": day, "farmers": farmers}
        for c in CROPS:
            row[c] = alloc.get(c, 0)
        row["total"] = sum(alloc.values())
        row["has_long"] = int(any(horizon_of(c) == "long" and alloc.get(c, 0) > 0 for c in CROPS))
        row["has_short"] = int(any(horizon_of(c) == "short" and alloc.get(c, 0) > 0 for c in CROPS))
        rows.append(row)

    # R2 observed d1 for comparison
    r2_d1 = {"WHEAT": 7, "MELON": 12, "STRAWBERRY": 0, "CARROT": 0, "TOMATO": 0}
    recon = allocate_portfolio(25, 27, 1, PRICES0, n_farmers=6)  # R2 d1 cash~27 after spend
    print(f"\n=== R2-like reconstruction (empty=25 cash=27 d1) ===")
    print(f"  planner: {recon}")
    print(f"  R2 obs:  {r2_d1}")
    # also with starting cash (before spend)
    recon0 = allocate_portfolio(25, 3000, 0, PRICES0, n_farmers=5)
    print(f"  planner d0 cash3000: {recon0}")

    # structural match: multi-horizon?
    def mh(a):
        h = set()
        for c, n in a.items():
            if n > 0:
                h.add(horizon_of(c))
        return h

    print(f"  R2 horizons: {mh(r2_d1)}")
    print(f"  planner d1 horizons: {mh(recon)}")
    print(f"  planner d0 horizons: {mh(recon0)}")
    print(f"  B-style wheat-only horizons: {mh({'WHEAT': 15})}")

    out = ROOT / "p14_1_portfolio_allocations.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out.name)

    out = ROOT / "p14_1_crop_value.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["crop", "horizon", "first_yield", "ev_d0_cash3000", "ev_d0_cash200", "seed"])
        for c in CROPS:
            w.writerow([c, horizon_of(c),
                        {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}[c],
                        round(crop_ev(c, PRICES0[c], 0, 3000), 1),
                        round(crop_ev(c, PRICES0[c], 0, 200), 1),
                        {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}[c]])
    print("wrote", out.name)


if __name__ == "__main__":
    main()
