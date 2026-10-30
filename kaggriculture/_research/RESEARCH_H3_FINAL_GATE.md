# H3 Final Gate — Actionability

**Date:** 2026-09-12  
**Design:** Control = pure R2; Treatment = R2 + suppress **one** `BUY_ANIMAL` after `opp_an(d10)≥13`  
**Opponent:** R2 mirror (trigger fires: opp_an=13 on all seeds)  
**n:** 4 seeds × 2 seats × 2 modes = 16 games  
**CSV:** `h3_action_counterfactual.csv`  
**Script:** `_h3_action_gate.py`

---

## Results

| Mode | gap20 | gap25 | margin | W |
|---|---|---|---|---|
| **C (control)** | **0** (all) | 0 | **0** (tie) | 0 ties |
| **T (treat)** | **−692 … −981** | −904 … −2402 | **−801 … −5217** | **0/8** |

Paired Δ(T−C):

| Metric | Mean | T better |
|---|---:|---:|
| Δ gap20 | **−889** | **0/8** |
| Δ gap25 | **−1976** | — |
| Δ margin | **−3223** | **0/8** |

Trigger: **8/8** (both seats, all seeds).  
Single intervention **hurts every time**.

---

## Falsifiers hit

| ID | Status |
|---|---|
| F1 no d20/d25 improve | **Hit** (strictly worse) |
| F2 money/W-L not better | **Hit** |
| F3 seat-only | **Hit — both seats lose** |
| F4 single seed | **Hit — all 4 seeds** |

---

## Answers

1. **Is opp_an only a strength classifier?**  
   **Yes.** High d10 animals mean a strong livestock peer; it is not a lever to “back off buying animals.”

2. **Does single production intervention help d20/d25?**  
   **No — it makes both worse.**

3. **Cross-seed?** Yes, fails on 4/4 seeds.  
4. **Cross-seat?** Yes, fails on 0–8 and 1–8 seats.  
5. **Worth an H3 adaptive policy?** **No.**

---

## Decision

```text
H3_PREDICTIVE_NON_ACTIONABLE
```

**H3 is closed.**

Do not design more thresholds, wheat overrides, crop avoidance, or a full adaptive agent from this signal.

No Kaggle submit. No R17.

---

## Research map after P0–H3

| Line | Close |
|---|---|
| public clone / overlays | STOP |
| inventory / RNG / order-book / price-curve | STOP |
| opponent composition / meta / goose / delayed-commit | REJECTED |
| **H3 opponent production response** | **PREDICTIVE_NON_ACTIONABLE** |

**Public shop-router family has no remaining locally validated lever to 2900+.**

Remaining options are **path/last-2 management** or a **from-scratch architecture without a bottleneck/forecast hypothesis** — not justified by current evidence.
