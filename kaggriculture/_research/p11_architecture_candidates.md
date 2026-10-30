# P11 Planner Architectures (refined after P10.1 + R2 tape mining)

## Hard constraints
- No R2 720-tape, no SHOP_PLANS copy, no schedule hidden in executor
- May reuse p10_executor primitives (weed repair, sanitize, liquidate)
- Must be behaviorally novel vs R2
- Planner reads live observable state; may runtime replan

## Critical facts that re-score architectures

1. **P10.1 executor MAINTAIN is a stub** — cannot plant/build/hire/place/feed.
   P9 mode machine banked $200–450 for this reason.
2. **R2 is a full production economy**, not a sell-tape:
   - HIRE 5–11× **every morning** (workers cleared each day)
   - Animals: 8 COW + 6 SHEEP + 3 GOOSE by d11
   - Land: 2 BUY_LAND → 3 quadrants (@d6, @d11)
   - Worker ops: WATER/HARVEST/FEED/CARE/PLANT/BUILD/COLLECT_FERT
   - Continuous sells; fertilizer as product
3. Therefore any planner that only emits high-level modes **without production
   programs** will lose by $100k+ regardless of strategic genius.

## Candidates

### A — Receding-Horizon Intent Search
State → generate feasible intents → short-horizon value → pick → executor.
Horizon 2–5 strategic decisions × 8–24 steps.

### B — Model-Predictive Resource Control (SELECTED)
State → **numeric resource targets** (cash reserve, land, animals, crops,
hire pressure, liquidation level) → production program → worker micro-policy
→ p10 repair/sanitize → action. Replan every step or on shocks.

Not P9 modes: targets are continuous, cash-adaptive, inventory-aware.
Not R2 tape: no fixed 720-step schedule; expansion speed tracks live money.

### C — Opponent-Aware Strategic Policy
Estimate opponent regime → race/neutral/defend → intents.
Weakened by H3 (predictive but non-actionable buy-one-less-animal 0/8).

### D — Imitate R2 **intent** abstraction
Mine R2 tapes → compact phase policy (expand/produce/monetize). Allowed as
*decision abstraction*, not action replay. Used **as a prior inside B**, not
as a standalone clone.

### E — Learned value function / RL
Rejected for this cycle: hand-designed production abstraction not yet proven;
RL before a competent baseline repeats P9 failure mode.

## Scores (1–5, higher better except cost)

| Arch | Novelty | Dist R2 | Cost | Observable | Searchable | Falsifiable | IG |
|---|---:|---:|---:|---:|---:|---:|---:|
| A Receding search | 4 | 5 | 2 | 5 | 3 | 5 | 24 |
| **B Resource targets** | 5 | 5 | 3 | 5 | 4 | 5 | **27** |
| C Opp-aware | 3 | 4 | 3 | 4 | 3 | 5 | 22 |
| D Intent imitation | 3 | 2 | 4 | 5 | 4 | 4 | 22 |
| E Learned value | 4 | 5 | 1 | 3 | 3 | 3 | 19 |

**Selected: B — Model-Predictive Resource Control**

Why:
- Only architecture that forces a **production-capable** fast layer (fixes P9 root cause)
- Continuous targets ≠ P9 mode soup; cash/inventory adaptive ≠ R2 fixed tape
- Fully falsifiable via intent trajectory + economic gap + 8-game gate
- D is folded in as the elite prior (8C/6S/3G/3land / daily hire), not as clone

A is second choice if B produces no decision divergence vs R2 phase schedule.
