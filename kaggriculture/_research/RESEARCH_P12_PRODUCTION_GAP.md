# P12 — Production Gap Decomposition

**Date:** 2026-09-12  
**Input:** P11 B planner (`p11_planner/`) vs R2 (`_push_medal/main.py`)  
**Method:** paired traces (seed 1–3 × both seats), day-end accounting, single-primitive ablation (seed 1–4 × both seats)  
**No Kaggle submit. v11E untouched.**

---

## Decision

```text
MULTI_FACTOR_GAP
```

Ranked contributors to the ~$140–150k final gap:

| Rank | Mechanism | Evidence | Single-primitive result |
|---|---|---|---|
| **1** | **Production throughput** (animal yield + plant fill) | d15 R2: 8C/6S/2.5G, 57 plants, shed 5; P11: 4C/1.5S/0G, 12 plants, shed 0.3, **21 empty + 13 weeds** | not yet intervened |
| **2** | **Daily labor employment** | B0 d10 hands often **0**; death spiral | **B1 confirmed causal** (+$6.5k bank, +1.9 hands@d10, 5/8 pairs) — **insufficient alone** |
| **3** | **Sales realization** | sell_req MILK/WOOL/EGG/STRAW/CARROT **~100×** R2 vs P11 | downstream of (1); shed empty so nothing to sell |

Not primary: seat artifact (both seats lose), executor crash (0 errors), interface (games complete).

---

## Phase 1–2 — Day-by-day cash (mean, 6 runs each)

File: `p12_cash_decomposition.csv`, `p12_day_traces.csv`

| Day | R2 $ | P11 $ | Gap | Interpretation |
|---:|---:|---:|---:|---|
| 0 | 27 | 904 | +877 | P11 over-holds cash |
| 5 | 823 | 880 | ≈0 | still parity |
| 8 | 1,519 | 124 | −1,395 | P11 cash collapses |
| **10** | **17,058** | **206** | **−16,853** | **R2 inflection: animals+plants online** |
| 15 | 35,238 | 293 | −34,945 | R2 compounds $5–8k/day |
| 20 | 69,867 | 1,522 | −68,344 | |
| 25 | 110,970 | 3,956 | −107,014 | |
| 29 | 148,112 | 6,477 | −141,635 | |

**Cash-delta gap accumulates almost entirely after d10** (cum Δ ≈ $17k by d10, $143k by d29).

---

## Phase 2b — Production state (mean day-end)

File: `p12_production_decomposition.csv`

| Metric @d15 | R2 | P11 |
|---|---:|---:|
| hands | 10.2 | 4.5 |
| plants | **57** | **12.5** |
| empty tiles | 1 | **21.3** |
| weeds | 0 | **13.3** |
| cows / sheep / goose | 8.2 / 6.3 / 2.5 | 4.2 / 1.5 / 0 |
| hungry animals | 0 | 1.7 |
| yield_units | 6.7 | 0.2 |
| shed_total | 5.2 | **0.3** |

@d10 R2 shed **53** vs P11 **1.8** — R2 has sellable stock; P11 does not.

---

## Phase 2c — Sales requested (sum over 6 games)

File: `p12_sales_decomposition.csv`

| Item | R2 req | P11 req | Δ |
|---|---:|---:|---:|
| MILK | 50,670 | 506 | +50,164 |
| WOOL | 42,646 | 244 | +42,402 |
| EGG | 49,455 | 53 | +49,402 |
| STRAWBERRY | 44,530 | 0 | +44,530 |
| CARROT | 103,288 | 2 | +103,286 |
| WHEAT | 110,677 | 316 | +110,361 |
| FERTILIZER | 70,128 | 1,251 | +68,877 |

(Req includes hollow caps / advance_sales — pattern still 50–100×.)

**二分结论：主要是「没生产出来」，不是「生产了卖不掉」。** Shed 在 d15 只有 0.3。

---

## Phase 2d — Worker ops (total)

| Op | R2 | P11 | Δ |
|---|---:|---:|---:|
| WATER | 6,652 | 2,062 | +4,590 |
| HARVEST | 2,855 | 1,205 | +1,650 |
| FEED | 2,202 | 859 | +1,343 |
| PASS | 2,718 | 171 | +2,547 |
| **PICKUP** | 1,154 | **4,030** | **−2,876** |
| HIRE req | 1,576 | 1,077 | +499 |

P11 **PICKUP-thrash**: workers cycle pickup without completing feed/place/harvest.

---

## Phase 3 — Largest single mechanism

**Not sales-first.** Sales gap is real but **empty shed** is upstream.

**Not only labor.** B0 hands@d10 ∈ {0,9}; when 0, bank dies. But even hands=9 @d10 (B0 s2 seat1) bank@$89 — labor alone ≠ revenue.

**Largest $ mechanism: production throughput** — animals not yielding (yield_units 0.2 vs 6.7), farm half-empty, weeds unchecked. That is what fills R2’s d10 shed (53) and the $14k/day cash delta.

