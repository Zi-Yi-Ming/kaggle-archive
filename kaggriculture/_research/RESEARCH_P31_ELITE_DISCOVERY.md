# P31 — Heterogeneous Elite Discovery

**Date:** 2026-09-12  
**Principle:** Performance first, explanation second  
**Harness:** pinned `env.info["seed"]`  
**Opponent:** fallow_finn, seeds 1–3  
**No submission.**

---

## Decision

```text
SECOND_ELITES_FOUND
```

**找到多条 bank≥170k 且 action-fingerprint 与 R2 近乎不重合的轨迹源。**  
异构 elite corpus 的前提成立 — 可进入 P32 cross-elite transfer。

---

## Scan results

| Candidate | mean bank | tier | action sim vs R2 | note |
|---|---:|---|---:|---|
| **R2** | **183,850** | ELITE | 1.00 | 自身 |
| prvsiyan_moon | 183,850 | ELITE | **1.00** | R2 同源 |
| danilchil | 183,507 | ELITE | **1.00** | R2 同源 |
| tetsu_msf | 183,471 | ELITE | 0.88 | 近亲 shop-router |
| **rayk_rank** | **176,893** | **ELITE** | **0.28** | 异构 |
| **kaito_v27** | **175,507** | **ELITE** | **0.00** | 异构 |
| **kaito_v58** | **175,368** | **ELITE** | **0.02** | 异构 |
| **kaito_v48** | **174,986** | **ELITE** | **0.00** | 异构 |
| kaito_v43 | 174,986 | ELITE | 0.00 | ≈ v48 |
| **qeinstein** | **170,467** | **ELITE** | **0.02** | 异构 |
| **florian** | **112,020** | **BRONZE** | **0.00** | 异构中档 |
| tetsu_shape / boatlee / kaito_v21 | 3,000 | WEAK | — | 本 env 未跑通 |

**sim** = 逐步 action JSON 完全相同的比例（seed1）。0.00 ≠ 无结构，只表示 **逐步动作几乎从不相同**。

---

## 高价值清单（bank ≥ 150k 且 sim < 0.5）

```text
R2          184k
rayk_rank   177k  sim 0.28
kaito_v27   176k  sim 0.00
kaito_v58   175k  sim 0.02
kaito_v48   174k  sim 0.00
qeinstein   170k  sim 0.02
```

**至少 4 个非 R2 族 ELITE**（kaito 系 + qeinstein + rayk）。

---

## 与 P28/P29 对照

| | |
|---|---|
| P28 R2 规则抽取 | ~20% |
| P29 R2×N corpus | 24.8% 不涨 |
| **P31** | **发现真正异构的第二/三/四 elite** |

P29 的「同源无用」现在有了对照物：**异构源已存在**。

---

## 下一步（P32，本轮不实现）

```text
R2 / kaito_v27 / qeinstein / rayk_rank
        ↓
cross-elite BC (R2, R2+K, R2+Q, R2+K+Q, …)
        ↓
transfer ratio vs 24.83% baseline
```

Falsification：

- 若混合 corpus 仍 ~25% → 异构 elite 也不迁移，imitation 路线弱  
- 若显著 >25%（如 40–60%）→ 进入 neural BC / offline improvement

---

## Caveats

- sim=0.00 是 **逐步 JSON 不等**，不是「策略无关」；kaito 各版本间也可能高度相关  
- 仅 vs finn bank；未测 vs R2 H2H / 混合池  
- kaito_v43 ≈ v48（同 bank）— 不要当成两个独立 elite  

---

## Artifacts

```text
RESEARCH_P31_ELITE_DISCOVERY.md
p31_candidate_scan.csv
_p31_scan.py
```
