# P4.1 — Same-Tier Opponent Swap

**Date:** 2026-09-12  
**Control:** seed + R2 code + R2 seat + 720 steps; only opponent changes  
**Opponents:** O1=R2, O_shape=tetsu_shape, O_v66, O_kaito58  
**n:** 8 seeds × 2 seats each  
**CSV:** `p4_1_crossplay.csv`

---

## 1. Strategy class closest to R2

| Opponent | Lineage | Local vs R2 | d20 animals (typ.) |
|---|---|---|---|
| **O1 R2** | SAME_FAMILY (Moon/prvsiyan) | exact tie | 3G/8C/6S or 11S/6C |
| **O_shape** | INDEPENDENT (Jaccard 0.03) | R2 +6k mean | 3G/8C/5S or 8–9C/8S |
| **O_v66** | INDEPENDENT (Kaito closed-loop) | R2 +6k mean | 9C/5S or 11S/6C |
| **O_kaito58** | INDEPENDENT minimax | R2 +12k mean | 8–9C/5S |

Closest **production signature** to live-loss 3G/8C/6S: **O_shape** and some **O1** seeds.  
Closest **mid-game pressure**: **O_v66** (see below).

---

## 2. Can any peer reproduce live LOSS d20 negative gap?

Live LOSS mean gap20 ≈ **−2,117** (P3).

| Opp | mean gap20 | n(gap20 < −500) | mean margin |
|---|---:|---:|---:|
| O1 R2 | **+10** | **0/16** | +8 |
| O_shape | +3,536 | **1/16** | +5,986 |
| **O_v66** | **+1,843** | **6/16** | +6,377 |
| O_kaito58 | +7,136 | **0/16** | +12,394 |

**No opponent has mean gap20 < 0.**  
**v66 is the only one with frequent negative gap20 (6/16)** — partial live-like pressure, not a stable reproduction.

---

## 3. Seed reproducibility

- O1: 15–16/16 exact tie — stable  
- O_v66 negative gap20: **6/16**, both seats (4 seat0, 2 seat1) — **not seed-stable as a loss regime**  
- O_shape/O_kaito58: essentially always R2 ahead at d20

---

## 4. Seat split

| Opp | seat0 margin | seat1 margin | seat0 neg20 |
|---|---:|---:|---:|
| O1 | 0 | +16 | 0/8 |
| shape | +8,408 | +3,565 | 1/8 |
| **v66** | +7,057 | +5,698 | **4/8 vs 2/8** |
| kaito58 | +13,337 | +11,452 | 0/8 |

v66 has mild seat asymmetry in negative-gap frequency, not a 0-8/8-0 flip.  
**Not SEAT_ARTIFACT** as the primary explanation for live losses.

---

## 5. Loss-signature distance

Normalized (gap20/5k, goose/3, animals/5) vs live-loss target (−2117, 2.2, 16.6):

| Opp | mean dist | min dist |
|---|---:|---:|
| O1 | 0.658 | 0.507 |
| shape | 1.307 | 0.482 |
| v66 | 1.357 | 0.739 |
| kaito58 | 2.099 | 0.982 |

O1 looks “close” on animals/gap≈0, but that is **equilibrium**, not loss.  
No local peer **systematically** matches live-loss mid-game collapse.

---

## Decision

```text
NOT_REPRODUCED
```

**Interpretation:** live R2 losses cannot be recreated by swapping in any available same-tier opponent under fixed seed/seat. Remaining explanations:

1. **Specific private opponent implementations** not in-repo  
2. **Path / matchmaking sequence** (shop RNG coupling is real but not predictive — H5-B)  
3. **Order-book / fill microstructure** not visible in replay  
4. Early trajectory lottery interacting with near-clone tapes

v66 is the best **diagnostic** peer (frequent mild negative gap20) but **not** a reliable live-loss clone.

---

## Answers

1. Closest strategy class: O_shape on animals; O1 = true clone.  
2. **None** stably reproduce d20 negative gap; v66 6/16 only.  
3. Effect **not** seed-stable for any peer.  
4. No catastrophic seat flip; v66 mild seat skew only.  
5. If not replication → **path + private near-clones + fill/order-book**, not “goose vs cow” composition.

No R17, no submit.
