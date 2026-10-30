# P13.4 — Generic WATER_READY_CROP (no melon hook)

**Date:** 2026-09-12  
**Constraint:** `p13_1_melon.ENABLED = False` (forced)  
**B0 vs B1:** only `p13_3_water` toggle  
**2 seeds × both seats vs R2**

---

## Decision

```text
WATER_CONTEXT_DEPENDENT
```

不是「所有 crop 的通用救星」；在 **长 first_yield、易缺水作物（如 MELON）** 上强，在 B 自然种植的 **WHEAT（2 日收）** 上几乎没有 crop-survival 增益。

---

## B0 自然会种什么（关键发现）

| Crop | planted (mean) | weed events |
|---|---:|---:|
| **WHEAT** | **129** | **0** |
| CARROT | 0 | 0 |
| STRAWBERRY | 0 | 0 |
| MELON | 0 | 0（hook 关） |
| TOMATO | 0 | 0 |

当前 B **只种 WHEAT**。`first_yield_day=2`，几乎不会撑到 `unwatered≥2→WEED`。  
→ **没有第二个可被 water 救活的长周期作物通道。**

---

## Crop-level（mean）

| Metric | B0 | B1 | Δ |
|---|---:|---:|---:|
| plant WHEAT | 129 | 110 | −20 |
| harvest events | 248 | 198 | −50 |
| weed events | 0 | 0 | 0 |
| rev WHEAT | $4,122 | $3,486 | **−637** |
| rev MILK | $15,269 | $24,240 | **+8,971** |
| rev WOOL | $0 | $1,694 | +1,694 |
| rev FERT | $11,254 | $12,305 | +1,051 |
| **rev total** | $30,645 | $41,724 | **+11,079** |
| WATER cmds | 45 | 74 | +29 |
| MOVE | 3063 | 3065 | +2 |
| FEED | 151 | 154 | +3 |

**收入增量不在作物，在 MILK/WOOL/FERT（动物链）。**  
WHEAT 收入略降；多种的株数/收获事件也下降。

---

## Cash

| | B0 | B1 | Δ |
|---|---:|---:|---:|
| d10 | $322 | $239 | −83 |
| d15 | $2,097 | $1,488 | **−609**（3/4 为负） |
| d20 | $3,899 | $7,626 | +3,727 |
| **d29** | **$6,149** | **$15,717** | **+9,568（4/4 正）** |

B0 d29 方差极大（$85～$22k）— 样本噪声高；d15 甚至变差。

---

## 对照 P13.3（有 melon hook）

| | 有 MELON hook | 无 hook（本轮） |
|---|---|---|
| 可救作物 | MELON first_yield=10 | 仅 WHEAT=2 |
| weed/死亡 | B0 大批死 | 0 |
| melon rev | $0→$9k | n/a |
| d15 | 4/4 大升 | 1/4 升 |
| d29 | 4/4 大升 | 4/4 升但主因疑似动物/路径 |

---

## Case mapping

| Case | 判定 |
|---|---|
| A Generic multi-crop | **否** — 无第二 crop 通道；weed 双方皆 0 |
| **B Context-dependent** | **是** — 强依赖「长 first_yield + 缺水风险」作物 |
| C Tradeoff high | 部分 — d15 均值下降、WHEAT 种植/收获减少 |

---

## Opportunity cost

- 农民 WATER +29，MOVE≈不变  
- PLANT −2、HARVEST 事件 −50（少种了 wheat）  
- FEED/CARE/PICKUP 略增  
- 对 **已能存活的 wheat** 额外浇水 ≈ **低价值劳动**；d29 改善更像 **时间再分配 / 路径** 间接抬升动物收入，**不能**记成「多作物 lifecycle 通用成功」

---

## Abstraction（保持）

```text
crop state → needs_water? → WATER / skip
```

**不是** `if melon: water()`。  
**何时值得浇** 应由 planner 按 `first_yield` 与死亡风险决定 — 本轮 **不** 上 lifecycle planner。

---

## 和 R2

未复制 R2 watering timeline。R2 的优势仍是完整产销（含 MELON d10）；B 自然策略 **不会种** 那类作物。

---

## Decision

```text
WATER_CONTEXT_DEPENDENT
```

- P13.3 的 MELON 路径：**真**  
- 扩成「B 上所有 crop 通用大杀器」：**证据不足**  
- **不** 因此自动进入 Production Lifecycle Planner  
- **NO SUBMISSION**

---

## Artifacts

```text
RESEARCH_P13_4_GENERIC_WATER.md
p13_4_generic_water.csv
p13_4_crop_survival.csv
p13_4_water_actions.csv
p13_4_crop_revenue.csv
p13_4_cash_effect.csv
p13_4_opportunity_cost.csv
_p13_4_generic_water.py
```
