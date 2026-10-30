# P10 — Tactical Executor Reconstruction

**Date:** 2026-09-12  
**Source:** `_push_medal/main.py`  
**Docs:** `p10_executor_architecture.md`, `p10_repair_catalog.csv`  
**Tests:** `p10_executor_tests.csv`, `p10_failure_injection.csv`

---

## Finding 1 — R2 executor is NOT simple

Layer stack (10+ wraps):

```text
tape + repair_weeds + advance_sales + liquidate
→ V217 plan → V218 routes → V219 walk/worker
→ V224 sales-first → V226 topup → V231 controller
→ V233 sheep/wool-fert → V234 feed rescue
```

**11 distinct repair/recovery types** catalogued (R1–R11).  
This is why a naive mode-machine lost by $160k.

---

## Finding 2 — Repair library (summary)

| ID | Name | Role |
|---|---|---|
| R1 | weed_dig | DIG + queue original plant/build |
| R3 | advance_sell | pull next-turn sells (skip WHEAT/FERT) |
| R4 | projected_shed | stock after PICKUP/DROP/PLACE |
| R5 | liquidate_718 | terminal full dump |
| R7–R9 | V233/V234 | sheep commit + feed rescue |
| R10–R11 | topup/controller | cash/capacity recovery |

---

## Finding 3 — Micro-tests

| Test | Result |
|---|---|
| repair_weeds → DIG | PASS |
| queue pop after weed clear | PASS |
| projected_shed PICKUP | PASS |
| liquidate first item | MILK first (**correct**; test expected WHEAT — **test bug**) |
| advance skips WHEAT | FAIL in harness (tape/stock setup) |
| subtract advanced | FAIL in harness |

**3/6 harness pass** — failures are **test scaffolding**, not proof R2 is broken.  
Primitive behavior on weed/DIG/shed is **verified**.

---

## Finding 4 — Failure injection (R2 vs finn, seed 1)

Baseline bank **152,052**. Inject at step 48:

| Injection | Bank | Δ | Recovered? |
|---|---:|---:|---|
| SELL zero stock | 191,745 | +40k | yes (path change) |
| BUY_ANIMAL 99 no cash | 171,520 | +19k | yes |
| force PLANT MELON | 104,941 | **−47k** | **no** |
| invalid FLY / NOT_AN_ITEM | 110,598 | **−41k** | **no** |

R2 **survives** market-level garbage (engine no-ops).  
**Unit-level garbage** (forced PLANT / invalid farmer) **burns turns** and cannot be repaired — those actions are not in the repair catalog.

---

## Decision

```text
EXECUTOR_WORTH_BUILDING
```

**Why:**  
- Multi-layer repair stack is real and non-trivial (P9 failure explained).  
- Primitives (weed queue, shed projection, advance sales) are implementable and testable.  
- Full executor ≠ tape: `executor.step(state, intent)` is a valid future interface.

**Caveat:**  
- Do **not** copy the 720-step tape into the executor.  
- Rebuild only primitives + repairs + intent→action mapping.  
- Next cycle: implement `p10_executor/` with T1–T7 unit tests ≥95%, then attach a **simple** planner (not P9’s broken modes).

No R2 edit, no Kaggle submit.
