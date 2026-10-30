# Kaggriculture Research Final — P9–P40

**日期：** 2026-09-14  
**Production：** R2 锁定，#1476 / 8955，**2012.7 Elo**  
**研究状态：** 反向工程 / 规则合成路线 **封闭**

---

## 一句话结论

> 在当前可构造的 program family 与搜索预算下，elite **不能**通过局部规则组合、模块迁移、离散旋钮枚举或从零规则合成逐渐逼近。  
> 已观察到的 elite 更符合 **完整、原子化的 720-step coupled open-loop trajectory/program**。  
> （**不是**「已证明全局最优一定是 open-loop tape」——证据只覆盖我们试过的路径。）

---

## 线上事实

| Slot | Agent | Elo |
|---|---|---:|
| 1 | R2 path-twin | **2012.7** |
| 2 | R2 | 1997.7 |

- path 效应仅 +15 Elo → R2 水平稳定，不是对手运气  
- Top10% ~2407（差 ~395）；奖牌区 ~2960（差 ~947）  
- **无 ≥5/8 本地门禁候选 → 不 submit**

---

## 排除链（P9–P40）

```text
P9–P15   planner / resource / portfolio          → 无法接近 elite
P16–P23  branch / retrieval / value surface      → 无稳定突破
P24–P27  local mutation                          → R2 为 deep basin
P28–P30  extraction / imitation / history        → 价值不可迁移
P31–P32  heterogeneous elite corpus + BC         → 当前 action 抽象下仍失败
P33      market × worker 强耦合                  → 不可拆
P34–P35  phase landmarks                         → 可描述，无 causal 迁移价值
P36      trajectory space 离散 family-like       → 非连续局部空间
P37      elite tape recombination                → ATOMIC_PROGRAM
P38      market grammar + p11 workers            → max 21k < p11 26k
P39      worker tape / market tape 独立迁移      → 5–329 / 0
P40      从零 coupled program ×500               → max 44，0×≥100k  HARD STOP
```

### 关键数字锚点

| 范式 | max bank (pinned, vs finn) |
|---|---:|
| R2 mean3 | **183,850** |
| p11 baseline | 26,725 |
| P38 grammar + p11 | 21,089 |
| P39 elite worker + weak mkt | 5–329 |
| P40 从零 coupled | **44** |

Harness 红线（P38/P39）：  
`env.info["seed"]` 固定；**finn 永不 wrap**（错误 arity 会把 R2 从 181k 打到 148k）。

---

## 已证明 / 未证明

**已证明（在我们的操作空间内）**

1. Elite 是异构的 program family（P31），不是单一规则的微扰  
2. Market 与 worker 不可分（P33）；完整 tape 回放 delta=0（P39）  
3. 重组、拆层、BC、skeleton、mutation、grammar、worker-first 合成均无法进入 100k+  
4. R2 是 deep local basin 与可靠 production baseline  

**未证明**

- 全局最优策略「一定」是 open-loop tape  
- 不存在我们未构造的 program family  
- 轨迹搜索 / 新外部 elite 一定无效  

---

## 唯一值得重开研究的条件

```text
新的完整 elite trajectory（非 R2 同源）
        ↓
识别其 program family
        ↓
找到 generation mechanism
        ↓
生成第五个异构 elite
        ↓
本地 ≥5/8 vs R2 + mean≥150k + novelty
        ↓
才考虑 Kaggle
```

**不要开 P41 旋钮实验。**

---

## 项目定性（三者可同时成立）

| 层面 | 结论 |
|---|---|
| 研究 | **成功封版** — 40 步排除了错误搜索空间 |
| 比赛 | Production ceiling ≈ R2，~2000 Elo / top 16.5% |
| 突破 | **未解决** — 需要新 trajectory / 外部 elite / 另一阶段问题 |

---

## 产物索引

```text
_push_medal/main.py              R2 production champion
RESEARCH_P9 … P40_*.md           分阶段报告
elite_corpus/                    四 elite 轨迹与 banks
p26_harness.py                   pin 协议
p39_worker_tape/harness.py       tape 录制/回放（finn 不 wrap）
p40_stage1.csv                   封版实验数据
```

**研究序列结束。R2 锁定。不 submit。**
