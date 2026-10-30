# -*- coding: utf-8 -*-
"""P49: is full shop identity necessary? Coarse vs full LOSO on 8 R2 traces."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
TRACES = ROOT / "p48_traces"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)

# product categories (from competition shops)
SHOP_PRODUCTS = {
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"),
    "BAKERY": ("WHEAT", "CARROT"),
    "PIZZA_SHOP": ("WHEAT", "TOMATO", "CHEESE_MILK"),  # approximate
    "ICE_CREAM_SHOP": ("MILK",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MELON"),
    "YARN_STORE": ("WOOL",),
    "PET_CAFE": ("EGG",),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "MILK"),
}


def load():
    rows = []
    for seed in SEEDS:
        data = json.loads((TRACES / f"trace_seed{seed}.json").read_text(encoding="utf-8"))
        for r in data:
            r["seed"] = seed
            rows.append(r)
    return rows


def mkey(a):
    return json.dumps(a.get("market"), sort_keys=True, default=str)


def wkey(a):
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def shop_key(shops):
    return "|".join(shops) if shops else "NONE"


def coarse_features(r):
    """Pre-registered coarse shop descriptors. No learning of feature defs."""
    shops = r["shops"] or []
    prices = r["prices"] or {}
    # product category mask
    cats = set()
    for s in shops:
        for p in SHOP_PRODUCTS.get(s, ()):
            cats.add(p.split("_")[-1] if "_" in p else p)
    # simplify to main product types
    cat_mask = tuple(sorted({
        "CROP" if any(x in cats for x in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")) else "",
        "DAIRY" if "MILK" in cats else "",
        "EGG" if "EGG" in cats else "",
        "WOOL" if "WOOL" in cats else "",
    } - {""}))

    # price ranks of key goods (lower rank = cheaper)
    keys = ("WHEAT", "MELON", "MILK", "WOOL", "STRAWBERRY", "FERTILIZER")
    px = [(k, int(prices.get(k) or 0)) for k in keys]
    order = tuple(k for k, _ in sorted(px, key=lambda x: x[1]))
    # price buckets (very coarse)
    def bucket(v):
        if v <= 0:
            return "0"
        if v < 15:
            return "lo"
        if v < 40:
            return "mid"
        return "hi"
    pbucket = tuple(bucket(int(prices.get(k) or 0)) for k in keys)

    # unlock event: new shop vs previous hour (approx via n_shops change not available;
    # use n_shops level)
    n = r["n_shops"]
    return {
        "nshop": n,
        "cat_mask": cat_mask,
        "price_order": order,
        "price_bucket": pbucket,
        "has_farmers": int("FARMERS_MARKET" in shops),
        "has_dairy_shop": int(any(s in shops for s in ("ICE_CREAM_SHOP", "BRUNCH_SPOT"))),
        "has_yarn": int("YARN_STORE" in shops),
        "has_egg_shop": int(any(s in shops for s in ("PET_CAFE", "BRUNCH_SPOT"))),
    }


def key_schemas():
    cf = lambda r: coarse_features(r)
    return {
        "day_hour": lambda r: (r["day"], r["hour"]),
        "day_hour_nshop": lambda r: (r["day"], r["hour"], r["n_shops"]),
        "day_hour_cat": lambda r: (r["day"], r["hour"], cf(r)["cat_mask"]),
        "day_hour_nshop_cat": lambda r: (r["day"], r["hour"], r["n_shops"], cf(r)["cat_mask"]),
        "day_hour_price_bucket": lambda r: (r["day"], r["hour"], cf(r)["price_bucket"]),
        "day_hour_price_order": lambda r: (r["day"], r["hour"], cf(r)["price_order"]),
        "day_hour_coarse": lambda r: (
            r["day"], r["hour"], r["n_shops"], cf(r)["cat_mask"],
            cf(r)["has_farmers"], cf(r)["has_dairy_shop"],
            cf(r)["has_yarn"], cf(r)["has_egg_shop"],
        ),
        "day_hour_coarse_px": lambda r: (
            r["day"], r["hour"], r["n_shops"], cf(r)["cat_mask"],
            cf(r)["price_bucket"], cf(r)["has_farmers"],
        ),
        "day_hour_full_shop": lambda r: (r["day"], r["hour"], shop_key(r["shops"])),
        "d6_hour_shop": lambda r: (r["hour"], shop_key(r["shops"])) if r["day"] == 6 else None,
        "d6_hour_coarse": lambda r: (
            (r["hour"], r["n_shops"], cf(r)["cat_mask"], cf(r)["has_farmers"])
            if r["day"] == 6 else None
        ),
        "d6_hour_nshop": lambda r: (r["hour"], r["n_shops"]) if r["day"] == 6 else None,
    }


def loso(rows, key_fn, subset=None):
    data = subset if subset is not None else rows
    seeds = sorted({r["seed"] for r in data})
    accs, mkts, wkrs, uns = [], [], [], []
    for held in seeds:
        train = [r for r in data if r["seed"] != held]
        test = [r for r in data if r["seed"] == held]
        if not test:
            continue
        gm, gw = defaultdict(Counter), defaultdict(Counter)
        for r in train:
            k = key_fn(r)
            if k is None:
                continue
            gm[k][mkey(r["action"])] += 1
            gw[k][wkey(r["action"])] += 1
        table = {k: (gm[k].most_common(1)[0][0], gw[k].most_common(1)[0][0]) for k in gm}
        hit = hm = hw = unseen = tot = 0
        for r in test:
            k = key_fn(r)
            if k is None:
                continue
            tot += 1
            if k not in table:
                unseen += 1
                continue
            ma, wa = table[k]
            if mkey(r["action"]) == ma:
                hm += 1
            if wkey(r["action"]) == wa:
                hw += 1
            if mkey(r["action"]) == ma and wkey(r["action"]) == wa:
                hit += 1
        if tot:
            accs.append(hit / tot)
            mkts.append(hm / tot)
            wkrs.append(hw / tot)
            uns.append(unseen / tot)
    if not accs:
        return None
    return {
        "acc": sum(accs) / len(accs),
        "mkt": sum(mkts) / len(mkts),
        "wkr": sum(wkrs) / len(wkrs),
        "unseen": sum(uns) / len(uns),
        "n_folds": len(accs),
    }


def main():
    rows = load()
    print(f"n={len(rows)}", flush=True)
    d6 = [r for r in rows if r["day"] == 6]
    print(f"d6 n={len(d6)}", flush=True)

    schemas = key_schemas()
    print("\n=== LOSO all days ===", flush=True)
    print(f"{'schema':24s} {'acc':8s} {'mkt':8s} {'wkr':8s} {'unseen':8s}")
    results = {}
    for name, fn in schemas.items():
        if name.startswith("d6"):
            continue
        st = loso(rows, fn)
        if not st:
            continue
        results[name] = st
        print(f"{name:24s} {st['acc']:8.4f} {st['mkt']:8.4f} {st['wkr']:8.4f} {st['unseen']:8.4f}", flush=True)

    print("\n=== LOSO day6 only ===", flush=True)
    for name, fn in schemas.items():
        if not name.startswith("d6"):
            continue
        st = loso(rows, fn, subset=d6)
        if not st:
            print(f"{name:24s} EMPTY", flush=True)
            continue
        results[name] = st
        print(f"{name:24s} {st['acc']:8.4f} {st['mkt']:8.4f} {st['wkr']:8.4f} {st['unseen']:8.4f}", flush=True)

    # cardinality
    print("\n=== key cardinality (full data) ===", flush=True)
    for name, fn in schemas.items():
        keys = set()
        for r in rows:
            k = fn(r)
            if k is not None:
                keys.add(k)
        print(f"  {name:24s} n_keys={len(keys)}", flush=True)

    # decision
    base = results.get("day_hour", {}).get("acc", 0)
    best_coarse = max(
        ((n, s) for n, s in results.items()
         if "full_shop" not in n and not n.startswith("d6") and "coarse" in n or n in
         ("day_hour_nshop", "day_hour_cat", "day_hour_price_bucket", "day_hour_price_order",
          "day_hour_nshop_cat")),
        key=lambda x: x[1]["acc"],
        default=("none", {"acc": 0}),
    )
    full = results.get("day_hour_full_shop", {})
    d6c = results.get("d6_hour_coarse", {})
    d6f = results.get("d6_hour_shop", {})

    print(f"\nbaseline day_hour LOSO={base:.4f}", flush=True)
    print(f"best coarse-ish={best_coarse[0]} {best_coarse[1].get('acc', 0):.4f}", flush=True)
    print(f"full shop LOSO={full.get('acc', 0):.4f} unseen={full.get('unseen', 0):.4f}", flush=True)
    print(f"d6 coarse={d6c.get('acc', 0):.4f} d6 full={d6f.get('acc', 0):.4f} "
          f"d6 unseen_full={d6f.get('unseen', 0):.4f}", flush=True)

    if full.get("unseen", 0) > 0.5:
        if best_coarse[1].get("acc", 0) >= base + 0.08 and best_coarse[1].get("unseen", 1) < 0.3:
            decision = "COARSE_SHOP_FEATURES_HELP"
        elif d6c.get("acc", 0) >= 0.85 and d6c.get("unseen", 1) < 0.25:
            decision = "D6_COARSE_SUFFICIENT"
        else:
            decision = "FULL_SHOP_ID_REQUIRED_DATA_HEAVY"
    else:
        decision = "FULL_SHOP_GENERALIZES"

    print(f"P49_DECISION={decision}", flush=True)

    with open(ROOT / "p49_loso.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["schema", "acc", "mkt", "wkr", "unseen", "scope"])
        w.writeheader()
        for name, s in results.items():
            scope = "d6" if name.startswith("d6") else "all"
            w.writerow({"schema": name, "scope": scope, **s})

    (ROOT / "p49_summary.json").write_text(json.dumps({
        "decision": decision,
        "day_hour": base,
        "best_coarse": {"name": best_coarse[0], **best_coarse[1]},
        "full_shop": full,
        "d6_coarse": d6c,
        "d6_full": d6f,
        "results": results,
    }, indent=2, default=str), encoding="utf-8")
    print("wrote p49_loso.csv p49_summary.json", flush=True)


if __name__ == "__main__":
    main()
