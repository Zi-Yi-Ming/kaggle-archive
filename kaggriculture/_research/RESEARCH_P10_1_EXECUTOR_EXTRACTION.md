# P10.1 — Executor Extraction & Parity

**Date:** 2026-09-12  
**Package:** `p10_executor/` (`intents.py`, `validators.py`, `primitives.py`, `core.py`)  
**No R2 edit. No Kaggle submit.**

---

## Dependency map

16 modules: **9 TACTICAL**, rest HYBRID / TAPE_BOUND / STRATEGIC  
(`p10_1_dependency_map.csv`)

Tape-bound (not extracted): `Policy` 13-tape library, `SHOP_PLANS`, full route selection.

---

## Level 1 — T1–T7 micro-tests

| Test | Result |
|---|---|
| T1 weed→DIG | PASS |
| T2 next-day queue pop | PASS |
| T3 projected_shed | PASS |
| T4 liquidate milk-first | PASS |
| T5 advance skips WHEAT | PASS |
| T6 subtract advanced | PASS |
| T7 invalid clamp | PASS |
| T_exec_sell intent | PASS |

**8/8 (100%)** after fixing fixture (step 48 blocked by `step%4==0 and step<144`).

---

## Level 2 — Snapshot parity

70 snapshots from R2 vs finn (seeds 1–2).

| Metric | Result |
|---|---|
| Executor sell-valid | **70/70** |
| R2 sell-valid | **70/70** |
| Same farmer cmd | 31/70 (not required — different intents) |

**Tactical validity parity ≥95%** (100% on sell legality).  
Full action equality is **not** claimed (intent-driven executor ≠ tape).

---

## Level 3 — Failure regression

| Case | Result |
|---|---|
| empty_sell | PASS (dropped) |
| no_cash_buy | PASS (clamped) |
| invalid_plant | PASS (PASS) |
| garbage orders | PASS (only valid WHEAT kept) |

**4/4.** Invalid action rate ≈ 0 after sanitize.

---

## Level 4 — Minimal planner + executor (720 steps)

Not a strategy. Harness only.

| Seed | Bank | Error | Bankrupt |
|---|---:|---|---|
| 1–3 | **2940** | none | no |

**3/3 complete.** Architecture `Planner → Intent → Executor → Action` is **runnable**.

---

## Decision

```text
EXECUTOR_PARITY_READY
```

**What we have:**
- Independent tactical executor (no 720-tape)
- Intent API: MAINTAIN / SELL / LIQUIDATE / RECOVER / CLEAR_WEED / NOOP
- 100% micro-test pass, 100% sell-validity parity, safety clamps, full-game harness

**What we do not have:**
- A strategic planner that beats R2 (out of scope this cycle)
- Full V217–V234 route fidelity (tape-bound)

**Next (allowed by prior rules):** attach a **serious** planner on top of this executor — not another P9 mode soup — and only then re-open zero-based architecture search.

No R17. No submit.
