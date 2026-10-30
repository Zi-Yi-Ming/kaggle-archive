# P29 — Elite Corpus Scaling

**Date:** 2026-09-12  
**Question:** Does imitation transfer ratio rise with elite-corpus size?  
**Corpus:** R2 trajectories, train seeds 1–N (N∈{1,2,4,8})  
**Policy:** tabular BC (state bucket → majority market bundle) + p11 workers  
**Holdout:** seeds 11–13 (unseen). **Pin harness. No PPO. No submit.**

---

## Decision

```text
CORPUS_SCALING_NO_GAIN
```

**C1 = C2 = C4 = C8 = 24.83% mean ratio。**  
同 policy 的多 seed elite 轨迹 **不提升** 迁移。

---

## Results

| Corpus | buckets | holdout s11 | s12 | s13 | **mean ratio** |
|---|---:|---:|---:|---:|---:|
| C1 | 168 | 40.4% | 17.8% | 16.3% | **24.83%** |
| C2 | 170 | 40.4% | 17.8% | 16.3% | **24.83%** |
| C4 | 170 | 40.4% | 17.8% | 16.3% | **24.83%** |
| C8 | 181 | 40.4% | 17.8% | 16.3% | **24.83%** |

Holdout bank（imit）**跨 corpus 逐 seed 完全相同** — 策略已饱和。

| holdout | R2 bank | Imit bank |
|---|---:|---:|
| s11 | 85,390 | 34,507 |
| s12 | 189,936 | 33,761 |
| s13 | 184,565 | 30,093 |

s11 R2 偏低 → ratio 40% 是分母效应；绝对 imit 仍 ~$30–35k。

---

## 解读

1. **不是「轨迹不够多」** — 1→8 条同源 elite，BC 行为不变。  
2. 粗粒度 state bucket 在 seed1 上已覆盖 holdout 的决策点；加样本不改 majority。  
3. 与 P28 的 20% 规则抽取一致：**稳定结构 ≠ R2 主收益**。  
4. 与 P27 一致：R2 收益在 **trajectory-specific coordination**，不是可加样本的 tabular policy。

---

## 重要限制（避免过度外推）

| | |
|---|---|
| 仅 **同一 policy**（R2×N） | 未测 **异构 elite**（多 top-agent） |
| Tabular BC | 非神经 BC；更强模型或可吃更多数据 |
| Holdout n=3 | 小样本 |
| Workers 固定 p11 | 未学习 worker 路径 |

因此 **不能** 说「imitation 永远无效」；只能说：

> **同源 R2 语料 + 粗表 BC 不随 N 提升。**

---

## 对路线的含义

```text
P28 规则抽取 20%
P29 同源 corpus 1→8 无增益  ← HERE
```

若继续 imitation：

- 需要 **异构 elite corpus**（不同 agent / 不同 shop 路径家族）  
- 或 **更细 state/action**（不是 day/hour/money bin）  
- 或放弃 tabular，上真 BC 模型（但须先证明数据多样性）

**不要** 在「多跑几条 R2 seed」上继续堆。

**不要** 直接 PPO on single-policy corpus。

---

## Artifacts

```text
RESEARCH_P29_CORPUS_SCALING.md
p29_corpus_scaling.csv
_p29_corpus_scaling.py
```
