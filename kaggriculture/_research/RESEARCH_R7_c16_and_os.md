# Open-Source Dig + C16 Surgical Swap

**Date:** 2026-09-12  
**R2 live:** ~2344 (stable band), rank ~885  
**Quota:** 5 unused

---

## High-value find: Beiciccc experiment ledger

`Beiciccc/Kaggriculture` documents C11–C35. Most relevant:

| ID | Change | Local effect |
|---|---|---|
| **C16** | At **step 649** only: MELON sell first, WHEAT last; same qty | **+8792 vs C15**, +5404 vs Moon (8-seed 2-seat, no negative pair) |
| C15 | Defer shed liquidation to step 681 (after town demand) | +2..+12 per seed, conservative |
| C13 | Licensed hand schedule restore | 7-1 vs C11/C12 |
| C21 | Moon hands cardinality repair | 8-0 vs Soil / Kaito v19 |
| C26 | Kaito v23 dual-regime | 80-0 local on KE 1.32.5 |

C16 proves **same multiset, only order at one late step** can be worth thousands — on *their* tape (Moon has a MELON sale at 649).

---

## Our R2 tape at 649/717

```text
649: WOOL, EGG, FERT×2, WHEAT   (no MELON)
717: all products 1000 dump
718: CARROT/WHEAT/WOOL 1000
```

Implemented **R13** (C16-style): steps {649,717,718} only, reorder existing sells premium-first / WHEAT-last, non-sells stay put.

### R13 vs R2 (8 games)

```text
4-4-0  mean=-163  seat0=-540  seat1=+213
```

**Not a pass.** R2’s 649 has no MELON; the C16 edge doesn’t transfer 1:1.  
R9 (global every-turn reorder) was worse; R13 (late only) is almost a no-op.

---

## Other open source this round

| Source | Status |
|---|---|
| FlorianTusek/kaggle-kaggriculture | competition **template**, not an agent |
| danilchil | research notes, not a drop-in |
| Otter/SpaTaro/Himanshu GitHub | **no public repos** |
| boatlee/Kaito48/43 (prior) | 3-3 seat-biased vs R2 |

---

## Decision

- **Do not submit** R13.
- Keep last-2 = R2 + v66.
- C16-style work is still the best *documented* late-game lever — next step would be **port Moon’s actual 649 schedule** (prvsiyan Moon notebook) and A/B vs R2, not another generic reorder.

## Next high-info option

Fetch `prvsiyan/kaggriculture-frontier-the-moon-counts-melons` and run it vs R2 (Beiciccc’s C21 base). One kernel download, then local paired. Low API cost.
