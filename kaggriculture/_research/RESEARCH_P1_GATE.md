# P1 Gate — Local In-Phase Check

**Date:** 2026-09-12  
**Method:** R2 vs fallow_finn, seeds 1–8 seat0 + 1–4 seat1 (n=12), fixed seeds, no policy edits  
**Elite envelope:** ashok 2026-08-03, winners, both banks ≥100k (n=227)  
**CSV:** `p1_gate_metrics.csv`  
**Raw:** `p1_gate_raw.json`

---

## Metric A — first day inventory ≥ 10 (median)

| Product | Local R2 | Elite | delta_days |
|---|---:|---:|---:|
| STRAWBERRY | **18** | 19 | **−1** |
| WOOL | **16** | 18 | **−2** |
| MILK | **22** | 18 | **+4** |
| MELON | 11 | 11 | 0 |

Local first10 steps were extremely stable across seeds (e.g. MELON 264, WOOL 384, STRAW 453, MILK 528 on most seeds).

**Live P1 “3–6 day lag” does not reproduce for STRAW/WOOL vs a no-op opponent.**  
Only **MILK is consistently ~4 days later**.

---

## Metric B — P(SELL | inventory ≥ 15)

| Product | Local R2 | Elite | ratio local/elite |
|---|---:|---:|---:|
| STRAWBERRY | 0.011 | 0.049 | **0.22** (lists less) |
| MILK | 0.059 | 0.020 | **2.99** (lists more) |
| WOOL | 0.062 | 0.014 | **4.44** (lists more) |

Not a uniform “R2 holds and never lists.”  
Strawberry is the only product where local R2 lists *less* than Elite at mid-high stock.

---

## Comparison table (required)

```text
product | local_first10 | elite_first10 | delta_days | local_P15 | elite_P15 | ratio
STRAWBERRY | 18 | 19 | -1 | 0.011 | 0.049 | 0.22
MILK       | 22 | 18 | +4 | 0.059 | 0.020 | 2.99
WOOL       | 16 | 18 | -2 | 0.062 | 0.014 | 4.44
MELON      | 11 | 11 |  0 | n/a   | 0.000 | n/a
```

---

## Interpretation

### What P1 live samples showed
R2 live vs *elite-mirror opponents*: inventory≥10 arrived d22–d24, listed floods huge.

### What the gate shows
Against **fallow_finn** (uncontested production):
- R2’s STRAW/WOOL phase is **on time or early** vs Elite
- Listing intensity is **not systematically low**
- Only MILK phase is late

### Therefore
The live “R2 is 3–6 days late on all premium” picture is **not a pure R2-policy invariant**.  
It is **opponent/path-contaminated** (shared market drain, contested production, tape floods vs live fills).

### Seed dependence
first10 steps almost identical across 12 local games → **low seed variance** for R2 vs no-op.  
Live variance is the opponent, not the seed.

---

## Case decision

| Case | Definition | Fit? |
|---|---|---|
| A | local ≈ Elite → stop inventory line | **Mostly** (STRAW/WOOL yes; MILK no) |
| B | local also 3–6d late + low P(SELL) | **No** |
| C | mixed → uncertainty | **Yes for MILK + STRAW P15** |

MILK lag + lower strawberry P(list) are **weak, product-specific** residuals — not a coherent “phase controller” story that would justify another tape/threshold candidate without a new causal test.

Continuing the inventory/timing line would be chasing a **live artifact**, not a verified R2 mechanism.

---

## Decision

STOP_INVENTORY_LINE
