# P45 — Branch-Preserving Distillation Diagnostic

**日期：** 2026-09-14  
**问题：** majority distillation 是否抹掉离散 trajectory branch，导致 99k vs 原 elite 160k+？  
**协议：** finn 不 wrap；`env.info["seed"]`；R2/last-2 冻结；无 submit

---

## Decision

```text
ORIGINAL_REPLAYS_NOT_ELITE_VS_FINN
DISTILLATION_NOT_PRIMARY_LOSS
```

**否定**「majority 平均掉 branch → 损失 60k+」主假设。

---

## 4-way 对照（均 vs finn，seeds 1/2/3，双 seat）

| label | kind | live_reward | W-D-L | bank vs finn |
|---|---|---:|---|---:|
| orig_top1 ep108843236 | original | **139,265** | 3-0-0 | **100,244** |
| orig_top2 ep108854008 | original | 136,777 | 3-0-0 | 100,244 |
| orig_top3 ep108810310 | original | 136,165 | 3-0-0 | 100,243 |
| orig_median | original | 89,351 | 3-0-0 | 100,244 |
| **global_majority** | distill | — | 3-0-0 | **99,142** |
| shop_cond_majority | distill | — | 3-0-0 | 99,142 |

`p45_distill_compare.csv`

---

## 关键数字

| 对比 | Δ bank |
|---|---:|
| 原始 top live tape vs finn | 100,244 |
| global majority vs finn | 99,142 |
| **蒸馏损失** | **~1,100（~1.1%）** |
| live_reward 139k vs 同 tape vs finn 100k | **~39k（上下文差）** |

原始 episode 与 global majority 的 tape similarity：**0.96–0.98**。  
Shop-conditioned majority 与 global **完全同 bank**（modal-shop 分组几乎退化为全局）。

Shop 签名 (d3,d6)：**24 种 / 30 局**——几乎每局一条分支，**无法**靠 shop 分组恢复「共享 elite tape」。

---

## 假设检验

| H | 判定 |
|---|---|
| H-a：majority 抹掉 branch，损失 60k+ | **REJECTED**（只损 ~1%） |
| H-b：单条原始 replay 自带 160k+ vs finn | **REJECTED**（top live 也只 ~100k vs finn） |
| H-c：live 高 bank 来自对手/路径上下文，不是 tape 绝对产能 | **SUPPORTED** |

---

## 解释

```text
live episode 139k
    = tape × 真实对手 × 该局 seed/shop/path
         ↓ 同一 action 序列
replay vs finn (seeds 1/2/3)
    ≈ 100k
         ↓ majority of 30
distilled tape
    ≈ 99k
```

P44 的 99k **不是**「比 elite 差 60k」，而是 **vs-finn 复跑的正常水平**；  
与 **任意一条** 原始 live tape 复跑 **同量级**。

R2 真 agent 在同 harness vs finn 仍 ~170–200k（活策略，吃 seed/shop）；  
**冻结后的任何 720-step 序列**（原始或蒸馏）都到不了那个数——因为活 R2 在本地也是按 seed 走分支，而 replay 是一条冻结路径。

（与 P35/P36/P42 一致：同 policy 跨 seed tape 会分叉；单条 tape ≠ 完整 policy。）

---

## 对 P44 的修正解读

```text
P44 PARTIALLY_REPRODUCED
  ├─ replay→tape 管道：成立
  ├─ tape vs finn ~99k：与原始 replay 复跑一致
  └─ 「未恢复 160k+」：不是蒸馏失败
        而是单 tape 表示 vs 活 policy 的固有差距
```

---

## 禁止事项（已遵守）

- 未扩大 mutation  
- 未改 R2  
- 未 submit  
- 未把 bank-only 差异当 Elo 突破  

---

## Artifacts

```text
RESEARCH_P45_BRANCH_DISTILL.md
p45_distill_compare.csv
p45_summary.json
_p45_branch_distill.py
```

---

## 最终输出

```text
P45 DECISION:
DISTILLATION_NOT_PRIMARY_LOSS
（附带：ORIGINAL_REPLAYS_NOT_ELITE_VS_FINN）

对照：
orig live top vs finn ~100244
global majority vs finn ~99142
蒸馏损失 ~1%

SUBMISSION:
FROZEN

NEXT:
瓶颈不在 branch-preserving distillation；单条冻结 tape 复现不了活 R2 的 seed/shop 分支产能。
```
