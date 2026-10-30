# P13.2 — Harvest-Ready Diagnostic

**Date:** 2026-09-12  
**Question:** Is B's d10 MELON gap caused by missing harvest of mature crops?  
**No R2 edit. No submit. No planner plant/sell changes.**

---

## Decision

```text
HARVEST_NOT_THE_GAP
```

**真缺口是「连续 2 天不浇水 → 作物变 WEED」**，在 first_yield 之前植株就死了。  
B **已有** harvest-ready 逻辑；lab 证明 water+harvest+DROP 整条链在引擎上是通的。

---

## Engine truth (kaggriculture.py)

| Fact | Code |
|---|---|
| Non-ongoing (MELON) starts `yield_units=1` | `_new_plant` |
| HARVEST before `first_yield_day` = **no-op** | `op==HARVEST` early return |
| Successful HARVEST → **worker inventory**, not shed | `_inv_add` |
| Non-ongoing plant **removed** on harvest | `tiles=None` |
| **`consecutive_unwatered >= 2` → WEED** | `_daily_refresh_plants` |

Melon `first_yield_day=10` → 必须 **连续浇水 ≥10 天** 才能收。

---

## Micro-tests (`p13_2_harvest_microtests.csv`)

| Case | plants d9 | shed MELON | 结论 |
|---|---:|---:|---|
| 不浇不收 | 0 | 0 | 种了也死/没收 |
| 只浇水 | **1**（d1–d13） | 0 | 能活到成熟窗 |
| **水+收+DROP** | 1→0 @d11 | **4 @d11** | **通路打通** |
| 收但不浇 | 0 | 0 | 先死于缺水 |

**T3 通过：** 每日 WATER → d11 HARVEST → DROP → **shed +4 MELON**。

---

## B 现状

`production.py` 已有：

```python
if _crop_ready(t, day):  # yield_units>0 and age>=first_yield
    HARVEST
```

P13.1 诊断：d1–d9 有 11 株 MELON，**d10 整地 empty** — 与 `unwatered>=2→WEED` 一致，不是 harvest 漏指令。

B 的 shepherd (0–2) 优先动物；农民浇水被路径/优先级挤掉 → melon 撑不到 d10。

---

## Paired B0 vs harvest-only B1

**不适用为新变量** — harvest-ready 已在 B0 内。  
再包一层 `p13_harvest.harvest_ready` 与现有 `_crop_ready` 等价（同引擎条件），Δ≈0。

`p13_harvest/harvest_ready.py` 保留为 **generic primitive**（含 `needs_water`），供下一轮单独测 **water-to-survive**。

---

## Success ladder

| Level | Result |
|---|---|
| harvest correctness (lab) | **PASS**（T3） |
| B d10 shed MELON | **FAIL**（植株先死） |
| B d10 melon revenue | **FAIL** |
| d10 cash 改善 | N/A（未改 B） |

---

## 下一轮（若开）唯一合法单变量

```text
WATER_READY_CROP / needs_water
```

在 B 上保证 PLANT 后连续浇水至 `first_yield`，**不**改种植清单/卖出/畜牧。  
若 d11 shed MELON>0 且 revenue>0 → 再谈 cash。

本轮 **STOP_HARVEST**（不是缺口）。

---

## Artifacts

```text
RESEARCH_P13_2_HARVEST.md
p13_harvest/harvest_ready.py
p13_2_harvest_microtests.csv
p13_2_harvest_gate.csv
_p13_2_microtests.py
```
