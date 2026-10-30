# P23 — Margin-Aware Selector Hold-Out

**Date:** 2026-09-12  
**Train:** P22 seeds 1–2, days 9–10 (n=4 pairs)  
**Val:** seeds 3–4 (n=4)  
**Hold-out:** **unseen seeds 5–6**, days 9–10, all 3 tails vs melon_mateo  
**Selectors:** S0 MAIN / S1 melon≥3→CASH / S2 fitted thr on cash0  
**No NN. No PPO. No submit.**

---

## Decision

```text
SELECTOR_NO_EXTRA_INFO
```

Hold-out 上 **S2 ≡ S1**（thr=2000 从不生效）。  
P22 的强 Δmargin **基本是 P20 melon 信号的重述**，尚未增加新决策信息。  
**按决策树：不进入 P24 learned selector。**

---

## Train 拟合

| pair | melon | cash0 | ΔCASH |
|---|---:|---:|---:|
| s1 d9 | 9 | 1573 | +8,381 |
| s1 d10 | 9 | 507 | +23,474 |
| s2 d9 | 9 | 1728 | +9,454 |
| s2 d10 | 9 | 494 | +21,918 |

拟合 `CASH if melon≥3 and cash0 < thr` → **thr=2000**  
（我们状态里 cash0 几乎总 &lt;2k → 规则退化为 **S1**。）

Val 唯一失手 s4d9（Δ=−6,081, cash0=1612, mel=11）**仍会被 thr=2000 选中 CASH** — S2 也躲不开。

---

## Hold-out（seeds 5–6，未见）

| seed/day | ΔCASH vs MAIN |
|---|---:|
| s5 d9 | +3,676 |
| s5 d10 | +12,521 |
| s6 d9 | +12,163 |
| s6 d10 | +8,799 |

| Selector | picks | meanΔ | pos | worst | flips | bankrupt |
|---|---|---:|---:|---:|---:|---:|
| S0 MAIN | MAIN×4 | 0 | 0/4 | 0 | 0 | 0 |
| **S1 melon≥3** | CASH×4 | **+9,290** | **4/4** | +3,676 | 0 | 0 |
| **S2 thr=2000** | CASH×4 | **+9,290** | **4/4** | +3,676 | 0 | 0 |

**S2 与 S1 逐局相同。**

---

## 决策树落点

```text
P23
 ├─ 不优于 MAIN     否（S1/S2 均 +9.3k）
 ├─ ≈ melon rule    是  ← HERE
 └─ 稳定 > melon    否
         → 不进入 P24
```

| | |
|---|---|
| Continuation 有信号？ | **是**（CASH vs MAIN hold-out 4/4） |
| Margin-aware **额外**信息？ | **否** |
| 需要 learned selector？ | **现在不需要** |
| 竞技 W/D/L 泛化？ | 仍 **未证明**（全 W，0 flip） |

严谨表述：

> Continuation choice 拥有可测的 paired relative-value 信号；  
> 在本 hold-out 上，**margin 阈值未提供超过 melon≥3 的增量**；  
> 向 competitive W/D/L 的迁移仍未证明。

---

## 对 2900 路径的含义

Selector 这条线 **暂时到顶**：  
继续加特征/换模型，若状态仍集中在 `melon≈9, cash0&lt;2k`，只会重学同一规则。

真正未打开的仍是：

```text
更强 backbone / 更大状态覆盖 / 学习 action 或 trajectory 生成
```

---

## Artifacts

```text
RESEARCH_P23_SELECTOR_HOLDOUT.md
p23_holdout_rolls.csv
p23_selector_compare.csv
_p23_selector_holdout.py
```
