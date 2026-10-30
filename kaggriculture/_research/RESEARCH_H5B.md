# H5-B — Shop Family Predictability

**Date:** 2026-09-12  
**Data:** ashok elite parquet n=268 (227 elite) + R2 live n=36 → **304 episodes**  
**Temporal rule:** features only from **day 2 hour 23** (last obs before first shop draw at end of day 2)  
**CSVs:** `shop_family_definition.csv`, `shop_family_prediction.csv`, `shop_family_outcome.csv`  
**Script:** `_h5b_shop_family.py`

---

## 1. Predictability

**Almost none.** Leave-one-out majority-in-bucket vs global majority baseline (~0.155):

| Feature (d2h23) | Label | acc | baseline | lift |
|---|---|---:|---:|---:|
| own_empty_b5 | first_shop | 0.151 | 0.155 | **−0.003** |
| opp_empty_b5 | first_shop | 0.155 | 0.155 | **0.000** |
| sum_empty_b5 | first_shop | 0.164 | 0.155 | **+0.010** |
| own_plants | first_shop | 0.175 | 0.155 | **+0.020** |
| opp_plants | first_shop | 0.155 | 0.155 | **0.000** |

first2 family: 58 unique labels; LOO acc **0** (no usable signal).

**Crosstab:** 270/304 episodes already have `sum_empty ≈ 5` at d2h23.  
Real agents **converge on nearly full boards by day 2** — the H5-A lever has almost no residual variance in production trajectories.

## 2. Driver

In **forced** C0 vs C1 experiments (H5-A), own planting moved shops 5/5.  
In **real** trajectories, empty-tile / plant counts at the shop-draw boundary are **not discriminative**.  
No evidence that **opponent-only** features predict better than own (both ~0 lift).

## 3. Horizon

Tested the **latest legal pre-draw snapshot** (d2h23). Even that is ~random.  
Earlier snapshots (d1h0) are even less variable.  
→ No useful prediction horizon for first shop / first2 in this corpus.

## 4. Outcome linkage

Elite mean margin by first_shop is uniformly ~3k–4.2k (ICE_CREAM 3046 … PET_CAFE 4187).  
**No shop family is a large win-rate separator** inside the elite set.

## 5. Decision

H5-A causal coupling is **real in the engine**.  
H5-B shows it is **not a usable predictive lever** on realistic R2/elite trajectories, and first-shop family does not explain elite W/L margins.

```text
STOP_H5
```

Return to **opponent-conditioned execution / order-book** if another line is needed.  
No R17, no submit, no agent edits this round.
