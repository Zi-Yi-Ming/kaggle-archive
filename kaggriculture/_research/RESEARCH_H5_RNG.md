# H5 — RNG / Shop Coupling Audit

**Date:** 2026-09-12  
**Engine:** `kaggle_environments` 1.32.7 `kaggriculture.py`  
**Artifacts:** `h5_shop_sequence_comparison.csv`, `experiments/h5_rng/h5_shop_sequence_comparison.json`, `_h5_causal.py`

---

## Finding

**H5: CONFIRMED**

Player actions **do** change subsequent shop draws via a shared end-of-day RNG stream whose call count depends on empty tiles.

---

## Causal chain (source)

```text
_end_of_day(state, env, day):
    rng = random.Random((seed * 1_000_003) ^ day)   # fresh per day
    for each player farm:
        _spawn_weeds(farm, ..., rng)
            for y,x in board:
                if tile is None:          # ← ONLY then
                    rng.random()          # action-dependent call count
    if shop unlock day:
        town["unlocked_shops"].append(rng.choice(sorted(SHOPS)))
```

```text
player plants / builds
  → fewer tiles are None at end of day
  → fewer rng.random() in _spawn_weeds
  → different position in the day’s RNG stream
  → rng.choice(SHOPS) draws a different shop
  → both players share the same town["unlocked_shops"]
```

**Important:** both farms are processed before the shop draw, so **opponent** empty-tile count also moves **your** shop sequence.

---

## Minimal reproducible example

```text
seed ∈ {1,2,3,4,5}, 72 steps, seed in env.configuration
C0: both agents mostly PASS (50 empty tiles at day0)
C1: player0 plants WHEAT days 0–5
C2: player0 plants WHEAT days 0–15

Result: C1 shop sequence ≠ C0 on 5/5 seeds
        C2 shop sequence ≠ C0 on 5/5 seeds
First shop draw already differs on several seeds (e.g. seed2 PIZZA vs PET_CAFE)
```

Day-2 empty tiles (before first shop unlock):

| condition | empty (typ.) | weeds |
|---|---:|---:|
| C0 | ~50 | 0–1 |
| C1/C2 | ~45–46 | 4–5 |

Fewer empty → fewer `rng.random()` → different `rng.choice`.

---

## Falsifiers checked

| ID | Status |
|---|---|
| F1 all actions same shops | **Failed** (shops differ 5/5) |
| F2 divergence unrelated to RNG | **Failed** (call-count mechanism in source) |
| F3 shop uses isolated stream | **Failed** (same `rng` object as weeds) |
| F4 only noise | **Failed** (systematic 5/5, first-draw diffs) |

---

## Relation to path dependence

**Explains a concrete source of trajectory families:**

- Same agent, different **opponent** planting/building → different empty-tile counts → different shop sequence for **both**.
- R2’s `SHOP_PLANS` keys on first shops → different route → different tape → different Elo neighborhood.
- Path twin (same code, 2301 vs 2280): different matchmaking opponents ⇒ different shop streams ⇒ different trajectories, **even with identical code**.

**Does not explain:**

- Which shop sequence is “better” for win rate.
- Whether elite 2900+ deliberately shape empty-tile counts.
- Full fill-price / order-book mechanism (still open).

---

## Next decision

```text
CONTINUE_H5
```

Next (if continuing H5): measure **observable predictors of shop family** under realistic agents (empty-tile count at day-end, plant rate, opponent plant rate) — still no exploit, no submit, no R17.

Do **not** start a candidate from this alone.
