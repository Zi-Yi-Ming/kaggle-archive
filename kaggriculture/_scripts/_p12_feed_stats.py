# -*- coding: utf-8 -*-
import csv, json
from pathlib import Path
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
rows = list(csv.DictReader((ROOT / "p12_day_traces.csv").open(encoding="utf-8")))
p11 = [r for r in rows if r["label"] == "P11"]
r2 = [r for r in rows if r["label"] == "R2"]


def m(lst, k):
    v = [float(r[k]) for r in lst if r.get(k) not in ("", None)]
    return sum(v) / len(v) if v else 0.0


def ops(lst, op):
    return sum(json.loads(r["ops"] or "{}").get(op, 0) for r in lst)


print("day | P11 hungry yield FEED PICKUP CARE | R2 hungry yield FEED")
for d in range(6, 22):
    ps = [r for r in p11 if int(r["day"]) == d]
    rs = [r for r in r2 if int(r["day"]) == d]
    if not ps:
        continue
    print(
        f"d{d:02d} | {m(ps,'hungry'):5.1f} {m(ps,'yield_units'):5.1f} "
        f"{ops(ps,'FEED'):4.0f} {ops(ps,'PICKUP'):4.0f} {ops(ps,'CARE'):4.0f} | "
        f"{m(rs,'hungry'):5.1f} {m(rs,'yield_units'):5.1f} {ops(rs,'FEED'):4.0f}"
    )

print("\n=== P11 shed products mean d10/d15/d20 ===")
for d in (10, 15, 20):
    for label, subset in (("R2", r2), ("P11", p11)):
        sheds = [json.loads(r["shed"]) for r in subset if int(r["day"]) == d]
        keys = ("MILK", "WOOL", "EGG", "WHEAT", "FERTILIZER")
        avg = {k: sum(float(s.get(k) or 0) for s in sheds) / len(sheds) for k in keys}
        print(f"  d{d} {label}: {avg}")
