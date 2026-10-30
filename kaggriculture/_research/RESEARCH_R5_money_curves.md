# R5 Money-Curve Reverse — R2 Mirror Losses

**Date:** 2026-09-12  
**Score:** R2 2361.8, rank ~870  
**Source:** 10 live R2 episodes, `_deep_r2_curves.py`

---

## Headline

In shop-router mirror matches, **R2 and opponents are nearly identical through d24**.
Losses open in the **last 2–3 days (d27–29)** by **1.5k–3k**.

### Loss curve template (Audric / Khalid / Nicolas / kurushun)

```text
d00–d24   diff within ±1k (often ±200)
d27       −700 … −2400
d29       −1300 … −3400
```

### Win curve templates

| Type | Example | Pattern |
|---|---|---|
| Blowout | yuuuki +19k | Lead from d18, compounds |
| Micro | bpb +1.1k | Never led by 500 until d25 |
| Late flip | Lucas +2.8k | Ahead mid, **lost lead on d29** (−1.2k) |

**Lucas is a warning:** even when ahead at d27, the d29 dump can reverse a micro lead.

---

## Sell-price quality (order-weighted, includes end dumps)

Milk avg price across games ranged **1.4 – 216** — dominated by end-dump order size × price, not mid-game milk economics. Not a usable mid-game signal from this metric alone.

Staple total order qty clusters at **85,539–85,540** (identical) vs blowout games at **118k** — the 85.5k cluster is the **standard R2 tape end-dump signature**. Mirrors share it.

---

## Experiments after this finding

| Build | Intent | Result |
|---|---|---|
| R11 day-29 morning premium slice (append-only) | Sell premium before shared flood | **2-2-4 mean +0.9 — no-op** |
| R8/R9/R10 earlier | Reorder / full dump | seat bias or no-op |

Local seeds often have **premium stock/price below R11 thresholds** in the 700–712 window, so the slice never fires. Live dump race may be seed/market-state specific.

---

## Revised belief

1. Mirror Elo edge is **not** a missing mid-game production step.
2. It is **late-game execution against a shared order book**.
3. Overlay hacks that fire rarely (R11) or reorder (R8/R9) fail locally.
4. A real fix likely needs **inside the tape/advance_sales**, not an outer wrapper — higher risk, do not rush.

---

## Decision

- **No submit** (quota still 5).
- Keep R2 running (2361 and climbing).
- Next: either (a) instrument local R2-vs-R2 to isolate dump-order effect, or (b) wait for more live losses with larger margins to find a different mode.
