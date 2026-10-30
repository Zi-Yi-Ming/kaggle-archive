# P14.2 — Joint Crop + Livestock Portfolio

**Date:** 2026-09-12  
**No hardcoded 8/6/3. No R2 tape. No submit.**  
**Arms:** B0 / PF14.1 (crop+water) / JOINT (crop+animal+water), 8 games vs R2 each.

---

## Decision

```text
LIVESTOCK_INCREMENTAL_WEAK
```

在现有 executor/sales 下，**joint 动物配置没有带来相对 crop-portfolio 的增量 bank**；还 **挤掉 MELON 长窗**。  
→ 现在 **不要** 继续堆 animals。  
→ R2 的动物优势更可能是 **tactical production/sales coupling**，不是 “再买几头” 的 allocation 层。

---

## Animal EV（自产麦成本 + 季节价混合，非市场麦价）

| Animal | fy | yields | gross | fert | feed | **EV @d0** |
|---|---:|---:|---:|---:|---:|---:|
| GOOSE | 4 | 4 | 278 | 0 | 148 | **−170** |
| COW | 8 | 6 | 870 | 0 | 148 | **+322** |
| **SHEEP** | 6 | 6 | 1068 | 636 | 148 | **+1056** |

模型 **自主** 排序 SHEEP > COW > GOOSE（不是 R2 的 8C 先行）。

---

## Offline joint @d0 $3000

```text
crops   WHEAT 5 + MELON 16 + TOMATO 4
animals SHEEP 2          # 现金上限 45% 留给畜牧
```

与 R2 结构同向（长窗作物 + 开局动物），**无 8/6/3 常数**。

---

## Live ablation（vs R2，8 局均）

| Arm | bank | d15 | C@10 | S@10 | MELON@10 | melon_rev | animal_rev | bankrupt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | $13.7k | $2.3k | **6.0** | 0.2 | 0 | $0 | $23.2k | 2 |
| **PF14.1** | **$14.5k** | **$5.1k** | 2.0 | 1.0 | **132** | **$7.3k** | $19.0k | 0 |
| JOINT | $14.4k | $3.7k | 1.0 | **3.9** | **0** | **$0** | $19.5k | 0 |

### 读数

1. **JOINT ≈ PF 在 bank**（$14.4k vs $14.5k）→ 动物 allocation **无增量**。  
2. **JOINT d15 < PF**（$3.7k vs $5.1k）→ 长窗作物被动物现金/格子挤掉。  
3. **JOINT MELON=0** → 耦合在当前实现里是 **拮抗**（抢 cash/tile），不是互补。  
4. B0 仍有 bootstrap 6C@10 且 animal_rev 不低 → 差距在 **执行/卖出**，不在 “有没有买动物”。  
5. 三臂 **均 0-8 vs R2**。

---

## Coupling 结论

| 假设 | 判定 |
|---|---|
| crop portfolio 有价值 | **是**（P14.1） |
| 加 livestock allocation 再提升 bank | **否**（本轮） |
| feed 耦合存在 | **是**（小麦地板↑） |
| 已实现耦合是否互补 | **否 — 拮抗**（melon 窗被吃掉） |

```text
MULTI_STAGE_COUPLING 证据：作物窗 × 动物窗 × 卖出 未在 allocation 层自动对齐
```

---

## 不做什么

- 不继续加 animal targets / 新 sell policy  
- 不提交  
- 不把 JOINT 写进默认策略（`p14_2_on.ENABLED=False`）

若再碰动物：必须先有 **FEED→CARE→HARVEST→DROP 与 melon 窗的时间表耦合**，而不是并行抢资源。

---

## Artifacts

```text
RESEARCH_P14_2_LIVESTOCK_PORTFOLIO.md
p14_2_joint_portfolio/livestock.py
p14_2_joint_portfolio/joint.py
p14_2_on.py
p14_2_animal_value.csv
p14_2_portfolio_allocations.csv
p14_2_local_results.csv
p14_2_ablation.csv
p14_2_cash_decomposition.csv
_p14_2_offline.py
_p14_2_live.py
```
