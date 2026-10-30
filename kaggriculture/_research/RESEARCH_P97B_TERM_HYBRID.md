# P97b — 原创：Metav4 + 终局收割/抢先卖（首次过双门）

日期：2026-09-27  
脚本：`_scripts/_p97_daygap.py`、`_p97b_term_hybrid.py`、`_p97c_expand.py`  
结果：`_research/p97_daygap_fieldcraft.json`、`p97b_term_hybrid.json`、`p97c_expand.json`

## 1. 日账 autopsy（Fieldcraft vs Metav4）

胜负在 **day26–29（step 624–718）**，不是开局：

| seed | day26 gap | day27–28 | 终局 |
|---:|---:|---:|---:|
| 1（FC 胜） | −3340→**−10700** | **+5019** / −9481 | **+6278** |
| 2（FC 负） | −5257 | −6399 / −5478 | **−4925** |
| 7（FC 胜） | −1561 | +326 / −2028 | **+546** |

→ 原创层只动 **day24+ 市场卖出**，不碰 step0 / 牧场 / 工人。

## 2. 发明变体（Metav4 底座薄包装）

| ID | 机制 |
|---|---|
| H1 term_cap | day26+ 单笔现金品 SELL cap 80（防砸价） |
| H2 term_advance | day24–28 现金品提前卖 min(stock,40)（LEAD 思想） |
| **H3 term_greedy** | **day27+ 余量现金品 SELL min(stock,60)**，不动 WHEAT/FERT |
| **H4 combo** | H1+H2+H3 |

## 3. 双门 + holdout

| 变体 | vs Metav4 smoke | holdout | vs shop | shop_h | 双门 |
|---|---:|---:|---:|---:|---|
| H0 Metav4 | 0% +0 | — | 100% +5797 | — | 基线 |
| H1 | = Metav4 全同 | — | 100% | — | 无感 |
| H2 | 66.7% +23 | 75% +40 | 100% | 100% | 弱过 |
| **H3** | **100% +432** | **75% +175** | **100% +5052** | **100% +2002** | **PASS** |
| **H4** | 66.7% +116 | **100% +245** | 100% +4606 | 100% +1568 | **PASS** |

**H3** 镜像边更大；**H4** holdout 8/8 更稳。扩大 seeds8–13 见 `p97c_expand.json`。

## 4. 含义

- **不是**公开包换皮：机制来自 Fieldcraft 胜局日账 → 自研薄层 → 双门  
- shop **未崩**（仍 ~100%）——避开 Pipe-16 毒点  
- 边幅约 **+$100~400/局** 量级，不是 +300 Elo 金牌保证  
- **Slot A**（替换 Metav4）候选：H3/H4 扩大复验仍稳则可谈  
- **Slot B** 也可（team=max，Metav4 作地板）  
- **9/24 前最多 1 发**，需用户明确授权  

## 5. 纪律

扩大复验过门 + Validation + **用户授权** 前 **不提交**。  
禁止 re-roll 现有 last-2（Fieldcraft + Metav4）。
