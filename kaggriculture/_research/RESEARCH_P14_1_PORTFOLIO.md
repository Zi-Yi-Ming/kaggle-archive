# P14.1 — Multi-Horizon Crop Portfolio

**Date:** 2026-09-12  
**Scope:** crop allocation only; animals/sales/executor unchanged  
**Live treatment:** portfolio ON + water ON (P13.3 lifecycle dependency)  
**8 games vs R2, both seats. No submit.**

---

## Decision

```text
PORTFOLIO_SIGNAL_CONFIRMED
```

结构与 d15/melon 收入成立；**尚未** d10 对齐 R2，**仍 0-8 vs R2**。  
下一阶段应是 **coupling（作物×动物×卖出）**，不是继续堆 crop feature。

---

## Offline reconstruction

| State | Planner alloc | Horizons |
|---|---|---|
| d0 cash=$3000 empty=25 | **WHEAT 5 + MELON 16 + TOMATO 4** | short+medium+long |
| d0 cash=$800 | WHEAT 7 + MELON 6 + TOMATO 1 | multi |
| B wheat-only | WHEAT 15 | **short only** |
| R2 obs d1 | WHEAT 7 + **MELON 12** | short+long |

无 `MELON=12` 硬编码；长窗比例由 cash/空地/水容量推导。

---

## Live gate（vs R2）

| | B0 | **PF+water** |
|---|---:|---:|
| W-L | 0-8 | **0-8** |
| bank | $8,730 | **$11,432** |
| d10 cash | $386 | $231 |
| **d15 cash** | **$2,093** | **$4,331** |
| **MELON revenue** | **$0** | **$7,279** |
| STRAW revenue | $0 | $0 |
| bankrupt | **2** | **0** |
| field MELON @d10 | 0 | ~5–6 株/局（step 累计见下） |

### 结构差异（成功标准第一层）

| | B0 | PF |
|---|---|---|
| 种什么 | 基本 WHEAT | **WHEAT + MELON + TOMATO** |
| 长窗 | 无 | 有 |
| melon 变现 | 0 | **有** |

---

## Cash attribution（PF）

- MELON sale ≈ **$7.3k**（P13 机制在 portfolio 下复现）  
- WHEAT sale 低于 B0（格子让给长窗）  
- d10 日界现金仍低：收获/卖出落在 d10 日内–d15  
- d15 抬升主要来自 melon 窗 + 后续动物链未破坏

---

## 为何仍 0-8

R2 = **作物组合 + 8C/6S/3G + 卖出/肥料/路由** 联动。  
本版只动 crop allocation；动物/卖出仍是旧 B。

按你的 P14.1§22：标记为趋向

```text
MULTI_STAGE_COUPLING
```

（下一轮 P14.2 再谈 animal portfolio，本轮不扩。）

---

## 约束遵守

- 未改 R2 / 未提交 / 无 day-schedule tape  
- 无 `MELON_TARGET=12`  
- water ON 为长作物存活依赖（P13.3），已披露  
- executor 仍 p10 路径

---

## Artifacts

```text
RESEARCH_P14_1_PORTFOLIO.md
p14_1_portfolio/allocator.py
p14_1_on.py
p14_1_crop_value.csv
p14_1_portfolio_allocations.csv
p14_1_r2_reconstruction.csv
p14_1_local_results.csv
_p14_1_offline.py
_p14_1_live.py
```

Default：`p14_1_on.ENABLED=False`。
