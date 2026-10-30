# P11 — Resource-Target Planner Search

**Date:** 2026-09-12  
**Package:** `p11_planner/` (decoupled from `p10_executor/` internals; reuses repair/sanitize/liquidate only)  
**R2:** `_push_medal/main.py` frozen  
**Gate:** 8 games vs R2, both seats, seeds 1–4  
**No Kaggle submit.**

---

## 1. Architecture discovery

Hard facts from P10.1 + R2 tape mining:

1. P10 executor `MAINTAIN` was a stub → P9 banked $200–450.
2. R2 is a **full production economy**:
   - HIRE 5–11× **every dawn** (workers wiped overnight)
   - 8 COW + 6 SHEEP + 3 GOOSE; 3 quadrants (@d6, @d11)
   - Worker ops: WATER/HARVEST/FEED/CARE/PLANT/BUILD/COLLECT_FERT
3. Any high-level mode planner without a production program will lose by $100k+.

| Arch | IG | Selected |
|---|---:|---|
| A Receding horizon | 24 | no (second) |
| **B Resource targets** | **27** | **YES** |
| C Opp-aware | 22 | no (H3 weak) |
| D Intent imitation | 22 | prior inside B |
| E Learned value / RL | 19 | too early |

**B:** live state → continuous resource targets → production program → worker micro-policy → p10 repair/sanitize.

Novel vs R2: cash-adaptive expansion, shop-aware crops, inventory-aware sells, runtime replan.  
Not a tape. Not P9 modes.

---

## 2. Engine constraints discovered (cause early P11 failures)

| Rule | Effect |
|---|---|
| Hands cleared every dawn | must HIRE daily |
| Shed tiles (5,4)(4,5)(5,5) often LOCKED | new hands spawn into locked; must walk WEST/NORTH |
| **Atomic PLANT**: requests > seeds ⇒ **all dropped** | must cap concurrent PLANT per crop |
| `validate_farmer` dropped BUILD_* | pastures never built until allowlisted |

---

## 3. Gate results

### vs weak bot (fallow_finn) — production competence

| | |
|---|---|
| W-L | **4-0** |
| bank | **$26.7k–$32.9k** |
| vs P9 mode machine | $400 → $26k+ |

### vs R2 — first-round breakthrough gate

File: `p11_local_results.csv`

| | |
|---|---|
| W-L-T | **0-8-0** |
| seat0 / seat1 | 0-4 / 0-4 |
| mean margin | **−152,902** |
| bankrupt | 1/8 ($111) |
| errors | none |
| gap d10 | −2.3k … −2.9k |
| gap d20 | −44k … −74k |
| gap d29 | −92k … −155k |

**Breakthrough gate: FAIL** (need ≥4-4 + novel + no bankruptcy).

---

## 4. Behavioral divergence (required check)

| Question | Answer |
|---|---|
| New strategic behavior? | **YES** — live targets, not fixed tape |
| Same as R2 economically? | **NO** — loses by ~$150k |
| Decision divergence vs R2 phase? | Land delayed/pulled by cash; animals paced by want-table; sells inventory-triggered |
| Executor stress? | Low — no crash; 1 near-bankrupt |
| Feasible intents? | Mostly yes after BUILD allowlist + PLANT budget |

`p11_intent_trajectory.csv` — daily priority / hire_n / buy_animals / buy_land.

Novel but **not profitable** vs R2. Behavioral novelty is not sufficient.

---

## 5. Diagnosis (evidence-based, Case A/B)

Per P11 §15 — do **not** invent new architectures after a clean 0-8.

| Case | Verdict |
|---|---|
| A Strategic choices bad | **Partial** — expansion pace still starves d10 cash |
| B Economic objective bad | **YES (primary)** — worker throughput + sell price path ≪ R2 |
| C Planner↔executor interface | **NO** — full games, no errors, produces vs finn |
| D R2 advantage unimprovable via planner | **Not proven** — gap is quality, not “tape magic” |

### Where the $150k goes

1. **Worker routing**: greedy nearest-task ≠ R2 V217/V218 batch routes; lots of wasted walks.
2. **Sell timing**: R2 late STRAW/MILK/WOOL at curve peaks; P11 dumps early at low px.
3. **Fertilizer + SE tomato (V219)**: not implemented at R2 quality.
4. **Early liquidity**: d10 P11 ~$150 vs R2 already compounding animals + sales.

This is **policy quality**, not architecture crash. Same class as P9, but one level up ($26k vs $400 baseline).

---

## 6. What P11 proved

1. First **runnable** strategic planner on P10 executor that actually produces (8C/6S path, plants, feeds, sells).
2. Architecture B is **behaviorally real** and **feasible**.
3. **Not competitive** with R2’s offline-optimized production tape + repair stack.
4. R2’s implicit value function is **not** recovered by naive elite-target control in one sprint.

---

## 7. Decision

```text
P11_B_PLANNER_NOT_COMPETITIVE
NO_SUBMISSION
KEEP_R2_AS_CHAMPION
```

Do not ship p11_planner.  
Do not open Architecture A/C/E this cycle (would repeat P9 pattern).  
Do not path-reroll as a substitute.

---

## 8. Highest-value next (not another architecture guess)

Ranked by expected information gain:

1. **Close the production gap** on Architecture B itself:
   - R2-quality worker routes (or extract V217/V218 as tactical, still no tape)
   - Late premium sells (STRAW/MILK/WOOL hold-to-peak)
   - Fertilizer + V219 SE tomato window
2. Only after bank gap &lt; $40k vs R2: re-run 8-game gate.
3. If still 0-8 with bank near R2: then the residual is true strategic policy — consider receding-horizon (A) **on top of** the now-competent production layer.

---

## 9. Artifacts

```text
p11_planner/                  package
p11_architecture_candidates.md
p11_architecture_score.csv
p11_r2_tape_timeline.csv      R2 event mine (no tape copy)
p11_r2_plan_summary.csv
p11_intent_trajectory.csv
p11_local_results.csv         8-game gate
p11_smoke_results.csv
_p11_mine_r2_timeline.py
_p11_local_gate.py
_p11_smoke_full.py
```

No R17. No submit. v11E untouched.
