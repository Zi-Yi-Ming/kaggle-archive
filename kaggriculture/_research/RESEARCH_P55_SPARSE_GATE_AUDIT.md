# P55 — Sparse Dynamic Gate Audit

**Date:** 2026-09-15  
**Anchor:** live alperen_meta (LB 2361.5)  
**Scope:** divergence landmarks only — **no submit, no SELL±1 expand**

---

## Decision

```text
SPARSE_GATES_MIDGAME_ONLY
EARLY_SKELETON_SHARED_VS_R2
LATE_FULL_BRANCH_AFTER_D20
```

与 Liquor「强骨架 + 少数特殊节点」**部分吻合**：  
稀疏 gate 主要在 **d7–d12**；**d20+ 不是稀疏 gate，而是整段分叉**。

---

## Step0 开局

几乎所有 pair 在 **step0 SELL** 即分叉（开局 market 顺序）。  
分析从 step≥1 计。

---

## vs R2（最近族，seed1 live）

| day | div steps |
|---:|---:|
| 2–5 | ~0 |
| **6** | **1/24** |
| **7** | **7/24** |
| **9** | **13/24** |
| 10 | 4/24 |
| 11 | 7/24 |
| 12 | 4/24 |
| 15–18 | 11–14/24 |
| **20–28** | **~23–24/24** |

`first_div_after0 = step 23 (d1)`，之后长期几乎同步，直到 **d7/d9** 才系统分叉。

---

## vs rayk / guru（同 meta 更远）

- rayk：d9 **17/24**，d18+ 接近全分  
- guru：d1 就 23/24（不同 opening）；d9 **15/24**；d20+ 全分  

**d9 是跨三个对手最稳的 mid landmark**（不是 d6）。

---

## 假设检验

| H | 判定 |
|---|---|
| 0–~180 步公共骨架 | **vs R2 SUPPORTED**（d2–5 几乎同轨） |
| 特殊节点稀疏 gate | **部分 SUPPORTED**（d7–d12） |
| 全程 sparse gates | **REJECTED**（d20+ 全分） |
| ML/lookup shop→action | 仍受 P48/P49 限制 |

---

## 下一步（未做）

在 **d7 / d9 / d12** 上做 **live** 单 gate A/B（语义 state，非 shop-id lookup）：  
- vs live alperen  
- vs R2  
- 跨 seed 方向一致才 positive  
- 否则 STOP  

**不** submit；**guru** 仍封存。

---

## Artifacts

```text
RESEARCH_P55_SPARSE_GATE_AUDIT.md
p55_gate_landmarks.csv
p55_gate_day_profile.csv
p55_live_sell.csv          # 前一轮 SELL delay 作废（无稳定信号）
_p55_gate_audit.py
_p55_gate_profile.py
```
