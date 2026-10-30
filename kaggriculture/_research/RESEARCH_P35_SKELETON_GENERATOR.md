# P35 — Skeleton Compiler & Open-Loop Audit

**Date:** 2026-09-12  
**Pin harness. No RL. No submit.**

---

## Decisions

| Audit | Result |
|---|---|
| **P35-A open-loop acc** | **ALL_ELITES_OPENLOOP**（acc=1.000） |
| **P35-B skeleton causal?** | **NOT_CAUSAL_IN_THIS_IMPL** |

---

## P35-A：全部 elite 都是 open-loop tape

| Policy | bank | f(day,hour) acc | unique (day,hour) | entropy |
|---|---:|---:|---:|---:|
| R2 | 181k | **1.0000** | 719/719 | 0.000 |
| kaito_v27 | 174k | **1.0000** | 719/719 | 0.000 |
| qeinstein | 163k | **1.0000** | 719/719 | 0.000 |
| rayk_rank | 163k | **1.0000** | 719/719 | 0.000 |

**震撼结果：** 四个结构不同、bank 160k+ 的 elite，**全部**可由 `(day, hour)` 完全描述。  
→ 高分生态的主形态是 **720-step executable trajectory**，不是 reactive policy。

（仍不能证明「最优解必须 open-loop」，只证明 **这些 elite 解是**。）

---

## P35-B：Skeleton ablation

| Arm | mean bank (seeds 1–3) |
|---|---:|
| R2 tape | **183,850** |
| **skeleton (normal landmarks)** | **36,341** |
| landmark_only | 36,341 |
| **random_shift7** | **36,341** |

- Skeleton 相对我们 ~27k baseline：**略升到 ~36k**  
- **随机打乱 landmark +7 天 → 完全相同 bank**  
- landmark_only ≡ normal

### Falsification

> Phase goal / milestone schedule **在本实现中不是 causal control**。  
> 收益主要来自 p11 workers + 少量 hire/sell overlay，**不是** P34 里程碑时刻表。

P34 的 landmark 更像 **elite 结果的共同描述**，而不是可直接编译的控制变量。

---

## 与 P27–P34 合并

```text
P27  deep local basin
P28  rules 20%
P29  same-corpus BC no gain
P30  history no gain
P31  heterogeneous elites exist
P32  cross-elite market BC no gain
P33  market×worker inseparable; R2 open-loop
P34  shared phase landmarks
P35  all elites open-loop; skeleton goals ≠ R2 value  ← HERE
```

**Elite = 不同的 720-step 耦合 tape，共享粗相位，但相位标签本身造不出 tape。**

---

## 下一步含义

| 优先级 | 方向 |
|---|---|
| 高 | **从 initial env 生成完整 coupled tape**（market+workers 同源） |
| 中 | 多 seed 验证 open-loop / landmark 稳定性 |
| 低 | 继续调 phase goal 参数（random=normal 已证伪） |
| 停 | tabular BC / 手工 mutation / 堆 heuristic |

若做 generator，必须 **直接产出 step 级 coupled program**，而不是「目标 → 弱 executor」。

---

## Artifacts

```text
RESEARCH_P35_SKELETON_GENERATOR.md
p35a_openloop_acc.csv
p35_skeleton_ablation.csv
p35_skeleton/__init__.py
_p35a_openloop.py
_p35b_ablation.py
```
