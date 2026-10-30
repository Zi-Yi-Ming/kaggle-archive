# P42 — Leaderboard Replay Differential Audit

**日期：** 2026-09-14  
**Agent：** R2 path-twin（submission 56181169）  
**数据：** 30 场 live public replays，28 个不同对手  
**访问：** `REPLAY_ACCESS = OK`（Kaggle `competition_list_episodes` + `competition_episode_replay`）  
**协议：** READ ONLY；finn 不 wrap；不修改 R2；不 submit

---

## Decision

```text
P42_CLOSED → GENERATION_MECHANISM
H0_DOMINANT（无 opponent-conditioned sell repair）
```

---

## 1. 同一个 elite 面对不同 opponent 是否改变 trajectory？

**实质性：否。微噪声：是。**

| 指标 | 值 |
|---|---|
| pairs | 435 |
| sim_full mean | 0.764（min 0.22） |
| sim_0_72 | **0.980** |
| sim_0_144 | **0.990** |
| sim_mkt / sim_wkr | 0.887 / 0.803 |

早期几乎同一条 tape；后期分叉来自 **路径/shop/产量**，不是「按对手重写策略」。

---

## 2. 第一次 divergence 在第几步？

| 统计 | step | day |
|---|---:|---:|
| median | 145 | **6** |
| p10 / p90 | 24 / 359 | — |
| day 直方图 top | d1 (209), d9 (70), d6 (44), d7 (32) | |

同对手不同 seed 的 2 对：first_div day **6** 与 **12** → **seed/path 也能分叉**。

---

## 3. divergence 是否主要集中在 sell？

首次分叉类型计数：

| type | n |
|---|---:|
| **SELL** | 312 |
| MARKET_QTY | 70 |
| BUY | 40 |
| CROP | 13 |

**但** 逐商品 **首次卖出时点** 在 30 局中 **完全固定**：

| item | first_sell step | stdev |
|---|---:|---:|
| WHEAT | 1 | **0** |
| FERTILIZER | 31 | **0** |
| WOOL | 150 | **0** |
| MILK | 197 | **0** |
| MELON | 250 | **0** |
| EGG | 361 | **0** |
| STRAWBERRY | 382–383 | 0.3 |

→ 标成 SELL 的分叉是 **有无 1 单位 wheat、后期数量档位**，**不是 sell timing repair**。

典型 day1 分叉（同 seat + 同 shops）：

```text
t24  A: SELL WHEAT 1    B: []
t25+ 双方完全相同（HIRE×3, fert sell, wheat buy…）
```

---

## 4. early phase 是否稳定？

**是。** sim_0_72=0.98，sim_0_144=0.99。  
开局 wheat 卖出量恒为 13；d1 hire 恒为 0；主 schedule 锁死。

---

## 5. divergence 是否与 opponent state 相关？

**未发现。**

| 相关 | pearson |
|---|---:|
| opp_money_d5 × first_melon_sell | **0.000** |
| opp_money_d10 × first_melon_sell | **0.000** |

总卖出量只有 **2–5 个离散档**（如 MILK 仅 {8257,8278,9322,9342}），不像连续 opponent-conditioned control。

---

## 6. 能否排除 RNG / seed / environment？

**不能归因于 opponent；应归因于 seed / shop / path。**

- 30 场 **30 个不同** `env.info["seed"]`  
- 同对手不同 seed：sim_full 仅 **0.41**，first_div day 6/12  
- 同 seat + 同 early shops 仍有 ~44% 在 day1 出现 **1 单位 wheat** 微分叉  
- market 与 worker 的 first_div 几乎不同时（≤2 步内仅 10/435）→ 非单一「对手触发开关」

**Causal 归类：`State/path/shop-conditioned deterministic tape`，不是 `Opponent-identity adaptive repair`。**

---

## 7. 最终裁定

```text
P42 = CLOSED
下一阶段 = Generation Mechanism（P42-A 已部分完成）
禁止进入 Replay-conditioned trajectory repair
```

### H 判定

| H | 判定 |
|---|---|
| H0 同 elite 多对手 ≈ 同 tape | **成立（主结论）** |
| H1 固定 backbone + opponent-conditioned sell repair | **不成立** |
| H2 有分叉但对不上 opponent state | **残余成立**（seed/shop/path） |
| H3 全 tape 完全不同 | **不成立**（early 0.98+） |

---

## 回答「银牌选手」假设

> 复制前排 tape → 按对局反馈分阶段修 sell timing  

在 **R2 live 30 局** 上 **未观察到**。  
R2 的 sell **时点表是常数**；变化的是路径噪声与离散数量档，**不是** opponent-conditioned repair。

Rayk 文中的 repair（P42-A）发生在 **设计期**（下载 tape → 蒸馏 → 有界 overlay → 门禁），  
**不是** agent 在单局内根据对手自适应。

两者不要混为一谈。

---

## 与 P9–P41 关系

```text
P35  elite open-loop f(day,hour)
P36  discrete program family
P37  atomic
P42  live 30 局：无 opponent-identity sell repair  ← HERE
P42-A generation = replay mining + 门禁（设计期）
```

---

## Artifacts

```text
RESEARCH_P42_REPLAY_DIFFERENTIAL.md
_external/p42_replays/episode-*.json   (30)
_external/p42_replays/meta.json
p42_replay_corpus.csv
p42_tape_similarity.csv
p42_divergence_points.csv
p42_sell_diff.csv
p42_opponent_conditioning.csv
```

**Production：R2 last-2 冻结。不 submit。**
