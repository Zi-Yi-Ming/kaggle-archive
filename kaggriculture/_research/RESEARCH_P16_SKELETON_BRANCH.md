# P16 — Open-Loop Skeleton + Branch-and-Repair

**Date:** 2026-09-12  
**Scope:** one skeleton backbone + **one** branch (FORCE_SELL @ d10 cash window)  
**Gate:** 8 games vs R2, both seats. **No submission.**

---

## Decision

```text
BRANCH_ARCHITECTURE_SUPPORTED
```

（骨架 + 单点 branch 有稳定、可重复的增量价值；**仍 0-8 vs R2** — 第一轮不要求 5/8。）

---

## 1. Skeleton mining（压缩，非 tape）

From R2 day milestones (`p14_r2_production_timeline.csv`, 2 seeds):

| Day | Money | Animals | WHEAT | MELON | STRAW | Land |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3000 | 0 | 0 | 0 | 0 | 1 |
| **1** | **27** | **4** | **7** | **12** | 0 | 1 |
| 5 | 724 | 6 | 7 | 12 | 0 | 1 |
| 7 | 1014 | 8 | 5 | 12 | 12 | 2 |
| **10** | **3193** | 13 | 5 | **12** | 20 | 2 |

### Compressed skeleton (`p16_skeletons.csv`)

| Phase | Days | Intent | Expected state |
|---|---|---|---|
| S0_SETUP | 0–2 | hire; short WHEAT + long MELON; 2C+2S | melon~12, animals~4 |
| S1_GROW | 3–9 | water/care; add STRAW; scale herd; land2 | animals 8–12 |
| S2_CASH_WINDOW | 10–15 | harvest long; sell; livestock | money inflection |
| S3_SCALE | 16–25 | milk/wool/fert | |
| S4_TERMINAL | 26–29 | liquidate | |

**不是** step-by-step tape。Backbone 实现 = P14.1 portfolio + P13.3 water（已验证的 multi-horizon 路径）。

---

## 2. One branch point

| | |
|---|---|
| **ID** | `B_CASH_WINDOW_STUCK` |
| **Day** | 10 only |
| **Trigger** | `(field_melon>0 or shed_melon>0) and money < 1800` |
| **Base** | 继续 portfolio hold |
| **Branch** | `FORCE_SELL`: sell_all, hold_wheat=0, stop long seeds/animals that day |

Evidence: P13 ledger — d10 MELON sale is R2 cash engine; P14.1 plants melon but conversion lags.

**Repair ≠ branch:** p10 weed/sanitize unchanged.

---

## 3. Ablation (8 games vs R2)

| Arm | W-L | bank | d15 | branch fires | bankrupt |
|---|---|---:|---:|---:|---:|
| **SKEL** (portfolio+water) | 0-8 | **$12,396** | $4,357 | — | 0 |
| **SKEL+BR** | 0-8 | **$17,971** | **$6,123** | **8/8** | 0 |

### Paired Δ (BR − SKEL)

| seed/seat | Δbank | fired |
|---|---:|---|
| s1 s0 | −1,004 | 1 |
| s2 s0 | +6,791 | 1 |
| s3 s0 | +7,950 | 1 |
| s4 s0 | +10,271 | 1 |
| s1 s1 | +8,829 | 1 |
| s2 s1 | +7,313 | 1 |
| s3 s1 | −8,605 | 1 |
| s4 s1 | +13,049 | 1 |

- **Mean Δbank = +$5,575 (+45%)**  
- **Mean Δd15 = +$1,766 (+41%)**  
- **6/8 改善**；触发 **稳定 8/8**  
- 无破产、无 crash

---

## 4. 与 R2 关系

仍 **0-8**。R2 bank $100k–$180k。  
Branch 解决的是「有 melon 却不及时变现」；**没有**解决路由/动物战术/卖出峰值全栈差距。

---

## 5. Falsifier check

| | |
|---|---|
| Trigger 可识别 | **是**（纯 observable） |
| A/B 差距小 | **否**（+45% bank） |
| 高度 seed dependent | 部分（2/8 变差，6/8 变好） |
| 需要大量额外 heuristic | **否**（单条件） |

→ 通过第一轮 branch gate。

---

## 6. Architecture 形态

```text
90% open-loop skeleton (multi-horizon portfolio + water + labor/EOD/shepherd)
10% branch (d10 cash-window FORCE_SELL)
+ p10 repair (weeds/sanitize)
```

与 top-agent 直觉一致：**大部分相信验证过的经济骨架，少数 divergence 才分枝**。

---

## 7. Next（本轮不做）

- 第二个 branch（FAIL_WINDOW / ANIMAL_STARVED）— 仅当第一 branch 保持有效  
- 更强 skeleton（动物 8C/6S 战术、卖出峰值）  
- **不** RL / 每步 replan / 提交

---

## Artifacts

```text
RESEARCH_P16_SKELETON_BRANCH.md
p16_skeletons.csv
p16_branch_points.csv
p16_branch_triggers.csv
p16_branch/__init__.py
p16_local_results.csv
p16_ablation.csv
p16_behavior_diff.csv
_p16_mine_skeleton.py
_p16_ablation.py
```

Defaults: `p16_branch` skeleton/branch **OFF** unless harness enables.
