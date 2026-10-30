# P3 — Opponent-Conditioned Execution

**Date:** 2026-09-12  
**Data:** 33 R2 live episodes (22 W / 11 L)  
**CSVs:** `p3_opponent_features.csv`, `p3_r2_win_loss_diff.csv`  
**Script:** `_p3_opp_features.py`

---

## Observation → Hypothesis

**Observation:** R2 losses cluster on livestock-heavy opponents (often 3G/8C/6S); wins include many non-mirrors.  
**Hypothesis:** opponent mid-game cash / listing behavior creates a market environment where R2’s fixed tape converts worse.

**Prediction:** R2 money gap at d20/d25 should be negative in losses; opponent late-flood / premium listing higher in losses.  
**Falsifier:** gaps ≈0 in losses, or opposite sign.

---

## Results

### 1. Why R2 loses to some opponents

| | WIN mean | LOSS mean |
|---|---:|---:|
| **money_gap d20** (R2−opp) | **+9,057** | **−2,117** |
| **money_gap d25** | **+12,431** | **−3,205** |
| opp late-flood qty (d27–29) | 28,165 | **62,342** |
| opp premium sell events | 150 | **188** |
| opp GOOSE @d20 | 1.0 | **2.2** |

R2 is **already behind by mid-game** in losses — not only at the final dump.

**Mirror-only (n=14, 6W/8L):**

| | WIN | LOSS |
|---|---:|---:|
| money_gap d20 | +2,202 | **−1,287** |
| money_gap d25 | +3,728 | **−2,378** |
| R2 listed events | 415 | 374 |
| R2 straw listed qty | 8,596 | 5,505 |

Even inside the 3G/8C/6S family, **losing games have R2 behind from ~d20**, with **less R2 listing volume**.

3/11 losses are **non-mirror** cow-heavy (9C, 0 goose): ShaoCharles, LX, Jiayi Tang.

### 2. Opponent behavior that separates

Not “who they are” alone, but:

- **More goose / animals by d20** when we lose  
- **Higher premium listing intensity**  
- **Larger late-game flood qty** (confounded with non-mirror blowouts; still present)  
- Within mirrors: R2’s **own mid-game listing volume is lower in losses**

### 3. Market / order-book states that change R2’s take

True **fill** prices are not in replay JSON (only list price × qty).  
Proxy: R2 **list-value** for straw/milk is lower in losses (straw qty 4.1k vs 3.1k win — wait, R2 lists *more* qty in losses but still loses on money gap at d20).  

**Correction:** `my_straw_qty` win=3132 lose=4075 — R2 lists **more** straw in losses overall; within mirrors win=8596 lose=5505.  
Overall vs mirror disagree → **opponent family confounds**. Prefer mirror-only: **less R2 listing when losing**.

### 4. Does Elite adapt?

Not tested as a paired counterfactual here. Elite first-list / inventory phase did **not** separate W/L (P0/P1).  
No evidence yet that Elite “reacts” to opponent depth in a way we can copy as a timestamp.

### 5. Falsifiable runtime boundary?

**Weak / not ready.** Best *observational* separators:

```text
money_gap(d20) < 0          → loss-prone
R2 mid-game listed volume   lower in mirror losses
opp goose≥2 + high prem listing → higher loss rate
```

Not yet a causal “if depth then hold” rule. Need controlled local replay of same R2 action under different opponent books.

### 6. Next highest-information experiment

**Matched-state counterfactual (local):**

> Fix seed + R2 tape. Vary **only opponent** among: (a) exact R2, (b) cow-heavy no-goose, (c) goose-heavy.  
> Measure R2 **money at d15/d20/d25** and **R2 listed volume d15–26**.

If (b)/(c) systematically push R2’s mid-game cash down vs (a), opponent-conditioned execution is **supported**.  
If all equal, live split is **path/selection** → RETURN_TO_EXECUTION or matchup graph.

---

## Supported / Rejected / Uncertain

| Claim | Status |
|---|---|
| Losses = only exact 3G/8C/6S | **Rejected** (8/11 mirror; 3 cow-heavy) |
| R2 behind at d20 in losses | **Supported** (all + mirror-only) |
| Opp late-flood higher in losses | **Supported** (overall; weaker in mirror-only) |
| R2 lists less in mirror losses | **Supported** |
| Elite has copyable adaptive response | **Uncertain** |
| Ready-to-code decision boundary | **Not supported** |

---

## Answers (summary)

1. **Why lose:** mid-game cash already behind; less R2 listing in mirror losses; some cow-heavy non-mirrors.  
2. **Opponent watershed:** goose/animal count + premium listing intensity + late flood; not a single shop family.  
3. **Market state:** money gap d20/d25 is the cleanest observable; fill-level book still unmeasured.  
4. **Elite adaptivity:** not demonstrated as W/L separator.  
5. **Boundary:** observational only (`money_gap_d20`, listing volume).  
6. **Next:** local matched-state opponent swap experiment.

No R17, no submit.
