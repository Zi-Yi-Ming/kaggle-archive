# P6.1 — Dump Inventory Audit

**Date:** 2026-09-12  
**Data:** live R2 replays (ZiYiMing) + local R2 vs fallow_finn (seeds 1–3)  
**Dump definition:** requested SELL qty ≥ 100  
**CSV:** `p6_1_dump_inventory.csv`  
**Script:** `_p6_1_dump_audit.py`

---

## Result

| Metric | Value |
|---|---|
| Total large-SELL events | **1,663** |
| Hollow (q > inv_before) | **1,663 / 1,663 (100%)** |

### inventory_before by product (q≥100)

| Item | n | mean | **median** | p75 | p90 | max |
|---|---:|---:|---:|---:|---:|---:|
| STRAWBERRY | 130 | 0.0 | **0** | 0 | 0 | **0** |
| MILK | 140 | 0.6 | **0** | 0 | 5 | 5 |
| WOOL | 229 | 1.1 | **0** | 0 | 0 | 20 |
| MELON | 106 | 0.0 | **0** | 0 | 0 | **0** |
| WHEAT | 317 | 2.1 | **0** | 0 | 0 | 32 |

**PREMIUM combined:** n=605, **median=0, p75=0**, ≥40: **0**, ≥50: **0**

Sample: `d27 SELL MILK 999` with shed MILK=0; `d28 SELL WHEAT 1000` with shed=0.

---

## Interpretation

R2’s `SELL 1000` / `SELL 997` lines are **action caps, not real volume**.  
Engine `_commit_unit` fails immediately if shed empty → **0 units settle**.  
There is **no glut dump** into the $1 zone in the measured regime.

P6’s theoretical “q=100 from I0” never happens for R2.

---

## Gate

### Gate A: **PASS**

```text
median inv_before_dump = 0 ≤ 20
p75 = 0 ≤ 30
```

---

## Decision

```text
STOP_PRICE_CURVE
```

Do **not** run split-vs-flood counterfactual.  
Do **not** build R17 from price-curve / drain timing.

Research budget moves to:

**path / private same-tier policy gap / adaptive strategy discovery.**
