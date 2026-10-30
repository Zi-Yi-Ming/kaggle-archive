# P17.1 — Continuation Library (Last Replay+Branch Paradigm Test)

**Date:** 2026-09-12  
**Architecture (Type E, not tape copy):**

```text
BACKBONE = MAIN  (p14.1 portfolio + p13.3 water + B labor/EOD/shepherd)
Checkpoints (sparse, observable, once):
  CP_CASH_WINDOW  d9–12: ready_melon+shed_melon≥2 ∧ money<1200 → tail CASH_WINDOW
  CP_HERD_SCALE   d11–16: n_animals<2 ∧ money≥900 → tail HERD_SCALE
Tails = future target overlays (prefix-compatible, no rewind)
Repair = p10 unchanged
```

**Gate:** 8 games vs R2, both seats, seeds 1–4. **NO SUBMIT.**

---

## Decision

```text
CONTINUATION_LIBRARY_SUPPORTED
```

在 **严格 paired** 下，library **8/8 优于 backbone**，效应量大且方向稳定 — 与 P16 的 NOT_ROBUST 形成对照。  
**仍 0-8 vs R2** — 这是范式内增益，不是 2900 解。

---

## Ablation

| Arm | W-L vs R2 | bank | d15 | d29 | bankrupt |
|---|---|---:|---:|---:|---:|
| BACKBONE | 0-8 | **$11,383** | $4,001 | $11,383 | 0 |
| **LIB** | 0-8 | **$25,086** | **$13,219** | **$25,086** | 0 |

| Metric | Δ (LIB − BACKBONE) |
|---|---:|
| bank | **+$13,703 (+120%)** |
| d15 | **+$9,218 (+230%)** |
| paired LIB better | **8/8** |

### Paired Δbank

| seed/seat | Δ |
|---|---:|
| s1 s0 | +32,311 |
| s2 s0 | +21,467 |
| s3 s0 | +9,676 |
| s4 s0 | +12,547 |
| s1 s1 | +14,990 |
| s2 s1 | +9,100 |
| s3 s1 | +1,676 |
| s4 s1 | +7,864 |

**无一局变差。** 触发 tail 均为 `CASH_WINDOW`（backbone 在 d9–12 稳定出现「可转换长作物 + 现金偏紧」）。

---

## 为何比 P16 稳

| | P16 FORCE_SELL | P17.1 library |
|---|---|---|
| 结构 | 单次动作 | **持续 tail overlay**（LIQUIDATE 模式粘住） |
| 触发 | day==10 硬编码 | **可观测窗口 d9–12 + 状态** |
| 复现 | +45% 后翻车 | **8/8 同向** |
| 与 tetsu 形态 | 弱相似 | **checkpoint → tail** 同构 |

---

## 仍 vs R2

| | bank |
|---|---:|
| LIB | $25k |
| R2 | $120k–$190k |

差距仍一个数量级。本结果说明：

> sparse checkpoint + continuation overlay **在我们骨架上真实有效**；  
> **不能**单独解释 2900+。

---

## 纪律（按你的失败判据）

- **未** 堆 tail A/B/C 无穷分支  
- **未** 按 seed 选 tail  
- 仅 2 个预注册 checkpoint；本 run 实际只用到 1 个（CASH_WINDOW）  
- 未实现第二范式；**未提交**

若下一步：只允许 **一个** 增量（例如 HERD_SCALE 在 CASH_WINDOW 未触发时的 ablation），禁止 tail 泥潭。

---

## 研究层级判断

P17.1 **通过** → 暂不必立刻判「范式已死」。  
但 bank $25k vs R2 $150k 仍支持你的分层假设：

```text
public adaptive family ≈ 2200–2500
private corpus / selector / RL ≈ 2900+
```

我们仍在前一层做 **架构正确的增量**，尚未触及 private corpus / learned selector。

---

## Artifacts

```text
RESEARCH_P17_1_CONTINUATION_LIBRARY.md
p17_1_library/__init__.py
p17_1_local_results.csv
p17_1_ablation.csv
_p17_1_ablation.py
```

Default: `p17_1_library.ENABLED = False` 除非 harness 打开。
