# P46 — Representation Boundary Audit

**日期：** 2026-09-14  
**实验：** Live R2 policy vs Frozen R2 tape  
**条件：** 相同 seeds × finn × harness；finn 不 wrap；`env.info["seed"]`  
**禁止：** GA / RL / mutation / 改 R2 / submit

---

## Decision

```text
REPRESENTATION_GAP_CONFIRMED
```

同一 R2 来源：**活 policy ≈ 174k，冻结 tape ≈ 97k**。  
差距 **~78k（frozen/live = 0.555）**，不是 sell timing 微调可解释的量级。

---

## 1. 设置

| 项 | 值 |
|---|---|
| seeds | 1,2,3,4,5,11,12,13 |
| opponent | finn（1-arg，未 wrap） |
| seats | 双 seat |
| live | `_push_medal/main.py` 每次 fresh load |
| frozen | P44 majority tape（hash `137311a504ac3d72`） |
| tape hash seed1 | live `224f4547…` ≠ frozen `0f954c8f…` |

---

## 2. vs finn（主结果）

| agent | bank mean±std | range | W-D-L |
|---|---:|---|---|
| **live R2** | **174,262 ± 30,740** | 96k–201k | **8-0-0** |
| **frozen tape** | **96,687 ± 9,426** | 76k–109k | **8-0-0** |

### 配对 gap（live − frozen）

| seed | live | frozen | gap |
|---:|---:|---:|---:|
| 1 | 181,389 | 95,502 | 85,887 |
| 2 | 169,210 | 93,022 | 76,188 |
| 3 | 200,950 | 108,901 | 92,049 |
| 4 | 178,754 | 103,123 | 75,631 |
| 5 | 192,838 | 101,716 | 91,122 |
| 11 | 96,456 | 76,263 | 20,192 |
| 12 | 189,936 | 91,935 | 98,001 |
| 13 | 184,565 | 103,036 | 81,529 |
| **mean** | | | **77,575 ± 22,895** |

`p46_live_vs_frozen.csv`

---

## 3. Live vs Frozen 直接 H2H

| seed | live | frozen | winner |
|---:|---:|---:|---|
| 1 | 193,749 | 62,657 | LIVE |
| 2 | 108,151 | 42,522 | LIVE |
| 3 | 133,432 | 60,807 | LIVE |
| 4 | 100,768 | 49,376 | LIVE |
| 5 | 116,278 | 53,567 | LIVE |
| 11 | 118,530 | 53,174 | LIVE |
| 12 | 103,882 | 46,185 | LIVE |
| 13 | 165,474 | 74,495 | LIVE |

**Live 8-0-0。**  
`p46_h2h_live_frozen.csv`

---

## 4. 解释（与 P44/P45 闭合）

```text
P44/P45: frozen tape vs finn ~97–99k
         原始 live replay 复跑 vs finn ~100k
         → 不是蒸馏损失

P46:     live policy vs finn ~174k
         同 seed frozen ~97k
         → 差在「是否按当局 shop/path 条件分支」
```

seed 11（BAKERY 为主）live 也掉到 96k——活 policy 也有坏路径；  
但 **同路径下冻结 tape 仍系统性更低**。

---

## 5. 对「elite 是什么」的更新

```text
Elite ≠ 一条 180k 的 720-step tape
Elite = 条件 policy：state/shop/path → 选 trajectory
冻结单条 tape ≈ 丢掉 conditional 分支 → ~55% 产能
```

与 P35/P36/P42/P43 一致：  
开放环是 **执行表示**；**分支选择** 才是 live 产能来源。

---

## 6. 未证 / 禁止外推

- **未**证明需要 RL / 神经网络  
- **未**枚举完整 branch 集合  
- **未**恢复「最小 conditional policy」  
- **未**达到 submit 门禁  

下一步若继续，应是：

```text
识别 R2 依赖的条件变量（shop 序列 / path）
→ 极小 branch 表，而不是 GA
```

---

## 7. Production

R2 last-2 **冻结**。**无 submit。**

---

## Artifacts

```text
RESEARCH_P46_REPRESENTATION_BOUNDARY.md
p46_live_vs_frozen.csv
p46_h2h_live_frozen.csv
p46_summary.json
_p46_representation.py
```

---

## 最终输出

```text
P46 DECISION:
REPRESENTATION_GAP_CONFIRMED

LIVE R2:
174262±30740，8-0 vs finn

FROZEN TAPE:
96687±9426，8-0 vs finn

GAP:
mean 77575±22895，ratio 0.555

H2H:
live 8-0-0 vs frozen

SUBMISSION:
FROZEN

NEXT:
产能在 conditional branch，不在单条 tape 的 sell 微调。
```
