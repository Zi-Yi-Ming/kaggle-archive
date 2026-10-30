# P10 Executor Architecture — R2 Reverse Engineering

**Source:** `_push_medal/main.py` (yhay81 + aurax7 + V217–V234 overlays)

---

## Layer stack (outermost last)

```text
Policy (tape + repair_weeds + advance_sales + liquidate)
  → V217 farmer plan
  → V218 path/routes
  → V219 walk / request / worker
  → V224 sales-first
  → V226 topup
  → V231 controller
  → V233 sheep commit / wool-fert credit
  → V234 feed rescue
  → agent() final
```

Each `agent()` wraps the previous; last definition wins.

---

## Production execution

| Concern | Mechanism |
|---|---|
| Plant/harvest | Fixed tape `PLANT`/`HARVEST`/`WATER` |
| Animals | Tape `BUY_ANIMAL` + V219/V233 place/feed/care |
| Repair weeds | `repair_weeds`: if tile WEED and cmd in {PLANT,BUILD_*} → **DIG**, original cmd queued for later same day |
| Day reset | queues cleared at dawn; unfinished work does not spill |

## Shop / market execution

| Concern | Mechanism |
|---|---|
| Orders | Tape market list, max 10 |
| Advance sell | `advance_sales`: pull next-turn non-WHEAT/FERT sells forward if stock≥q and price≥2 |
| Subtract | `subtract_advanced_sales` next turn reduces those sells (keeps slots) |
| Projected shed | `projected_shed`: estimate stock after PICKUP/DROP/PLACE this turn |
| Liquidate | `liquidate` @718: DROP + sell all projected stock, premium value sort |

## Recovery / rescue

| Layer | Trigger | Action |
|---|---|---|
| V226 topup | low cash / missing input | buy top-up |
| V231 controller | capacity / cash | adjust |
| V233 | day≥12 sheep commit | worker override for wool/fert |
| V234 | hungry sheep afternoon | BUY_PRODUCT WHEAT rescue (capped 6/day) |

---

## Executor interface (target)

```text
intent ∈ {EXPAND, LIVESTOCK, CROP, SELL, RECOVER}
executor.step(obs, intent) → action
```

**Not implemented as a full engine this cycle** — first prove primitives + repair quality.

---

## Why P9 failed

Mode machine had **no tape quality**: no weed queue, no advance_sales, no projected_shed, no rescue.  
R2’s 0-8 gap is **execution stack**, not mode selection.
