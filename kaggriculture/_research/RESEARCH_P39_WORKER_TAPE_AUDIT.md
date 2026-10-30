# P39 — Worker-Tape Discovery Audit

**Date:** 2026-09-13  
**Protocol:** pin `env.info["seed"]`, finn **unwrapped**, seed 1  
**Question:** 高分 program 的核心是否是可迁移的 worker choreography？

---

## Decision

```text
WORKER_TAPE_IS_NOT_AN_INDEPENDENT_TRANSFERABLE_CORE
```

Elite worker tape + 弱 market → **5–329**（纯 elite 为 162k–181k）。  
Elite market tape + PASS workers → **0**。  
完整同族 tape 回放 → **delta = 0**（harness 无 bug）。

**价值在耦合的完整 program，不在可拆出的 worker 层。**

---

## P39-A 交叉矩阵（seed1, vs finn）

| 配置 | bank |
|---|---:|
| weak_market_only | 5 |
| p11_full | 26,725 |
| **pure_R2** | **181,389** |
| R2_worker + weak_mkt | **57** |
| R2_market + PASS_wkr | **0** |
| R2_market + p11_wkr | 11,170 |
| **pure_kaito_v27** | **174,341** |
| kaito_worker + weak_mkt | **5** |
| kaito_market + PASS_wkr | **0** |
| kaito_market + p11_wkr | 26,152 |
| **pure_qeinstein** | **162,690** |
| Q_worker + weak_mkt | **31** |
| Q_market + PASS_wkr | **0** |
| Q_market + p11_wkr | 1,613 |
| **pure_rayk_rank** | **163,494** |
| rayk_worker + weak_mkt | **329** |
| rayk_market + PASS_wkr | **0** |
| rayk_market + p11_wkr | 14,317 |

### Sanity（同族完整 tape 回放）

| elite | pure | replay | delta |
|---|---:|---:|---:|
| R2 | 181,389 | 181,389 | **0** |
| kaito_v27 | 174,341 | 174,341 | **0** |
| qeinstein | 162,690 | 162,690 | **0** |
| rayk_rank | 163,494 | 163,494 | **0** |

回放精确恢复 ⇒ 交叉崩溃 **不是** 录制/步进错误。

---

## 机制诊断（R2_worker + weak_mkt）

| day | money | plants | animals | seeds 积压 |
|---:|---:|---:|---:|---|
| 1 | 36 | 9 | 1 | wheat 9, melon 7 |
| 6 | 106 | 9 | 1 | melon 9 |
| 12 | 2,491 | 4 | 1 | wheat 23, straw 6, melon 13 |
| 18 | 18 | 2 | 0 | wheat 44 |
| 29 | 57 | 0 | 0 | **wheat 60, straw 15, melon 13** |

- 开局 worker tape **能** 种下 ~9 株（弱 market 也买了种）  
- 随后植株 **塌缩**，种子积压到 60+ 却无人种  
- 原因：open-loop worker 走向 **R2 自己 market 造出的 tile 坐标**；状态一分叉，指令全空转  

⇒ worker tape **依赖** 配套 market 产生的农场几何/库存时序，**不是** 可迁移生产原语。

---

## 对假设的判定

| 假设 | 判定 |
|---|---|
| H-W1：elite worker tape 携带独立产能，弱 market 下仍能拉高 bank | **REJECTED**（5–329） |
| H-W2：elite market tape 无 worker 也有价值 | **REJECTED**（0） |
| H-W3：market+p11 workers 可接近 elite | **REJECTED**（≤26k ≈ p11） |
| H-W4：worker-first 轨迹搜索可用 elite worker 当种子 | **REJECTED** |

与 P33/P37/P38 一致并加强：

```text
P33  market × worker 不可分
P37  program 时间窗不可拆
P38  market grammar + 弱 worker ≤ 21k
P39  worker tape 单独不可迁移  ← HERE
```

---

## P39-B/C 含义

用户设想的 P39-B：

```text
WorkerProgram（完整 720-step）+ 配套 market program
```

在 **不用 elite tape 当种子** 的前提下，等于从零合成耦合 program。  
P38 已否掉「旋钮式 market + p11 worker」；P39-A 否掉「elite worker 当可迁移底座」。

**尚未证明存在** 可枚举的「新完整 coupled program」达到 100k+。

P39-C 门禁保持：

```text
Stage1  seed1 ≥ 100k
Stage2  mean3 ≥ 120k
Stage3  8-seed mean ≥ 150k
Novelty 与四 elite tape sim < 0.8
Kaggle  仅在本地 ≥5/8 vs R2 之后
```

当前 **没有任何候选** 过 Stage1。

---

## Decision tree 落点

```text
worker tape 独立有产能？     否
elite worker 当种子能迁移？  否
market tape 独立有产能？     否
完整 tape 回放是否可信？     是（delta=0）
→ COUPLED_ATOMIC_PROGRAM（再次确认）
→ worker-first discovery 路线关闭
```

---

## 下一步（若继续）

只剩三条，且都 **不是** 小改进：

1. **真正 coupled program synthesis**（worker+market 同时生成，维度远高于 P38 grammar）— 成本高、先验弱  
2. **扩大 external corpus**（新 elite / 公开解）  
3. **停止启发式搜索**，宣布：  
   > 当前可达 production ceiling = R2/现有 elite program family；突破需要 trajectory search 或外部新解

**若再做一轮 structured 冲刺仍无 ≥100k 稳定候选，建议正式封版。**

**NO SUBMISSION。**

---

## Artifacts

```text
RESEARCH_P39_WORKER_TAPE_AUDIT.md
p39_worker_tape/harness.py
_p39a_cross.py
_p39a_sanity.py
p39a_crosses.csv
```
