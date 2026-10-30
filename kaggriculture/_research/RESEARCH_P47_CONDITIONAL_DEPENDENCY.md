# P47 — Conditional Dependency Audit

**日期：** 2026-09-14  
**对象：** Live R2，seeds 1,2,3,4,5,11,12,13（vs finn，finn 不 wrap）  
**问题：** R2 在何状态分叉？最小 sufficient state 是什么？

---

## Decision

```text
SHOP_CONDITIONED_BRANCH_SUPPORTED
```

**不是** opponent-conditioned（P42 已否），**不是**纯 cash。  
**100%** 首次分叉时 shop 序列已不同；分叉日集中在 **shop unlock 日（d6/d9）**；类型以 **SELL** 为主。

**「极小 branch 表」未证：** 8 个 seed → **8 种** (d3,d6) shop 签名。  
更像 **shop-signature → trajectory**，而非 3–5 个固定 tape。

---

## 1. Live–Live 分叉（28 pairs）

| 统计 | 值 |
|---|---|
| 全部分叉 | **28 / 28** |
| first_div 日直方图 | **d6: 17**, d7: 7, d9: 3, d24: 1 |
| 类型 | **SELL 17**, WORKER 9, BUY_HIRE 2 |
| 分叉时 state 差 | **shops 25**, **prices 25**, money 17, empty 6 |
| **shop_now_diff** | **28 / 28（100%）** |
| shop_prev_diff | 25 / 28 |
| live–live sim | mean **0.537**（0.21–0.996） |

`p47_divergence_pairs.csv`

---

## 2. Shop 签名 × bank

| seed | bank | d3 shops | d6 shops | fd vs s1 |
|---:|---:|---|---|---:|
| 1 | 181,389 | YARN_STORE | YARN+FARMERS | — |
| 2 | 169,210 | PET_CAFE | PET+ICE | 144 |
| 3 | **200,950** | SMOOTHIE | SMOOTHIE+ICE | 144 |
| 4 | 178,754 | SMOOTHIE | SMOOTHIE+FARMERS | 144 |
| 5 | 191,857 | YARN_STORE | YARN+YARN | 144 |
| 11 | **85,390** | **BAKERY** | **BAKERY+BAKERY** | 144 |
| 12 | 189,936 | ICE_CREAM | ICE+PET | 144 |
| 13 | 184,565 | SMOOTHIE | SMOOTHIE+YARN | 216 |

**8 unique shop sigs / 8 seeds。**  
BAKERY×2 → 最差路径（85k）；含 FARMERS/ICE 的路径普遍 170k+。

---

## 3. 与 Frozen majority 的关系

| seed | live bank | first_div vs frozen |
|---:|---:|---|
| 全部 8 | 85k–201k | **step 0** |

Frozen majority 与任一 live 路径从 **第 0 步** 就不同（开局 market 微差被 majority 抹平/混合）。  
→ 与 P46 一致：单条 majority tape **不是**任一 shop 路径上的 live R2。

`p47_live_vs_frozen_div.csv`

---

## 4. 假设检验

| H | 判定 |
|---|---|
| H-shop：分叉由 shop 序列条件驱动 | **SUPPORTED**（100% shop_now_diff；d6/d9 峰） |
| H-cash：仅 cash/库存驱动 | 弱（money 仅 17/28） |
| H-opp：对手 identity | 否（P42；本实验对手均为 finn） |
| H-极小 branch（≤5 tapes） | **未证 / 偏否定**（8 seed → 8 shop sig） |
| H-逐阶段条件过程 | **更符合**（d6 SELL → d7 WORKER → d9 BUY…） |

---

## 5. 模型更新

```text
R2 live:
  action[t] = π(day, hour, shops, prices, inventory, cash, workers, …)
  分叉高峰 = shop unlock 后的 market SELL
  随后 worker / hire 跟随

Frozen tape:
  action[t] = 常数表
  ≈ 某条路径的平均，≠ 任一完整 live 路径
  ≈ 55% live 产能（P46）
```

**未**要求 RL；**未**发明 branch policy；**未** submit。

若做可执行压缩，复杂度上限受 **shop 组合空间** 限制，不是 3 个开关。

---

## 6. STOP 纪律

- 未扩大为搜索  
- 未改 R2  
- **SUBMISSION FROZEN**

---

## Artifacts

```text
RESEARCH_P47_CONDITIONAL_DEPENDENCY.md
p47_divergence_pairs.csv
p47_live_vs_frozen_div.csv
p47_summary.json
_p47_conditional_audit.py
```

---

## 最终输出

```text
P47 DECISION:
SHOP_CONDITIONED_BRANCH_SUPPORTED

分叉：
28/28 pairs；高峰 d6/d9；SELL 为主；shop_now_diff 100%

极小 branch 表：
未证（8/8 unique shop sigs）

SUBMISSION:
FROZEN

NEXT:
条件变量已定位为 shop/price 路径；可执行压缩受 shop 组合空间约束，不在本阶段做 policy 搜索。
```
