# P2 — Mechanism Discovery (first pass)

**Date:** 2026-09-12  
**Artifacts:** `p2_straw_execution.csv`, scripts `_p2_straw_exec.py`, `_p2_prem_compare.py`, `_p2_r2_live_opp.py`

---

## Current belief

**Live R2 Elo (~2300) is driven by beating non-mirror / weaker families, while exact 8C/6S+3GOOSE clones are roughly even (1.5k–5k micro margins).**

Inside the elite mirror set, **first-list day does not separate winners from losers** (STRAW/MILK/WOOL all ~identical).  
Winners list **more quantity** at **slightly better list-price**; margin correlates with `d_px` and `dq`, **not** `dfirst`.

So:
- **H1 Early execution (as win mechanism in elite): REJECTED**
- **H2 Same-qty different-price: WEAK** — qty actually differs; price gap is small (straw 175.4 vs 173.2)
- **H4 Path / H1-opponent-family: STRENGTHENED** for *live rating*
- **Inventory phase (P1): STOPPED** (local gate)

---

## Strongest alternative

**Selection bias:** ashok “top-10 archive” already conditions on high banks; elite W/L differences are residual noise inside one family, not a transferable 2900 mechanism.  
2900+ may still be the same family + better path/neighborhood, not a new execution policy.

---

## Evidence (P2-E1 elite execution)

| Product | win q | lose q | win first | lose first | corr(margin,d_first) | corr(margin,d_px) | corr(margin,d_q) |
|---|---:|---:|---:|---:|---:|---:|---:|
| STRAWBERRY | 498 | 431 | 11.25 | 11.25 | 0.015 | **0.459** | 0.357 |
| MILK | 514 | 439 | 8.00 | 8.00 | n/a | **0.513** | 0.391 |
| WOOL | 295 | 263 | 5.19 | 5.00 | 0.048 | **0.478** | 0.411 |

MILK first-list is **day 8 in all 227 games** — pure tape constant, not a decision.

## Evidence (P2-E2 R2 live)

| Result | n | Opponent structure |
|---|---:|---|
| WIN | 22 | Mixed: non-goose, 11–18 animals, **and** some exact 3G/8C/6S |
| LOSS | 11 | **11/11 exact or near-exact 3GOOSE+8COW+6SHEEP, 17 an, 3 quads** |

Loss margins −1.5k…−12k; win margins vs non-clones often +20k…+80k.

---

## Falsifier status

| Hypothesis | Status |
|---|---|
| H1 early list → elite win | **Falsified** (dfirst≈0) |
| H2 price-only same qty | **Weak / not primary** |
| H1 opponent-sensitive live Elo | **Supported** (losses = clone family) |
| H4 path | Still open (twin 600→2280) |
| H5 RNG | Untested this round |

---

## Highest-information next experiment

**Not** another tape overlay.

> **Controlled local clone-vs-clone tournament with *near*-clones** (byte-identical R2, Moon, and a third shop-router if available) across many seeds, measure whether any *deterministic* execution difference exists *at all* in-engine.

If R2 vs Moon is always exact tie (already 6/6), then **in-engine near-clones are identical**; live margins require **different code**, not path.

Then the only remaining levers for 2900 are:
1. **Genuinely different execution policy** (not overlay on R2)
2. **Opponent-neighborhood / path**
3. **Something H5/H6** we have not measured

### Expected result if H4-only
Local clone-vs-clone stays exact ties; live spread stays large.

### Falsifier
If we find a near-clone that **reliably beats R2 ≥5/8 locally**, H4-only is false and we have a candidate.

---

## Decision for this pass

- Do **not** form R17.
- Do **not** submit.
- Next single experiment: **clone-vs-clone determinism + any third shop-router** (Moon already tie; confirm + search for a *different* public router we have not treated as identical).

If no such agent exists in-repo, next is **H5 RNG/shop coupling audit** (cheap, local).
