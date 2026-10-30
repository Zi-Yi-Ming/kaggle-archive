# P9 Zero-Based New Agent Sprint

**Date:** 2026-09-12  
**R2:** ~2300 last-2  
**Gate:** 8 games vs R2, both seats

---

## Three architectures

See `p9_architecture_candidates.md`.

| | A Mode machine | B Receding horizon | C Opp counter |
|---|---|---|---|
| Abstraction | economic mode ×5 | 24-step replan | one production pivot |
| Decision freq | 5×/season + per-step | every 24 steps | once @d10 |
| Novelty vs R2 | mode switches | no 720-tape | pivot |
| IG score | **19 (selected)** | 18 | 16 (H3 already weak) |

**Selected A** for implementability + falsifiability.

---

## Prototype A result

File: `_p9_mode_machine.py`  
8 games vs R2:

| | |
|---|---|
| W-L-T | **0-8-0** |
| seat0 | 0-4 |
| seat1 | 0-4 |
| mean margin | **−162,261** |
| Mode machine bank | **$212–$451** |
| R2 bank | $127k–$194k |
| Mode switches | 1 (mostly → RECOVER after cash collapse) |

**FAIL.** Not a close loss — the fast layer is **economically incompetent** (bankruptcy).  
Behavioral novelty exists (RECOVER mode) but is a **symptom of failure**, not adaptation value.

---

## Why A failed (not “wrong idea”)

The **decision structure** is novel; the **tactical policy** cannot compete with R2’s 13-tape + repair stack.  
Zero-based architecture needs a production/sell engine at least as good as R2’s before mode switching can matter.

This is **F1-style failure** (policy quality), not “modes are useless.”

---

## B / C not prototyped

- **B** receding-horizon: same tactical gap; high impl cost for one sprint.  
- **C** already weakened by H3 non-actionability.

Per instructions: do **not** invent D/E/F/G after A catastrophically fails.

---

## Final report answers

| Question | Answer |
|---|---|
| Architecture A | Two-timescale mode machine — **0-8 bankrupt** |
| Architecture B | Receding-horizon block planner — not built this cycle |
| Architecture C | Opp-conditioned pivot — H3 already non-actionable |
| ≠ R2? | Yes structurally (modes vs tape) |
| Chosen | A (highest IG) |
| First gate | **FAIL** |
| Next | See below |

---

## Decision

```text
NO_PROMISING_ARCHITECTURE_THIS_CYCLE
```

**Do not submit.**  
**Do not ship mode machine.**

---

## What this means

R2’s advantage is **not only “the right route”** but a **high-quality tactical execution engine** (tape + repairs + sell timing).  
A new decision abstraction without that engine loses by $150k+.

Next highest-value work (not another architecture guess):

1. **Tactical engine quality** — understand R2’s per-step repair/sell stack well enough to build an equal-or-better executor, **then** attach a new decision layer.  
2. Or **path/last-2** only (R2 + twin).  
3. Or **accept ~2300 public ceiling** until a new external signal appears.

No R17. No Kaggle submission.
