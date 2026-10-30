# -*- coding: utf-8 -*-
"""Build snapshot counterfactual + summary tables for P12 report."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")

# From ablation runs
abl = list(csv.DictReader((ROOT / "p12_primitive_ablation.csv").open(encoding="utf-8")))
for r in abl:
    for k in r:
        if k in ("label", "errors"):
            continue
        try:
            r[k] = float(r[k]) if r[k] not in ("", None) else None
        except Exception:
            pass
    r["seed"] = int(r["seed"]) if r.get("seed") is not None else None
    r["seat"] = int(r["seat"]) if r.get("seat") is not None else None
    r["win"] = int(r["win"]) if r.get("win") is not None else 0
    r["bankrupt"] = int(r["bankrupt"]) if r.get("bankrupt") is not None else 0

# Pairwise B0 vs B1 same seed/seat
pairs = []
b0 = {(r["seed"], r["seat"]): r for r in abl if r["label"] == "B0"}
b1 = {(r["seed"], r["seat"]): r for r in abl if r["label"] == "B1"}
for key in sorted(b0.keys()):
    a, b = b0[key], b1[key]
    pairs.append({
        "seed": key[0], "seat": key[1],
        "b0_my": a["my"], "b1_my": b["my"], "bank_delta": b["my"] - a["my"],
        "b0_d10": a.get("d10_my"), "b1_d10": b.get("d10_my"),
        "d10_delta": (b.get("d10_my") or 0) - (a.get("d10_my") or 0),
        "b0_d20": a.get("d20_my"), "b1_d20": b.get("d20_my"),
        "d20_delta": (b.get("d20_my") or 0) - (a.get("d20_my") or 0),
        "b0_hands10": a.get("d10_hands"), "b1_hands10": b.get("d10_hands"),
        "hands10_delta": (b.get("d10_hands") or 0) - (a.get("d10_hands") or 0),
        "b0_margin": a["margin"], "b1_margin": b["margin"],
        "margin_delta": b["margin"] - a["margin"],
    })

out = ROOT / "p12_snapshot_counterfactual.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
    w.writeheader()
    w.writerows(pairs)

print("=== B0 vs B1 paired (same seed/seat vs R2) ===")
print(f"{'seed':>4} {'seat':>4} {'B0$':>8} {'B1$':>8} {'Δbank':>8} {'B0h10':>6} {'B1h10':>6} {'Δh':>4} {'Δd20':>8}")
for p in pairs:
    print(f"{p['seed']:4d} {p['seat']:4d} {p['b0_my']:8.0f} {p['b1_my']:8.0f} {p['bank_delta']:+8.0f} "
          f"{p['b0_hands10'] or 0:6.0f} {p['b1_hands10'] or 0:6.0f} {p['hands10_delta']:+4.0f} {p['d20_delta']:+8.0f}")

improved = sum(1 for p in pairs if p["bank_delta"] > 0)
print(f"\nbank improved: {improved}/{len(pairs)}")
print(f"mean Δbank: {sum(p['bank_delta'] for p in pairs)/len(pairs):+.0f}")
print(f"mean Δhands10: {sum(p['hands10_delta'] for p in pairs)/len(pairs):+.2f}")
print(f"mean Δd20: {sum(p['d20_delta'] for p in pairs)/len(pairs):+.0f}")
print("wrote", out.name)
