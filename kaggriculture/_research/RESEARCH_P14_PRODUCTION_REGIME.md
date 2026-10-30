# P14 — R2 Early Production Regime Forensics

**Date:** 2026-09-12  
**Scope:** d0–d10 only, R2 vs B, vs finn (own-side clean trajectory)  
**No B changes. No submit.**

---

## Decision

```text
MULTI_FACTOR_PRODUCTION
```

R2 不是单一 crop argmax，而是 **多时间窗生产组合**。  
简单 `net_per_day_to_cash` score **能解释 d0–d1 MELON 承诺**，**不能**单独解释 d5+ STRAWBERRY。

---

## 1. First strategic divergence

| | R2 | B |
|---|---|---|
| **Commitment day** | **d1** | **never** |
| **Committed crop** | **MELON ×12 tiles** | WHEAT only |
| d1 field | W=7 **M=12** empty=2 | W=15 M=0 empty=5 |
| d10 field | W=5 **M=12** | 全空/无长作物 |
| d0–10 seed buys | MELON 24, WHEAT 66, STRAW 40 | WHEAT 52, STRAW 15*, CARROT 20* |
| d0–10 plant cmds | MELON 24, WHEAT 62, STRAW 40 | **WHEAT 46 only** |

\*B 在 d8–d9 才买 STRAW/CARROT 种子，且 **plant cmd 仍全是 WHEAT**（种序优先 wheat）。

**第一个不可忽略的 production allocation 分叉 = d1：R2 把 ~12/25 格投入 MELON（10 日后变现），B 全部 WHEAT（2 日变现）。**

---

## 2. R2 commitment timeline (both seeds)

```text
d0  BUY MELON + WHEAT
d1  PLANT MELON×12 + WHEAT×7     ← commitment
d5  BUY/PLANT STRAWBERRY
d6–d10  MELON 保持 12 株；WHEAT 少量轮作
d10 MELON 收割变现（P13 ledger +$27k 日）
```

---

## 3. First-yield value proxy（浇满水、base 价）

| Crop | fy | seed | max_yld | px | gross | **net** | **net/day** |
|---|---:|---:|---:|---:|---:|---:|---:|
| WHEAT | 2 | 10 | 6 | 25 | 150 | 140 | **70** |
| CARROT | 2 | 20 | 4 | 35 | 140 | 120 | 60 |
| STRAWBERRY | 10 | 100 | 4 | 120 | 480 | 380 | **38** |
| TOMATO | 8 | 50 | 4 | 60 | 240 | 190 | 24 |
| **MELON** | **10** | 80 | 6 | 250 | 1500 | **1420** | **142** |

**MELON 的 net/day-to-cash 最高（$142）** — R2 d0 买 MELON 与该 score 一致。

---

## 4. Opportunity cost（粗算，每 tile d0–d10）

| 策略 | 10 日净额 proxy |
|---|---|
| MELON 一发（含水） | **~$1,420** |
| WHEAT 反复种（~5 轮） | ~$700 |
| 差额 | MELON 理论更高，但 **锁格 10 天 + 每日浇水** |

R2 实际选 MELON×12：支付 **~半天下格 + 10 日水**，换 d10 集中现金。  
B 选 WHEAT：早期现金更稳，**没有 d10 窗口**。

---

## 5. Regime score 验证

Score: `net / first_yield_day`（可选 quote 加权）

| | top1 match |
|---|---|
| **R2 plant-days** | **12/18 = 67%** |
| B plant-days | 0/6（B 全 WHEAT；若 avail 含 MELON 则 pred=MELON） |

R2 MISS 全部是 **d6–d8 实际种 STRAWBERRY，score 仍选 WHEAT (70>38)**。

→ 单一 argmax score **不够**；STRAW 是 **第二时间窗**（配合后续价/店/持续产），不是 d0 最优。

---

## 6. R2 生产结构（本质）

```text
短窗  WHEAT     fy=2   饲料+早现金+复种
长窗  MELON     fy=10  d10 现金尖峰（P13 已证）
中窗  STRAWBERRY fy=10  d5 起布局，后期价
动物  8C/6S/3G       d8+ 奶/毛/肥（P12/P13）
```

这是 **multi-horizon portfolio**，不是 “永远种 net/day 最大作物”。

B = **单窗 WHEAT-only** + 晚才买种子却不种非 wheat。

---

## 7. 为什么 B 不偏离

1. `crop_priority` d&lt;8 强制 WHEAT  
2. plant 序 WHEAT 优先，买了 STRAW/CARROT 也不种  
3. 无 “10 日后高价值窗” 概念  
4. 无 tile 锁定/浇水预算（P13.3/4 已证 survival 依赖 water）

---

## 8. Decision mapping

| 选项 | 判定 |
|---|---|
| PRODUCTION_REGIME_IDENTIFIED（单一 score） | 否 — 67%，STRAW 全错 |
| NO_SIMPLE_REGIME | 部分 — 但 MELON d0 可被 score 解释 |
| **MULTI_FACTOR_PRODUCTION** | **是** — 多时间窗 + 动物 + 饲料 |

---

## 9. 对下一阶段的含义（本轮不做）

若做 **P14.1 Minimal Production Regime Planner**，必须是：

```text
state
→ 评估多个 horizon 组合（短/长/动物）
→ 选 portfolio，不是 if melon
→ executor + water lifecycle（P13.3）
```

**禁止** 复制 d0 买 melon 的 tape。

---

## Artifacts

```text
RESEARCH_P14_PRODUCTION_REGIME.md
p14_r2_production_timeline.csv
p14_seed_buys.csv
p14_plant_cmds.csv
p14_production_divergence.csv
p14_first_yield_value.csv
p14_opportunity_cost.csv
p14_regime_score.csv
_p14_trace.py
_p14_analyze.py
```

NO SUBMISSION. v11E / R2 / last-2 未动。
