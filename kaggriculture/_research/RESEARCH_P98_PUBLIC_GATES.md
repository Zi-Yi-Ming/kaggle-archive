# P98 公开新包双门（2026-09-27）

## 来源
`kaggle kernels list` 新拉：v56 / v55 / v54fork / v54leak / orderbook / pipe18 / pipe19

## 提取
- pipe18/pipe19: AGENT_B64 gzip+base64
- v55/v56/orderbook: SOURCE_BLOB/PAYLOAD = zlib + b85
- v54leak: V54_B85 = lzma + b85（cell5=V54 底座；cell6=+LAYER_SEED_FLOAT+FERT_DAY29）

## 双门（vs Metav4 / shop_v7 / thomas）— `_research/p98_dual_gates.json`

| agent | vs Metav4 | vs shop_v7 | vs thomas | 结论 |
|---|---|---|---|---|
| v56 | 75% mean **-68** | **0% -16907 崩** | 100% +2322 | **NO** shop 毒 |
| orderbook (V55+D) | 75% **+384** | **0% -16802 崩** | 100% +2410 | **NO** shop 毒 |
| v54leak base | **100% +79** | **0% -16797 崩** | 100% +3173 | **NO** shop 毒 |
| v55 / pipe18 / pipe19 | （未跑完/同族） | 预期同崩 | — | **NO** Pipe/V 族 |

### 机制
- 全是 **Pipe-16 / V25–V56 谱系**：镜像/对 Metav4 有小边，**shop_v7 0% −16k～−19k**
- 与 P88–P96 诊断一致：step0 market 单是毒点；shop 会把边吃光
- **唯一过 shop 的仍是 H3（100%）/ Fieldcraft（66.7%）/ Metav4 本身**

### 提交决策
- **不提交任何 P98 公开包**
- 不 re-roll；H3 已在爬分（600→796.3）
- 继续盯：thomastschinkel 真更新 / adaptive family（非 Pipe 换皮）/ Andrey V12 exact

## 下一步
1. 试 v54leak **叠层**（V54+seed_float+fert）— 预期仍 shop 崩，作确认
2. 若叠层也崩 → P98 关闭
3. 在 H3 终局卖出上再拧（H3+ / 更大 holdout），仍须双门
