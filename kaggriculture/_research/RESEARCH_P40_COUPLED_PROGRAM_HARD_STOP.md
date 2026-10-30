# P40 — New Coupled Program Discovery (HARD STOP)

**Date:** 2026-09-14  
**Budget:** ≤500 coupled programs  
**Gate:** Stage1 seed1 ≥ 100k，否则封版  
**Protocol:** pin `env.info["seed"]`，finn 不 wrap

---

## Decision

```text
P40_STAGE1_FAIL_HARD_STOP
```

| 检查 | 结果 |
|---|---|
| Stage0 determinism（同 program 同 seed） | **PASS**（hash/bank 全同） |
| grid size | **500** |
| Stage1 max bank (seed1) | **44** |
| Stage1 median | **37** |
| **n ≥ 100k** | **0** |
| R2 mean3 reference | 183,850 |

**0 / 500 过第一关。研究范式正式封版。**

---

## P40 是什么

完整 **coupled** program：每个 candidate 同时决定 market + worker，**不**调用 p11，**不**拆 elite tape。

参数维度（离散）：

```text
opening × mid_crop × animal_mix × land × sell × hire × long_cut × route
→ 500 unique programs
```

Stage0 证明 compile → 720-step tape 是确定性的。

---

## Stage1 分布

```text
max     44
median  37
≥100k    0
```

与 P38（market grammar + p11，max 21k）对比：

| 范式 | max bank |
|---|---:|
| p11 baseline | 26,725 |
| P38 grammar + p11 | 21,089 |
| **P40 从零 coupled** | **44** |

从零手写 coupled program **更差**——不是「差一点」，是 **三个数量级**。

---

## 为什么（机制，不是借口）

1. **Open-loop 产能锁死在 tape 几何上**  
   R2 d2 有 19 植株、d12 有 16 动物。P40 开局能种 ~11，随后杂草/现金/坐标分叉导致塌缩。

2. **Worker↔Market 时序不可拆也不可手拼**  
   P39：elite worker 单独 + 弱 market = 5–329。  
   P40：自写 worker+market 耦合 = 30–44。  
   可迁移的是 **整条已进化 tape**，不是我们能枚举的规则。

3. **离散旋钮空间是平坦盆地**  
   500 个 program bank 几乎常数（30–44），没有梯度可爬。

---

## 研究链最终判定（P9–P40）

```text
❌ closed-loop planner
❌ BC / policy extraction
❌ skeleton / landmark
❌ manual mutation
❌ market|worker split
❌ elite tape recombination
❌ market grammar + p11
❌ worker-tape transfer
❌ 从零 coupled program 枚举   ← P40 HARD STOP
```

**可达 production ceiling：**  
现有 elite program family（R2 ~2012 Elo / #1476 / top 16.5%）。

---

## Production 锁定

```text
last-2 slot 1:  R2 path-twin   2012.7
last-2 slot 2:  R2             1997.7
```

- **不**用任何未过门禁的候选替换  
- **不**为 Top10% 做「小优化」（P27–P39 已杀完）  
- 唯一 submit 条件不变：本地 ≥5/8 vs R2 + multi-seed ≥150k + novel program  

**当前 0 候选。不 submit。**

---

## 若仍要冲牌（非本线程默认路径）

仅当接受高成本、低先验：

1. 更大 external elite corpus（非 R2 同源）  
2. 真·trajectory search / program synthesis（非离散旋钮）  
3. 或接受封版结果  

**不要**再开 P41 旋钮实验。

---

## Artifacts

```text
RESEARCH_P40_COUPLED_PROGRAM_HARD_STOP.md
p40_program/compiler.py
_p40_search.py
p40_stage1.csv
```

**研究序列 P9–P40 结束。R2 锁定为 production champion。**
