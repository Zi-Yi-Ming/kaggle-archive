# P30 — History Dependence & Opponent Archetypes

**Date:** 2026-09-12  
**Harness:** `p26_harness` / `env.info["seed"]` pinned  
**No submission. No new heuristic policy.**

---

## Final Decisions

| Hypothesis | Verdict |
|---|---|
| **HISTORY_DEPENDENCE** | **NOT_SUPPORTED** |
| **REGIME_STRUCTURE** | **NOT_SUPPORTED**（history 无增益 → 不启 regime search） |
| **OPPONENT_ARCHETYPE_CONCENTRATION** | **NOT_APPLICABLE_NO_LOSSES** |

---

## P30-A History Dependence

**Data:** R2 vs finn, seeds 1–5, 3595 steps.  
**Label:** market action-bundle signature.  
**Models:** M0 current-state bucket; M1/M3/M5/M10 = state + k-day history summary.

| Model | buckets | test acc |
|---|---:|---:|
| M0 | 755 | **0.775** |
| M1 | 755 | **0.775** |
| M3 | 755 | **0.775** |
| M5 | 755 | **0.775** |
| M10 | 755 | **0.775** |

**Δacc = 0.000**（&lt; 2pp 阈值）。

### Ambiguity

- Train buckets: **755**，其中 **161 (21%)** 含多种 `sig`  
- 加 history 后：**仍 755 桶 / 161 ambiguous** — history **未拆分** 歧义桶  
- 有 18 种不同 h1 向量，但与 cur_bucket 组合后 **不产生新键**

### 解释

R2 是 **确定性 tape policy**。在粗粒度 state（day/hour/money/animals/plants/hands）下：

> 过去 k 日轨迹 ≈ 当前 state 的函数，不是独立决策变量。

残余 21% 歧义来自 **更细 state**（shop 序列、具体 inventory、worker 位置），**不是** day-level history。

### Falsification

`M1–M10 acc ≈ M0` → **HISTORY_DEPENDENCE = NOT_SUPPORTED**  
→ **不启动 P30-B regime search**。

---

## P30-B Regimes

**Skipped.** Regime discovery 需要 history/change-point 信号；A 已否定。

若强行聚类 day-level features，只会重述 tape 阶段（SETUP/GROW/CASH），**无新信息**。

---

## P30-C Opponent Archetypes

**R2 vs 10 pool agents × 2 seeds（pinned）**

| Opponent | W/L | mean margin | opp bank | opp d10 money |
|---|---|---:|---:|---:|
| broker_bea / ledger_lena / slotter_silas | 2-0 | **+38k～+42k** | 60–70k | ~430 |
| closer_cleo | 2-0 | +40k～+50k | 22–50k | ~1.6k |
| finn / walter / rosa / hana / mateo / rita | 2-0 | **+146k～+165k** | **3000** | 未真正开局 |

**R2 losses: 0/20**

| 结论 | |
|---|---|
| Loss 集中在少数 archetype？ | **无法评估 — 无 loss** |
| Margin 结构 | 仅 **active vs passive** 两档，不是 loss archetype |
| OPPONENT_ARCHETYPE_CONCENTRATION | **NOT_APPLICABLE_NO_LOSSES** |

弱对手 bank 卡在 $3000 → 其 trajectory features 无信息。  
中档对手有真实生产但仍全败 → 本地 pool **测不出** R2 的失败面。

**若要测 loss archetype，需要更强对手（R2 镜像 / top public / 真实 Kaggle pool），不是 reference_agents tier0–9。**

---

## 永久停止 / 下一步

### 停止

```text
❌ day-level history-dependent policy
❌ 在 R2 tape 上做 regime 分段学习（A 已否定）
❌ 对手条件分支（本地无 loss 可学）
❌ 继续 heuristic / 单源 corpus / 粗 mutation
```

### 下一步（若继续 2900）

| 优先级 | 方向 |
|---|---|
| 1 | **更强/异构 elite corpus**（非 R2×N） |
| 2 | 更细 state（shop path, tile-level）— 仅当有明确目标 |
| 3 | 真 BC/RL — 仅当有多样 elite 数据 |

P27–P30 共同结论：

> R2 是 **高耦合、history-free（day-level）、本地 basin、对 pool 全胜** 的 elite trajectory。  
> 突破需要 **新数据/新轨迹生成机制**，不是继续拆 R2。

---

## Artifacts

```text
RESEARCH_P30_HISTORY_OPPONENT.md
p30_history_features.csv
p30_history_model_comparison.csv
p30_opponent_features.csv
p30_opponent_clusters.csv
_p30a_history.py
_p30c_opponents.py
```
