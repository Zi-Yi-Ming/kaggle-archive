# -*- coding: utf-8 -*-
"""H5-B v2: shop family + pre-draw features at end of day 2 (hour 23)."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
ASHOK = ROOT / "_external" / "public_data" / "ashok_top10" / "replays_2026-08-03.parquet"
REPLAYS = ROOT / "_external" / "replays"


def farm_counts(farm):
    empty = plants = animals = weeds = 0
    for row in farm.get("tiles") or []:
        for t in row or []:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "WEED":
                    weeds += 1
                elif t.get("kind") == "PLANT":
                    plants += 1
                elif t.get("animal"):
                    animals += 1
    return empty, plants, animals, weeds


def extract(data):
    info = data.get("info") or {}
    steps = data.get("steps") or []
    shops_seq = []
    last = None
    # feature at last observation of day 2 (step 47 = day2 hour23) — still before
    # end_of_day shop draw which happens after hour 23 actions.
    feat_d2h23 = None
    feat_d1h0 = None
    for idx, snap in enumerate(steps):
        if not snap:
            continue
        rec = snap[0] or {}
        obs = rec.get("observation") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        unlocked = tuple((obs.get("town") or {}).get("unlocked_shops") or [])
        if unlocked != last:
            shops_seq.append(unlocked)
            last = unlocked
        farms = obs.get("farms") or []
        if len(farms) < 2:
            continue
        if step == 24:  # day1 hour0
            e0, p0, a0, w0 = farm_counts(farms[0] or {})
            e1, p1, a1, w1 = farm_counts(farms[1] or {})
            feat_d1h0 = {"e0": e0, "e1": e1, "p0": p0, "p1": p1}
        if step == 47:  # day2 hour23 — last obs before first shop draw
            e0, p0, a0, w0 = farm_counts(farms[0] or {})
            e1, p1, a1, w1 = farm_counts(farms[1] or {})
            feat_d2h23 = {
                "e0": e0, "e1": e1, "p0": p0, "p1": p1,
                "a0": a0, "a1": a1, "w0": w0, "w1": w1,
            }
    if len(shops_seq) < 2:
        return None
    # after first unlock: shops_seq[1] has 1 shop; after 2nd: shops_seq[2] has 2
    first = shops_seq[1][0] if shops_seq[1] else None
    first2 = tuple(shops_seq[2][:2]) if len(shops_seq) > 2 and len(shops_seq[2]) >= 2 else None
    full = list(shops_seq[-1]) if shops_seq else []
    return {
        "first_shop": first,
        "first2": first2,
        "full_shops": full,
        "n_unlocks": len(shops_seq) - 1,
        "d1": feat_d1h0 or {},
        "d2h23": feat_d2h23 or {},
    }


def loo_acc(rows, feature_fn, label_key):
    buckets = defaultdict(Counter)
    for r in rows:
        fv = feature_fn(r)
        lv = r.get(label_key)
        if fv is None or lv is None:
            continue
        buckets[fv][lv] += 1
    correct = total = 0
    for r in rows:
        fv = feature_fn(r)
        lv = r.get(label_key)
        if fv is None or lv is None:
            continue
        c = Counter(buckets[fv])
        c[lv] -= 1
        if sum(c.values()) <= 0:
            continue
        pred = c.most_common(1)[0][0]
        total += 1
        correct += int(pred == lv)
    maj = Counter(r[label_key] for r in rows if r.get(label_key) is not None)
    base = maj.most_common(1)[0][1] / sum(maj.values()) if maj else None
    return total, (correct / total if total else None), base, len(buckets)


def main():
    rows = []
    df = pd.read_parquet(ASHOK)
    for i in range(len(df)):
        try:
            data = json.loads(df.iloc[i]["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            r0, r1 = float(rew[0]), float(rew[1])
        except Exception:
            continue
        elite = min(r0, r1) >= 100000
        ex = extract(data)
        if not ex:
            continue
        ex["source"] = "ashok"
        ex["elite"] = elite
        ex["margin"] = abs(r0 - r1) if elite else None
        rows.append(ex)
    for p in sorted(REPLAYS.glob("episode-*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        ex = extract(data)
        if not ex:
            continue
        ex["source"] = "live"
        ex["elite"] = False
        ex["margin"] = None
        rows.append(ex)

    print(f"n={len(rows)} elite={sum(1 for r in rows if r.get('elite'))}")
    print("first shops", Counter(r["first_shop"] for r in rows).most_common())
    print("first2 n_unique", len(Counter(r["first2"] for r in rows)))

    def b5(x):
        return None if x is None else int(x) // 5 * 5

    def sum_e23(r):
        d = r.get("d2h23") or {}
        if d.get("e0") is None or d.get("e1") is None:
            return None
        return d["e0"] + d["e1"]

    def own_e23(r):
        return (r.get("d2h23") or {}).get("e0")

    def opp_e23(r):
        return (r.get("d2h23") or {}).get("e1")

    def own_p23(r):
        return (r.get("d2h23") or {}).get("p0")

    def opp_p23(r):
        return (r.get("d2h23") or {}).get("p1")

    tests = [
        ("own_empty_d2h23_b5", lambda r: b5(own_e23(r)), "first_shop"),
        ("opp_empty_d2h23_b5", lambda r: b5(opp_e23(r)), "first_shop"),
        ("sum_empty_d2h23_b5", lambda r: b5(sum_e23(r)), "first_shop"),
        ("own_plants_d2h23", own_p23, "first_shop"),
        ("opp_plants_d2h23", opp_p23, "first_shop"),
        ("sum_empty_d2h23_b5", lambda r: b5(sum_e23(r)), "first2"),
        ("own_empty_d2h23_b5", lambda r: b5(own_e23(r)), "first2"),
        ("opp_empty_d2h23_b5", lambda r: b5(opp_e23(r)), "first2"),
    ]
    pred_rows = []
    print("\n=== LOO predictability ===")
    for name, fn, label in tests:
        n, acc, base, nb = loo_acc(rows, fn, label)
        lift = (acc - base) if (acc is not None and base is not None) else None
        print(f"  {name:28s} → {label:10s} n={n:3d} acc={acc} base={base} lift={lift} buckets={nb}")
        pred_rows.append({"feature": name, "label": label, "n": n, "acc": acc, "baseline": base, "lift": lift, "n_buckets": nb})

    # crosstab sum empty vs first shop
    print("\n=== crosstab sum_empty_d2h23 vs first_shop ===")
    ct = defaultdict(Counter)
    for r in rows:
        s = sum_e23(r)
        if s is not None and r.get("first_shop"):
            ct[b5(s)][r["first_shop"]] += 1
    for bucket in sorted(ct):
        print(f"  empty~{bucket}: n={sum(ct[bucket].values())} {ct[bucket].most_common(3)}")

    # outcome
    elite = [r for r in rows if r.get("elite")]
    if elite:
        print("\n=== elite mean margin by first_shop ===")
        by = defaultdict(list)
        for r in elite:
            if r.get("first_shop") and r.get("margin") is not None:
                by[r["first_shop"]].append(r["margin"])
        for k, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
            print(f"  {k}: n={len(v)} mean={sum(v)/len(v):.0f}")

    # CSV
    def_row = []
    for r in rows:
        d = r.get("d2h23") or {}
        def_row.append({
            "source": r["source"], "elite": r.get("elite"),
            "first_shop": r.get("first_shop"), "first2": str(r.get("first2")),
            "n_unlocks": r.get("n_unlocks"),
            "own_empty_d2h23": d.get("e0"), "opp_empty_d2h23": d.get("e1"),
            "own_plants_d2h23": d.get("p0"), "opp_plants_d2h23": d.get("p1"),
            "sum_empty_d2h23": (d.get("e0") or 0) + (d.get("e1") or 0) if d.get("e0") is not None else None,
            "margin": r.get("margin"),
            "shops": "|".join(r.get("full_shops") or []),
        })
    pd.DataFrame(def_row).to_csv(ROOT / "shop_family_definition.csv", index=False)
    pd.DataFrame(pred_rows).to_csv(ROOT / "shop_family_prediction.csv", index=False)
    pd.DataFrame([
        {"first_shop": r.get("first_shop"), "first2": str(r.get("first2")),
         "margin": r.get("margin"),
         "sum_empty_d2h23": (r.get("d2h23") or {}).get("e0", 0) + (r.get("d2h23") or {}).get("e1", 0)}
        for r in elite
    ]).to_csv(ROOT / "shop_family_outcome.csv", index=False)
    print("\nwrote 3 CSVs")


if __name__ == "__main__":
    main()
