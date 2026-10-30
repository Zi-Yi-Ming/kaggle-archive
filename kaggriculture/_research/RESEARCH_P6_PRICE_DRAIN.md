# P6 — Price Curve × Town Drain

**Date:** 2026-09-12  
**Engine API:** `kaggriculture.market_price`  
**CSVs:** `p6_price_curve.csv`, `p6_marginal_revenue.csv`  
**Script:** `_p6_price_drain.py`

---

## Engine rule

```text
price(inv):
  if inv < I0:  base + amp * f(I0 - inv)     # scarcity
  else:         base - amp * f(inv - I0)     # glut
  floor at $1

SELL unit:
  quote at current inv → money += quote → inv += 1  (if price > 1)

TOWN drain:
  shops every 4 steps, center every 24 → inv -= k → price rises
```

**Selling walks inventory up → later units get worse prices.**  
**Town drain walks inventory down → next sells get better prices.**

---

## Curve (from I0=10000, sequential sell)

| Item | q=10 avg | q=50 avg | q=100 avg | last unit q=100 |
|---|---:|---:|---:|---:|
| STRAWBERRY | 111 | 73 | **38** | **$1** |
| MILK | 151 | 109 | **62** | **$1** |
| WOOL | 198 | 153 | **80** | **$1** |
| MELON | 250 | 242 | 217 | 152 |

**Finding:** From I0, premium **collapses after ~50 units**; units 50–100 are nearly worthless.  
MELON is flatter until ~100+.

---

## Drain interaction (analytical, inv start 9800)

| Item | flood 100 @9800 | after drain 50 | split 50+drain+50 |
|---|---:|---:|---:|
| STRAWBERRY | 22,256 | **23,863 (+1.6k)** | 23,120 (+0.9k) |
| MILK | 26,613 | **28,276 (+1.7k)** | 27,508 (+0.9k) |

**Sell-after-drain beats sell-before-drain** by ~7% on 100 units.  
Effect is **real but modest** vs path noise (~thousands on final bank).

---

## In-engine flood vs split

Harness under-reported (money stayed 3000) — **not trusted**.  
Analytical curve uses the **same engine `market_price`** as production; treat that as primary.

---

## R2 relevance

R2’s **listed** floods are often `SELL item 1000`.  
Actual **shed stock** in live traces is typically **tens**, not hundreds.  
So the 1000 is a **cap**, not 1000 units sold — flood may **not** be dumping 100 into the $1 zone.

R2 **does** sometimes hold mid-stock (P1: inv 20–29 rarely listed).  
If those units wait until a **scarcity** window (post-drain), that is the only place a timing rule could pay.

---

## Falsifier

If R2 shed stock at dump time is almost always ≤20, then “flood kills MR” is **false for R2**.  
If stock is often 50+ before a 1000-flood, then split/hold is **supported**.

---

## Decision

```text
PRICE_MECHANISM_WEAK
```

**Engine law is confirmed** (sequential sell walks price to $1; drain-before-sell helps ~7%).  
**As an R2→2900 explanation it is weak:** R2’s real sell quantities are often small; the 1000-floods are mostly hollow.  
No R17 from this line alone. Do not submit.

---

## What this does justify

A **narrow** candidate only if live shed-stock audit shows large pre-dump inventory:

```text
if shed[premium] >= 40 and price low and drain soon:
    sell ≤20 now, hold rest until after drain
```

That audit is the **next single experiment** — not another tape step.
