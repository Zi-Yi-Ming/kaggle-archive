# H3 Phase 1 — Opponent-Visible Production Signal

**Date:** 2026-09-12  
**Data:** 33 live R2 episodes (22W / 11L)  
**Script:** `_h3_opp_signal.py`  
**CSVs:** `h3_opponent_features.csv`, `h3_predictive_signal.csv`, `h3_counterfactual_candidates.csv`

---

## A. Does opponent-visible state add predictive power?

**Yes, for relative gap — not for our absolute cash.**

| Target | Best own | Best opponent |
|---|---|---|
| **gap20** | d12_gap ρ=**+0.62** | d10_opp_animals ρ=**−0.74** |
| **my_money20** | d12_my_money ρ=+0.30 | d10_opp_straw ρ=+0.19 |

Opponent livestock at d10 is the **strongest single predictor of d20 money gap**.  
It does **not** predict R2’s own d20 cash.

---

## B. Most informative variables

| Feature | ρ vs gap20 |
|---|---:|
| **d10_opp_animals** | **−0.74** |
| **d12_opp_wheat** | **−0.74** |
| d12_opp_animals | −0.59 |
| d12_opp_melon | +0.58 |
| d10_opp_plant_rate | +0.51 |
| d10_opp_cow / sheep | −0.50 |

WIN vs LOSS at d10: opponent animals 11.7 vs **13.0**; d12 goose 0.8 vs **2.2**.

---

## C. Horizon

Signal is present by **d10** (10 days before d20 gap).  
d12 is equally strong for wheat/animals.

---

## D. Is it actionable?

**Unclear — likely weak.**

- More opponent animals at d10 = they are **ahead in the livestock race**, not a product we can “avoid.”
- P4.1: weak livestock opponents → R2 wins huge; strong mirrors → gap≈0.  
  So `opp_an` mostly encodes **opponent strength / family**, not a production switch.
- No evidence that changing **our** crop/animal mix in response would flip gap20.

---

## E. Minimal counterfactual (if any)

Only if we insist on testing actionability:

```text
baseline: R2 production
counterfactual: when opp_an(d10) >= 13, delay 1 animal purchase / shift 1 plant to WHEAT
```

That is a **production allocation** change, not a tape-step patch.  
**Not run this round** — predictive signal does not yet justify a specific intervention.

---

## F. Why it may fail

`opp_an → gap20` is confounded with **who we matched** (strong vs weak clones).  
It is a **matchup classifier**, not a **decision variable**.

---

## Decision

```text
H3_WEAK
```

**Opponent livestock at d10 predicts relative gap (ρ≈−0.74) but does not predict own cash and is not yet shown actionable.**

Do **not** build a full H3 adaptive agent from this alone.  
Do **not** submit.

---

## Remaining breakthrough paths

1. **Actionability test** (only if we still believe H3): controlled production swap under high vs low `opp_an` — one experiment, then close or promote.  
2. **From-scratch independent policy** without bottleneck/forecast hypothesis — high cost, weak motivation after P0–P8.  
3. **Path / last-2 management** — secondary.  
4. **Accept public-policy ceiling ~2300** and stop inventing mechanisms without evidence.
