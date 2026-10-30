# P13.3 — WATER_READY_CROP

**Date:** 2026-09-12  
**Single variable:** generic `water_ready` for farmer workers (actor≥3), hour&lt;20  
**Both arms:** early MELON planting ON (`p13_1_melon`)  
**No sell/livestock/routing/planner-count changes.**

---

## Decision

```text
WATER_PRIMITIVE_SUPPORTED
```

（附注：primary `Δcash_d10`≈0；真实经济抬升在 **d11–d15+**，因 `first_yield_day=10` 收入落在 d10 日内/d11。）

---

## Micro-tests (`p13_3_water_microtests.csv`)

| Test | Result |
|---|---|
| T1 已浇水 → 不再 at-risk | PASS |
| T2 干土 → at-risk | PASS |
| T3 已成熟 → 不优先浇水 | PASS |
| T4 非作物 | PASS |
| T5 走向缺水作物 | PASS (WEST) |
| T6 无作物 → None | PASS |
| Lab water OFF | d9=0 |
| Lab water ON | **d9=1, d11=1** 存活 |

Unit+lab：**9/9**。

---

## Paired B0 vs B1（melon ON，2 seed × 双座位 vs R2）

| | B0 | **B1 water** |
|---|---:|---:|
| d10 cash | $103 | $94 |
| **d15 cash** | **$1,039** | **$7,326** |
| **d29 bank** | **$7,813** | **$21,220** |
| **MELON revenue d7–12** | **$0** | **$9,023** |
| WATER cmds | 149 | 393 |
| field MELON @d10 | 11（从未变现） | 4.8（多数已收） |
| field @d11 | 11 | 0–7 |

### Paired Δ (B1−B0)

| seed/seat | Δd10 | Δd15 | Δd29 | Δmelon_rev |
|---|---:|---:|---:|---:|
| s1 s0 | +7 | **+12,291** | **+24,821** | +13,910 |
| s2 s0 | +35 | **+3,717** | **+5,583** | +7,266 |
| s1 s1 | −15 | **+4,829** | **+6,619** | +7,458 |
| s2 s1 | −63 | **+4,308** | **+16,606** | +7,458 |

**4/4 d15↑、4/4 d29↑、4/4 melon_rev↑。**  
**4/4 d10 ≈ 0**（−63～+35，path noise 级）。

---

## Why d10 endpoint failed but mechanism succeeded

| | |
|---|---|
| Engine `first_yield_day` MELON | 10 |
| B 种下日 | d0–d1 |
| 可收日 | **d10 日内 / d11** |
| 我们测的 d10 cash | **day-boundary hour0** — 收入尚未入账 |
| B0 | 11 株一直站在地里，**rev=0**（水不够/未完成收） |
| B1 | d10 起田里 melon 掉下来 + **rev $7k–14k** + d15 现金暴涨 |

所以：**不是 MELON 不值钱，也不是 d10 账户尖峰复制失败那么简单** —  
B0 根本没走完 lifecycle；B1 走完了，钱在 **d11–d15** 体现。

---

## Success ladder

| Level | Result |
|---|---|
| 1 watering correctness | **PASS** (9/9) |
| 2 first-yield 保住 + 有产出 | **PASS** (rev&gt;0, field 下降) |
| 3 d10 cash 实质上升 | **FAIL**（时点错位） |
| 4 d15 无反噬 | **PASS**（+4k～+12k） |
| 5 跨 seed/seat | **PASS** (4/4) |

---

## Opportunity cost / confound

| | |
|---|---|
| WATER cmds | +244/局（B1 农民浇水） |
| 畜牧/卖出策略 | 未改 |
| 额外种植数量 | 未改（同一 melon hook） |
| Collateral | 农民更多走路/浇水 → 可能略减其它田间动作；**净效应仍强正** |

非 melon 全量产出未单独拆完；d29 bank 2.7× 说明没有明显总崩溃。

---

## 归因（P13 链条闭合）

```text
P13:   R2 d10 现金 = MELON sale
P13.1: 只种 MELON → B rev=0
P13.2: harvest 通路 lab 通；B 植株先死
P13.3: WATER_READY_CROP → 存活到 first_yield → MELON rev $9k → d15/d29 现金大幅上升
```

**Crop survival (water-to-survive) 是 B 缺失的 production completion 环节。**

---

## 不自动做的事

- 不把 water 默认 ENABLED=True 写进生产策略包（`p13_3_water.ENABLED=False`）
- 不改 melon 数量 / 卖出 / 畜牧
- 不提交 Kaggle

下一轮若开：在 **无 melon hook** 的 B 上单独开 `WATER_READY_CROP`，看是否同样提升现有作物（wheat/carrot）吞吐 — 验证 generic 性。

---

## Artifacts

```text
RESEARCH_P13_3_WATER.md
p13_water/water_ready.py
p13_3_water.py
p13_3_water_microtests.csv
p13_3_water_counterfactual.csv
p13_3_crop_survival.csv
p13_3_cash_effect.csv
p13_3_opportunity_cost.csv
_p13_3_microtests.py
_p13_3_water_run.py
```
