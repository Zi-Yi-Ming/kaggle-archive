# Kaggriculture R2 Field Notes — Open Source & Tape Bots

**Date:** 2026-09-11  
**Baseline frozen:** v11E not modified for research (only a restore submit)

---

## 1. What "录像带机器人 / tape bot" means

A **tape bot** (录像带机器人) is an agent that **replays a pre-recorded 720-step action schedule** ("tape"), usually with a few observation-conditioned repairs.

Typical stack:

```text
observe first 2 town shops
    → pick one of N complete action tapes (shop-pair router)
    → each turn: copy tape[step]
    → repairs: weed DIG, weed-block delay, advance/delay sells, terminal liquidate
```

Examples already in this repo:

| Agent | Tape core | Extra |
|---|---|---|
| **Medal R2 / prvsiyan / yhay81 Shop Router** | 13 tapes keyed by first two shops | weed repair, sale advance, liquidate |
| **tetsu2131** | 5 route tapes (`_kawa_route_label`) | many heuristic repairs |
| **v11E / closer_cleo family** | one meta field-plan tape | market controller / sell ordering |

This is **Tier B heuristic adaptive**, not RL. Public "clone open source → silver" claims almost always mean: **ship a strong public tape+router**, not invent new RL.

---

## 2. Live rating scale (important)

From `kaggle/kaggriculture-episodes-index` (host daily dumps):

| Date | top_avg_score | median_avg_score |
|---|---:|---:|
| 2026-08-09 | 3218 | 3068 |
| 2026-09-06 | 3018 | 2863 |

Leaderboard top today: **~3130**.  
Your API `publicScore` starts at **600** and climbs with matchups.

Current actives:

| Ref | Agent | publicScore |
|---|---|---:|
| 56166861 | **Medal R2 ShopRouter** | **882.0** (was 600) |
| 56167289 | tetsu R3 (just submitted) | initial |
| 56167039 | v11E restore | 647.8 (was 600) |
| 56047543 | old settled v11E | 809.7 |

**Only last 2 submissions stay active.** Medal R2 already beats old settled v11E (882 > 809.7) and is still matching.

**Win/loss/tie only** — coin margin does not affect rating.

---

## 3. Best open resources found this round

### Datasets (downloaded index + ref pack)

- `raykkretzschmar/kaggriculture-reference-agents` (152 KB) — tiered ladder Finn→Cleo, **meta-line banks ~148k–164k**
- `kaggle/kaggriculture-episodes-index` — daily top-episode dumps
- `georgymamarin/kaggriculture-episodes` — ~14 GB full corpus
- `destbreso/kaggriculture-benchmark-matchups` — replayable matchups
- `vijaikm/kaggriculture-match-replay-corpus` — 500+ match replays

### GitHub strategy docs (high signal)

- `Kinjuriu/washamba_bots` — full mechanics + rating notes
- `LeEmperor/kaggriculture` — OCaml native sim + league search plan
- `Rohanjain2312/kaggriculture-lab` — clean rules reference; notes a **164k winning replay** (14 animals cows+sheep, fert, ~12 hands by day 11, 3 lands, strawberry>melon)
- `Tamizharuvi2006/Kaggriculture` — large research index; **market realization (milk/strawberry price) is the elite separator**, not raw production; naive milk-hold rules failed paired gates

### Kaggle notebooks already local

- yhay81 Shop Router 0909 (via prvsiyan packaging) → **Medal R2**
- tetsu2131 Adaptive Farming → **tetsu R3**
- flexonafft / salemali7 also 16-0 vs v11E locally

---

## 4. Reference-agent league (what "strong" looks like locally)

From `baseline_league.csv` expected banks:

| Tier | Agent | expected bank |
|---|---|---:|
| 0 | fallow_finn | 3,000 |
| 5 | rancher_rita | 46,211 |
| 6 | broker_bea | 164,265 |
| 8 | slotter_silas | 162,999 |
| 9 | closer_cleo | 148,546 |

**Meta-line (Bea/Silas/Lena/Cleo) share one field plan**; they differ mainly in **sell-slot ordering**. That alone is worth thousands of coins.

Our Medal R2 locally crushes this meta-line — but live ladder is a much harder pool (median top-episode ~2860).

---

## 5. What we submitted today

1. **Medal R2** = yhay81 shop-router + aurax7 sell timing (prvsiyan package)  
   - Local: 6-0 vs v11E mean +51k; 6-0 vs tetsu mean +36k  
   - Live: 600 → **882** and climbing  

2. **tetsu R3** = tetsu2131 adaptive farming (second active slot)  
   - Local: 16-0 vs v11E  

3. v11E restore was a false alarm (user correctly noted 600 is the initial rating).

---

## 6. Honest gap to medal

- Prize: **top 10 × $5,000** (not a soft silver auto-award).
- Gold band ~**2960–3130**.
- "Clone public tape → silver" is **directionally true vs weak baselines**, but public notebooks (best-score 2483–2879) are **not automatically gold**.
- Live pool already contains many tape routers; edge must come from **better tapes, better sell timing, better opponent handling**, or a **meta-router over multiple strong tapes**.

---

## 7. Next high-info moves

1. **Let Medal R2 + tetsu R2 converge** for a few hours; watch if either clears ~1500–2000.  
2. Pull a **recent small episodes day** (not 21 GB) and reverse-engineer top-agent action stats (hands, animals, sell cadence).  
3. Hunt **Kaito Fukami** public notebooks (dzjiann: Kaito v35 beat tetsu 17-15).  
4. If both public tapes stall below ~1800: build a **2-tape meta router** (shop-pair → choose Medal R2 vs tetsu) rather than jumping to PPO.

---

## 8. One-line

> **Tape bots = 预录 720 步行动表 + 观测修补。开源复刻确实能显著超过 v11E，但要冲牌还要在真实 3000 分池里继续收敛，并拿到比公开 notebook 更强的 tape/卖出时序。**
