# P86 — 暴力扫公开包 vs Metav4 + shop_v7 对照（无提交）

日期：2026-09-20/21  
生产：Metav4 ref 56390446 CLI **~2705–2710**（峰值 ~2792 后回落）  
脚本：`_scripts/_p86_hunt_vs_metav4_shop.py`、`_p86b_targeted_gate.py`  
结果：`_research/p86b_gate.json`、`p86c_gate.json`

## 双门禁标准（继承 P85）

| 条件 | 阈值 |
|---|---|
| vs **生产 Metav4** | 本地 WR **≥60%** 才有资格谈提交 |
| vs **shop_router v7** | WR **≥50%**，禁止 Pipe-16 式 0/x 崩盘 |
| Validation | 自对战 DONE |

## 本轮结果

| 候选 | vs Metav4 | vs shop_v7 | 判定 |
|---|---:|---:|---|
| **Ahmed V53 Opening Signature**（今日新） | **0/6**，-1.9k | **6/6**，+4.8k | **NO** — 不如 Metav4 |
| **Pipe-8 Clean Opening** | **0/6**，-5.7k | **0/6** | **NO** |
| **Pipe-15 Two Layers** | **0/4**，-2.8k | **0/4**，-16.5k | **NO** |
| **prvsiyan Soil Remembers Rain**（今日更新） | **4/4**，+78 | **0/4**，-16.8k | **NO** — 与 Pipe-16 同病：打父本小赢、打 shop 崩 |
| guru master-engine v3 | payload **≡ Metav4** | — | 同源，无增量 |
| salemali7 / Ahmed V49–V52 等 | 提取失败或 no_agent | — | 不可门禁 ≠ 更强 |
| **Pipe-16**（P85，已否决） | ~95%，+50 | **0/24+** | **NO** |

## 结论

```text
P86_NO_DUAL_PASS
HOLD last-2 = Metav4 56390446
禁止 re-roll / 禁止交未过双门禁的包
```

- 今日新公开包（V53、Pipe-8/15、prvsiyan 更新）**没有**「稳赢 Metav4 且 shop 不崩」的  
- prvsiyan +78/局与 Pipe-16 类似：**镜像小胜、异构大输** → 榜上风险高  
- Ahmed V53 **全面弱于 Metav4**，但对 shop 正常 — 仍不可替代生产包  
- 公开世界在 Metav4 之上 **尚未出现可提交替代品**

## 榜况

- Metav4 公开分从峰值 ~2792 回落到 **~2705–2710**（Elo/池波动，last-2 仍在）  
- 公榜约 **top 3%** 量级；银区相对稳，金仍看 BT + 是否出现真·更强包  

**动作：继续守 Metav4；作者/社区若再发新公开包，用同一套双门禁再扫。**
