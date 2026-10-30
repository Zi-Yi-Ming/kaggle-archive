# P21 — W/D/L Counterfactual Surface

**Date:** 2026-09-12  
**Protocol:** force tail from d8–10 × MAIN/CASH/HERD × seeds 1–2, seat 0  
**Opponents tried:** rancher_rita (tier5), closer_cleo (tier9), broker_bea (tier6)  
**No NN. No submit.**

---

## Decision

```text
WDL_LABEL_SATURATED
```

在 **单一固定对手** 上，二值 W/D/L 对 continuation **没有区分度**：

| Opponent | 结果 |
|---|---|
| rancher_rita | **18/18 W**（score 全 1.00） |
| closer_cleo | **18/18 L**（score 全 0.00） |
| broker_bea | **12/12 L**（score 全 0.00） |

`P(W)+0.5P(D)` 在 tail 之间 **完全打平** — 不能当 selector label。

---

## 有区分度的是什么

### 同对手下的 **bank / margin**（仍全 L 时）

vs broker_bea（全 L）：

| tail | bank mean | margin 例 |
|---|---:|---|
| MAIN | $9.6k | −52k～−137k |
| **CASH** | **$17.9k** | −99k～−125k |
| HERD | $17.2k（d10） | −90k～−145k |

vs rita（全 W）：CASH bank 也显著更高（$32–43k vs $24–27k）。

### P20 cash+5 边界仍成立

`melon≥3 → CASH` 在短时 cash 上 10/12 — 与 W/D/L 无关。

---

## 为什么 W/D/L 饱和（机制）

我们的 stack 与 pool 对手 **不在刀锋区**：

```text
finn/rita     ≫ us     → 全 W
us ≪ bea/cleo/R2       → 全 L
```

二值标签把所有 tail 压成同一类。  
这不是「continuation 无价值」，是 **label 分辨率不足**。

---

## 对 P21 目标的回答

> P20 的 melon≥3 是在「赚钱」还是「赢比赛」？

在当前对手集上：

- **赚钱**：是（cash+5 / bank 明确）  
- **赢比赛**：**测不出来**（W/D/L 饱和）

不能把 bank 提升直接读成 P(W) 提升。

---

## 可用的 outcome proxy（按信息量）

| Proxy | 区分度 | 对齐 Kaggle？ |
|---|---|---|
| binary W/D/L vs 单一对手 | **无** | 名义对齐，实际饱和 |
| final bank vs 固定对手 | 有 | 弱 |
| margin vs 固定对手 | 有 | 弱 |
| **多对手混合 / 刀锋对手集** | 应有 | **更接近** |
| **Elo / pairwise 相对分** | 应有 | 更接近 |
| vs R2 margin | 有 | 间接 |

下一步若做 outcome-aware selector，应优先：

```text
margin 或 pairwise-vs-mixture
```

而不是对单一 pool 对手硬套 W/D/L。

---

## Selector 对比（仅 bank，in-sample）

| Rule | vs bea bank |
|---|---:|
| fixed MAIN | $9.6k |
| melon≥3 CASH | **$17.9k** |

W/D/L score 三者皆 0.00 — **无法排序**。

---

## Artifacts

```text
RESEARCH_P21_WDL_SURFACE.md
p21_wdl_surface.csv
p21_wdl_summary.csv
_p21_wdl_surface.py
```
