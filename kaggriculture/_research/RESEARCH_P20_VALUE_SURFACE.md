# P20 — Continuation Value Surface

**Date:** 2026-09-12  
**Protocol:** backbone → force day D ∈ {7…12} × tail {MAIN, CASH, HERD} × seeds {1,2}, seat 0  
**Rows:** 12 state groups × 3 tails = 36 rollouts  
**No model training. No submit.**

---

## Decision

```text
VALUE_SURFACE_MAPPED
```

**短 horizon（cash+5）边界清晰；终局 bank 边界不清晰。**

---

## Surface 摘要（cash+5 / best final）

| seed | day | c0 | melon | ani | best **+5** | best **final** |
|---:|---:|---:|---:|---:|---|---|
| 1 | 7 | 276 | 9 | 3 | **CASH 13.6k** | CASH |
| 1 | 8 | 411 | 9 | 3 | **CASH 16.3k** | HERD |
| 1 | 9 | 1348 | 9 | 3 | **CASH 15.0k** | HERD |
| 1 | 10 | 417 | 9 | 3 | **CASH 13.7k** | CASH |
| 1 | 11 | 4243 | 3 | 3 | **CASH 10.7k** | MAIN |
| 1 | 12 | 3925 | **1** | 3 | **MAIN 9.2k** | MAIN |
| 2 | 7 | 286 | 9 | 3 | **CASH 14.3k** | HERD |
| 2 | 8 | 398 | 9 | 3 | **CASH 16.5k** | CASH |
| 2 | 9 | 1273 | 10 | 3 | **CASH 15.7k** | HERD |
| 2 | 10 | 736 | 9 | 3 | **CASH 11.7k** | MAIN |
| 2 | 11 | 3947 | 3 | 3 | **CASH 12.3k** | CASH |
| 2 | 12 | 1710 | **0** | 3 | **MAIN 6.9k** | CASH |

---

## Decision boundary（cash+5 objective）

**CASH 胜 10/12。**

| 条件 | +5 最优 |
|---|---|
| **melon field ≥ 3**（day 7–11） | **CASH_WINDOW** |
| **melon ≤ 1**（day 12，已基本收完） | **MAIN** |

经验规则：

```text
if melon_tiles >= 3:
    CASH_WINDOW
else:
    MAIN
```

→ 对 `best5` 应为 **10/12**（两例 miss 正是 melon 0/1）。  
`animals≈3` 在本 surface **未拉开** HERD 优势（HERD 几乎从不赢 +5）。

---

## 终局 bank：无单一 boundary

| day 窗 | 常见 best final |
|---|---|
| d7–d9 | 常 **HERD**（继续扩产） |
| d10–d11 | **CASH / MAIN 混杂** |
| d12 | 常 **MAIN** |

再次确认 P19：

> **优化 cash@+5 会得到「救火型」selector；优化 final bank 又是另一套边界。**  
> 最终 Kaggle 看 **W/D/L** — 与两者都不等价。

---

## 与 2900 问题的接口

现在可以干净地写：

```text
state (day, melon, cash, animals, …)
        ↓
counterfactual values (MAIN / CASH / HERD)
        ↓
objective choice: short cash | final bank | (future) W/D/L
        ↓
selector (rule 先于 learned)
```

第一版 selector **不必是 NN**：上表 melon≥3 规则已覆盖短时最优。

---

## 限制

- 仅 **我们 backbone** 的状态（非 R2 / 非 ashok 全库）  
- seat0 only；2 seeds  
- tail 只有 3 个；horizon 只有 +5 与 final  
- 未碰 PPO

---

## Artifacts

```text
RESEARCH_P20_VALUE_SURFACE.md
p20_value_surface.csv
p20_boundary_table.csv
_p20_surface.py
```
