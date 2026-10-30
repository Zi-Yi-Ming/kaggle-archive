# -*- coding: utf-8 -*-
"""Debug hist_features with synthetic + real CSV."""
import csv
from pathlib import Path

# synthetic
def hist_features_syn(recs, i, k):
    day = recs[i]["day"]
    past = [r for r in recs if day - k <= r["day"] < day]
    if not past:
        return ()
    hires = sum(r["hires"] for r in past)
    sells = sum(r["sells"] for r in past)
    buys = sum(r["buys"] for r in past)
    first = past[0]
    last = past[-1]
    d_money = last["money"] - first["money"]
    d_animals = last["animals"] - first["animals"]
    d_plants = last["plants"] - first["plants"]
    return (
        min(hires, 20) // 4,
        min(sells, 20) // 4,
        min(buys, 10) // 2,
        max(-5, min(5, int(d_money / 500))),
        max(-5, min(5, d_animals)),
        max(-5, min(5, d_plants // 3)),
    )

recs = []
for day in range(30):
    for hour in range(0, 24, 6):
        recs.append({"day": day, "hour": hour, "money": 1000+day, "hires": 3,
                     "sells": 2, "buys": 1, "animals": day//2, "plants": day})
for i in (0, 20, 50, 100):
    print(i, recs[i]["day"], hist_features_syn(recs, i, 1), hist_features_syn(recs, i, 5))

# real CSV
rows = list(csv.DictReader((Path(r"D:\桌面\Kaggle\kaggriculture")/"p30_history_features.csv").open(encoding="utf-8")))
for r in rows:
    for k in ("day","hour","money","hands","animals","plants","melon","shed_total","n_shops","hires","sells","buys","seed"):
        r[k] = int(float(r[k]))
print("real n", len(rows))
for i in (0, 50, 200, 500):
    print("real", i, rows[i]["day"], hist_features_syn(rows, i, 1), hist_features_syn(rows, i, 5))
