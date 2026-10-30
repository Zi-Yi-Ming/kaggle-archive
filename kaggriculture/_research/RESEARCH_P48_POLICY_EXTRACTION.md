# P48 — Minimal Policy Extraction（Stage 1）

**日期：** 2026-09-14  
**数据：** Live R2 × 8 seeds（1,2,3,4,5,11,12,13）vs finn  
**观测：** 5,752 条 state→action  
**禁止：** 发明策略 / GA / RL / 改 R2 / submit

---

## Decision

```text
STAGE1_TRAIN_HIGH_FIDELITY_BUT_LOSO_WEAK
SHOP_KEYED_TABLE = MEMORIZATION_RISK
NOT_READY_FOR_STAGE2_EXECUTION
```

---

## 1. 训练集覆盖（in-sample）

| schema | acc | mkt | wkr | n_keys | multi_obs |
|---|---:|---:|---:|---:|---:|
| day_hour | 0.723 | 0.835 | 0.745 | 719 | **719** |
| day_hour_nshop | 0.723 | 0.835 | 0.745 | 719 | 719 |
| **day_hour_shop** | **1.000** | 1.000 | 1.000 | **5032** | **216** |
| day_hour_shop_price / money / plants / full | 1.000 | 1.000 | 1.000 | 5032 | 216 |

`day_hour_shop` 训练 100%，但 **5032 unique keys / 5752 obs**，仅 **216** 个 key 有重复。  
→ **几乎逐点记忆**，不是可泛化 policy。

`p48_coverage.csv`

---

## 2. Leave-One-Seed-Out（真·泛化）

| schema | LOSO acc | mkt | unseen |
|---|---:|---:|---:|
| **day_hour** | **0.714** | 0.830 | 0.000 |
| day_hour_nshop | 0.714 | 0.830 | 0.000 |
| day_hour_shop | **0.163** | 0.163 | **0.837** |
| day_hour_shopid_set | 0.256 | 0.258 | 0.738 |
| hour_nshop | 0.175 | 0.486 | 0.000 |
| day_nshop | 0.004 | 0.428 | 0.000 |

`p48_loso.csv`

**结论：**

- 无 shop：**~71%** 可由 (day, hour) 开环解释  
- 加 shop 字符串：held-out seed 上 **84% unseen**，acc 崩到 16%  
- **不能**把 8 seed 的 shop 表当成 R2 policy

---

## 3. multi-obs 一致性（有重复的 key）

| schema | multi_keys | mkt_acc on those obs |
|---|---:|---:|
| day_hour | 719 | 0.835 |
| day_hour_shop | 216 | **1.000** |
| day_hour_shopid_set | 503 | 0.991 |

当 **(day,hour,shop)** 在多局重复时，动作 **100% 一致**。  
→ shop 条件性 **真实存在**（与 P47 一致），但 **shop 路径几乎不重复**，无法从 8 局学到可外推的 shop 分支表。

---

## 4. 分解：解释力从哪来

```text
(day, hour) 开环底座     ≈ 71% action match
+ shop 字符串（记忆）     = 100% in-sample / 16% LOSO
重复 shop 路径上          = 100% 确定
```

unique full actions：**2074 / 5752**。  
d6–d9 的 (hour, shop) 组合在 8 局中 **几乎不共享**。

---

## 5. Stage 门禁

| Stage | 状态 |
|---|---|
| Stage1 高保真重放 observed | 训练 100% **但** LOSO 弱 → **未通过可执行提取门** |
| Stage2 extracted policy vs live R2 | **未做**（禁止用 memorization 表进环境宣称突破） |
| Stage3 simplification / overlay | **未做** |

```text
P48_STAGE1  = STAGE1_TRAIN_HIGH_FIDELITY
P48_STAGE1B = WEAK_GENERALIZATION / MEMORIZATION_RISK_HIGH
```

**STOP：** 不进入 Stage2 执行。  
若继续，需要 **更多 seed / 更粗 shop 等价类 / 其它条件变量**，而不是把 8 局 lookup 当 policy。

---

## 6. 与 P46/P47 闭合

```text
P46  frozen tape = 55% live
P47  分叉 100% 伴随 shop 差；d6/d9 高峰
P48  shop 键表可 100% 记住 8 局，但不能外推
      (day,hour) 底座 ~71%
```

Elite 产能 = **开环底座 + 高维/稀疏 shop-path 条件**；  
8 局不足以恢复可执行的低维 branch policy。

---

## 7. Production

R2 last-2 **冻结**。**无 submit。**

---

## Artifacts

```text
RESEARCH_P48_POLICY_EXTRACTION.md
p48_traces/trace_seed{1,2,3,4,5,11,12,13}.json
p48_coverage.csv
p48_loso.csv
p48_stage1_summary.json
p48_stage1b_summary.json
_p48_extract_policy.py
_p48_loso.py
```

---

## 最终输出

```text
P48 DECISION:
STAGE1_MEMORIZATION_RISK — 不进入 Stage2

TRAIN (day,hour,shop):
acc=1.000，但 keys=5032 / multi=216

LOSO (day,hour,shop):
acc=0.163，unseen=0.837

LOSO (day,hour) 开环底座:
acc=0.714

multi-obs 上 (day,hour,shop):
mkt_acc=1.000（条件性真实，但路径稀疏）

SUBMISSION:
FROZEN

NEXT:
需要更大轨迹语料或更粗条件类，才能做可泛化 policy 提取；禁止 8-seed lookup 进环境。
```
