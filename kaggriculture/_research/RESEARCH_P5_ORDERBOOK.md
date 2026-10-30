# P5 — Order Book / Fill Mechanism

**Date:** 2026-09-12  
**Engine:** `kaggriculture.py` `_process_market` / `_commit_unit` / `_town_consume`  
**Docs:** `p5_engine_execution_graph.md`  
**Tests:** `p5_synthetic_market_tests.csv` (format-fixed; live debug confirms BUY/SELL settle)

---

## Finding

**There is no order book, matching engine, fill queue, cancel, or reprice.**

```text
_process_market:
  for slot i in 0..9:
    quote both players' unit i against SAME inventory
    commit seat0 then seat1   # money += quoted price (SELL)
```

Every valid unit **fills immediately** at the **pre-commit quoted price**.

```text
listing price = fill price = realized cash delta
```

---

## Causal chain (actual)

```text
player SELL order
  → quote price = f(shared inventory)
  → seat0 commits: shed-1, money+price, inventory+1 (if price>1)
  → seat1 commits: same, but inventory already moved → slightly worse price
  → town/shop drain later lowers inventory → future prices rise
```

**Not:**
```text
order → book → match → partial fill → cancel
```

---

## Synthetic confirmation

With valid `market=[[op,...]]` format, BUY_PRODUCT WHEAT then SELL settles:

- money decreases on buy (~$133 for 5 wheat)
- shed gains wheat
- SELL increases money and decreases shed at curve price
- **No unfilled remainder** unless shed empty / no cash

---

## Relation to “Elite better fills”

| Hypothesis | Status |
|---|---|
| Elite wins via queue / time priority | **Impossible** — no queue |
| listing ≠ fill | **False** for valid SELL |
| Seat0 commit-order edge on simultaneous units | **True** (small) |
| Large dump walks price down | **True** (curve) |
| Sell before vs after town drain | **True** |

This explains:
- C16 order-swap gains on a specific tape
- Seat bias when globally reordering sells
- Why “same qty, different price” can still happen: **timing vs inventory curve**, not book depth

---

## Replay “missing fills”

**Case C:** settlement is immediate; replay lists orders and next-obs money.  
There is no hidden fill layer.  
`OBSERVABILITY_GAP` is **not** the issue for cash — cash delta is fully determined by quoted prices at commit.

---

## Decision

```text
ORDERBOOK_NOT_CAUSAL
```

The execution layer is **shared-inventory price curve + lockstep seat-0-first commit**.  
It is not an order-book microstructure problem in the HFT sense.

---

## What remains for 2300→2900

After P0–P5:

| Line | Status |
|---|---|
| Clone another public tape | exhausted |
| Inventory phase | STOP |
| RNG/shop predictability | STOP |
| Opponent composition swap | NOT_REPRODUCED |
| Order-book fills | **Does not exist** |

Remaining honest levers:

1. **Price-curve timing** (when to dump vs town drain) — still real, but R2 tape already encodes much of this  
2. **Path / matchmaking neighborhood** — explains Elo spread, not a local exploit  
3. **Something not yet measured** (e.g. mid-game cash conversion vs private clones)

No R17, no submit this round.
