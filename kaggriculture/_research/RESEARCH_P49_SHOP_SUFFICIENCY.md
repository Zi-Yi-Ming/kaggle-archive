# P49 — Shop State Sufficiency Audit

**日期：** 2026-09-14  
**数据：** 仅 P48 的 8-seed live R2 traces（5752 obs）  
**禁止：** 下载更多 replay / Stage2 / 复杂模型 / submit

---

## Decision

```text
FULL_SHOP_ID_REQUIRED_DATA_HEAVY
```

粗粒度 shop 特征 **不能** 替代完整 shop identity；  
且在 8-seed LOSO 上 **全部劣于** 纯 (day, hour) 开环底座。  
→ **coverage 是瓶颈**，不是特征工程不够巧。

---

## 1. LOSO（全部天）

| schema | acc | mkt | unseen | n_keys |
|---|---:|---:|---:|---:|
| **day_hour（基线）** | **0.714** | 0.830 | 0.00 | 719 |
| day_hour_nshop | 0.714 | 0.830 | 0.00 | 719 |
| day_hour_cat | 0.524 | 0.635 | 0.20 | 2446 |
| day_hour_price_bucket | 0.537 | 0.658 | 0.15 | 1793 |
| day_hour_price_order | 0.346 | 0.400 | 0.48 | 3640 |
| day_hour_coarse | 0.419 | 0.523 | 0.34 | 3237 |
| day_hour_coarse_px | 0.384 | 0.474 | 0.41 | 3533 |
| day_hour_full_shop | **0.163** | 0.163 | **0.837** | 5032 |

**任何粗 shop 特征都使 LOSO 变差**（key 变多、重复更少、unseen 升高）。

`p49_loso.csv`

---

## 2. 仅 d6（P47 分叉高峰）

| schema | acc | unseen | n_keys |
|---|---:|---:|---:|
| d6_hour_full_shop | **0.000** | **1.000** | 192 |
| d6_hour_coarse | 0.250 | 0.750 | 168 |
| **d6_hour_nshop** | **0.760** | **0.000** | 24 |

- 完整 shop identity：8 局 d6 **零共享**  
- 粗特征仍 75% unseen  
- 仅 **n_shops** 在 d6 上可泛化（76%）——信息量不足以单独驱动 SELL 分支

---

## 3. 假设检验

| H | 判定 |
|---|---|
| 粗 shop 特征可替代 full signature | **REJECTED** |
| 完整 shop 在 8-seed 上可泛化 | **REJECTED**（LOSO 16%） |
| (day,hour) 开环仍是最佳可泛化底座 | **SUPPORTED**（71.4%） |
| 瓶颈 = 轨迹 coverage，非算法 | **SUPPORTED** |

---

## 4. 对研究树的封口

```text
P46  frozen ≠ live（55%）
P47  shop/price 条件分叉（100% pairs）
P48  8-seed shop 表 = 记忆（LOSO 16%）
P49  粗 shop 特征更差；full id 需要大 corpus  ← HERE
```

**R2 reverse-engineering / policy extraction 路线：关闭。**

不要：更强模型、更多特征、Stage2 执行、P50 旋钮。

---

## 5. 资源结论

```text
8 seeds → 8 shop paths → insufficient coverage
继续冲分需要：更大 elite trajectory corpus
或接受 production ceiling = R2 last-2
```

**SUBMISSION FROZEN。R2 不修改。**

---

## Artifacts

```text
RESEARCH_P49_SHOP_SUFFICIENCY.md
p49_loso.csv
p49_summary.json
_p49_shop_sufficiency.py
```

---

## 最终输出

```text
P49 DECISION:
FULL_SHOP_ID_REQUIRED_DATA_HEAVY

day_hour LOSO:     0.714
best coarse:       ≤0.714（无提升）
full shop LOSO:    0.163 / unseen 0.84
d6 full shop:      0.000 / unseen 1.00

SUBMISSION:
FROZEN

NEXT:
R2 反向工程封口；瓶颈是 corpus coverage。保持 last-2，除非获得新 elite 轨迹源。
```
