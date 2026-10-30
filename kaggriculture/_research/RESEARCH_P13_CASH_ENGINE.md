# P13 — R2 Cash Engine Ledger

**Date:** 2026-09-12  
**Method:** per-step engine money path + action-correlated events  
**Identity:** `init + ΣΔ = final` **closed (err = 0.00)** on all 4 traced games  
**No agent changes. No submit.**

---

## Decision

```text
CASH_ENGINE_IDENTIFIED
```

R2 **d7–d10** 现金尖峰（尤其 d10 单日 +$27.5k net / +$35.6k sale）主要来自：

> **MELON 在 d10 集中收获并按 $230–266/个 卖出（qty≈120，收入 ≈$30k）**

不是 routing、不是 mystery engine reward、不是 advance-sale 魔法。

---

## Accounting identity

| Game | init | final | inflow | outflow | id_err |
|---|---:|---:|---:|---:|---:|
| R2 s1 | 3000 | 148,448 | 164,276 | −18,828 | **0.00** |
| B s1 | 3000 | 116 | 16,048 | −18,932 | **0.00** |
| R2 s2 | 3000 | 108,389 | 122,935 | −17,546 | **0.00** |
| B s2 | 3000 | 4,321 | 24,814 | −23,493 | **0.00** |

Instrumentation 完整，可以解释战略。

---

## Day waterfall（净现金流 / 销售额）

| Day | R2 net | R2 cash | R2 sale$ | B net | B cash | B sale$ |
|---:|---:|---:|---:|---:|---:|---:|
| 0–5 | small | ~$800 | 1–1.5k/day | small | ~$900 | 0–1k |
| 6 | +126 | 863 | **6,553** | −1,307 | 311 | 862 |
| 7 | −566 | 711 | 2,384 | +439 | 532 | 890 |
| 8 | +1,850 | 1,753 | 6,619 | +1,678 | 1,284 | 5,293 |
| 9 | +2,281 | 2,785 | 5,962 | −2,164 | 488 | 1,227 |
| **10** | **+27,559** | **17,115** | **35,594** | +1,257 | 937 | 4,032 |
| 11–15 | +5～14k/day | 34k | 10–80k/day | ~0–1k | ~1–2k | 2–3k |

**第一次大额不可逆差距在 d10。**

---

## d7–d10 最大正现金流（R2）

| step | Δcash | 事件 |
|---:|---:|---|
| s250 d10h10 | **+6,263** | SALE **MELON 24 @ $266** (+FERT 5) |
| s251 d10h11 | **+2,927** | SALE **MELON 12 @ $246** |
| s258 d10h18 | +1,700 | SALE MILK 9 @ $195 |
| s224 d9h8 | +1,583 | SALE WOOL 8 @ $200 |
| s253 d10h13 | +1,406 | SALE **MELON 6 @ $236** |
| s255 d10h15 | +1,357 | SALE **MELON 6 @ $232** |
| s252 d10h12 | +1,247 | SALE **MELON 6 @ $240** |

**+$14k 不是一笔，是 d10 上多笔 MELON 卖出累积。**

B 同期最大单笔只有 ~$1.8k（MILK+FERT），**零 MELON**。

---

## Product revenue

### d7–d10

| | R2 qty | R2 $ | B qty | B $ |
|---|---:|---:|---:|---:|
| **MELON** | **120** | **30,432** | **0** | **0** |
| MILK | 45 | 8,178 | 39 | 6,582 |
| FERTILIZER | 83 | 7,139 | 42 | 3,574 |
| WOOL | 20 | 4,302 | 0 | 0 |
| WHEAT | 14 | 508 | 36 | 1,286 |

### d11–15（复利段）

| | R2 qty | R2 $ | B $ |
|---|---:|---:|---:|
| **WOOL** | **846** | **200,131** | 0 |
| FERT | 156 | 11,311 | 3,814 |
| MILK | 111 | 10,272 | 7,128 |

d10 尖峰 = **MELON**；d11+ 雪崩 = **WOOL**。

---

## Event-type contribution d7–d10

| | R2 $ | B $ |
|---|---:|---:|
| SALE | **+50,559** | +11,442 |
| PRODUCT_BUY | −7,435 | −2,474 |
| ANIMAL_BUY | −7,400 | −3,800 |
| SEED_BUY | −1,920 | −1,000 |
| HIRE | −835 | −548 |
| RESIDUAL | −1,845 | −410 |
| **NET** | **+31,124** | **+1,210** |

二分：**Revenue hypothesis 成立**。Non-sales income 可忽略（residual 小且为负=估计误差）。

---

## Advance sale？

**不需要 advance-sale 才能解释 d10。**  
MELON 是真实库存卖出：`first_yield_day=10`，s249 起卖，与引擎时序一致。  
（R2 tape 里有 advance_sales 机制，但 **d10 尖峰的 $ 用普通 SELL 即可闭合。**）

---

## Phase 14 分类

| Case | 判定 |
|---|---|
| A 只是生产更多 | **部分** — B 没有 MELON/WOOL 产量 |
| B 变现更快 | 次要 — B 有 MILK/FERT 也在卖 |
| C advance / projected | **非 d10 主因** |
| D 特殊 engine 事件 | **否** |
| E 多因子 | d11+ WOOL 叠加，但 d10 可单因子解释 |

**d7–d10：Case A（MELON 生产/收获政策）为主。**

---

## 与 P12 衔接

```text
P12: routing 不是那 $14k
P13: 那 $14k ≈ d10 MELON 集中变现 (~$30k sale in window)
      + 同期 MILK/WOOL/FERT 辅助
之后 d11+: WOOL 成为主引擎
```

B 的 planner **从未种/收/卖 MELON**（cash crop 偏好 + 种子/地/工人未导向 melon）。

---

## Parity check（Phase 10）

| Q | A |
|---|---|
| B 能否触发同一 SALE MELON 事件？ | 能（引擎通用） |
| 为何没触发？ | **没种出 MELON** → shed 无货 |
| planner 不知道 / executor 不支持 / state 未到？ | **planner 生产配置未导向 melon d0 种 d10 收** |
| 是否依赖 R2 固定 trajectory？ | 时序依赖种植日；机制本身 state-driven 可复现 |

---

## Decision

```text
CASH_ENGINE_IDENTIFIED
```

**本轮不改 B、不提交、不进 R17。**

下一轮（若开）最小 counterfactual：  
仅在 B 中加入「d0–d2 种植 MELON 目标 + d10 收获卖出」— 单变量，对照 d10 cash。

---

## Artifacts

```text
RESEARCH_P13_CASH_ENGINE.md
p13_cash_ledger.csv
p13_cash_ledger_meta.csv
p13_cash_waterfall.csv
p13_r2_b_gap.csv
p13_revenue_by_product.csv
p13_event_contributions.csv
_p13_ledger.py
_p13_analyze.py
```
