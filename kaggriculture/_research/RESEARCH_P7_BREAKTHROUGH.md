# P7 Breakthrough — Missing Mechanism Search

**Date:** 2026-09-12  
**Live:** R2 2286, twin 2208, rank ~988  
**Goal:** reverse-engineer missing same-tier mechanism OR build meta-agent

---

## Probe A — Shop-family complementarity (meta-agent feasibility)

24 games: R2 vs v66 (12) + R2 vs tetsu_shape (12), seeds 1–6, both seats.

| Result | |
|---|---|
| R2 W-L | **24-0** |
| Shop families where R2 loses ≥50% | **none** |
| Complementary policy for meta-router | **none** |

**Meta-agent over existing public policies is dead.**  
R2 dominates v66 and shape on every sampled shop pair.

---

## Probe B — Live LOSS action-stream identity

For 6 live losses, compare R2 vs opponent **farmer/hand command counts** and **market order counts** in d14–17, d18–21, d22–25.

### Mirror losses (Audric, Khalid)

```text
d14-17 farmer cmds: IDENTICAL (WATER 173, WEST 130, NORTH 115, ...)
d18-21: IDENTICAL
d22-25: IDENTICAL
market: same HIRE/BUY_SEED_WHEAT/SELL_* histogram (±1–3 events)
money d14/d18/d22: within ~200–1,000
```

**Opponent is running the same (or byte-similar) tape as R2.**  
Final −1.5k…−3k is **not a different policy** — it is micro-execution / seat / price-quote noise inside a true mirror.

### Non-mirror losses (automatylicza, LX, Jiayi)

Opponent differs in animal mix and sometimes more `BUY_SEED_WHEAT` / `CARE` / `COLLECT_FERTILIZER`.  
These are **different implementations**, not a hidden module we can lift from the action stream.

---

## What this rules out

| Hypothesis | Status |
|---|---|
| Mirror losses hide a copyable superior action policy | **Rejected** (action streams match) |
| Meta-router over R2/v66/shape | **Rejected** (no complementary family) |
| Price-curve / inventory / order-book / RNG as local exploit | **Already closed (P1–P6.1)** |

---

## Breakthrough conclusion

> **There is no missing implementable mechanism in the public action space for R2 mirror losses.**

The 2300 band is a **real equilibrium** among shop-router clones.  
Live 1.5k–5k margins are **noise / seat / path**, not a private move we can reverse-engineer from replay histograms.

Getting to 2900+ is **not** “find the secret step in the public tape.”

It requires one of:

1. **A genuinely stronger private-class policy** (not in repo; ashok top-10 is the same family)  
2. **Path / matchmaking optimization** (twin already 2208; one more reroll allowed)  
3. **A new independent policy design** that beats R2 on the full opponent distribution — large build, 18 days left, high risk

---

## Recommendation (no submit this round)

**Do not burn quota on another overlay or public clone.**

Practical plan for remaining ~18 days:

1. **Keep last-2 = R2 + path-twin** (or swap twin if it stalls well below R2)  
2. **At most one more path reroll** of R2 (side experiment only)  
3. If a real candidate appears, gate: local ≥5/8 vs R2, both seats, ≥2 opponents  
4. Otherwise treat **2300–2400 as the honest public-policy ceiling** and decide whether a from-scratch livestock+market rebuild is worth the remaining days

---

## Files

- `p7_meta_shop_complement.json` — 24-game shop-conditioned margins  
- Script: `_p7_shop_complement.py`, `_p7_loss_action_diff.py`

No R17, no submit.
