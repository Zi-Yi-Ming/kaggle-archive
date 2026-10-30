# Open-Source Inventory vs Medal R2

**Date:** 2026-09-12  
**R2:** 2361.8, rank ~847  
**Quota:** 5 unused

---

## Gate used

Local paired vs R2. **PASS** = ≥5/8 wins, no large seat bias, no crash.

---

## Already known (prior sessions)

| Agent | vs R2 | Note |
|---|---|---|
| **Medal R2** (yhay81 shop-router) | self | **champion local + live** |
| prvsiyan | same family as R2 | packaging of yhay81 |
| tetsu2131 | loses locally, weak live | dropped from last-2 |
| v66 (Kaito-v58 closed-loop) | seat-biased 2-2 | live 1448 diversity only |
| Kaito v58 main | 0-4 vs R2 | weaker than v66 package |
| Kaito v27 | 0-4 | older |
| Rayk rank-your-agent | 2-2 | near R2 |
| R5/R8/R9/R10/R11 overlays | fail / no-op | don't submit |

---

## Newly tested today

### Local GitHub agents (4 games — seat-biased, not PASS)

| Agent | W-L | mean | seat0 / seat1 |
|---|---|---:|---|
| lonespear | 2-2 | −254 | — |
| gzmcr | 2-2 | −1530 | — |
| asajjadi | 2-2 | −1491 | — |
| sey_v21 | 2-2 | +1454 | — |
| cok_v10 | 2-2 | +174 | — |
| gytdrop | 2-2 | +1978 | — |
| pomagrenate | 2-2 | −12k | crushed |
| grigorii | ERROR | missing `src` package |
| smartex-dan | ERROR | needs `sentry_sdk` |

### New public notebooks (6 games)

| Agent | W-L | mean | seat0 | seat1 |
|---|---|---:|---:|---:|
| boatlee v20 | 3-3 | +4250 | **−22.5k** | **+31k** |
| Kaito v48 | 3-3 | +365 | −21k | +22k |
| Kaito v43 | 3-3 | +2629 | −18k | +23k |

**None PASS.** Strong agents vs R2 produce **seat-asymmetric mutual destruction**, not a stable edge.

---

## Interpretation

1. **R2 is still the only agent that locally and live both perform at 2300+.**
2. Public “top” notebooks (boatlee/Kaito) are **not locally better than R2**; live Elo for them is unknown or lower.
3. GitHub mid-tier agents are not close.
4. Cloning more open source **has diminishing returns** — the remaining edge is inside R2’s own tape/endgame or a genuinely new mechanism.

---

## Decision

- **Do not submit** any of today’s candidates.
- Keep last-2 = R2 + v66.
- Research shifts from “find a better public clone” → **“understand R2’s remaining live losses”** (already: d27–29 dump race vs slightly different clones).

---

## Still untested / blocked

| Item | Status |
|---|---|
| tetsu-shape (qeinstein “strongest external”) | not fetched (Kaggle submission archive) |
| rayk-k320 SUBMISSION_B85 | only rank-your-agent main tested |
| ashok top-10 full replay shards | index only, 30–50MB/day |
| smartex-dan | needs sentry_sdk — skip |
