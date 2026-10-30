# GOLD SHOT v1 — 多窗口 macro + 现金 reward（预算内）

日期：2026-09-27  
脚本：`_scripts/_goldshot_v1.py`  
结果：`_research/goldshot_v1.json`、`goldshot_v1_policy.json`  
生产：Slot A **Metav4 56390446 HOLD**；Slot B **Thomas 不主动替换**；**v1 不提交**

## 为何不是社区级 RL

| 指标 | 本机实测 | 社区参考 |
|---|---:|---:|
| env SPS | **~94–126** | ~10k（JAX / 3090） |
| 局/小时 | **~470–630** | 数万～百万级 rollout |
| 500M steps 预估 | **数周～数月** | 1–2 天量级（有 fast sim） |

参谋门槛：**Python 数十/百 SPS → 社区级 shot 算力预算不成立 → STOP。**  
v1 = **预算内**多窗口探针，**不是** 100M+ PPO。

## v1 配置

| 项 | 值 |
|---|---|
| 骨架 | Metav4 执行器 + 41-route chassis |
| 决策窗 | day **6/9/12/15/18/21**（step 144…504；day27 前） |
| 特征 | shops / YARN / 窗口 / money·hands·plants·animals buckets / rkey / wheat_inv / milk_px |
| 算法 | 表格 contextual bandit，ε=0.35 |
| Reward | **0.7·clip(Δcash/20k) + 0.3·WDL** |
| 联赛 | Metav4, shop_v7, thomas, alperen, pipe16, kaito_v48 |
| 训练 | **90 局** · 688s · q_states **66** |
| 策略用量 | default 539 / explore 201 / greedy **16** / updates 90 |

## 评估（goldshot v1 vs 面板）

| 对手 | n | WR | mean margin | 解读 |
|---|---:|---:|---:|---|
| **Metav4** | 6 | **0.0** | **0.0** | 镜像全同 — **无新边** |
| shop_v7 | 6 | 1.0 | +4521 | ≈ Metav4 基线 |
| thomas | 6 | 0.667 | +617 | 轻微波动 |
| alperen | 6 | 1.0 | +3979 | 正常 |
| pipe16 | 6 | 0.0 | −50 | 同 Metav4 输镜像边 |
| kaito_v48 | 6 | 1.0 | +21856 | 正常 |

评估时 Q 几乎未触发（特征未见过 → default route）→ **行为 ≈ 纯 Metav4**。

## Kill Gate

```json
{
  "throughput_gate": "FAIL_COMMUNITY_SCALE",
  "measured_sps_approx": 94.1,
  "decision": "STOP_NO_SIGNAL",
  "wr_mv": 0.0,
  "mean_margin_mv": 0.0,
  "wr_shop": 1.0,
  "slot_a": false,
  "slot_b_signal": false
}
```

### 精确判定（赛后复盘用语 · 禁止写成 RL=FAIL）

```text
GOLDSHOT_V1
= INFRASTRUCTURE_PASS / LEARNING_SIGNAL_UNTESTED

throughput              = FAIL   (~94 SPS ≪ 社区 ~10k)
learning coverage       = FAIL   (eval 时 Q 几乎未触发 → default ≈ Metav4)
strategy improvement    = NOT EVALUABLE
shop hetero robustness  = PASS
production candidate    = NO
```

| 结论 | 是否成立 |
|---|---|
| 社区级 100M–500M RL 本机赛前可行 | **否 — 吞吐门失败（100M≈数周）** |
| 预算内多窗口 bandit 已充分检验 learned macro | **否 — coverage FAIL，策略退化为 default** |
| shop 异构崩盘 / 架构有问题 | **否 — executor 鲁棒性 PASS** |
| 「RL / learned policy 没希望」 | **否 — 学习信号未测出 ≠ 已证伪** |
| 应提交 Gold Shot v1 | **否** |

**真正 kill reason:** 当前硬件/时间无法达到能证明 RL 有效性的样本规模；**不是**「90 局已证明学习层失败」。

## 生产决策

```text
FINAL COMPETITION FREEZE
Slot A = Metav4 56390446 · HOLD
Slot B = Thomas 56358711 · HOLD
Gold Shot v0/v1 = CLOSED
不提交 Gold Shot
赛后 v2 = fast sim + neural macro + large-scale league
```

## 赛后 v2（Gold Shot 继承资产）

已有起点（不必从零）：

```text
41-route Metav4 chassis
→ multi-window policy interface (d6…d21)
→ deterministic executor
→ league evaluator
```

v2 必须新增：**fast simulator（目标 ≫1k SPS）**、neural macro π、更大 rollout、warm-start、population。  
门禁不变：无族崩 + 异构面板 + Validation + 授权；Metav4 在候选过门前保持 Slot A。

## 产物

- `_scripts/_goldshot_v1.py`  
- `_research/goldshot_v1.json`  
- `_research/RESEARCH_GOLDSHOT_V1.md`
