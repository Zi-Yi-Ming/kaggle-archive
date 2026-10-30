# -*- coding: utf-8 -*-
"""P12 analysis: day-by-day R2 vs P11 gap decomposition."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
TRACE = ROOT / "p12_day_traces.csv"


def load():
    rows = list(csv.DictReader(TRACE.open(encoding="utf-8")))
    for r in rows:
        for k in ("day", "seed", "seat", "hands", "unlocked", "shed_total", "plant",
                  "empty", "weed", "coop", "pasture", "animal_cow", "animal_sheep",
                  "animal_goose", "hungry", "uncared", "yield_units", "fert_ready",
                  "dry_plant", "hires_req", "land_req"):
            if r.get(k) not in (None, ""):
                r[k] = int(float(r[k]))
            else:
                r[k] = None
        for k in ("money", "cash_delta", "opp_money", "gap"):
            r[k] = float(r[k]) if r.get(k) not in (None, "") else None
        r["shed"] = json.loads(r.get("shed") or "{}")
        r["seeds"] = json.loads(r.get("seeds") or "{}")
        r["inv"] = json.loads(r.get("inv") or "{}")
        r["sell_req"] = json.loads(r.get("sell_req") or "{}")
        r["buy_req"] = json.loads(r.get("buy_req") or "{}")
        r["ops"] = json.loads(r.get("ops") or "{}")
    return rows


def avg_by_day(rows, label, key):
    by = defaultdict(list)
    for r in rows:
        if r["label"] == label and r.get(key) is not None:
            by[r["day"]].append(r[key])
    return {d: (sum(v) / len(v) if v else None) for d, v in sorted(by.items())}


def sum_json_by_day(rows, label, field, item=None):
    by = defaultdict(float)
    for r in rows:
        if r["label"] != label:
            continue
        d = r["day"]
        data = r.get(field) or {}
        if item:
            by[d] += float(data.get(item) or 0)
        else:
            by[d] += sum(float(v or 0) for v in data.values())
    return dict(sorted(by.items()))


def ops_by_day(rows, label, op):
    by = defaultdict(float)
    for r in rows:
        if r["label"] != label:
            continue
        by[r["day"]] += float((r.get("ops") or {}).get(op) or 0)
    return dict(sorted(by.items()))


def main():
    rows = load()
    days = list(range(30))

    print("=== FINAL (mean over seeds/seats) ===")
    for label in ("R2", "P11"):
        finals = [r["money"] for r in rows if r["label"] == label and r["day"] == 29 and r.get("money") is not None]
        print(f"  {label}: {sum(finals)/len(finals):.0f}  n={len(finals)}")

    print("\n=== DAY-BY-DAY MEAN MONEY ===")
    r2m = avg_by_day(rows, "R2", "money")
    p11m = avg_by_day(rows, "P11", "money")
    r2g = avg_by_day(rows, "R2", "gap")  # R2 - P11 when R2 is own... actually gap = own - opp
    # For P11 rows, gap = P11 - R2 (negative). For R2 rows, gap = R2 - P11 (positive).
    p11g = avg_by_day(rows, "P11", "gap")
    print(f"{'d':>3} {'R2$':>10} {'P11$':>10} {'Δ$':>10} {'P11gap':>10}")
    for d in days:
        a, b = r2m.get(d), p11m.get(d)
        g = p11g.get(d)
        if a is not None and b is not None:
            print(f"{d:3d} {a:10.0f} {b:10.0f} {a-b:10.0f} {g if g is not None else float('nan'):10.0f}")

    print("\n=== CASH DELTA (mean $/day) ===")
    r2d = avg_by_day(rows, "R2", "cash_delta")
    p11d = avg_by_day(rows, "P11", "cash_delta")
    print(f"{'d':>3} {'R2Δ':>10} {'P11Δ':>10} {'gapΔ':>10}")
    cum = 0
    for d in days:
        if d == 0:
            continue
        a, b = r2d.get(d), p11d.get(d)
        if a is not None and b is not None:
            cum += a - b
            print(f"{d:3d} {a:10.0f} {b:10.0f} {a-b:10.0f}  cum={cum:.0f}")

    print("\n=== PRODUCTION STATE (mean day-end) ===")
    keys = ["hands", "unlocked", "plant", "coop", "pasture", "animal_cow", "animal_sheep",
            "animal_goose", "hungry", "yield_units", "shed_total", "weed", "empty"]
    print(f"{'d':>3} " + " ".join(f"{k[:8]:>10}" for k in keys) + "   | " + " ".join(f"{k[:8]:>10}" for k in keys))
    for d in (0, 5, 10, 15, 20, 25, 29):
        r2s = [r for r in rows if r["label"] == "R2" and r["day"] == d]
        p11s = [r for r in rows if r["label"] == "P11" and r["day"] == d]
        def m(lst, k):
            vals = [r[k] for r in lst if r.get(k) is not None]
            return sum(vals)/len(vals) if vals else 0
        r2line = " ".join(f"{m(r2s,k):10.1f}" for k in keys)
        p11line = " ".join(f"{m(p11s,k):10.1f}" for k in keys)
        print(f"{d:3d} {r2line}   | {p11line}")

    print("\n=== SELL REQUESTED QTY (cumulative to day) ===")
    items = ["MILK", "WOOL", "EGG", "STRAWBERRY", "MELON", "CARROT", "WHEAT", "FERTILIZER", "TOMATO"]
    for item in items:
        r2s = sum_json_by_day(rows, "R2", "sell_req", item)
        p11s = sum_json_by_day(rows, "P11", "sell_req", item)
        r2c = sum(r2s.values())
        p11c = sum(p11s.values())
        print(f"  {item:12s} R2_total={r2c:8.0f}  P11_total={p11c:8.0f}  Δ={r2c-p11c:+.0f}")

    print("\n=== BUY REQUESTED (cumulative) ===")
    buy_keys = set()
    for r in rows:
        buy_keys.update((r.get("buy_req") or {}).keys())
    for bk in sorted(buy_keys):
        r2c = sum(float((r.get("buy_req") or {}).get(bk) or 0) for r in rows if r["label"]=="R2")
        p11c = sum(float((r.get("buy_req") or {}).get(bk) or 0) for r in rows if r["label"]=="P11")
        print(f"  {bk:28s} R2={r2c:8.0f}  P11={p11c:8.0f}  Δ={r2c-p11c:+.0f}")

    print("\n=== WORKER OPS TOTAL (all days, all games) ===")
    op_keys = set()
    for r in rows:
        op_keys.update((r.get("ops") or {}).keys())
    print(f"{'op':20s} {'R2':>10} {'P11':>10} {'Δ':>10}")
    for op in sorted(op_keys, key=lambda o: -sum(float((r.get('ops') or {}).get(o) or 0) for r in rows if r['label']=='R2')):
        r2c = sum(float((r.get("ops") or {}).get(op) or 0) for r in rows if r["label"]=="R2")
        p11c = sum(float((r.get("ops") or {}).get(op) or 0) for r in rows if r["label"]=="P11")
        print(f"{op:20s} {r2c:10.0f} {p11c:10.0f} {r2c-p11c:+10.0f}")

    print("\n=== HIRES / LAND requested total ===")
    for label in ("R2", "P11"):
        h = sum(r["hires_req"] or 0 for r in rows if r["label"]==label)
        land = sum(r["land_req"] or 0 for r in rows if r["label"]==label)
        print(f"  {label}: hires_req={h:.0f} land_req={land:.0f}")

    # Shed composition at d15/d25/d29
    print("\n=== SHED COMPOSITION mean (d15 / d25 / d29) ===")
    for d in (15, 25, 29):
        for label in ("R2", "P11"):
            sheds = [r["shed"] for r in rows if r["label"]==label and r["day"]==d]
            keys = set()
            for s in sheds:
                keys.update(s.keys())
            avg = {k: sum(float(s.get(k) or 0) for s in sheds)/len(sheds) for k in sorted(keys)}
            avg = {k:v for k,v in avg.items() if v > 0.5}
            print(f"  d{d} {label}: {avg}")

    # Write cash decomposition CSV
    out = ROOT / "p12_cash_decomposition.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day", "r2_money", "p11_money", "money_gap", "r2_cash_delta", "p11_cash_delta", "delta_gap", "cum_delta_gap"])
        cum = 0
        for d in days:
            a, b = r2m.get(d), p11m.get(d)
            da, db = r2d.get(d), p11d.get(d)
            if d > 0 and da is not None and db is not None:
                cum += da - db
            w.writerow([d, a, b, (a-b) if a is not None and b is not None else None,
                        da, db, (da-db) if da is not None and db is not None else None,
                        cum if d > 0 else None])
    print("\nwrote", out.name)

    # Production decomposition CSV
    out = ROOT / "p12_production_decomposition.csv"
    pkeys = ["hands", "unlocked", "plant", "coop", "pasture", "animal_cow", "animal_sheep",
             "animal_goose", "hungry", "yield_units", "shed_total", "fert_ready"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day"] + [f"r2_{k}" for k in pkeys] + [f"p11_{k}" for k in pkeys] + [f"gap_{k}" for k in pkeys])
        for d in days:
            r2s = [r for r in rows if r["label"]=="R2" and r["day"]==d]
            p11s = [r for r in rows if r["label"]=="P11" and r["day"]==d]
            def m(lst, k):
                vals = [r[k] for r in lst if r.get(k) is not None]
                return sum(vals)/len(vals) if vals else None
            w.writerow([d] + [m(r2s,k) for k in pkeys] + [m(p11s,k) for k in pkeys]
                        + [(m(r2s,k)-m(p11s,k) if m(r2s,k) is not None and m(p11s,k) is not None else None) for k in pkeys])
    print("wrote", out.name)

    # Sales decomposition
    out = ROOT / "p12_sales_decomposition.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item", "r2_sell_req_total", "p11_sell_req_total", "gap"])
        for item in items:
            r2c = sum(float((r.get("sell_req") or {}).get(item) or 0) for r in rows if r["label"]=="R2")
            p11c = sum(float((r.get("sell_req") or {}).get(item) or 0) for r in rows if r["label"]=="P11")
            w.writerow([item, r2c, p11c, r2c-p11c])
    print("wrote", out.name)


if __name__ == "__main__":
    main()
