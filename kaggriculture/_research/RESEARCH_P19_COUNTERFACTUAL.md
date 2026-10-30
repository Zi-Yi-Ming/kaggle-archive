# P19 — Counterfactual Continuation Scoring

**Date:** 2026-09-12  
**Method:** backbone to day D ∈ {9,10}; force tail MAIN / CASH_WINDOW / HERD_SCALE for next 10 days; score cash@+5/+10 and final bank.  
**Our states** (not R2 states): ~$500–1400 cash, melon 9–10, animals ~3.  
**No learned model. No PPO. No submit.**

---

## Decision

```text
COUNTERFACTUAL_SCORING_READY
```

第一次在 **同一 backbone state** 上得到可比较的 continuation value 标签。  
**不是** selector 上线，是 **selection dataset v0**。

---

## Dataset (`p19_counterfactual.csv`)

| seed | day | tail | cash0 | **cash+5** | cash+10 | final |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 9 | MAIN | 1253 | 2,016 | 3,360 | 2,953 |
| 1 | 9 | **CASH** | 1256 | **14,117** | **15,545** | 7,726 |
| 1 | 9 | HERD | 1251 | 3,941 | 6,071 | **9,417** |
| 1 | 10 | MAIN | 617 | 8,364 | 12,636 | **22,979** |
| 1 | 10 | **CASH** | 488 | **11,690** | **13,012** | 12,097 |
| 1 | 10 | HERD | 750 | 6,893 | 8,111 | 10,856 |
| 2 | 9 | MAIN | 1343 | 3,935 | 7,319 | 10,872 |
| 2 | 9 | **CASH** | 1249 | **14,563** | **15,991** | 10,564 |
| 2 | 9 | HERD | 1419 | 6,505 | 9,620 | **15,826** |
| 2 | 10 | MAIN | 726 | 4,917 | 6,115 | 9,170 |
| 2 | 10 | **CASH** | 751 | **13,390** | **14,645** | **15,861** |
| 2 | 10 | HERD | 485 | 5,733 | 8,760 | 14,220 |

---

## 核心发现

### 1. 短 horizon：CASH_WINDOW 全面最优

**4/4**（seed×day）在 cash+5 / cash+10 上 CASH 最高（+$13k–$16k @+5）。  
与 P13/P17.1 一致：**有 melon 时先变现** 是高短时价值动作。

### 2. 终局 bank：排序不稳定

| 组 | best final |
|---|---|
| s1 d9 | HERD |
| s1 d10 | MAIN |
| s2 d9 | HERD |
| s2 d10 | CASH |

→ **短时最优 ≠ 终局最优**。Selector 的 **objective 必须先定义清楚**（d10 cash vs d29 bank）。

### 3. 状态特征（本库）

D≈9–10：`melon≈9–10, animals≈3, money≈0.5–1.4k` — 典型「长作物就绪但现金薄」。

---

## 方法学结论

| | |
|---|---|
| 反事实打分 | **可行**（同 seed、同 day、只改 tail） |
| 样本量 | 12 行 — v0，可扩到更多 seed/day |
| 用途 | 之后 rule / tree / 学习 selector 的 **标签** |
| 本轮 | **未训练任何模型** |

---

## 与研究链条衔接

```text
P17.1  continuation overlay 有效（8/8）
P18    naive kNN(R2) 未迁移（库稀疏/不对齐）
P19    在我们 state 上可直接标 value → 为 selector 提供监督信号
```

下一步（仍非 PPO）：把该协议扩到更多 day（如 d6/d12/d16）与多 seed，得到  
`state → argmax_tail` 数据集；再决定 tree / 线性规则 / 小模型。

---

## Artifacts

```text
RESEARCH_P19_COUNTERFACTUAL.md
p19_counterfactual.csv
_p19_counterfactual.py
```
