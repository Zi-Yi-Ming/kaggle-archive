# H2 Phase 1 — Decision Bottleneck

**Date:** 2026-09-12  
**Data:** 33 live R2 episodes (22W / 11L)  
**Scripts:** `_h2_bottleneck.py`  
**CSVs:** `h2_win_loss_timeline.csv`, `h2_commitment_analysis.csv`, `h2_option_set_by_day.csv`  
**Proxy:** `option_count` = cash headroom + land remaining + empty tiles + under-specialized animals + shops still arriving (0–6). **Not** a true game-theoretic option set.

---

## Timeline (mean)

| Day | W gap | L gap | W opt | L opt | W cash | L cash | W animals | L animals |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | −195 | −61 | 3.18 | 3.00 | 280 | 433 | 9.7 | 10.0 |
| 10 | +297 | +122 | 3.68 | 3.64 | 2151 | 2128 | 12.7 | 13.0 |
| **11** | **+4647** | **−24** | 4.59 | 4.27 | 15626 | 14388 | 13.8 | 15.1 |
| 12 | +3510 | −111 | 3.27 | 3.27 | 13486 | 13103 | 14.8 | 15.8 |
| 15 | +4316 | −361 | 3.00 | 3.00 | 21353 | 21284 | 15.2 | 16.1 |
| 20 | +9057 | −2117 | 2.00 | 2.00 | 46398 | 41150 | 15.3 | 16.1 |

**WIN and LOSS option proxies are almost identical every day.**  
**LOSS has slightly more animals**, not fewer.

---

## Permanent lock-in metrics

| Metric | WIN | LOSS |
|---|---|---|
| first day gap permanently ≤ −1000 | **1/22** (d29) | **11/11** — days **11,16,17,20,22,25,28,29** (spread) |
| first day option permanently ≤ 1 | **0/22** | **0/11** |

There is **no single bottleneck day** where losses uniquely collapse options.  
Permanent negative gap appears **late and scattered** (d11–d29), after the economic race is already decided by **rate of cash gain**, not by losing route choice.

---

## Interpretation

| Claim | Evidence |
|---|---|
| R2 loses optionality at a fixed early day | **Not supported** |
| Delayed commit would recover lost routes | **Not supported** — W and L look alike on option proxy through d15 |
| Divergence is mid-game cash conversion | **Supported** — gap opens from d11, widens steadily |
| Animals lock-in is the failure mode | **Rejected** — L has more animals |

**H2 as stated (early commit → irreversible lock-in → LOSS) is not what the live data shows.**

---

## Phase 2 gate

**Do not build delayed-router.**  
Phase 1 found no causal bottleneck for early SHOP_PLANS commit.  
Implementing delayed commit would test a **non-existent** mechanism.

---

## Decision

```text
H2_REJECTED
```

---

## What this means for breakthrough

Closed after P0–P8:

- public clones, overlays, inventory, RNG, composition, order-book, price-curve, meta-router, goose H1, **delayed-commit H2**

Remaining honest options (not yet tested as new architectures):

1. **H3 opponent-tile production counter** — still open, but must be a real forecast mechanism, not “avoid strawberry”  
2. **From-scratch independent livestock+market policy** — large build; elite ashok is same 8C/6S family so local ceiling may remain ~R2  
3. **Path / submission routing** — secondary; at most one more twin reroll  
4. **Accept public-policy ceiling** and decide whether 18 days justify a new architecture without a bottleneck hypothesis

No R17, no submit.