Labor is the **hard blocker** that must be fixed first (else no one works the farm). We intervened on it as the single extractable primitive this cycle.

---

## Phase 4–5 — Primitive: `daily_labor`

Package: `p12_primitives/daily_labor.py`

```text
INPUT:  obs, target_hands (planner-chosen, default from land/cash)
OUTPUT: market orders = [optional SELL to fund] + [HIRE × k]
```

State-driven. No 720-tape. No fixed day schedule.  
**Planner independence:** `target_hands` is a parameter; planner may pass 0 (disable).

B1 wrapper (`_p12_b1_agent.py`): at hour 0, inject labor orders first; drop dawn BUY_LAND/BUY_ANIMAL so expansion cannot starve hire.

---

## Phase 6 — B0 vs B1 (4 seeds × both seats vs R2)

File: `p12_primitive_ablation.csv`, `p12_snapshot_counterfactual.csv`

| | B0 (P11) | B1 (+labor) | Δ |
|---|---:|---:|---:|
| W-L vs R2 | 0-8 | 0-8 | — |
| mean bank | $4,362 | **$10,829** | **+147%** |
| mean margin | −137,614 | −136,170 | +1,444 |
| d10 cash | $177 | $471 | +294 |
| d20 cash | $1,624 | $4,754 | +3,130 |
| d29 cash | $4,362 | $10,829 | +6,467 |
| hands@d10 | 3.4 | **5.2** | +1.9 |
| pairs bank↑ | — | **5/8** | |

**Level check**

| Level | Target | B1 |
|---|---|---|
| L1 no bankruptcy | 0/8 | **PASS** (0 bankrupt) |
| L2 d10 ≈ R2 | ~$17k | **FAIL** ($471) |
| L3 d20 gap shrink | visible | partial (still −$100k+) |
| L4 d29 gap &lt; −40k | | **FAIL** (≈ −$130k) |

Primitive is **causal and real**, **not sufficient**. Keep it; do not pretend it closes the gap.

---

## Phase 9 — Production vs sales 二分

```text
P11 挣不到的钱
= 没生产出来 (主因: animals yield≈0, plants 12 vs 57, empty 21)
+ 有货但变现弱 (次因: sell timing / premium; 本轮未单独测)
```

**先修 production throughput，再测 terminal premium。**

---

## Phase 12–13 — 不是 hidden tape

- 无 V217–V234 整包复制  
- 无固定 day schedule  
- planner 可设 `target_hands=0` 关闭  
- 只在 hour==0 触发，其余 23 step 不改变 P11 策略  

---

## Phase 14 — Counterfactual note

Paired same seed/seat B0 vs B1: 5/8 bank improved, mean +$6,467.  
Largest wins when B0 hands@d10 was 0 (death spiral avoided).  
Losses when B1 blocked dawn expansion that a lucky cash path needed (s4 seat1) — acceptable single-variable noise.

---

## Phase 15 — 当前 **不** 重开 planner search

B + extracted labor layer: no bankrupt, but production still obviously behind, d20 gap not meaningfully closed.  
**禁止** receding horizon / PPO / value search this cycle.

---

## Phase 16 — Submission

**NO SUBMISSION.** Gate not met (0-8, both seats, single opponent family).

---

## Next (highest IG, still one primitive at a time)

1. **Animal care/feed completion primitive** — kill PICKUP-thrash; ensure FEED→CARE→HARVEST→DROP closes; target yield_units ≈ R2 by d15.  
2. Re-trace: if shed_total@d15 rises toward R2, production rank-1 is addressed.  
3. Then plant-fill (empty tiles → 0) as B3.  
4. Only when d29 gap &lt; −40k: sales/terminal premium decomposition.

---

## Artifacts

```text
RESEARCH_P12_PRODUCTION_GAP.md
p12_primitives/           daily_labor.py
p12_day_traces.csv
p12_run_meta.csv
p12_cash_decomposition.csv
p12_production_decomposition.csv
p12_sales_decomposition.csv
p12_primitive_ablation.csv
p12_snapshot_counterfactual.csv
_p12_trace.py
_p12_analyze.py
_p12_b1_agent.py
_p12_ablation.py
```

R2 champion unchanged. No R17. No submit.

---

## Addendum — 败局深潜（seed1 seat0, `_p12_loss_dive.py`）

### 硬伤 1：过夜 cargo 蒸发

| | |
|---|---|
| EOD 带货天数 | **57** |
| 成功入仓 | 33 |
| **被清空** | **24 天** |

典型损失（日终 inventory，次日消失）：

- d10: MILK 3 + MELON 12 + FERT 11
- d12: FERT 17 + WHEAT 10
- d14: FERT 11 + MILK 6 + EGG 4 + WHEAT 21

引擎 **每日 dawn 清空 worker inventory**。日终不 DROP/PLACE 进 shed = 产出归零。

### 硬伤 2：`DROP` 被 validator 剥成 PASS

