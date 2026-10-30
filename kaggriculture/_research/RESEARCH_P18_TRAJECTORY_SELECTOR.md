# P18 — Trajectory Library & Selector

**Date:** 2026-09-12  
**Library:** R2 vs finn, seeds 1–2, day-boundary states + inferred mode  
**Modes (resource-delta labels):** MAIN 30 / HERD_SCALE 22 / CASH_WINDOW 2  
**Selectors:** S0 fixed MAIN / S1 rule checkpoints / S2 kNN (day±2, k=3)  
**8 games vs R2, both seats. No PPO. No submit.**

---

## Decision

```text
RETRIEVAL_NOT_TRANSFERRED
```

**S2（nearest-state 检索）没有稳定超过 S1，更没有全面超过 S0。**  
在当前 **薄 library + 当前 backbone 状态空间** 下，**不能** 证明「R2 优势主要来自 trajectory retrieval」。

---

## Library 形态

| | |
|---|---|
| 行数 | ~54（2 seeds × ~27 days） |
| 主导 mode | HERD_SCALE 早期；CASH_WINDOW **仅 d10 melon 转换 1 次/局**；MAIN 中后期 |
| 特征 | money, melon, animals, plant, shed_total, n_shops |

**CASH_WINDOW 在库里极稀疏** → kNN 几乎学不到「何时该切变现」。

---

## Ablation（vs R2）

| Selector | bank | d15 | bankrupt |
|---|---:|---:|---:|
| S0 fixed MAIN | $14,033 | $4,637 | 0 |
| **S1 rules** | **$17,420** | **$16,642** | 0 |
| **S2 kNN** | **$11,961** | $5,479 | **1** |

| Paired | S2 wins |
|---|---|
| S2 &gt; S1 | **3/8** |
| S2 &gt; S0 | **3/8** |

S1 的 d15 显著最高（+$12k vs S0）— 与 P17.1 规则型 CASH_WINDOW 一致。  
S2 更差且 1 局近破产。

---

## 为何 retrieval 失败（证据，非猜测）

1. **状态分布不对齐**：R2 d15 已有 ~16 animals / $30k；我们 d15 仍在 $5k 量级 → 最近邻仍是「异世界」状态。  
2. **关键 event 稀疏**：CASH_WINDOW 库内只有 d10 两点。  
3. **Day±2 窗口过窄/过宽**：既限制样本，又在错误相位上匹配。  
4. **Mode 标签噪声**：从 R2 行为反推，不是 gold intent。

不能据此说「retrieval 范式无用」，只能说：

> **本 library + 本 feature + 本 backbone 下，S2 无效。**

---

## 与 P17.1 对照

| | P17.1 LIB (rules) | P18 S2 |
|---|---|---|
| 结构 | 稀疏 checkpoint → 粘性 tail | kNN → mode |
| paired | **8/8 胜 backbone** | **3/8 胜 S1** |
| 结论 | continuation overlay 有效 | **retrieval 未迁移** |

---

## 对研究层级的含义

你的分层假设得到 **更硬的支持**：

```text
我们的 25k ≈ 手写规则 + 弱 backbone
R2 150k ≈ 强 backbone（tape 质量）本身
2900+ ≈ 仍未知；naive kNN(R2 states) 不是银弹
```

下一步若再碰 library：

- 必须 **更大 corpus**（ashok top10 + 多 seed R2 + 强 public）  
- 必须 **对齐状态**（相对 rank / z-score，而非绝对 money）  
- 或直接 **学习 selector**（仍非每步 PPO）

**本轮禁止** 继续堆 k 窗口/特征而不换数据。

---

## Artifacts

```text
RESEARCH_P18_TRAJECTORY_SELECTOR.md
p18_trajectory_library.csv
p18_ablation.csv
p18_selector/__init__.py
_p18_mine_library.py
_p18_ablation.py
```

Default: `p18_selector` S0 / ENABLED=False.
