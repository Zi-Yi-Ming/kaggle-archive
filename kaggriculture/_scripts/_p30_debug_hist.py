# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"D:\桌面\Kaggle\kaggriculture")
from _p30a_history import hist_features, cur_bucket, record

# quick: record one seed and inspect hist
recs, bank = record(1)
print("n", len(recs), "bank", bank)
# print a few
for i in (0, 100, 300, 500, 700):
    r = recs[i]
    h1 = hist_features(recs, i, 1)
    h5 = hist_features(recs, i, 5)
    print(f"i={i} day={r['day']} hour={r['hour']} money={r['money']:.0f} sig={r['sig']!r} h1={h1} h5={h5}")
