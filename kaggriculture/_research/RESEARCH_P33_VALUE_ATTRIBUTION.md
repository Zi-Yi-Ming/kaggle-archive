# P33 — R2 Value Attribution & Open-Loop Audit

**Date:** 2026-09-12  
**Pinned harness. No NN. No PPO. No submit.**

---

## Final Decisions

| Audit | Result |
|---|---|
| **P33-A market↔worker 可分性** | **COUPLED_NOT_SEPARABLE** |
| **P33-B 跨 elite worker 共同 policy** | **NOT_SUPPORTED** |
| **P33-C open-loop by time** | **SUPPORTED**（acc=1.000） |

---

## P33-A Oracle hybrid（seed 1–3，vs finn）

| Arm | mean bank |
|---|---:|
| **A0 纯 R2** | **183,850** |
| A1 R2 market + 我们 workers | **14,840** |
| A2 我们 market + R2 workers | **23,415** |
| A3 纯我们 | 27,491 |

### 读数

- **R2 market + 弱 workers → 比我们自己还差**（14k）  
- **R2 workers + 弱 market → 仅 23k**（略低于我们）  
- **合在一起 → 184k**

> **100k+ 的价值在 market×worker 耦合，不在任一可拆组件。**

这解释了 P24/P28/P32：拆开或只学一层，都到不了 R2。

---

## P33-B Worker trajectory similarity vs R2（seed1）

| Policy | bank | **worker_sim** | market_sim |
|---|---:|---:|---:|
| R2 | 181k | 1.00 | 1.00 |
| kaito_v27 | 174k | **0.003** | 0.36 |
| qeinstein | 163k | **0.038** | 0.40 |
| rayk_rank | 163k | 0.32 | 0.76 |

**高 bank + worker_sim≈0** → 不存在「跨 elite 的简单共同 worker policy」。  
各自用不同路径达到 160k+。

---

## P33-C Initial / open-loop predictability（R2 market sig）

| Model | acc | buckets |
|---|---:|---:|
| current-state bucket | 0.573 | 142 |
| day + hour-bin | 0.559 | 120 |
| **day + hour（时间开环）** | **1.000** | **719** |

**R2 的 market action = f(day, hour) 完全确定。**  
与 P30 history=0、P27 deep basin 一致：

> R2 是 **step-indexed open-loop plan**，不是 reactive policy。

残余 worker 侧仍有状态依赖（路径），但 **market 主干是 tape**。

---

## 决策树（按你 P33 设定）

```text
worker 强？     否 — 跨 elite worker_sim≈0；R2 workers 单独也不够
joint 强？      是 — 但 joint = market×worker 耦合，无法拆层学习
initial 强？    是 — market 由 (day,hour) 开环决定
```

**指向：trajectory generator / open-loop plan + 耦合执行，不是可分离 BC。**

---

## 与 P27–P32 合并

```text
P27  粗 mutation → 深 basin
P28  规则抽取 → 20%
P29  同源 corpus → 不涨
P30  history → 无
P31  发现异构 elite
P32  异构 market BC → 仍 26%
P33  market×worker 不可分 + open-loop by time  ← 现在
```

**R2 的核心是：按 step 执行的开环计划，且与 worker 执行强耦合。**

---

## 下一步（若继续）

```text
initial env / seed realization
        ↓
generate full coupled trajectory (market+workers)
        ↓
tactical repair
```

而不是：

```text
learn market table
learn worker table
combine
```

**不要**在本 stack 上继续 tabular BC。

---

## Artifacts

```text
RESEARCH_P33_VALUE_ATTRIBUTION.md
p33a_oracle_hybrid.csv
p33b_worker_similarity.csv
p33c_initial_predictability.csv
_p33a_oracle.py
_p33bc_worker_init.py
```
