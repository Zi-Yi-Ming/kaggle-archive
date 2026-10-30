# -*- coding: utf-8 -*-
"""Quick analysis of _pm_bench.csv for the E agent."""
import csv, math, os

BASE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE, "_pm_bench.csv")

rows = []
with open(path, encoding="utf-8") as f:
    for line in f:
        p = line.strip().split(",")
        if len(p) >= 6:
            rows.append((p[0], p[1], int(p[2]), p[3], float(p[4]), float(p[5])))

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)

targets = ["broker_bea", "rancher_rita", "closer_cleo", "melon_mateo"]
for opp in targets:
    subset = [r for r in rows if r[0] == "E" and r[1] == opp]
    n = len(subset)
    if n == 0:
        print(f"{opp}: no data")
        continue
    wins = sum(1 for r in subset if r[3] == "1")
    losses = sum(1 for r in subset if r[3] == "0")
    ties = sum(1 for r in subset if r[3] == "tie")
    p, lo, hi = wilson(wins, n)
    margin = sum(r[4] - r[5] for r in subset) / n
    print(f"{opp}: n={n} W={wins} L={losses} T={ties} win_rate={p:.3f} Wilson=({lo:.3f}, {hi:.3f}) avg_margin={margin:+.1f}")

print("\n-- Combined 4 opponents --")
subset = [r for r in rows if r[0] == "E" and r[1] in targets]
n = len(subset)
wins = sum(1 for r in subset if r[3] == "1")
losses = sum(1 for r in subset if r[3] == "0")
ties = sum(1 for r in subset if r[3] == "tie")
p, lo, hi = wilson(wins, n)
margin = sum(r[4] - r[5] for r in subset) / n
print(f"n={n} W={wins} L={losses} T={ties} win_rate={p:.3f} Wilson=({lo:.3f}, {hi:.3f}) avg_margin={margin:+.1f}")
