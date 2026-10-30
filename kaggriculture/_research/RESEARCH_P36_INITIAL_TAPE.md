# P36 — Initial → Tape Audit

**Date:** 2026-09-12  
**Elites:** R2, kaito_v27, qeinstein, rayk_rank × seeds 1–5  
**Pin harness. No training.**

---

## Decision

```text
TAPE_SPACE_IS_DISCRETE_FAMILY_NOT_CONTINUOUS
```

同 policy 跨 seed tape **几乎相同**（kaito/rayk ~97%）；跨 policy tape **几乎完全不同**（P31 sim≈0）。  
→ 生成空间更像 **离散 elite program 族 + shop 分支**，不是 720 维连续搜索。

---

## L2：Tape 唯一性

| | |
|---|---|
| unique hashes | **19 / 20** |
| 例外 | qeinstein s2 ≡ s4（同 hash，shops@144 不同） |

---

## 同 policy 跨 seed tape match（full / after144）

| Policy | 跨 seed full match | 解读 |
|---|---|---|
| **kaito_v27** | **0.967–0.987（全部）** | **几乎同一条 tape** |
| **rayk_rank** | **0.960–0.978（全部）** | **几乎同一条 tape** |
| R2 | 0.21–0.28 一组；**0.97–0.99 另一组**；s5 离群 | shop 路由出 **少数离散变体** |
| qeinstein | 0.37 一簇；**0.97–1.00 另一簇** | 两簇 |

R2 s2×s3/s4 full≈0.97–0.99 — **不同 shops@144 仍几乎同一 tape**（非 SHOP_PLANS 主导？或同 plan）。  
R2 s5 与其它 full≈0.21 — 真正另一条 tape。

---

## L0：shops@144 → policy？

**否。** 同一 shops 对出现在 R2 / qeinstein / rayk。  
**初始 shop realization 不能区分 elite family。**

---

## L1：前缀 → 后缀？

| K | 前缀近同 & 后缀也同 | 前缀近同但后缀不同 |
|---:|---:|---:|
| 1–72 | 26 | 14 |
| 144 | 19 | **39** |

早期前缀 **不能** 唯一决定后续 tape（跨 policy）。  
同 policy 内则高度一致（见上表）。

---

## H1 / H2 / H3

| Hyp | 判定 |
|---|---|
| **H1 可搜索连续 tape 空间** | **弱** — kaito/rayk 各自几乎是 1 个点 |
| **H2 低维程序展开** | **强支持** — policy id + 少量 shop 分支 → 720-step tape |
| **H3 高度偶然** | **部分** — R2 s5 离群；kaito/rayk 不偶然 |

---

## 含义

```text
不需要「在 720 维里搜索」
需要「枚举 / 合成 discrete elite programs」
每个 program ≈ 极低维参数（开模板 / 资源优先级 / 卖出节奏 / shop 分支）
```

与 P35 全员 open-loop 一致：

> 高分生态 = **少数可执行程序** 的展开，不是通用 policy。

---

## 下一步（若做 generator）

1. **程序合成 / 离散枚举**（opening + priority + sell cadence）  
2. 用 cheap eval（finn / 多 seed bank）过滤  
3. **不要** 连续 RL 在 720-step action 上直接搜  

**STOP：** tabular BC、skeleton 调参、手工 mutation、把 elite 混成一个 BC 数据集。

---

## Artifacts

```text
RESEARCH_P36_INITIAL_TAPE.md
p36_tape_similarity.csv
_p36_initial_tape.py
```
