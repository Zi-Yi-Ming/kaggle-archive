# GOLD SHOT v0 — Metav4 宏路由学习（Slot-B moonshot）

日期：2026-09-27  
脚本：`_scripts/_goldshot_v0.py`  
结果：`_research/goldshot_v0.json`、`goldshot_policy.json`  
生产：Metav4 **56390446 HOLD**；**本包不提交**

## 设计（非端到端 PPO）

| 组件 | 实现 |
|---|---|
| 骨架 | 生产 **Metav4** 执行器 + chassis **41 条 route tape** |
| 宏决策点 | 与 Metav4 相同：**step≥144（day6）** 依 shop 选 route |
| 改动 | 学习策略可在 day6 **覆盖 route_id**（仅此一层） |
| 特征 | 前两 shop、YARN、money bucket、rival money、hands、rkey |
| 算法 | 表格 contextual bandit（ε=0.35 探索）；reward = 现金 WDL ±1 |
| 联赛 | Metav4 / shop_v7 / thomas / alperen / pipe16 轮换 |
| 规模 | 训练 **30** 局；评估 seeds500–503 × 双座 × 6 对手 |
| Kill gate | Slot A 或 Slot B 信号；shop 0/x → KILL |

## 训练摘要

- stats: default 22 / explore 11 / greedy_q 45 / updates 30  
- Q 状态数 **24**（特征离散后覆盖少）  
- 对局结果大量 **与 Metav4 镜像同 bank**（未覆盖到 route 或覆盖后无差）

## 评估 vs 面板（goldshot）

| 对手 | n | WR | mean margin | 对照纯 Metav4 |
|---|---:|---:|---:|---|
| **Metav4** | 8 | **0.125** | **0.0** | 镜像 0 — **无边** |
| shop_v7 | 8 | **1.0** | +4672 | 纯 Metav4 4/4 +4481 — **同级，未崩** |
| thomas | 8 | 1.0 | +2170 | 正常 |
| alperen | 8 | 1.0 | +5905 | 正常 |
| pipe16 | 8 | 0.125 | −50 | 与 Metav4 输 Pipe-16 镜像边一致 |
| kaito_v48 | 8 | 1.0 | +31759 | 正常 |

## Kill Gate

```json
{
  "wr_mv": 0.125,
  "mean_margin_mv": 0.0,
  "wr_shop": 1.0,
  "field_wr": 0.825,
  "collapses": [],
  "slot_a": false,
  "slot_b_signal": false,
  "decision": "STOP_NO_SIGNAL"
}
```

**解读**

1. 基建可用：day6 覆盖 route **技术上成立**，shop **未崩**（仍像 Metav4）。  
2. 30 局 bandit **没有学到**「偏离 Metav4 默认 route 且稳定更赚」的策略。  
3. field_wr 0.825 ≈ Metav4 打弱包，**不是新 BT 边**。  
4. 按约定 **NO GOOD SIGNAL → STOP**：不打包、不投 Slot B、不烧配额。  

### v0 证明了什么 / 没证明什么（必读）

| 问题 | v0 能否回答 |
|---|---|
| day6 + 4 特征 + tabular + **30 局** 能否超过 Metav4？ | **否 — 无信号** |
| chassis / route 覆盖接口是否可用？ | **是 — 且 shop 鲁棒** |
| hierarchical 多窗口 macro RL 是否无效？ | **不能回答** |
| 「RL 在本赛无效」？ | **不得写成此结论** |

```text
GOLDSHOT_V0
= minimal macro-bandit probe
= no signal under tiny sample / single decision node
≠ RL = FAILED
```

## 与金牌目标的关系

- 路线 **理论上** 仍对准 2960 缺口（strong backbone + learned macro）。  
- v0 **样本与动作粒度都不够**；截止前 **无 Slot-B 可交信号**。  
- 生产：**HOLD Metav4 56390446**。  

## 赛后 v1 边界（非本周）

```text
Metav4 chassis
→ macro policy @ d0/d3/d6/d9/d12/...
→ option / route transition
→ deterministic executor
→ fast simulator + large rollouts + population league
```

- 多决策窗 + 更富特征 + 数量级更大 rollout  
- offline replay warm-start  
- Slot-B 门禁 + Validation + 授权  

## 决策

```text
GOLDSHOT_V0 decision: STOP_NO_SIGNAL
含义: 极简探针无信号；赛中 moonshot 关闭；非 RL 定论
PRODUCTION: HOLD Metav4 56390446
SUBMIT: NO
```
