# R3 Live Replay Reverse-Engineering

**Date:** 2026-09-11  
**Source:** 7 live public episodes of submission `56167289` (tetsu R3, team ZiYiMing)  
**Artifacts:** `_external/replays/episode-*-replay.json`, `_analyze_replays.py`

---

## 1. Live snapshot

| Agent | publicScore | note |
|---|---:|---|
| **tetsu R3** | **1277.4** | last-2, still climbing |
| v66 | 1047.0 | last-2 |
| Medal R2 | 1089.1 | inactive |
| Rank | ~2800 | was ~4200 this morning |

Sampled 7 public games: **ZiYiMing (tetsu) 7–0**.

| Opponent | Our bank | Their bank | margin |
|---|---:|---:|---:|
| Enshi Zhang | 144,623 | 63,179 | +81k |
| Stanislav Kuznetsov | 132,549 | 85,334 | +47k |
| hansama.qht | 109,827 | 70,109 | +40k |
| nianyu | 79,950 | 48,827 | +31k |
| Priestess | 55,936 | 46,470 | +9k |
| CuteClaw | 109,692 | 104,004 | +6k |
| Trex | 41,322 | 39,828 | +1k |

---

## 2. What tetsu actually does live (VERIFIED from actions)

### Production template (day 15–25)

```text
quadrants: 3 (sometimes 4)
animals:   12 → 14
mix:       10 COW / 4 SHEEP   or   8 COW / 6 SHEEP   or   6 COW / 8 SHEEP
plants:    ~55–61 (strawberry / wheat / melon)
hands:     0 at day-boundary sample (reset artifact; hires happen mid-day)
```

### Sell ledger (our totals across games)

| Commodity | Typical sold units | Role |
|---|---:|---|
| **FERTILIZER** | **1,800–2,930** | **dominant cash line** |
| WHEAT | 850–1,200 | staple throughput |
| STRAWBERRY | 225–300 | premium, metered |
| MILK | 190–280 | premium, metered |
| WOOL | 150–210 | premium, metered |
| MELON | 70–120 | premium, metered |
| CARROT | 10–20 | negligible |

### Cadence

- Day **20–27** is the main sell window (often 200–470 units/day).
- Day **28** often quieter (cash already banked).
- Day **29** secondary dump (~140–170).

---

## 3. The actual separator: fertilizer economy

When opponents sell **≲300 fertilizer**, they get crushed (40–70k vs our 110–145k).  
When opponents also sell **~1,900+ fertilizer** (CuteClaw, Priestess), games become close (+1k..+9k).

**Mechanism:** every surviving animal yields **1 free fertilizer/day** via `COLLECT_FERTILIZER`.  
14 animals × ~15 mature days ≈ **~2,000 fertilizer** — matches our sell totals almost 1:1.

This is not a side hustle; it is a **second product line** on top of milk/wool, with almost no market-glut risk compared to melon (above_target 3.60).

### Ranking of income lines in 100k+ games

```text
1. FERTILIZER volume (collect + sell)
2. WHEAT throughput
3. MILK / WOOL / STRAWBERRY (metered)
4. MELON (small; crash-prone)
```

---

## 4. Implications for beating 1264 → 2500+

| Wrong hypothesis | Evidence against |
|---|---|
| Need RL / PPO now | tetsu is Tier-B tape+repair and already 1277 climbing |
| Need more melon | Melon sell volume is tiny among winners |
| Need 4th land always | 3 quadrants dominate; 4th appears only in one game |
| Need more cows always | 8C/6S and 6C/8S also win |

| High-value hypothesis | Why |
|---|---|
| **Maximize fertilizer collect+sell** | Largest volume line; explains 40k→140k gaps |
| Keep 14 animals fed/cared | Unfed = lost fert + lost milk + escape risk |
| Don't dump premium at $1 | Meter; day 20–27 window |
| Mid-game cash is decided by d15–20 | Losers already behind then |

---

## 5. Next experiment (local, no submit)

**Goal:** take Medal R2 or tetsu and raise fertilizer throughput without starving animals.

Ablations (paired, seeds 1–4, both seats):

1. **A0** current tetsu / Medal R2  
2. **A1** force `COLLECT_FERTILIZER` priority when `fertilizer_available` and shed has room  
3. **A2** A1 + never buy fertilizer (only collect)  
4. **A3** A1 + sell fert every turn when price ≥ 2 and stock ≥ 8  

Gate: beat A0 with WR ≥ 62.5% (5/8) and no starvation deaths.

---

## 6. What remains uncertain

- n=7 is small; 7–0 may be path luck this afternoon.
- We have not yet parsed **top-10 archive parquet** production stats (episodes.parquet is an index; full replay shards are 30–50MB/day).
- Hands count at day boundary is 0 (engine reset) — real labor scaling not measured here.
- PublicScore still converging; 1277 is not final.

---

## 7. One-line

> **线上赢家不是“种更多瓜”，而是“14 只动物把肥料当第二主业卖出去”。tetsu 已经在这么做；下一步应把这条线做到更强，而不是再换一个公开 notebook。**
