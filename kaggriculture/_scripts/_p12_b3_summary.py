# -*- coding: utf-8 -*-
"""Append B3 results summary row set for report."""
import csv
from pathlib import Path
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
rows = list(csv.DictReader((ROOT / "p12_b3_results.csv").open(encoding="utf-8")))
print("label n mean_bank mean_d20 mean_d29 wins")
for label in ("finn", "R2"):
    sub = [r for r in rows if r["label"] == label]
    def mean(k):
        v = [float(r[k]) for r in sub if r.get(k) not in ("", None)]
        return sum(v)/len(v) if v else float("nan")
    print(f"{label} {len(sub)} bank={mean('my'):.0f} d20={mean('d20'):.0f} d29={mean('d29'):.0f} "
          f"wins={sum(int(r['win']) for r in sub)}")
