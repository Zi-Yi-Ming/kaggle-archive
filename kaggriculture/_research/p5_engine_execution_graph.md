# P5 Engine Execution Graph — Kaggriculture Market

**Source:** `kaggle_environments/envs/kaggriculture/kaggriculture.py` 1.32.7

---

## Summary

**There is NO player-to-player order book, no matching, no fill queue, no cancel/reprice.**

The market is a **shared inventory pool** with a **deterministic price curve**.  
Every valid unit SELL/BUY **immediately settles** at a **quoted price** derived from current inventory.

---

## Call graph (per turn)

```text
interpreter()
  ├─ apply unit actions (farmer/hands)          # no market RNG
  ├─ _process_market(state, env)
  │    ├─ collect each player's market queue (max 10)
  │    ├─ for slot i in 0..max_len-1:
  │    │    ├─ parse order i for each player
  │    │    ├─ HIRE / BUY_LAND once, player order 0 then 1
  │    │    └─ lockstep unit loop:
  │    │         quote both players at SAME pre-commit inventory
  │    │         _commit_unit(player 0)
  │    │         _commit_unit(player 1)
  │    │         decrement remaining; abort order if commit fails
  │    └─ _refresh_prices(market)
  ├─ _town_consume()   # shops/town drain inventory on interval
  └─ reward = farm.money  (end)
```

---

## Settlement (`_commit_unit`)

| Op | Condition | Cash | Inventory |
|---|---|---|---|
| **SELL** | shed has item | `money += price` | if price>1: `inventory += 1` |
| **BUY_PRODUCT** | money≥price, shed not full | `money -= price` | `inventory -= 1` |
| **BUY_SEED** | money≥price | `money -= price` | seeds+1 |
| **BUY_ANIMAL** | money≥price, shed not full | `money -= price` | shed+1 |

**Failed commit** (no stock / no cash / shed full) → order aborted (no retry).

**Price at commit = price quoted this unit step.**  
There is no later fill at a different price.

---

## Pricing

```text
price = f(market.inventory[item])   # curve from MARKET_PARAMS
_refresh_prices after market batch and after town consume
```

I0=10,000; town/shop **drain** inventory → prices rise; player **sells** (price>1) → inventory up → prices fall.

---

## Priority (the only “order book”)

1. **Queue slot order** within a player (first 10 orders).
2. **Lockstep unit index**: both players’ k-th remaining unit quoted together.
3. **Player order on commit**: seat 0 commits before seat 1 at the same quote.
4. **Town drain** on step multiples after market (raises future prices).

No time-priority queue across turns. No cancel. No partial-fill remainder beyond `remaining` in the current turn’s order.

---

## Implications for prior research

| Assumption | Status |
|---|---|
| Traditional fill / queue / time priority | **Does not exist** |
| listing price ≈ realized price | **True** (same quoted price) |
| Seat 0 slight advantage on simultaneous units | **True** (commit order) |
| Dumping large qty walks price down | **True** (curve) |
| Sell before vs after town drain | **True** (inventory) |
| “Elite better fills via book depth” | **Not applicable** as order-book theory |

This explains why C16 (reorder sells in one turn) can matter, and why global reorders caused seat bias.
