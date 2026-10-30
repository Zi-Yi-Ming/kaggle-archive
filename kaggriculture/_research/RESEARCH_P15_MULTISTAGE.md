# P15 — Multi-Stage Coupling Interaction

**Date:** 2026-09-12  
**Method:** 2×2 factorial vs finn (cleaner own cash). Arms: 0 / A=early MELON / B=forced SHEEP×2 / AB.  
Water ON in all arms. 2 seeds × both seats. **No planner. No submit.**

Interaction: `I(t) = V(AB) − V(A) − V(B) + V(0)`

---

## Decision

```text
MULTI_STAGE_COUPLING_WEAK
```

存在依赖图与 **弱的晚期正交互**，但 **不足以解释 R2**，也 **不是** P14.2 melon 被挤掉的主因（那是 mid-game 资源竞争 / 负交互）。

---

## Dependency graph（engine，22 edges）

关键路径：

```text
WHEAT → FEED → ANIMAL → PRODUCT → CASH
MELON → d10 CASH → BUY_ANIMAL → later PRODUCT   # H_MULTI_STAGE
ANIMAL → FERTILIZER → CASH / CROP
LAND → TILES → (CROP | STRUCT) 资源争夺
```

文件：`p15_dependency_graph.csv`

---

## Cash curves（mean，vs finn）

| d | 0 | A melon | B sheep | AB | **I** |
|---:|---:|---:|---:|---:|---:|
| 5 | 868 | 77 | 348 | 80 | +524 |
| 10 | 609 | 71 | 167 | 72 | +443 |
| **15** | 6,448 | **13,254** | 6,157 | 11,274 | **−1,688** |
| 20 | 18,538 | 23,099 | 15,534 | 21,322 | +1,228 |
| 25 | 31,286 | 31,832 | 24,572 | 31,853 | +6,736 |
| **29** | **42,180** | 38,113 | 33,175 | 39,115 | **+10,007** |

### Unit marginal (mean)

| | ΔA (melon) | ΔB (sheep) | ΔAB | I |
|---|---:|---:|---:|---:|
| d15 | **+6,806** | −291 | +4,826 | **−1,688** |
| d29 | −4,067 | −9,005 | −3,065 | **+10,007** |

---

## 解读

1. **A (MELON) d15 强、d29 略负** — 与 P13/P14.1 一致：中期窗有效，对弱对手终局不一定加分。  
2. **B (SHEEP×2) 终局为负** — 单独强加羊在本栈上不划算。  
3. **I(d15) < 0** — melon+羊在中期 **负交互**（抢现金/格子），解释 P14.2 “joint 挤掉 melon”。  
4. **I(d29) ≈ +10k** — 晚期有正交互，但 **A、B 单独都输给 base**，AB 只是少输，**不是** R2 级放大。  
5. 对照：**base vs finn 终局最高** — 在本 B 栈上，这两个 unit 都不是终局最优。

---

## 与 P14 对照

| | |
|---|---|
| P14.1 crop-only | melon 窗真实 |
| P14.2 + livestock EV | 无增量；melon 被挤 |
| P15 interaction | mid **负**、late **弱正**；非 superadditive 主引擎 |

**R2 的 8C/6S/3G 不能用 “melon×sheep 正交互” 解释。**  
更可能仍是 **战术生产/卖出/路由质量**（P12 线）与多阶段 **时序**，不是简单 pairwise EV。

---

## Nonlinear threshold

本轮未做 sheep 数量扫描（0–6）。现有 2 头羊已显示终局负边际；**不做** 无证据的阈值搜索。

---

## Decision mapping

| | |
|---|---|
| Strong（可重复大交互且解释 R2） | 否 |
| Medium | 否 |
| **Weak / 基本可加 + 竞争** | **是** |

```text
MULTI_STAGE_COUPLING_WEAK
```

**不进入 P15.1 Coupled Portfolio Planner。**  
**不提交。**

---

## Artifacts

```text
RESEARCH_P15_MULTISTAGE.md
p15_dependency_graph.csv
p15_key_paths.csv
p15_unit_marginal_value.csv
p15_interaction_effect.csv
p15_cash_curves.csv
p15_force_sheep.py
_p15_graph.py
_p15_interaction.py
```
