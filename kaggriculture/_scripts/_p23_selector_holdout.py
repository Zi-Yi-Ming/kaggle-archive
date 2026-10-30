# -*- coding: utf-8 -*-
"""P23: fit margin-aware rule on train, evaluate S0/S1/S2 on hold-out.

S0 fixed MAIN
S1 melon>=3 -> CASH   (P20)
S2 margin-aware: CASH if melon>=3 AND cash0 < thr (thr fit on train only)

Primary: paired Δmargin vs MAIN on hold-out.
No NN. No submit.
"""
from __future__ import annotations

import csv
import importlib.util
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))

# reuse P22 runner
spec = importlib.util.spec_from_file_location("p22run", str(ROOT / "_p22_margin_surface.py"))
p22 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p22)


def load_existing():
    path = ROOT / "p22_margin_surface.csv"
    if not path.exists():
        return []
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        for k in ("seed", "day", "my", "opp_bank", "margin", "cash_d5", "melon0", "animals0", "cash0"):
            if r.get(k) not in ("", None):
                try:
                    r[k] = float(r[k]) if "." in str(r[k]) or "e" in str(r[k]).lower() else int(float(r[k]))
                except Exception:
                    r[k] = None
            else:
                r[k] = None
    return rows


def fit_threshold(train_pairs):
    """Fit cash0 threshold: CASH if melon>=3 and cash0 < thr.

    Search thr over train cash0 values; maximize mean Δmargin of policy vs MAIN
    with constraint melon>=3 for CASH picks.
    """
    # train_pairs: list of dicts with cash0, melon0, delta_CASH, day
    candidates = [0, 200, 400, 600, 800, 1000, 1200, 1500, 2000, 3000, 5000, 1e9]
    best = (1e9, -1e18)  # thr, score
    for thr in candidates:
        total = 0.0
        n = 0
        for p in train_pairs:
            mel = p.get("melon0") or 0
            c0 = p.get("cash0") or 0
            if mel >= 3 and c0 < thr:
                total += p["delta_CASH"]
            else:
                total += 0.0  # pick MAIN
            n += 1
        score = total / max(n, 1)
        if score > best[1]:
            best = (thr, score)
    return best[0], best[1]


def main():
    existing = load_existing()
    # build pairs from existing
    groups = defaultdict(dict)
    for r in existing:
        groups[(r["seed"], r["day"])][r["tail"]] = r
    pairs = []
    for key, g in groups.items():
        if "MAIN" not in g or "CASH_WINDOW" not in g:
            continue
        pairs.append({
            "seed": key[0], "day": key[1],
            "melon0": g["MAIN"].get("melon0"),
            "cash0": g["MAIN"].get("cash0"),
            "margin_MAIN": g["MAIN"]["margin"],
            "margin_CASH": g["CASH_WINDOW"]["margin"],
            "delta_CASH": g["CASH_WINDOW"]["margin"] - g["MAIN"]["margin"],
            "margin_HERD": g.get("HERD_SCALE", {}).get("margin"),
        })

    train = [p for p in pairs if p["seed"] in (1, 2)]
    val = [p for p in pairs if p["seed"] in (3, 4)]
    print(f"existing pairs: train={len(train)} val={len(val)}")
    thr, tr_score = fit_threshold(train)
    print(f"fit thr={thr} train_score(mean Δ if pick CASH under rule)={tr_score:+.0f}")
    print("train pairs:")
    for p in train:
        print(f"  s{p['seed']} d{p['day']} mel={p['melon0']} c0={p['cash0']} dCASH={p['delta_CASH']:+.0f}")
    print("val pairs:")
    for p in val:
        print(f"  s{p['seed']} d{p['day']} mel={p['melon0']} c0={p['cash0']} dCASH={p['delta_CASH']:+.0f}")

    # Hold-out: unseen seeds 5,6 days 9,10 — collect all 3 tails
    holdout_rows = []
    for seed in (5, 6):
        for day in (9, 10):
            for tail in ("MAIN", "CASH_WINDOW", "HERD_SCALE"):
                holdout_rows.append(p22.run(day, tail, seed, seat=0))

    out = ROOT / "p23_holdout_rolls.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(holdout_rows[0].keys()))
        w.writeheader()
        w.writerows(holdout_rows)

    hgroups = defaultdict(dict)
    for r in holdout_rows:
        hgroups[(r["seed"], r["day"])][r["tail"]] = r

    def eval_sel(name, pick_fn):
        deltas = []
        margins = []
        picks = []
        flips = 0
        bankrupt = 0
        for key, g in sorted(hgroups.items()):
            mel = g["MAIN"].get("melon0") or 0
            c0 = g["MAIN"].get("cash0") or 0
            tail = pick_fn(mel, c0, key[1])
            picks.append(tail)
            m = g[tail]["margin"]
            base = g["MAIN"]["margin"]
            deltas.append(m - base)
            margins.append(m)
            if g[tail]["outcome"] != g["MAIN"]["outcome"]:
                flips += 1
            if g[tail]["my"] < 1000:
                bankrupt += 1
        n = len(deltas)
        pos = sum(1 for d in deltas if d > 0)
        print(f"  {name}: picks={dict((p, picks.count(p)) for p in set(picks))} "
              f"meanΔ={sum(deltas)/n:+.0f} medΔ={statistics.median(deltas):+.0f} "
              f"pos={pos}/{n} worst={min(deltas):+.0f} flips={flips} bankrupt={bankrupt}")
        return deltas

    print("\n=== HOLD-OUT selectors (vs MAIN) ===")
    eval_sel("S0 MAIN", lambda m, c, d: "MAIN")
    eval_sel("S1 melon>=3 CASH", lambda m, c, d: "CASH_WINDOW" if m >= 3 else "MAIN")
    eval_sel(f"S2 margin thr={thr}", lambda m, c, d: "CASH_WINDOW" if (m >= 3 and c < thr) else "MAIN")

    # write summary
    out2 = ROOT / "p23_selector_compare.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["selector", "train_thr", "note"])
        w.writerow(["S0", "", "fixed MAIN"])
        w.writerow(["S1", "", "melon>=3 -> CASH"])
        w.writerow(["S2", thr, f"fitted on seeds1-2 only; holdout seeds5-6"])
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