`p10_executor/validators.py` 原先不允许 `DROP`。  
引擎 `DROP` = **一次倒空全部背包**；`PLACE` 每回合只放一格。

d8h23 日志：`PLACE, EAST, EAST, PLACE, SOUTH, SOUTH` — 多人未到家/只放一格，MILK 6 留 inv → 次日 shed 无 MILK。

### 已修

1. `validate_farmer` 放行 `DROP`
2. EOD：`hour >= max(19, 22-dist)` 回家后 **DROP 全背包**

### B2 快检（B1 labor + DROP 修复，4 局 vs R2）

| | B1 (8局均) | B2 (4局均) |
|---|---:|---:|
| bank | $10,829 | **$12,842** |
| wins | 0/8 | 0/4 |

有提升、样本小、仍远差 R2。  
**hour≥16 过早回仓更差**（bank→$3.7k）— 走路吃掉生产时间。

### 修订因果链

```text
HARVEST/COLLECT → inventory
    ↓ 日终未 DROP（或 DROP 被 validator 剥掉）
dawn 清空背包
    ↓
shed ≈ 0 → 无货可卖 → 无现金 → 雇不起人 → 死亡螺旋
```

**rank-1「生产吞吐」的可执行子因 = 日终入仓失败**，不只是没养/没种。

下一步仍单变量：在 B2 上专攻 **FEED→CARE 闭环**（d15 hungry>0, yield≈0），不堆销售策略。

---

## B3 — FEED→CARE shepherd primitive

Package: `p12_primitives/animal_care.py`  
Wired: `production.py` actor≤2 only + wheat top-up in planner.

### 数据依据

| day | P11 FEED | P11 PICKUP | P11 yield | R2 FEED | R2 yield |
|---|---:|---:|---:|---:|---:|
| d10 | 18 | 49 | 6.8 | 96 | 0 |
| d15 | 25 | 127 | 0.2 | 102 | 6.7 |
| d20 | 37 | 189 | 0.0 | 102 | 9.8 |

PICKUP 空转 ≈ FEED 的 4–5×；yield 后期归零。

### 变体

| Variant | 描述 | bank vs R2 | 结果 |
|---|---|---:|---|
| B3_all | 全员 animal_care 优先 | $8.1k | **REJECT** — 种田被抽空 |
| **B3** | **仅 actor 0–2 shepherd** | **$30.1k** | **KEEP** |

### B3 快检（4 局 vs R2，双座位 seed1–2）

| | B2 | **B3** | R2 |
|---|---:|---:|---:|
| mean bank | $12.8k | **$30.1k** | ~$149k |
| d20 | $3.7k | **$16.0k** | — |
| d29 range | — | $19k–$51k | $140k–$184k |
| vs finn bank | — | **$61k** | — |
| wins vs R2 | 0/4 | 0/4 | — |

**相对 B0：bank ×7。** 相对 R2 仍差 ~$120k。  
L1 不破产 PASS；L2 d10≈R2 FAIL（d10 仍 ~$90，钱是 d20 后才起来）；L4 FAIL。

### 解释

- Shepherds 把 FEED/CARE/HARVEST/DROP 闭环跑通 → 后期奶/毛/蛋入仓可卖。  
- d10 仍起不来：缺 R2 的早期小麦囤货 + 肥料产品现金流（d10 R2 shed WHEAT=53 vs P11≈2）。  
- **下一刀应是早期 feed-wheat buffer / 肥料经济**，不是 terminal premium。

Artifacts add: `p12_primitives/animal_care.py`, `p12_b3_results.csv`, `_p12_b3_check.py`.

Decision 不变：`MULTI_FACTOR_GAP`；B3 保留为当前最优 substrate。NO SUBMISSION.

---

## B4 / B5 / B6 — 后续单变量

| ID | 干预 | bank vs R2 | 判定 |
|---|---|---:|---|
| B4 | 饲料小麦产品缓冲 + 加大 hold | $26.5k | **REJECT** — d10 仍死，抽血 |
| B5 | 空地种子洪泛 plant_fill | $17.6k | **REJECT** — 雇佣/买畜被挤掉 |
| B6 | 更早卖出 + 卖 FERTILIZER | $29.1k | **中性保留**（≈B3） |

### 当前最优 stack（代码里生效的）

```text
B1 daily_labor
+ B2 EOD DROP
+ B3 animal_care (shepherd actor≤2)
+ B6 aggressive product/fert sell
≈ bank $30k vs R2 $130–180k   still 0-4
```

### 仍未解决

**d10 现金尖峰**（R2 单日 +$14k）不能靠「多买饲料 / 多买种子 / 早卖」单独打开。  
更像 R2 tape 级的 **路线吞吐 + 从 d0 起的复利产销**，不是缺一个 buy/sell 旋钮。

下一刀若继续，应是 **worker routing primitive**（减少 PICKUP 空转、提高 FEED/PLANT 单位时间产出），而不是再堆市场订单。

NO SUBMISSION. R2 线上 last-2 未动。
