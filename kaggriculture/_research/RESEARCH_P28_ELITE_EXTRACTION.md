# P28 — Elite Policy Extraction from R2

**Date:** 2026-09-12  
**Method:** mine R2 trajectories (seeds 1–5, pinned) → extract state/action-bundle rules → rollout on **new seeds 6–10** vs R2.  
**No tape copy. No PPO. No submit.**

---

## Decision

```text
ELITE_POLICY_LOW_TRANSFER_RATIO
```

抽取的可泛化 action-bundle policy 只达到 **R2 的 ~20% bank**。  
→ R2 的优势 **主要是 trajectory-specific**，不是几条可迁移规则。

---

## 1. 从 R2 轨迹挖到的可迁移规则

| 规则 | 证据 |
|---|---|
| **每日 dawn HIRE**（workers 过夜清空） | d1–d15 hour0 几乎必有 HIRE，hands@hour0≡0 |
| **持续 SELL**（留少量 wheat） | 全程 sell steps；d6+ 密度升高 |
| **BUY_ANIMAL 阶梯** | d1 ani=4 → d10 ani=13 → d11+ 15–17 |
| **d0 特殊** | BUY_PRODUCT/SELL，不 HIRE |
| **Worker 分布** | WATER+移动主导；CARE/FEED/HARVEST/PLANT 次之 — **无神秘 op** |

Worker 操作分布本身 **不足以解释** $150k 级差距。

---

## 2. Extracted policy（非 tape）

```text
hour==0:
  HIRE × min(10, cash-limited)
  SELL products (hold ~4 WHEAT)
  BUY_ANIMAL if under cap & cash
  BUY_SEED WHEAT if empty tiles
workers:
  existing p11 production stack (water/feed/harvest/plant)
```

State-driven；无 720-step tape；无 SHOP_PLANS。

---

## 3. 迁移评测（新 seed 6–10, pinned, vs finn）

| seed | R2 bank | Extracted | ratio |
|---:|---:|---:|---:|
| 6 | 195,587 | 34,289 | 17.5% |
| 7 | 177,490 | 35,080 | 19.8% |
| 8 | 135,732 | 33,836 | **24.9%** |
| 9 | 162,346 | 31,555 | 19.4% |
| 10 | 199,849 | 34,606 | 17.3% |

| | |
|---|---:|
| **mean ratio** | **19.8%** |
| range | 17.3%–24.9% |
| Extracted 方差 | **极低**（$32–35k） |
| R2 方差 | 高（$136–200k，真 shop-path） |

落入你预设的分支：

> **「只有 ~20–30%」→ R2 核心不是可泛化 policy，而是 trajectory-specific planning / 路径协同。**

---

## 4. 解释

抽取规则抓住了 **结构骨架**（dawn hire、持续卖、动物阶梯），但缺失：

| 缺失 | 作用 |
|---|---|
| 精确 tape 时序 | d0–d10 每步 route/sell 量 |
| SHOP_PLANS 分支 | shop-pair → 13 tails |
| Worker 路径 | V217 级走位与任务绑定 |
| 卖出窗口 | d10 melon / 后期 WOOL 等 |

与 P24/P27 一致：**不能靠拆模块或粗规则复现 R2。**

---

## 5. 对 2900 路径的含义

```text
弱 backbone + branch     → ~25k（P17.1）
弱 backbone + 规则抽取   → ~35k（P28, 20% of R2）
R2 elite trajectory      → ~160k
```

若要逼近 R2/2900，候选不再是 heuristic，而是：

1. **更大 elite corpus**（多 top-agent trajectory）  
2. **imitation + offline improvement**（在 R2 邻域用 **更细** action-bundle，且 pin harness）  
3. **真 RL / action-bundle learning**（有足够覆盖后再上）

P28 的 20% ratio 是 **负向但高信息量** 的结果：它否定了「规则提取即可泛化」。

---

## Artifacts

```text
RESEARCH_P28_ELITE_EXTRACTION.md
p28_r2_trajectories.csv
p28_r2_banks.csv
p28_extracted_policy.py
p28_extracted_eval.csv
_p28_record.py
_p28_mine_rules.py
_p28_eval.py
```
