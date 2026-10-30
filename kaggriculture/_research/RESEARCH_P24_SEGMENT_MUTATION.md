# P24 — R2 Segment Mutation (Trajectory Search v0)

**Date:** 2026-09-12  
**T0** = pure R2  
**T1** = R2 but d9–12 actions ← our CASH production  
**T2** = R2 but d0–5 actions ← our MAIN portfolio  
Opponent: fallow_finn (same for all arms). seeds 1–3, seat 0.  
**No submit.**

---

## Decision

```text
SEGMENT_MUTATION_DESTRUCTIVE
```

**用我们的 production 段替换 R2 任意窗口，bank 全面崩溃。**  
→ R2 的优势 **不是**「我们能本地 patch 进去的单段」；  
→ 与 P23 一致：继续在弱 backbone 上堆 selector/branch 到顶。

---

## Results

| Arm | s1 | s2 | s3 | mean |
|---|---:|---:|---:|---:|
| **T0 R2** | 170,460 | 186,595 | 142,077 | **166,377** |
| T1 R2+d9–12 CASH | 54,690 | 57,405 | 47,107 | **53,067** |
| T2 R2+d0–5 MAIN | **0** | **0** | 822 | **274** |

| Δ vs T0 | meanΔ | pos |
|---|---:|---:|
| T1 | **−113,310** | **0/3** |
| T2 | **−166,103** | **0/3** |

---

## 解读

1. **替换中段（d9–12）**：R2 ~166k → ~53k。我们的 CASH production 在 R2 状态上 **不能承接** 其后续复利。  
2. **替换开局（d0–5）**：直接破产级 — 开局与 R2 tape 强耦合，撕开即毁。  
3. 这不是「branch 没价值」，而是：

> **弱 production 段无法作为强 trajectory 的 drop-in 替代。**

---

## 与 P17–P23 合并

```text
P17.1  我们 backbone 上 overlay 有效
P23    selector ≈ melon rule，无增量
P24    把同一套 production 贴进 R2 → 巨额负 Δ
```

结论升级：

```text
R2 的 150k 来自整段 horizon 的协同执行质量，
不是「缺一个我们已有的 tail」。
```

---

## 对 P24 目标（strong backbone generation）的含义

**未找到 T\* > R2。** 第一轮 mutation 全是负向。

若继续 trajectory search，必须换 mutation 算子：

| 不要 | 要 |
|---|---|
| 整日窗口换成我们弱 planner | **R2 段内的微扰**（少步 action bundle） |
| 无状态硬切 | 保持 R2 内部 DayState 连续 |
| 我们 portfolio 当替代 | **R2→R2 的邻域搜索** |

否则只是重复证明「我们比 R2 弱」。

---

## 封存清单（P17–P24）

```text
❌ 全闭环 planner
❌ naive kNN retrieval
❌ 单点 bailout branch
❌ margin-threshold selector
❌ 无限制加 tail
❌ 直接 PPO
❌ 用我们 production 整窗替换 R2   ← NEW
```

剩余问题仍是：**如何生成/搜索出与 R2 同级或更强的整段 trajectory。**

---

## Artifacts

```text
RESEARCH_P24_SEGMENT_MUTATION.md
p24_trajectory_mutation.csv
_p24_mutation.py
```
