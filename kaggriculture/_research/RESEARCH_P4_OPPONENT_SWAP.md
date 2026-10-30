# P4 — Matched-State Opponent Swap

**Date:** 2026-09-12  
**Design:** same seed, same R2 policy, same seat, same 720-step config; **only opponent policy changes**  
**Conditions:**
- **O1** = R2 vs R2 (mirror)
- **O2** = R2 vs rancher_rita (livestock, no goose)
- **O3** = R2 vs scripted 3-goose/cow/sheep bot  
**n:** 8 seeds × 2 seats × 3 conditions = 48 games  
**CSVs:** `p4_matched_state.csv`, `p4_money_gap.csv`, `p4_listing_behavior.csv`, `p4_opponent_features.csv`

---

## Controlled?

| Variable | Controlled? |
|---|---|
| seed | **Yes** |
| R2 policy / code | **Yes** |
| R2 seat | **Yes** (both seats) |
| env config (720 steps) | **Yes** |
| early trajectory / inventory at d10 | **No** — opponent actions differ from turn 0 |
| true fill / order book | **No** — not in replay |

Closest legal matched-state: **seed+R2+seat fixed, opponent swapped**.

---

## Effect size

| Opp | W-L-T | mean gap20 | mean gap25 | mean margin | R2 list ev d15–26 |
|---|---|---:|---:|---:|---:|
| **O1 mirror** | 0-1-15 | **0** | −11 | **−11** | 170 |
| **O2 rita** | 16-0-0 | **+57k** | +91k | **+114k** | 177 |
| **O3 mixed bot** | 16-0-0 | **+70k** | +115k | **+148k** | 187 |

**Seat:** O1 both seats ≈0; O2/O3 both seats huge positive (no seat reversal).

---

## Reproducibility

- O1: 15/16 exact tie (1× −176 at seat1 seed6) — **stable local equilibrium**
- O2/O3: 16/16 wins both seats — **stable, but vs weak opponents**

---

## Mechanism

Weak livestock opponents **do not** recreate the live LOSS environment.  
They leave R2 **ahead** by d15–20 by tens of thousands.  
Live losses (P3) showed R2 **behind at d20** against **strong near-clones**.

O1 confirms: **byte-similar shop-router = exact tie in-engine**.  
Live 1.5k–5k margins require **different competitive code**, not “goose vs cow composition” alone.

---

## Decision

```text
CONTROL_INVALID
```

Reason: seed/R2/seat control succeeded, but **O2/O3 are not the live-loss opponent class**.  
This experiment **cannot** support or refute H_OPP among **peer-strength** agents.  
It **does** show: replacing the mirror with weak livestock **helps** R2, not hurts it.

---

## Next (not a candidate)

To test H_OPP properly need a **peer-strength non-R2** opponent already in-repo:

- **tetsu_shape** (independent, seat-split vs R2)  
- **Moon** (=R2, useless for swap)  
- **v66** / **Kaito v58**

Recommended next: **R2 vs tetsu_shape / v66** same seed matrix, measure R2 money_gap d20 — still diagnostic, no submit.
