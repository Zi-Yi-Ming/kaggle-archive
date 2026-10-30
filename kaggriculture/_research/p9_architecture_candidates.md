# P9 Architecture Candidates

## R2 (for contrast)

- **State:** shop pair @144, per-step obs for repairs
- **Decision frequency:** one route commit + step-level tape + repairs
- **Abstraction:** exact 720-step action tape
- **Adaptation:** weed repair, advance sales, terminal liquidate
- **Not reproducible by:** “add an if” — route+tape are a fixed library

---

## A — Two-Timescale Mode Machine

| | |
|---|---|
| **State** | day, cash, animals, plants, shops seen, opp animals, prices |
| **Decision freq** | Slow: d0/6/12/18/24 mode select; Fast: every step within mode |
| **Abstraction** | economic **mode** (EXPAND / LIVESTOCK / CROP / SELL / RECOVER), not a tape |
| **Adaptation** | mode switch on observable thresholds |
| **Why ≠ R2** | R2 never changes “route class” after commit; this re-picks mode 5×/season |

## B — Receding-Horizon Block Planner

| | |
|---|---|
| **State** | full obs + opponent tiles |
| **Decision freq** | every 24 steps plan next 24-step block |
| **Abstraction** | short action block (hire/buy/plant/sell schedule) |
| **Adaptation** | re-plan from live state |
| **Why ≠ R2** | no 720-tape; horizon is 1 day |

## C — Opponent-Conditioned Production Counter (H3-harden)

| | |
|---|---|
| **State** | opp crop/animal mix @d10 |
| **Decision freq** | one production pivot @d10 |
| **Abstraction** | production allocation |
| **Adaptation** | switch crop/animal mix |
| **Why ≠ R2** | one irreversible pivot vs fixed plan |

---

## Scores (1–5)

| Arch | Novelty | Mechanism | Impl cost | Search | Falsifiable | **IG** |
|---|---:|---:|---:|---:|---:|---:|
| A Mode machine | 4 | 4 | 3 | 3 | 5 | **19** |
| B Receding horizon | 5 | 4 | 2 | 2 | 5 | **18** |
| C Opp counter | 2 | 2 | 4 | 3 | 5 | **16** |

**C is weak:** H3 already showed animal-count response hurts.  
**B** high novelty but hard to make competitive in one prototype.  
**A** best IG: clear behavioral novelty (mode switches), implementable, locally falsifiable.

**Selected: Architecture A — Two-Timescale Mode Machine.**
