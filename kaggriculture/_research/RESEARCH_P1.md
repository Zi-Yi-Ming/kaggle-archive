# P1 — Inventory × Drain Phase

**Date:** 2026-09-12  
**Data:** ashok `replays_2026-08-03.parquet` elite n=227 (both ≥100k); R2 live replays n=17  
**Method:** observational only — no agent edits, no submit  
**Artifacts:**
- `inventory_drain_phase.csv` — per game/day/product inv_start/end, listed, price
- `inventory_listing_probability.csv` — P(list) by inventory bucket
- `elite_vs_r2_phase_diff.csv` — per-step inv/listed/price

---

## Confirmed

### 1. Elite winner ≈ Elite loser on inventory phase

STRAWBERRY day-mean `inv_start` / `listed` are nearly identical (e.g. d18 listed 43.6 vs 39.6; d20 inv 12.5 vs 12.6).

**Within the 2300+ elite mirror set, inventory phase does not separate winners from losers.**

### 2. Elite vs R2: inventory formation is later on R2

First day with mean `inv_start ≥ 10`:

| Product | Elite win | R2 live |
|---|---:|---:|
| STRAWBERRY | **d19** | **d22** |
| MILK | **d16** | **d22** |
| WOOL | **d18** | **d24** |

R2’s premium stock builds **3–6 days later**.

### 3. R2 uses huge “listed” floods; Elite lists gradually

STRAWBERRY listed (order qty, not fills):

| Day | Elite win mean listed | R2 live mean listed |
|---|---:|---:|
| d11–14 | 0–6 | 0 |
| d16 | 1.0 | **896** |
| d17 | 9.5 | **379** |
| d18–23 | 28–51 | 16–36 |
| d29 | 23 | **4943** |

R2’s tape mega-orders dominate the listed series; Elite’s listed volume is smoother.

### 4. P(list | inventory) — R2 holds without listing at mid-high stock

STRAWBERRY, steps d12–27:

| inv bucket | Elite win P(list) | R2 live P(list) |
|---|---:|---:|
| 1–4 | 0.078 | 0.320 |
| 5–9 | 0.026 | 0.094 |
| 10–14 | 0.145 | 0.087 |
| 15–19 | 0.071 | 0.021 |
| 20–29 | 0.059 | **0.003** |

**R2 almost never lists when strawberry stock is 20–29.** Elite still lists ~6% of such steps.

*(Note: `inv=0` shows P(list)=1.0 for all tags — measurement artifact: inventory is read from the observation *before* that turn’s harvest/list; treat 0-bucket as invalid for policy inference.)*

### 5. End residual ≈ 0 on both sides

Full liquidation at season end is shared; not the separator.

---

## Rejected

| Hypothesis | Why rejected |
|---|---|
| **H1-simple:** “Elite wins because they list earlier / list more” | Elite win vs lose list-counts and first-list medians are nearly equal; winner≠loser by early listing |
| “More sell events ⇒ win in elite set” | prem events 165 vs 159 — tiny |
| “End residual explains elite gap” | both ~0 |
| “R2 is just elite with later tape on one step” | gap is a **multi-day phase shift** + different listing intensity vs stock, not one step |

---

## Best hypothesis

**H2-phase (refined):**

```text
Elite 8C/6S family:
  production → inventory buffer d16–25
  → frequent small listings while holding mid stock
  → smooth realization into town/shop drain

R2:
  same macro 8C/6S
  but inventory phase lags 3–6 days
  and mid-high stock is mostly unlisted until tape mega-floods
```

So Elite’s edge vs **our live R2 samples** is **execution/inventory phase**, not a different crop mix.

**Caveat (must keep):** Elite **win vs lose** inside the same day still looks like path/micro-fill noise. P1 does **not** prove a single causal “target inventory” that wins mirrors. It *does* show R2 is **out of phase** with the elite production/listing envelope.

---

## H1 vs H2

| | Status |
|---|---|
| H1 Early execution (just list earlier) | **Not supported as a *win* mechanism inside elite**; **supported as a *R2 vs elite* desync** |
| H2 Phase control (drain × inventory × listing) | **Preferred** for the R2↔elite gap; not yet a proven runtime controller |

---

## Next experiment (single highest information gain)

**Do not edit R2 yet.**

Build a **local paired observational test**:

> On a fixed seed, replay R2 vs R2 and vs a *instrumented clone that only logs* (no behavior change), then measure:
> 1. first day each premium product’s shed stock exceeds 10  
> 2. fraction of steps with stock≥15 that issue a SELL for that product  
> 3. whether those two metrics match Elite envelopes in `_p1` CSVs  

If R2 on **local seeds** is already in-phase with Elite, then live lag is **path/opponent** and Phase-2 should stop chasing inventory.  
If R2 is late **even vs itself’s elite-shaped envelope**, then the next *candidate* (not submit) is a **listing-when-stock≥threshold** policy tested locally vs R2 — still not a tape-step hack.

That test is the gate before any R17.

---

## Discipline note

Goal is a mechanism that can be **falsified on R2 locally**, not a story that flatters Elite.  
If the local in-phase check shows no lag, **drop this line** and return to path/opponent modeling.
