# -*- coding: utf-8 -*-
"""P13 analysis: waterfall, top events, product revenue, R2 vs B gap."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
rows = list(csv.DictReader((ROOT / "p13_cash_ledger.csv").open(encoding="utf-8")))
for r in rows:
    for k in ("step", "day", "hour", "qty", "n_events", "market_n", "hands", "n_land", "seed", "seat"):
        r[k] = int(float(r[k])) if r.get(k) not in ("", None) else None
    for k in ("cash_before", "cash_after", "cash_delta", "expected_from_orders", "residual", "unit"):
        r[k] = float(r[k]) if r.get(k) not in ("", None) else None
    r["events"] = json.loads(r.get("events_json") or "[]")
    r["shed_delta"] = json.loads(r.get("shed_delta") or "{}")


def day_waterfall(label):
    by = defaultdict(lambda: {"in": 0.0, "out": 0.0, "net": 0.0, "cash": None, "n_sale": 0, "sale_amt": 0.0})
    for r in rows:
        if r["label"] != label:
            continue
        d = r["day"]
        delta = r["cash_delta"] or 0
        if delta > 0:
            by[d]["in"] += delta
        else:
            by[d]["out"] += delta
        by[d]["net"] += delta
        by[d]["cash"] = r["cash_after"]
        for e in r["events"]:
            if e["t"] == "SALE" and e["d"]:
                by[d]["n_sale"] += 1
                by[d]["sale_amt"] += e["d"]
    return by


print("=== DAY WATERFALL ===")
print(f"{'d':>3} {'R2net':>10} {'R2cash':>10} {'R2sale':>10} | {'Bnet':>10} {'Bcash':>10} {'Bsale':>10}")
r2w = day_waterfall("R2")
bw = day_waterfall("B")
for d in range(16):
    a, b = r2w[d], bw[d]
    print(f"{d:3d} {a['net']:10.0f} {a['cash'] or 0:10.0f} {a['sale_amt']:10.0f} | "
          f"{b['net']:10.0f} {b['cash'] or 0:10.0f} {b['sale_amt']:10.0f}")

print("\n=== R2 TOP positive steps d7-d10 ===")
r2_pos = [r for r in rows if r["label"] == "R2" and 7 <= r["day"] <= 10 and (r["cash_delta"] or 0) > 50]
r2_pos.sort(key=lambda r: -(r["cash_delta"] or 0))
for r in r2_pos[:15]:
    evs = ",".join(f"{e['t']}:{e['p']}{e['q']}@{e['u']}=+{e['d']:.0f}" for e in r["events"] if (e.get("d") or 0) > 0)
    print(f"  s{r['step']} d{r['day']}h{r['hour']} Δ=+{r['cash_delta']:.0f} exp={r['expected_from_orders']:.0f} "
          f"res={r['residual']:.0f} [{evs}] shedΔ={r['shed_delta']}")

print("\n=== B TOP positive steps d7-d10 ===")
b_pos = [r for r in rows if r["label"] == "B" and 7 <= r["day"] <= 10 and (r["cash_delta"] or 0) > 50]
b_pos.sort(key=lambda r: -(r["cash_delta"] or 0))
for r in b_pos[:10]:
    evs = ",".join(f"{e['t']}:{e['p']}{e['q']}@{e['u']}=+{e['d']:.0f}" for e in r["events"] if (e.get("d") or 0) > 0)
    print(f"  s{r['step']} d{r['day']}h{r['hour']} Δ=+{r['cash_delta']:.0f} [{evs}]")

# product revenue d7-d10
print("\n=== PRODUCT REVENUE d7-d10 (sum SALE event $) ===")


def prod_rev(label, lo, hi):
    acc = defaultdict(lambda: {"qty": 0, "rev": 0.0, "n": 0, "first": None})
    for r in rows:
        if r["label"] != label or not (lo <= r["day"] <= hi):
            continue
        for e in r["events"]:
            if e["t"] == "SALE" and e.get("d"):
                acc[e["p"]]["qty"] += e["q"]
                acc[e["p"]]["rev"] += e["d"]
                acc[e["p"]]["n"] += 1
                if acc[e["p"]]["first"] is None:
                    acc[e["p"]]["first"] = r["step"]
    return acc


for lo, hi, name in ((7, 10, "d7-10"), (0, 6, "d0-6"), (11, 15, "d11-15")):
    print(f"\n-- {name} --")
    for label in ("R2", "B"):
        acc = prod_rev(label, lo, hi)
        items = sorted(acc.items(), key=lambda kv: -kv[1]["rev"])
        print(f"  {label}:")
        for p, v in items[:8]:
            if v["rev"] > 0:
                print(f"    {p:12s} qty={v['qty']:6.0f} rev={v['rev']:9.0f} n={v['n']:4d} first_s={v['first']}")

# event type contribution d7-10
print("\n=== EVENT TYPE $ d7-10 ===")
for label in ("R2", "B"):
    by_t = defaultdict(float)
    for r in rows:
        if r["label"] != label or not (7 <= r["day"] <= 10):
            continue
        for e in r["events"]:
            if e.get("d"):
                by_t[e["t"]] += e["d"]
        by_t["RESIDUAL"] += (r["residual"] or 0)
        by_t["NET_DELTA"] += (r["cash_delta"] or 0)
    print(f"  {label}: " + ", ".join(f"{k}={v:+.0f}" for k, v in sorted(by_t.items(), key=lambda kv: -abs(kv[1]))))

# write CSVs
out = ROOT / "p13_cash_waterfall.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["day", "r2_net", "r2_cash", "r2_sale_amt", "b_net", "b_cash", "b_sale_amt", "net_gap"])
    for d in range(30):
        a, b = r2w[d], bw[d]
        w.writerow([d, a["net"], a["cash"], a["sale_amt"], b["net"], b["cash"], b["sale_amt"],
                    a["net"] - b["net"]])
print("\nwrote", out.name)

out = ROOT / "p13_revenue_by_product.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["window", "label", "product", "qty", "revenue", "n_sales", "first_step"])
    for lo, hi, name in ((0, 6, "d0-6"), (7, 10, "d7-10"), (11, 15, "d11-15")):
        for label in ("R2", "B"):
            acc = prod_rev(label, lo, hi)
            for p, v in sorted(acc.items(), key=lambda kv: -kv[1]["rev"]):
                w.writerow([name, label, p, v["qty"], v["rev"], v["n"], v["first"]])
print("wrote p13_revenue_by_product.csv")

out = ROOT / "p13_event_contributions.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["window", "label", "event_type", "cash_contrib"])
    for lo, hi, name in ((0, 6, "d0-6"), (7, 10, "d7-10"), (11, 15, "d11-15")):
        for label in ("R2", "B"):
            by_t = defaultdict(float)
            for r in rows:
                if r["label"] != label or not (lo <= r["day"] <= hi):
                    continue
                for e in r["events"]:
                    if e.get("d"):
                        by_t[e["t"]] += e["d"]
                by_t["RESIDUAL"] += (r["residual"] or 0)
            for k, v in sorted(by_t.items(), key=lambda kv: -abs(kv[1])):
                w.writerow([name, label, k, v])
print("wrote p13_event_contributions.csv")

out = ROOT / "p13_r2_b_gap.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["day", "r2_cash", "b_cash", "cash_gap", "r2_sale", "b_sale", "sale_gap"])
    for d in range(16):
        a, b = r2w[d], bw[d]
        w.writerow([d, a["cash"], b["cash"], (a["cash"] or 0) - (b["cash"] or 0),
                    a["sale_amt"], b["sale_amt"], a["sale_amt"] - b["sale_amt"]])
print("wrote p13_r2_b_gap.csv")
