# -*- coding: utf-8 -*-
"""P14 analysis: divergence, first-yield economics, regime score vs R2 choices."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")

FIRST = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
SEED = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
# conservative expected units if watered (non-ongoing max_yield-ish fraction)
MAXY = {"WHEAT": 6, "CARROT": 4, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}
PRICE0 = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250}


def load_csv(name):
    return list(csv.DictReader((ROOT / name).open(encoding="utf-8")))


def main():
    tl = load_csv("p14_r2_production_timeline.csv")
    buys = load_csv("p14_seed_buys.csv")
    plants = load_csv("p14_plant_cmds.csv")

    print("=== SEED BUYS by label/crop (d0-10) ===")
    buy_c = defaultdict(lambda: defaultdict(int))
    first_buy = {}
    for r in buys:
        d = int(r["day"])
        if d > 10:
            continue
        buy_c[r["label"]][r["crop"]] += int(r["qty"])
        key = (r["label"], r["seed"], r["crop"])
        if key not in first_buy or d < first_buy[key]:
            first_buy[key] = d
    for lab in ("R2", "B"):
        print(f"  {lab}: {dict(buy_c[lab])}")
    print("  first buy day (seed,crop):")
    for k, d in sorted(first_buy.items()):
        print(f"    {k}: d{d}")

    print("\n=== PLANT CMDS by label/crop ===")
    pl_c = defaultdict(lambda: defaultdict(int))
    first_plant = {}
    for r in plants:
        d = int(r["day"])
        if d > 10:
            continue
        pl_c[r["label"]][r["crop"]] += 1
        key = (r["label"], r["seed"], r["crop"])
        if key not in first_plant or d < first_plant[key]:
            first_plant[key] = d
    for lab in ("R2", "B"):
        print(f"  {lab}: {dict(pl_c[lab])}")
    print("  first plant day:")
    for k, d in sorted(first_plant.items()):
        print(f"    {k}: d{d}")

    print("\n=== FIELD CROPS mean by day ===")
    for day in range(0, 11):
        line = f"  d{day:02d}"
        for lab in ("R2", "B"):
            rows = [r for r in tl if r["label"] == lab and int(r["day"]) == day]
            def m(c):
                v = [int(float(r.get(c) or 0)) for r in rows]
                return sum(v) / len(v) if v else 0
            line += f" | {lab} W={m('WHEAT'):.0f} M={m('MELON'):.0f} C={m('CARROT'):.0f} empty={m('empty'):.0f} $={m('money'):.0f}"
        print(line)

    # commitment: first day with non-wheat plant > 0
    print("\n=== COMMITMENT (first non-WHEAT plant on field) ===")
    for lab in ("R2", "B"):
        for seed in ("1", "2"):
            day_c = None
            crop_c = None
            for day in range(0, 11):
                rows = [r for r in tl if r["label"] == lab and r["seed"] == seed and int(r["day"]) == day]
                if not rows:
                    continue
                r = rows[0]
                for c in ("MELON", "CARROT", "STRAWBERRY", "TOMATO"):
                    if int(float(r.get(c) or 0)) > 0:
                        day_c, crop_c = day, c
                        break
                if day_c is not None:
                    break
            print(f"  {lab} s{seed}: commitment_day={day_c} crop={crop_c}")

    # first-yield value table
    print("\n=== FIRST-YIELD PROXY (per tile, watered) ===")
    rows_fy = []
    for c in FIRST:
        fy = FIRST[c]
        units = MAXY[c]
        px = PRICE0[c]
        gross = units * px
        net = gross - SEED[c]
        # cash per day of occupancy until first cash
        cpd = net / max(fy, 1)
        rows_fy.append({
            "crop": c, "first_yield": fy, "seed": SEED[c], "max_yield": units,
            "price0": px, "gross": gross, "net": net, "net_per_day_to_cash": cpd,
        })
        print(f"  {c:12s} fy={fy:2d} seed=${SEED[c]:3d} yld={units} px=${px:3d} "
              f"gross=${gross:4.0f} net=${net:4.0f} net/day=${cpd:6.1f}")

    # regime score: net_per_day_to_cash * price_quote_factor
    # Validate: at each plant decision day, did R2 plant the top-score crop among available?
    print("\n=== REGIME SCORE vs R2 ACTUAL PLANTS ===")
    # Use plant cmd log: for each (label,seed,day) crops planted
    by_ls_day = defaultdict(list)
    for r in plants:
        d = int(r["day"])
        if d <= 10:
            by_ls_day[(r["label"], r["seed"], d)].append(r["crop"])

    def score(crop, quote=None):
        base = PRICE0[crop]
        px = quote if quote else base
        net = MAXY[crop] * px - SEED[crop]
        return net / max(FIRST[crop], 1)

    # For R2, check if planted crop is argmax of score among crops they bought seeds for that day
    hit = miss = 0
    details = []
    for (lab, seed, day), crops in sorted(by_ls_day.items()):
        if lab != "R2":
            continue
        planted = Counter(crops)
        # available = crops they have seed inventory for that day from timeline
        trow = next((r for r in tl if r["label"] == lab and r["seed"] == seed and int(r["day"]) == day), None)
        if not trow:
            continue
        avail = []
        for c in FIRST:
            have_seed = int(float(trow.get(f"seed_{c}") or 0)) > 0 or c in planted
            # also crops bought this day
            if have_seed:
                avail.append(c)
        # buys that day
        for r in buys:
            if r["label"] == lab and r["seed"] == seed and int(r["day"]) == day and r["crop"] not in avail:
                avail.append(r["crop"])
        if not avail:
            avail = list(planted.keys())
        scores = {c: score(c) for c in avail}
        pred = max(scores, key=scores.get) if scores else None
        actual = planted.most_common(1)[0][0] if planted else None
        ok = pred == actual
        if ok:
            hit += 1
        else:
            miss += 1
        details.append((day, actual, pred, scores, ok))

    print(f"  top1 score match R2 plant-days: {hit}/{hit+miss} = {hit/max(1,hit+miss):.2f}")
    for d, a, p, s, ok in details[:20]:
        if not ok:
            print(f"    MISS d{d} actual={a} pred={p} scores={ {k: round(v,1) for k,v in s.items()} }")

    # B same check
    hitb = missb = 0
    for (lab, seed, day), crops in sorted(by_ls_day.items()):
        if lab != "B":
            continue
        planted = Counter(crops)
        if not planted:
            continue
        avail = list(planted.keys()) + ["WHEAT", "CARROT", "MELON"]
        avail = list(dict.fromkeys(avail))
        scores = {c: score(c) for c in avail}
        pred = max(scores, key=scores.get)
        actual = planted.most_common(1)[0][0]
        if pred == actual:
            hitb += 1
        else:
            missb += 1
    print(f"  top1 score match B plant-days: {hitb}/{hitb+missb} = {hitb/max(1,hitb+missb):.2f}")

    # Write CSVs
    out = ROOT / "p14_first_yield_value.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_fy[0].keys()))
        w.writeheader()
        w.writerows(rows_fy)
    print("wrote", out.name)

    out = ROOT / "p14_regime_score.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day", "r2_actual", "r2_pred", "match", "scores"])
        for d, a, p, s, ok in details:
            w.writerow([d, a, p, int(ok), str({k: round(v, 1) for k, v in s.items()})])
    print("wrote", out.name)

    # opportunity cost melon vs wheat tile
    out = ROOT / "p14_opportunity_cost.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["compare", "net_melon", "net_wheat_per_slot_d0_d10", "note"])
        # if tile used for wheat replant every 2 days from d0: ~5 cycles * net wheat
        wheat_cycle = MAXY["WHEAT"] * PRICE0["WHEAT"] - SEED["WHEAT"]
        wheat_d10 = wheat_cycle * 5  # rough 5 harvests in 10 days
        melon_net = MAXY["MELON"] * PRICE0["MELON"] - SEED["MELON"]
        w.writerow(["MELON_vs_WHEAT_replant", melon_net, wheat_d10,
                    f"melon_fy10_oneshot={melon_net}; wheat_replant~{wheat_d10}"])
        w.writerow(["MELON_vs_WHEAT_plus_water", melon_net, wheat_d10,
                    "water cost ~10 actions; melon needs daily water"])
    print("wrote", out.name)

    out = ROOT / "p14_production_divergence.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "R2", "B"])
        for c in FIRST:
            w.writerow([f"plants_{c}_d0_10", pl_c["R2"][c], pl_c["B"][c]])
            w.writerow([f"seed_buy_{c}_d0_10", buy_c["R2"][c], buy_c["B"][c]])
        r2_m = [int(float(r["money"])) for r in tl if r["label"]=="R2" and int(r["day"])==10]
        b_m = [int(float(r["money"])) for r in tl if r["label"]=="B" and int(r["day"])==10]
        w.writerow(["money_d10", sum(r2_m)/len(r2_m) if r2_m else 0, sum(b_m)/len(b_m) if b_m else 0])
        w.writerow(["score_top1_match", f"{hit}/{hit+miss}", f"{hitb}/{hitb+missb}"])
    print("wrote", out.name)


if __name__ == "__main__":
    main()
