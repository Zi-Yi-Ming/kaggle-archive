# P37 — Elite Program Recombination

**Date:** 2026-09-12  
**Splices:** time-window / phase-boundary (NOT market|worker — P33)  
**Pinned, vs finn, seeds 1–3**

---

## Decision

```text
ATOMIC_PROGRAM
```

**没有 hybrid 超过 pure elite。**  
多数跨族拼接 **崩溃**；看似持平的 hybrid 实际是 **拼接无效**（一侧被另一侧吞掉）。

---

## Mean banks

| Candidate | mean bank |
|---|---:|
| **pure_R2** | **183,850** |
| rayk_boot + R2_rest@d6 | 183,847 |
| R2_then_Q@144 | 183,844 |
| rayk_then_R2@144 | 176,896 |
| pure_rayk | 176,893 |
| pure_kaito | 175,507 |
| pure_Q | 170,467 |
| Q_then_R2@144 | 168,459 |
| R2_convert_Q_rest@d10 | 161,695 |
| R2_then_kaito@144 | 83,589 |
| kaito_scale_rayk@d12 | 65,514 |
| kaito_boot_R2@d2 | 11,061 |
| kaito_then_R2@144 | **857** |
| R2_expand_kaito@d6 | **857** |
| R2_boot_kaito@d2 | **96** |

`hybrid_max ≈ pure_max`，且最优 hybrid 与对应 pure **差 &lt;$10** — **无新点**。

---

## 拼接语义

| 现象 | 解释 |
|---|---|
| rayk_d0–5 + R2_rest ≈ R2 | rayk 早期与 R2 族几乎同轨，或 R2 后段完全接管 |
| R2→Q@144 ≈ R2 | Q 后段与 R2 后段经济等价/兼容 |
| R2→kaito 多数崩溃 | **开环 program 内部强耦合**，中途换轨破坏前提 |
| kaito→R2@d2/d144 崩溃 | kaito 开局后 R2 tape 的假设不成立 |

与 P33 一致：**program 不可按时间窗自由重组。**

---

## Decision tree 落点

```text
新组合 ≥ elite？  否
全部崩溃？        多数是
→ ATOMIC PROGRAM
```

**每个 elite ≈ 不可拆的完整 program。**  
搜索空间不是 `opening × worker × sell`，而是 **离散 program 家族**。

---

## 对 medal 路线的含义

```text
P35  elite = open-loop tape
P36  tape = discrete program × seed/shop branch
P37  program 不可时间窗重组  ← HERE
```

下一步若继续：

- **不要**再拆 elite 内部模块  
- **要**做 **新 program 的合成/搜索**（新 opening + 新 cadence 的整体程序）  
- cheap eval：pinned multi-seed bank vs finn  
- 目标：第 5 个 **160k+** program，而非复现 R2

**STOP：** recombination of existing elite tapes、tabular BC、skeleton 调参、手工 mutation。

---

## Artifacts

```text
RESEARCH_P37_PROGRAM_RECOMBINATION.md
p37_recombination.csv
_p37_recombine.py
```
