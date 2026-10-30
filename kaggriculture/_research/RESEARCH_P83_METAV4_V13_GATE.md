# P83 — 发现 Metav4 v13（门禁通过，待授权提交）

日期：2026-09-26  
来源：`kaggle kernels pull thomastschinkel/the-metav4-farm-submission-v13`  
包：`_external/scan_p83_metav4/metav4_v13_main.py`（1,004,288 bytes）  
SHA256：`9d63494603f88219…`（与 notebook 自述一致）  
结果：`_research/p83_metav4_gate.json`、`p83_metav4_full_panel.json`

## 当时 Thomas 是怎么发现的（P74）

1. 公开 notebook 扫描（作者 thomastschinkel「The 2945 Farm」）  
2. 提取 `agent()`，本地门禁 vs alperen / R2 / tetsu **各 8/8**  
3. 与 farm_v4 对照后 **你授权提交** → last-2 爬到 ~2673/2634 银  
4. 同字节 sunil top-10 ≡ thomas；goodpjw 等薄皮/ERROR 被否  

**同一套路径**今天扫到了作者 **09-20 新公开包 Metav4 v13**。

## Metav4 v13 自述（notebook）

- 对 **2945 champion (v9/4)**：**40–0**，mean +$798/局  
- 相对 v_gate：+8/−2  
- 改动：Fibonacci 雇工跳过、CARROT2 feed 2→1、施肥提前到 day14、Metav4 1200 局 replay 预测卖表等  
- **自述强于 2945**，与我们本地结果一致  

## 本地门禁（钉种子，双 seat，finn 不 wrap）

| 对手 | 局数 | 胜率 | mean margin |
|---|---:|---:|---:|
| **生产 thomas**（seeds1–4） | 8/8 | **100%** | **+2447** |
| **生产 thomas holdout**（seeds5–8） | 8/8 | **100%** | **+1850** |
| alperen | 8/8 | 100% | +5239 |
| R2 | 8/8 | 100% | +8029 |
| tetsu_r3 | 8/8 | 100% | +33613 |
| shop_router_v7 | 8/8 | 100% | +4952 |
| prvsiyan | 8/8 | 100% | +8029 |
| **自对战 Validation** | DONE/DONE | — | 双方 bank 91843 |

**门禁判定：`LOCAL_GATE_PASS`（vs 生产 thomas 16/16）**  
→ 满足「本地明确强于当前生产包 + 自对战可跑」；**是否上榜冲金仍需你授权 + 接受 path/LB 风险**。

## last-2 算术（若你授权交 1 次）

当前 CLI：thomas **2634** + twin 1771；goodpjw ERROR。

| 假设 | 提交 Metav4 后 |
|---|---|
| ERROR 不占有效槽 | last-2 = **[Metav4, thomas@2634]**，twin 出局；队分 = max(爬分, 2634) |
| ERROR 占「最近2次」名额 | last-2 = **[Metav4, goodpjw]** → **thomas 掉出**（风险） |

**建议：** 提交前你打开 Submissions → Successful，确认计分 last-2 仍是 thomas + twin。  
若确认 → **交 1 次 Metav4 可保留 thomas 在 last-2 作保险**，twin 换成更强候选。  
若不确定 ERROR 占坑 → **先别交**，或你截图给我再判。

## 风险（必须知情）

- 新 path 从 **~600** 起爬；本地 16/16 ≠ 榜上必超 2634（farm_v4 教训）  
- 但与 farm_v4 不同：这次 **打赢的是你场上生产包 thomas**，不是只赢 alperen  
- 作者公开宣称对 2945 全胜；与本地一致  
- 每日配额有限；若 Validation 失败会 ERROR（本地自对战已 DONE）  
- **不授权则不动 last-2**

## 决策状态

```text
METAV4_LOCAL_GATE_PASS
AWAITING_USER_SUBMIT_AUTH
production thomas still FROZEN (do not overwrite package dir)
```

---

## P83b 加压门禁（2026-09-26）

结果文件：`_research/p83b_metav4_stress.json`

| 对手 | 局数 | 胜率 | mean margin |
|---|---:|---:|---:|
| thomas seeds1–8（复测） | 16/16 | **100%** | +2149 |
| **thomas seeds9–20** | 19/24 | **79.2%** | +751 |
| **vs thomas 合计（20 unique seeds）** | **35/40** | **87.5%** | ~+1400 |
| metav4 镜像自战 | 多平 | — | path 噪声 |
| thomas_no_race | 8/8 | 100% | +2311 |
| yhay81-0913 | 8/8 | 100% | +12590 |
| evgendvorkin | 8/8 | 100% | +4588 |
| salemali7 加载失败 | — | — | — |

seeds9–20 败局：s12/s13/s16 等，margin **-463~-1113**，非崩盘；综合 **87.5% vs 生产 thomas**，仍高于门禁 60%。

**加压结论：`METAV4_GATE_PASS_STRESS`** — 本地证据链完整；是否冲榜仍取决于你是否授权提交 + 接受 path/LB 方差。

---

## P83c 更多局数（seeds 1–50 汇总 vs 生产 thomas）

| 批次 | 局数 | 胜 | 胜率 | mean margin |
|---|---:|---:|---:|---:|
| seeds1–8 | 16 | 16 | 100% | +2149 |
| seeds9–20 | 24 | 19 | 79.2% | +751 |
| **seeds21–40** | 40 | 39 | **97.5%** | +1615 |
| seeds41–50 | 20 | 11 | **55.0%** | +780 |
| **合计** | **100** | **85** | **85.0%** | ~+1300 |

公开对手 seeds5–8：alperen / R2 / shop / prvsiyan / yhay81 / evgendvorkin **全部 8/8**。

**综合判定：`METAV4_LOCAL_PASS_85pct_VS_THOMAS`**  
- 门禁（≥60% vs thomas + Validation 过 + 公开面板全胜）→ **通过**  
- seeds41–50 有回落（55%），说明 **非必胜**，仍有 path/池方差  
- 与 farm_v4 差异：这次对象是 **你场上生产包 thomas**，不是只赢 alperen  

**提交仍待你明确授权；未授权则 last-2 不动。**
