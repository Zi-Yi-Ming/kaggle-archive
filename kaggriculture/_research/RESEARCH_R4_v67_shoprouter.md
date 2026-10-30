# R4 Morning Research — v67 shop-router counter

**Date:** 2026-09-12  
**Baseline:** Medal R2 2348 / v66 1448 / rank ~872  
**Quota:** 5 available, 0 used

---

## Hypothesis

v66 live losses to shop-router clones (automatylicza −12k) are due to missing a
public-state branch. Add signature at day 15+: opponent livestock
`GOOSE≥2 or (COW≥8 and SHEEP≥4)`, total≥13, quads≥3 → switch to `clone` route
(same counter used vs historical_victor).

## Build

`_push_v67` = copy of v66 package with patch in `candidate_v66_meta_closed_loop.py`.

## Results (local paired)

| Matchup | W-L-T | mean margin |
|---|---|---:|
| V67 vs R2 | 3-3-0 | **−2,960** |
| V67 vs v66 | 1-0-3 | +16 |

## Interpretation

1. Signature window at step 144 was **too early** (only 4C/2S, 1 quad). Fixed to 360/432/504.
2. Even at day-15, **clone route does not reliably beat shop-router** in local seeds.
3. V67 vs v66 is nearly identical — branch rarely fires or is inert.
4. **Not submitted.** Overlay-on-v66 does not beat R2.

## What this confirms

- v66's live value is **named historical counters**, not generic anti-shop-router.
- R2 remains the main horse; v66 is diversity only.
- Further "signature → route" patches need a route that is **locally proven** vs R2 first.

## Next (no submit)

1. Let R2 continue converge (2348).
2. Harvest more R2 losses at 2300+ mirror meta.
3. Only submit a candidate that locally beats R2 **≥6/8, no seat bias**.
