# P13.1 — Early MELON Counterfactual

**Date:** 2026-09-12  
**Control B0:** current B stack (no melon hook)  
**Treatment B1:** B0 + d0–d2 buy 6 MELON seeds + plant-first (`p13_1_melon.py` ENABLED)  
**No other policy changes.** vs R2, 2 seeds × both seats.

---

## Decision

```text
MELON_MECHANISM_REJECTED
```

---

## Primary results

| | B0 | B1 melon |
|---|---:|---:|
| mean d10 cash | **$198** | **$92** |
| mean d15 cash | **$1,296** | **$669** |
| mean d29 bank | $12,179 | $12,394 |
| **melon revenue d7–10** | **$0** | **$0** |
| melon revenue total | $0 | **$0** |
| melon seeds bought | 0–10* | 13–21 |
| PLANT MELON cmds | 0 | **14 / game** |

\*B0 sometimes bought melon via later cash-crop code but never planted (plant order prefers wheat).

### Paired Δ (B1 − B0)

| seed/seat | Δd10 | Δd15 | Δd29 |
|---|---:|---:|---:|
| s1 seat0 | −161 | −1,164 | −8,623 |
| s2 seat0 | −239 | +160 | +11,239 |
| s1 seat1 | +78 | −68 | −287 |
| s2 seat1 | −104 | −1,437 | −1,472 |

**Δd10 mean ≈ −$106（负）。** 按 gate：B1 ≤ B0 → REJECT.

---

## Tile diagnostic（B1 vs finn, seed1）

| day | melon plants | all plants | empty | shed MELON | money |
|---:|---:|---:|---:|---:|---:|
| d01 | **11** | 15 | 5 | 0 | 148 |
| d05 | **11** | 14 | 0 | 0 | 235 |
| d09 | **11** | 14 | 0 | 0 | 119 |
| **d10** | **0** | **0** | **25** | **0** | 1,696 |
| d11+ | 2 | 2 | 0 | **0** | — |

1. Melon **确实种下了**（11 株，不是没种）。  
2. **全程 shed.MELON = 0，revenue = 0** — 没有完成「收获→入仓→卖出」。  
3. d10 地上作物整批消失（原因未在本轮闭合；可能是收获移除或其它，但 **没有变成 MELON 现金**）。

---

## Why transfer failed (not “melon is worthless”)

P13 的 R2 机制仍然成立：R2 在 d10 **真收到** MELON 货款 ~$30k。

P13.1 说明：

> 在 **当前 B executor/worker 栈** 上，只加「买种子 + 优先种」**不能**复现 cash conversion。

| Parity Q | A |
|---|---|
| B 能否触发 SALE MELON？ | 引擎层可以 |
| 为何 B1 没触发？ | **地里有种、仓里无货、账上无收入** — 收获/入仓链未闭合 |
| 是否 confound RNG？ | 植物数稳定 14 cmds / 11 tiles；不是 shop path 问题 |

Collateral：买种子占用 d0 现金、占格 10 天 → d10/d15 机会成本为负。

---

## Gate mapping

| Gate | 结果 |
|---|---|
| Strong positive | 否 |
| Partial (d10↑ d15↓) | 否（d10 也↓） |
| Weak | — |
| **Negative B1≤B0** | **是** |

---

## What this does / does not prove

| | |
|---|---|
| 不证明 | MELON 经济对 R2 不重要（P13 ledger 仍显示它是 d10 主收入） |
| **证明** | **「只种 MELON」不是可迁移 primitive**；缺的是 melon 收获→入仓执行 |
| 下一步若做 | 必须先修 **非 ongoing 作物 HARVEST→shed** 通路，而不是继续加种子 |

本轮 **不** 自动进入 melon planner / 不改其它策略 / 不提交。

---

## Artifacts

```text
RESEARCH_P13_1_MELON.md
p13_1_melon.py
p13_1_melon_counterfactual.csv
_p13_1_melon_run.py
_p13_1_melon_diag.py
```

Default `p13_1_melon.ENABLED = False`（B0）。
