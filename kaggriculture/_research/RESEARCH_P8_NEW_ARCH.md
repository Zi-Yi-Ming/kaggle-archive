# P8 New Policy Architecture — First Prototype Gate

**Date:** 2026-09-12  
**File:** `_new_goose_bakery.py`  
**Gate:** 8 games vs R2, both seats

---

## Top 3 new hypotheses (structurally ≠ R2)

### H1 — Goose/Egg bakery economy
**Mechanism:** daily egg production + bakery demand; different from 8C/6S milk/wool tape.  
**Observable:** shops, egg price, goose count.  
**Failure:** feed starvation, egg glut, slow mid-game cash.

### H2 — Delayed specialization (optionality)
**Mechanism:** R2 commits at day 6 (SHOP_PLANS @ step 144). Keep a generalist farm until d10–12, then specialize using fuller shop + opponent tile info.  
**Observable:** shop list, opponent crops/animals at d10.  
**Failure:** generalist is strictly worse mid-game; late commit loses production window.

### H3 — Opponent-tile production counter
**Mechanism:** if opponent tiles show heavy STRAWBERRY, avoid strawberry (price crash) and tilt milk/egg; use visible opponent plants as market forecast.  
**Observable:** opponent `tiles` (public).  
**Failure:** forecast is noisy; switching cost > benefit.

---

## Prototype: H1 goose-bakery (minimal)

Result vs R2 (8 games):

| Goose seat | W-L | mean margin |
|---|---|---:|
| seat0 | 0-4 | **−164,219** (bank $200) |
| seat1 | 4-0 | **+186,334** (R2 at $200) |

**4-4 with mutual bankruptcy.**  
Not “close loss” — **one side collapses to ~$200**.  
Seat0 goose is **broken** (likely egg/wheat dump or feed failure), not a viable architecture.

**Gate 1: FAIL.** Do not expand this prototype.

---

## Decision

```text
NO_STRONG_CANDIDATE_THIS_CYCLE
```

- H1 prototype **falsified** in first gate (bankrupt / seat-artifact).  
- H2 / H3 **not yet implemented**; they remain the only untested new spaces.  
- **Do not submit.**  
- **Do not treat goose as a near-miss** — $200 is a hard failure.

---

## Highest-information next experiment (if continuing)

**H2 decision-bottleneck + delayed commit:**

1. On R2 live/local traces, find first day where money_gap stays permanently ≤ −1k (optionality loss).  
2. Build a **delayed-shop-router**: generalist wheat+1cow+2goose until d12, then switch to R2-like 8C/6S.  
3. Gate: 8 games vs R2; require ≥4-4 **and** no bankruptcy.

H3 is secondary (needs reliable opponent-tile features).

No R17, no Kaggle submit.
