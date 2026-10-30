# -*- coding: utf-8 -*-
import csv
from pathlib import Path
rows = list(csv.DictReader((Path(r"D:\桌面\Kaggle\kaggriculture") / "p16_1_trigger_features.csv").open(encoding="utf-8")))
print("SKEL trajectories d7-10:")
for r in rows:
    if r["label"] == "SKEL":
        print(f"  s{r['seed']} seat{r['seat']} d{r['day']} $={float(r['money']):.0f} "
              f"fm={r['field_melon']} ready={r['melon_ready']} sm={r['shed_melon']} "
              f"wh={r['field_wheat']} st={r['field_straw']} milk={r['shed_milk']} "
              f"final={float(r['final']):.0f}")
print("\nBR vs SKEL finals:")
for r in rows:
    if r["day"] == "10":
        print(f"  {r['label']} s{r['seed']} seat{r['seat']} d10$={float(r['money']):.0f} "
              f"ready={r['melon_ready']} sm={r['shed_melon']} final={float(r['final']):.0f}")
