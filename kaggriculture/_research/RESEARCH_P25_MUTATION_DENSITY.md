# P25 — R2 Local Mutation Density

**Date:** 2026-09-12  
**Operator:** 2-step action-bundle ablation (DROP_SELL / SKIP_HIRE / NO_WORK / DROP_BUY) at days {4,7,10,14,20,25}  
**Baseline:** pure R2, same seed, vs fallow_finn  
**Seeds:** 1–3. **No NN. No submit.**

---

## Decision

```text
LOCAL_ROBUST_WITH_NOISY_POSITIVES
```

粗粒度邻域里 **约 72% mutation 为负**；正向存在但 **跨 seed 不稳定**，不足以宣称「可爬山的改进邻域」。

---

## Density（3 seeds × 24 = 72）

| | |
|---|---:|
| positive | **20/72 (28%)** |
| mean Δbank | **−19,713** |
| median Δ | −17,238 |
| best | +38,424 |
| worst | −95,066 |

Seed1 单独曾出现 54% 正 — **多 seed 后不成立**。

---

## By mutation kind

| kind | pos | meanΔ |
|---|---:|---:|
| **DROP_SELL** | 9/18 | **+1,465** |
| DROP_BUY | 6/18 | −15,090 |
| NO_WORK | 3/18 | −28,188 |
| SKIP_HIRE | 2/18 | **−37,040** |

- **跳过雇佣几乎总是亏** — 日更劳动力是 R2 硬约束（与 P12 一致）  
- **少卖两步** 均值略正，但 seed 间翻转大  

---

## By day

| day | pos | meanΔ |
|---:|---:|---:|
| 4 | 4/12 | −18.8k |
| 7 | 4/12 | −19.8k |
| **10** | **0/12** | **−42.3k** |
| 14 | 2/12 | −17.6k |
| 20 | 4/12 | −15.0k |
| 25 | 6/12 | −4.8k |

**d10 全负** — 与 P13「d10 melon 变现窗」一致：**不要动 R2 的 d10**。

---

## Validity caveat

同 seed 下两次 T0 bank 出现过不一致（140k vs 179k）— 可能来自 pool 对手缓存状态 / path 敏感。  
因此「+Δ」更应读作 **path 噪声内可能改善**，而非可重复 hill-climb 步。

---

## 对「R2 是否局部最优」的回答

| 问 | 答 |
|---|---|
| 90%+ 为负？ | **否**（72% 为负） |
| 稳定正向邻域？ | **否**（28% 正、kind/day 强依赖、seed 不稳） |
| 可沿 mutation 爬山？ | **证据不足** |

更准确：

> R2 对 **粗粒度 2-step 消融** 相当稳健；邻域有噪声正向点，但 **未形成可重复改进方向**。

---

## 与 P24 合并

```text
P24 大窗替换 → 毁灭性
P25 2-step 微扰 → 多数为负，少数噪声正
```

R2 既不是「随便可 patch 的模块堆」，也 **尚未证明** 是完美局部最优。  
要爬山需要：更细 action 空间、更稳的 T0 复现、以及 **vs R2 / vs 混合池** 的 margin，而不是仅 vs finn bank。

---

## Artifacts

```text
RESEARCH_P25_MUTATION_DENSITY.md
p25_mutation_density.csv
_p25_density.py
```
