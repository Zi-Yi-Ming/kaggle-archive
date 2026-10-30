# P44 — Minimal Replay-Distillation Reproduction

**日期：** 2026-09-14  
**性质：** 机制最小复现（非新算法 / 非 GA / 非 submit）  
**红线：** finn 不 wrap；`env.info["seed"]` pin；R2 不修改

---

## P44 DECISION

```text
PARTIALLY_REPRODUCED
```

- **RECONSTRUCTION = PASS**（public replay → majority tape → 99k，3-0 vs finn）  
- **OVERLAY = NO_ELO_SIGNAL**（12 个有界 market 变体 W-L 均为 3-0，无相对 baseline 改善）  
- **SUBMISSION = FROZEN**

---

## A. Replay reconstruction

| 项 | 值 |
|---|---|
| 源 | P42 已下载 R2 live public episodes（submission 56181169） |
| 条数 | **30**（全部 720 steps） |
| 同一 elite？ | **是**（同一 submission / 同一 R2 path-twin） |
| 非 R2 family | 本轮未再下载（spec 允许优先用已有 artifact；pipeline 用 R2 验证） |
| seed 注入 | `env.info["seed"]` |
| finn arity | **1-arg，未 wrap** |

`p44_replay_sources.csv`

---

## B. Field stability（majority vote，market/worker 分开）

| 指标 | ratio |
|---|---:|
| market ≥95% agreement | **0.583** |
| market unanimous | **0.536** |
| worker ≥95% agreement | **0.254** |
| worker unanimous | **0.253** |
| both ≥95% | **0.224** |
| market ties | 1（按首局顺序，已记录） |
| worker ties | 0 |

Worker 在 live 多对手下 **不稳定**（草/路径），与 P42 一致。  
Market 更稳定，但仍非 100%——distillation 取 **逐 step majority**，**无「聪明修复」**。

`p44_distillation.csv`，`p44_distilled_tapes/r2_live_distilled.json`  
tape_hash=`137311a504ac3d72`

---

## C. Base tape（reconstruction gate）

双 seat vs finn，seeds 1/2/3：

| | |
|---|---|
| **W-D-L** | **3-0-0** |
| **W-L** | **+3** |
| bank mean±std | **99,142 ± 6,975** |
| min / max | 93,022 / 108,901 |
| live source reward mean | 94,550（vs 真实对手，非 finn） |
| 真 R2 agent vs finn 同 seed | 181k / 169k / 201k |

判定：

```text
完整 720 执行 · 无 runtime error · 双 seat 正常
bank 与 live 源同量级（甚至更高，因对手是弱 finn）
相对真 R2 有退化（~99k vs ~180k）但非数量级灾难
→ RECONSTRUCTION_PASS
```

`p44_candidate_results.csv`（base 行）

---

## D. Overlay（≤12，P43 粒度）

粒度：**单商品首次 SELL 时点 ±1/±2 步**（opening wheat 未改到则未生成）。

| candidate_id | mutation | changed_steps | W-D-L | W-L | bank mean |
|---|---|---|---|---:|---:|
| c00_baseline | none | — | 3-0-0 | 3 | 99,142 |
| c_melon_d-1 | first MELON −1 | 249,250 | 3-0-0 | 3 | 99,193 |
| c_melon_d+1 | first MELON +1 | 250,251 | 3-0-0 | 3 | 99,142 |
| c_melon_d-2 | first MELON −2 | 248,250 | 3-0-0 | 3 | 99,193 |
| c_milk_d-1 | first MILK −1 | 196,197 | 3-0-0 | 3 | 95,728 |
| c_milk_d+1 | first MILK +1 | 197,198 | 3-0-0 | 3 | 96,479 |
| c_milk_d-2 | first MILK −2 | 195,197 | 3-0-0 | 3 | 95,728 |
| c_strawberry_d-1 | first STRAW −1 | 382,383 | 3-0-0 | 3 | 99,157 |
| c_strawberry_d+1 | first STRAW +1 | 383,384 | 3-0-0 | 3 | 99,142 |
| c_strawberry_d-2 | first STRAW −2 | 381,383 | 3-0-0 | 3 | 99,157 |
| **c_wool_d-1** | first WOOL −1 | 149,150 | 3-0-0 | 3 | **101,118** |
| c_wool_d+1 | first WOOL +1 | 150,151 | 3-0-0 | 3 | 99,142 |

`p44_h2h.csv`

**无 W-L 改善。** vs finn 已全部顶格 3-0。  
`c_wool_d-1` bank +2k，按纪律：

```text
bank up, W-L flat → NO_ELO_SIGNAL
```

**不**据此继续优化，**不**扩大 mutation，**不** vs R2 当「候选替代」。

---

## E. Conclusion（仅允许枚举）

```text
PARTIALLY_REPRODUCED
```

| 组件 | 结果 |
|---|---|
| public replay 解析 | OK |
| stable field distillation | OK（market 54% unanimous） |
| base tape 双 seat 多 seed | OK（3-0，99k） |
| bounded overlay W-L | **无信号** |
| H2H/BT vs 强 field | **未做**（finn 天花板；非本阶段扩展） |

P43 机制中 **「distill → 可执行 elite 级 tape」** 得到复现。  
**「overlay → Elo」** 在 vs finn 门禁上 **不可检出**（目标已饱和）。

---

## 与 P42/P43 一致性

- Worker majority 只有 25% 稳定 → live 路径噪声（P42）  
- Market 时点在 distill 后仍可整段 replay → 开环 tape（P35/P41）  
- 有界 sell 时点扰动不改 vs-fin W-L → overlay 需 **强 field** 才有意义（P43 rayk 经验）

---

## Hard stop 纪律

- 未扩大 mutation space  
- 未提交 Kaggle  
- 未改 R2  
- 未用 bank-only 宣称成功  

---

## Artifacts

```text
RESEARCH_P44_MINIMAL_REPRO.md
p44_replay_sources.csv
p44_distillation.csv
p44_candidate_results.csv
p44_h2h.csv
p44_distilled_tapes/r2_live_distilled.json
p44_phase4_base.json
p44_summary.json
```

---

## 最终输出

```text
P44 DECISION:
PARTIALLY_REPRODUCED

RECONSTRUCTION:
PASS（30×R2 live → majority tape，720-step 完整）

BASE TAPE:
W-D-L 3-0-0，W-L=+3，bank 99142±6975

OVERLAY:
12 candidates

BEST CANDIDATE:
c_wool_d-1（bank 101118，W-L 仍 3，无 Elo 信号）

H2H:
vs finn 全部 3-0；无相对 baseline 的 W-L 改善

SUBMISSION:
FROZEN

ARTIFACTS:
RESEARCH_P44_MINIMAL_REPRO.md + p44_*.csv + p44_distilled_tapes/

NEXT:
机制已最小复现；overlay 需强 field 门禁才有意义，不在本阶段扩展。
```
