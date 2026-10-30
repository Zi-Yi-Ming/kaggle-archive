# -*- coding: utf-8 -*-
"""P20: expand counterfactual value surface over days 7–12 × 3 tails."""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))

# reuse P19 runner
import importlib.util
spec = importlib.util.spec_from_file_location(
    "p19cf", str(ROOT / "_p19_counterfactual.py")
)
p19 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p19)


def main():
    rows = []
    for seed in (1, 2):
        for day in (7, 8, 9, 10, 11, 12):
            for tail in ("MAIN", "CASH_WINDOW", "HERD_SCALE"):
                rows.append(p19.run(day, tail, seed, seat=0))

    out = ROOT / "p20_value_surface.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # pivot: best by cash+5 and by final
    print("\n=== SURFACE: cash+5 / final by (seed,day) ===")
    groups = defaultdict(list)
    for r in rows:
        groups[(r["seed"], r["force_day"])].append(r)
    boundary_rows = []
    for key, g in sorted(groups.items()):
        by5 = {x["tail"]: x["cash_d5"] or 0 for x in g}
        byf = {x["tail"]: x["final"] for x in g}
        best5 = max(by5, key=by5.get)
        bestf = max(byf, key=byf.get)
        st = g[0]
        print(f"  s{key[0]} d{key[1]}: c0={st['cash_force']:.0f} mel={st['melon_force']} "
              f"ani={st['animals_force']} | +5: {by5} best5={best5} | fin: bestf={bestf}")
        boundary_rows.append({
            "seed": key[0], "day": key[1],
            "cash0": st["cash_force"], "melon": st["melon_force"],
            "animals": st["animals_force"], "plant": st["plant_force"],
            "shed": st["shed_force"],
            "c5_MAIN": by5.get("MAIN"), "c5_CASH": by5.get("CASH_WINDOW"),
            "c5_HERD": by5.get("HERD_SCALE"),
            "best5": best5,
            "fin_MAIN": byf.get("MAIN"), "fin_CASH": byf.get("CASH_WINDOW"),
            "fin_HERD": byf.get("HERD_SCALE"),
            "best_final": bestf,
            "cash_margin5": (by5.get("CASH_WINDOW") or 0) - max(by5.get("MAIN") or 0, by5.get("HERD_SCALE") or 0),
        })

    out2 = ROOT / "p20_boundary_table.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(boundary_rows[0].keys()))
        w.writeheader()
        w.writerows(boundary_rows)

    # simple boundary rules empirically
    print("\n=== EMPIRICAL BOUNDARY (cash+5) ===")
    cash_win = [r for r in boundary_rows if r["best5"] == "CASH_WINDOW"]
    cash_lose = [r for r in boundary_rows if r["best5"] != "CASH_WINDOW"]
    print(f"  CASH wins +5: {len(cash_win)}/{len(boundary_rows)}")
    if cash_win:
        print(f"  when win: melon={ [r['melon'] for r in cash_win] } "
              f"cash0={ [r['cash0'] for r in cash_win] } day={ [r['day'] for r in cash_win] }")
    if cash_lose:
        print(f"  when not: melon={ [r['melon'] for r in cash_lose] } "
              f"cash0={ [r['cash0'] for r in cash_lose] } day={ [r['day'] for r in cash_lose] } "
              f"best={ [r['best5'] for r in cash_lose] }")

    # rule candidate: CASH if melon>=5 and cash0<2000
    rule_hits = 0
    rule_total = 0
    for r in boundary_rows:
        pred = "CASH_WINDOW" if (r["melon"] >= 5 and (r["cash0"] or 0) < 2000) else (
            "HERD_SCALE" if (r["animals"] or 0) < 4 and (r["cash0"] or 0) >= 800 else "MAIN"
        )
        rule_total += 1
        if pred == r["best5"]:
            rule_hits += 1
    print(f"  simple rule acc vs best5: {rule_hits}/{rule_total}")
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
