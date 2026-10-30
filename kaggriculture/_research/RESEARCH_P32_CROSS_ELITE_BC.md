# P32 — Cross-Elite BC Transfer

**Date:** 2026-09-12  
**Corpus:** elite_corpus/ — R2, kaito_v27, qeinstein, rayk_rank  
**Train:** seeds 1–4 · **Holdout:** 11–13 · **Pin harness**  
**BC:** tabular state→market-sig; workers = fixed p11 stack  
**No PPO. No submit.**

---

## Decision

```text
CROSS_ELITE_TRANSFER_NO_GAIN
```

异构 elite **没有**把 transfer ratio 从 ~25% 抬到 35%+。  
**约束在固定 worker/tactical 栈，不在「缺第二个 elite」。**

---

## Transfer ratios（vs R2 holdout bank）

| Config | mean ratio | holdout banks |
|---|---:|---|
| single_R2 | **26.55%** | 35k / 40k / 31k |
| single_kaito | 26.18% | 34k / 36k / 35k |
| single_qeinstein | 26.55% | 同 single_R2 |
| single_rayk | 26.55% | 同 single_R2 |
| multi R2+kaito+Q+rayk | **26.55%** | 同 |
| multi 3-hetero (无 R2) | 26.18% | 同 kaito |
| conditioned R2 / kaito / uncond | 26.55% / 26.18% / 26.55% | 同 |
| LOO 任意 held-out | 26.18–26.55% | 同 |

**P29 同源 24.83% → P32 异构 26.55%（+1.7pp，噪声级）。**

---

## Conditioned vs Unconditioned

| | buckets | ratio |
|---|---:|---:|
| uncond multi | 247 | 26.55% |
| cond as R2 | 706 | 26.55% |
| cond as kaito | 706 | 26.18% |

**policy_id 不改变 holdout bank** — 粗表 BC 学不到可迁移的「家族差异」。

---

## 解读

1. **不是 corpus 不够异构** — P31 sim≈0 的 elite 加进来也无效。  
2. **不是没做 leave-one-out** — 同样 ~26%。  
3. **不是 conditioned 没试** — 无增益。  
4. **天花板在固定 p11 workers + 我们的 market 执行语义**：  
   再好的 market 指令表，也发不出 R2 级路径/卖出/生产协同。

与 P12（routing 非主因但吞吐是）、P28（规则 20%）一致：

> **imitation of market-action tables on this executor is capped ~$30–40k.**

---

## Go/No-Go（按你设的阈值）

| 区间 | 判定 |
|---|---|
| &lt;25% | multi-elite 无效 |
| **25–35%** | **🟡 微弱 — 我们在这里（26.5%）** |
| 35–50% | 未达到 |

**未进入「明显突破」。**  
**不**自动切 neural BC / offline RL。

若继续 learned policy，必须先换 **action space / worker learning**，而不是再堆 market-table 语料。

---

## 仍有效的资产

```text
elite_corpus/
  R2/ kaito_v27/ qeinstein/ rayk_rank/
  banks.csv
```

可供未来 neural BC / worker-level imitation 使用。

---

## 永久停止（本 stack 上）

```text
❌ tabular market-action BC 多源扩语料
❌ 只靠 policy_id conditioning
❌ 期望 R2×N 或 R2+异构 → 自动涨 ratio
```

---

## Artifacts

```text
RESEARCH_P32_CROSS_ELITE_BC.md
elite_corpus/
p32_bc_transfer.csv
_p32a_record_corpus.py
_p32b_bc_eval.py
```
