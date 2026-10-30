# P2 Router Lineage + Cross-play

**Date:** 2026-09-12  
**CSV:** `router_lineage.csv`, `p2_router_crossplay.csv`

---

## Lineage

| Pair | Verdict | Evidence |
|---|---|---|
| R2 ↔ Moon | **SAME_FAMILY** | yhay81+aurax7+SHOP_PLANS; token Jaccard **0.982**; local **6/6 exact tie** |
| R2 ↔ prvsiyan | **SAME_FAMILY** | Jaccard 0.994 |
| R2 ↔ tetsu_msf router.py | **SAME_FAMILY** | explicit yhay81 header |
| R2 ↔ tetsu (adaptive) | **PARTIAL / different tapes** | Jaccard low; no yhay81 markers; local historically beatable by R2 |
| R2 ↔ **tetsu_shape** | **INDEPENDENT** | Jaccard **0.030**; no yhay81/SHOP_PLANS markers |
| R2 ↔ boatlee | **INDEPENDENT** | Jaccard ~0 with R2; tetsu↔boatlee 0.996 (boatlee≈tetsu family) |
| R2 ↔ rayk / kaito58 | **INDEPENDENT** | low Jaccard |

### Third independent executable router

**`tetsu_shape`** (`tetsutani/shape-the-shop-work-the-pasture-kaggriculture`) — best non-homologous executable router in-repo.

---

## Cross-play: tetsu_shape vs R2 (8 games)

| X seat | Result |
|---|---|
| seat0 | **0-4**, mean **−16,257** |
| seat1 | **4-0**, mean **+9,960** |
| overall | **4-4**, mean −3,149 |

**Result C — severe seat split.** Not Result B (no ≥5/8). Not clean Result A either (independent code, not exact tie).

---

## Interpretation

1. **Same-family (R2/Moon):** exact equilibrium in-engine.  
   → “2300 mirror band is strategy-family equilibrium” is **supported** for yhay81 clones.

2. **Independent router (shape):** not a free win; **first/second-mover / market-order interaction** dominates (seat0 loses big, seat1 wins big).  
   → Cannot promote shape as candidate from this matrix.

3. Live losses vs 3G/8C/6S clones + local exact-tie clones ⇒ **rating spread is path/neighborhood**, not a missing overlay on R2.

---

## Files

- `router_lineage.csv` — sha / markers / jaccard / verdict  
- `p2_router_crossplay.csv` — 8-game margins  

---

## Final

```text
FINDING:
- third independent router found: tetsu_shape
- R2/Moon same-family exact-tie equilibrium
- independent X is Result C seat-split, not a local champion

EVIDENCE:
- lineage hashes/Jaccard
- R2↔Moon 6/6 tie
- shape↔R2 4-4 seat0 −16k / seat1 +10k
- live losses 11/11 3G/8C/6S

DECISION:
- RUN_H5
```

(Seat-split investigation is noted; H5 RNG/shop coupling is the prescribed next mechanism audit. No R17, no submit.)
