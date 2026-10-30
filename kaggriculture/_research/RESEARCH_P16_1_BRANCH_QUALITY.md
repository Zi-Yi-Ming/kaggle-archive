# P16.1 — Branch Trigger Quality

**Date:** 2026-09-12  
**Arms:** S0 skeleton off-branch / S1 fixed d10 / S2 state-derived (once-only)  
**8 games vs R2, both seats, seeds 1–4.**

---

## Decision

```text
BRANCH_VALUE_NOT_ROBUST
```

P16 的 +45% branch 增益 **不能在复现中稳定成立**。  
State-derived trigger **没有** 改善 fixed，且本 run 更差。  
**不增加第二 branch。不提交。**

---

## 1. d7–d10 features（SKEL，2 seed 示意）

| day | money | field melon | true-ready* | shed melon | notes |
|---:|---:|---:|---:|---:|---|
| 7 | 286–366 | 9–10 | 0 | 0 | yield_units>0 但 **fy 未到** |
| 8 | 329–416 | 9–10 | 0 | 0 | |
| 9 | 1270–1797 | 9–10 | 0 | 0 | milk 小峰 |
| 10 | 409–601 | 9–10 | 0–1 | 0 | 现金回落 |

\*`day-planted>=10` 才是引擎合法 HARVEST。  
**d7 的 `yield_units>0` 是假 ready**（non-ongoing 初始即为 1）— 不能当 trigger。

---

## 2. Fixed vs State trigger

| | Fixed (S1) | State (S2) |
|---|---|---|
| 条件 | day==10 ∧ melon ∧ money&lt;1800 | once；day≥10； ready+shed≥3； money&lt;1000 |
| 触发次数 | 1/局 | 1/局（latch 后） |
| 未加 latch 时 | — | **d10+d11 双触发 → 更差** |

---

## 3. Three-arm results（vs R2）

| Arm | mean bank | mean d15 | fires | bankrupt |
|---|---:|---:|---:|---:|
| **off (S0)** | **$16,300** | **$5,512** | 0 | 0 |
| fixed (S1) | $12,140 | $4,832 | 8/8 | 0 |
| state (S2) | $10,448 | $4,356 | 8/8 | **1** |

**本轮 off 最好。** 与 P16 原 run（SKEL $12.4k → BR $18.0k）**方向相反**。

### Paired state−fixed

4/8 为正，4/8 为负，幅度 ±$3k–$15k — **噪声级，非稳定改进**。

---

## 4. False positive / negative

| | |
|---|---|
| P16 原 2 个变差局 | 本 run 未稳定复现同一 seat/seed 模式 |
| off 在本 run 最好 | branch 触发本身可能在部分路径上 **打断** 后续 milk/wool 复利 |
| state 1 局 $900 | 过严/过早 LIQUIDATE 可伤后期 |

---

## 5. 为什么 P16 的 +45% 不可靠

1. vs R2 path noise 极大（同代码 bank $4k–$26k）  
2. 单次 8 局 vs 复现 8 局符号可翻转  
3. trigger 8/8 全开 → 更像 **固定 d10 bailout**，不是稀有 deviation detector  
4. 用户要求的 specificity（多数走 skeleton）**未满足**

---

## 6. 结论

| | |
|---|---|
| Branch architecture 有价值？ | 概念仍可能成立，但 **本 branch 证据不足** |
| Fixed d10 已足够？ | **否** — 不稳健 |
| State-derived 更好？ | **否** |
| 下一步 | **停**；不要第二 branch；不要 RL |

若再开 P16.2：必须先有 **跨 seed 稳定的 branch value**（例如 vs finn 低噪声、或 ≥16 局 + 预注册 trigger），否则属于过拟合单次 sample。

---

## Artifacts

```text
RESEARCH_P16_1_BRANCH_QUALITY.md
p16_1_trigger_features.csv
p16_1_counterfactual.csv
p16_1_ablation.csv
p16_branch/__init__.py
_p16_1_features.py
_p16_1_ablation.py
```

**NO SUBMISSION.**
