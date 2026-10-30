# Kaggle kaggriculture 冲榜现状简报（可外发参谋）

**日期:** 2026-09-27  
**截止:** 提交 2026-09-30；BT 终榜约 10-01→10-15  
**身份:** 单人账号 ZiYi-Ming；赛中研究不公开；GitHub 赛后归档  

---

## 1. 赛制（与决策相关）

- Featured 农场模拟赛；提交 agent，系统自动匹配对局。
- **每日提交配额 5**；**最终评价只看最新 2 次提交（last-2）**。
- Validation 自对战失败 → ERROR；**不进入匹配**；是否占用 last-2 名额 **未官方确认**。
- **队公开分 = last-2 中较强的 bot**。
- **奖牌/名次 = 截止后约两周 Bradley-Terry（封榜对局）**，不是瞬时 public Elo。
- 公榜奖牌 UI 为 **相对档位**（池内他人爬分会挤你），分跌 ≠ last-2 丢失。
- 重交同一策略 = **新路径约从 600 起爬**，不会继承旧 Elo。

---

## 2. 当前生产状态（CLI 实查）

| ref | 名称 | status | publicScore |
|---|---|---|---:|
| **56390446** | **Metav4 v13**（thomastschinkel 公开包） | COMPLETE | **2687.6** |
| 56359570 | goodpjw melon-2749 | **ERROR** | — |
| 56358711 | thomas 2945 farm | COMPLETE | **2411.4** |
| 56346424 | alperen path twin | COMPLETE | 1772.6 |

- **Team 分 ≈ 2688**（Metav4）。
- 金带经验线约 **2960+**（榜前部 ~2950–3100）；差距约 **+270 Elo**。
- 生产包目录: `_push_metav4_v13/`；**策略: HOLD，勿 re-roll**。
- Metav4 公开分轨迹: 曾峰 ~2792 → 现 ~2688（Elo/对手池波动，非 last-2 丢失）。

**提交纪律（执行中）:**  
无「本地双门通过 + Validation + 用户明确授权」→ **不提交**。一次最多 1 发，且交前确认 Successful 里 Metav4 仍在 last-2。

---

## 3. 双门标准（本地）

候选仅当同时满足才讨论提交：

1. vs **生产 Metav4** 胜率 **≥60%**（扩大 seed holdout 仍成立）  
2. vs **shop_router v7** 胜率 **≥50%**（禁止 Pipe-16 式 0/x 崩盘）  
3. 自对战 Validation DONE  
4. 用户明确授权  

引擎: `kaggle-environments 1.32.7`（conda env，非损坏的 MIMO_PYTHON）。  
对照基线（同 seeds）: Metav4 vs shop_v7 本地 **~100%**，mean 约 +3k～+8k。

---

## 4. 公开包扫描结论（P84–P88）

### 4.1 作者侧

- `thomastschinkel` 公开最新仍是 **Metav4 v13**（2026-09-20），**无更新包**。
- 作者榜上更新号 **56358231** 曾击败我们 thomas；**公开 kernels 无对应源码**。
- Ahmed V51/V52 文档自报 vs thomas13 约 **28/100**（弱于 Metav4）。
- Ahmed V53: vs Metav4 **0/6**，vs shop 正常 → 更弱，不能替换。

### 4.2 「高分标题」包 — 本地双门（关键）

| 公开包 | 自称 | vs Metav4 | vs shop_v7 | 判定 |
|---|---|---:|---:|---|
| haideptry **the-2965-master-hybrid-engine** | 2965 | 100% **+50** | **0% −16627** | **= Pipe-16 克隆** |
| haideptry **the-2950-peak-farm** | 2950 | 100% +50 | 0% −16627 | 同克隆 |
| **guru master-engine v4** | 统一系统 | 100% +50 | 0% −16627 | **同克隆** |
| dmitrii **one-more-wheat** | Pipe16+1天 | 100% **+78** | 0% **−16797** | 边更大、毒更深 |
| nathanjacob **Pipe-16** | 50-0 vs Metav4 | ~92–100% +50 | 0% −16k | 镜像毒药 |
| haideptry countering/demystifying | 反 meta | **0% −3105** | 100% +5k | 输 Metav4 |
| shiiin9 beat-v48 | V48+层 | 0% −6200 | ~50% | 输 Metav4/thomas |
| kenanzhang a1-t31-guard | A1+预留 | 0% −7580 | 0% −2550 | 全面弱 |

**验证方法:** 从 notebook 提取 agent 后，与 `_push_pipe16/main.py` 对局 **逐 seed 终局 bank 完全一致**（例 seed1: 149878 vs Metav4 149828；vs shop 72902–82768）。  
→ 榜面「2965/2950」**不是新机制**，是 HybridOpening 谱系换皮；公开分高 ≠ 本地可加载优势。

### 4.3 公开世界结构判断

- 赛中可加载公开策略 **卡在局部最优**: 「Metav4 + 开局空闲工人 HybridOpening」。
- 该边: **镜像/父本 +$50/局**；**异构 shop-router 族 −$10k～−$16k/局**。
- 能稳赢 shop 的包 **打不过 Metav4**；能赢 Metav4 的包 **崩 shop**。
- **截至 2026-09-27，无一公开可加载候选通过双门。**

---

## 5. 原创/自研实验（P87–P91，全部未提交）

### 5.1 机制诊断（关键事实）

对 Metav4 生产包本地探针（seed1–2）:

| 点 | Metav4 | Pipe-16 |
|---|---|---|
| `seeds.WHEAT` @step0–24 | **恒 0** | step1 起为 1（step0 `BUY_SEED`） |
| 格子 (2,4) / tiles[4][2] @day2 | **PASTURE**（未来牧场） | **PLANT WHEAT**（牧场被占） |
| day1 (step24) money | **~11**（现金极紧） | ~1 |
| step0 market | `[BUY_PRODUCT WHEAT 20, SELL WHEAT 15]` | 同上 + `BUY_SEED WHEAT 1` |
| day1 hand2 | **BUILD_PASTURE** | Hybrid 改写后时间线被拆 |

结论:  
1. **不买麦种 → PLANT 空转**（字段层钱与 Metav4 全同）。  
2. Pipe-16 的 +$50 **绑定** step0 市场单 + 抢牧场格 + day2 重建。  
3. **仅 step0 加 BUY_SEED**（无字段改动）vs shop 已可到 **−21k**。  
4. 对手农场 day0–2 特征与 Metav4 高度相似 → **早期「像不像 Metav4」指纹不可靠**。

### 5.2 自研变体双门摘要

| ID | 机制 | vs Metav4 | vs shop_v7 | 结论 |
|---|---|---:|---:|---|
| P87 M1 | 仅 step0 买麦种 | 0% −11 | **0% −21570** | 市场毒点 |
| P87 M14 / Pipe-16 | 完整 Hybrid | 100% +50 | 0% −16k | 经典病 |
| P87 C6/C7 | 不买种字段 / 指纹开关 | = Metav4 全同 | 100% | 空转 |
| P87 C13 | 侧位种麦+改手 | 0% −4685 | 0% −23691 | 比 Pipe-16 更毒 |
| P87 C8 D29 | 末日大单限卖 | = Metav4 | 100% | 无感 |
| P89 A1 | 中盘空闲手种麦 | **0% −17109** | 50% | PASS≠免费劳力 |
| P89 A2/E1/E2 | 对手成熟产量限卖 | 0～−26 | 100% | 微层空转或微亏 |
| P90 T1 | **tape 感知**（未来3步也是 PASS 才注入） | 0% −1624 | 50% | 仍伤相位 |
| P90 F7 | `V9_FERT_FIRST_DAY` 14→10 | 烟测 100% +20 | 100% | **holdout 50% −15** |
| P91 F7 wide seeds7–12 | 同上扩大 | **33% −4** | 100% | **假阳性确认** |
| P91 W3 | F7+终局分批卖 | 66.7% **mean −37** | 100% | 胜率虚高，不可交 |
| P90 F9/F10 | RACE 阈值突变 | holdout **25%** | 100% | 镜像上回归 |

**P87–P91 + P88 公开扫描: 无一同时满足「稳定正边 vs Metav4 + shop 不崩 + holdout」。**

---

## 6. 交包赌局分析（供外部参谋）

### 候选 A: 交 Pipe-16 谱系（2965/guru v4/one-more-wheat）

| 项 | 评估 |
|---|---|
| 本地 vs Metav4 | +50～+78/局，胜率高 — **仅镜像/父本** |
| 本地 vs shop_v7 | **0%，−16k** — 异构系统性崩盘 |
| 换算 Elo | +$50/局通常 **远小于 +270**；冲金不够 |
| 榜路径 | 新号从 600 爬，截止前约 2–3 天，难超 2688 |
| last-2 影响 | 预期挤掉 **thomas 2411**；Metav4 应作地板（**前提 ERROR 不占槽**） |
| BT 终榜 | last-2 两 bot 都打；Pipe-16 遇异构可能大量负场 |
| 历史 | farm_v4 本地 8–0 → 榜上 ~1980（本地≠榜） |
| **建议** | **不值得**；冲金增量极低，仍有挤掉弱槽/占槽风险 |

### 候选 B: 交 F7 / W3 / 其他自研

- holdout 已否或 mean 为负 → **无赌的资格**。

### 候选 C: HOLD Metav4

| 项 | 评估 |
|---|---|
| 队分 | ~2688，银区量级（UI 相对档位） |
| BT | Metav4 仍可对局；不引入毒包 |
| 风险 | 金无望（公开无过门包）；分数可上可下 |
| **建议** | **默认策略** |

### 何时才值得赌一次（需用户明确授权）

1. Successful 页确认交后 **Metav4 仍在 last-2**  
2. 本地 vs Metav4 **≥60% 且 mean 明显高于 +50**（非噪声）  
3. vs shop_v7 **≥50%**  
4. Validation 通过  
5. 接受「即使全过，3 天内大概率仍到不了金」  

**当前候选均不满足 2+3。**

---

## 7. 请外部参谋回答的问题

1. 在「BT 只认 last-2、队分取 max、ERROR 占槽未知」下，**交 Pipe-16 谱系的 EV 是否仍为负**？  
2. 若 BT 对 last-2 两 bot **分别计分再取队最优**，弱第二槽是否几乎无害？是否改变结论？  
3. 截止前 2–3 天，是否存在 **不依赖 shop 毒点** 且可能 > Metav4 的公开机制（我们漏掉的）？  
4. 金带 ~2960 在本池是否 **只有私有自适应 agent** 才能稳定到达？  
5. HOLD 下，公开分 2688 封榜 BT **银区是否稳**？相对 UI 奖牌如何理解？  
6. 有没有 **第二槽专用** 策略：保留 Metav4，用配额交一个「对 Metav4 小亏但对异构不崩」的 bot 抬高 max？现有公开包似乎都不满足。

---

## 8. 我们已排除的方向（避免重复建议）

- 盲交公开高分标题包（2965 等）— 已克隆验证  
- 开局 Hybrid / 买种 / 抢牧场 / 侧位麦 / 中盘闲置劳力 — 双门全灭  
- 仅改 Metav4 常量（施肥/RACE/HERD/COURIER/feed）— 烟测假阳性，扩大无边  
- 终局大单 cap / 价格分批卖 — 镜像 bank 无感或 mean 为负  
- 早期对手指纹开 Hybrid — day0–2 特征不可分  
- 重交 Metav4 同包 — 只会从 600 爬，毁路径  

---

## 9. 产物路径（本地，赛中不公开）

- 生产状态: `kaggriculture/_production/STATUS.md`  
- 公开扫描: `_research/RESEARCH_P88_NEW_PUBLIC_HUNT.md`  
- 自研: `RESEARCH_P87_CONDITIONAL_HYBRID.md` / `P89_SELF_INVENT` / `P90_FLAGS` / `P91_F7_TERMINAL`  
- 结果 JSON: `p88c_clean_gates.json` / `p89_self_invent.json` / `p90_flags.json` / `p91_f7_terminal.json`  

---

## 11. 外部参谋后复核脚注（2026-09-27 追加）

### 11.1 官方第二槽机制（接受）

- Team score = last-2 **更好 bot**；第二槽 = hedge，**无 downside**（Kaggle discussion）。  
- 因此 Slot-B 门禁 **不必**要求候选直接打赢 Metav4。  
- 更新后的 Slot-B：新 lineage、Validation、**无 0/x 族崩**、≥4 异构对手、local BT proxy 不显著差、有独立证据。

### 11.2 Kaito v43 定点复核（reopen trigger → 关闭）

| 项 | 结果 |
|---|---|
| Artifact | `public_nb/kaito_v43/main.py` SHA **=** notebook manifest（exact） |
| 公开声称 | public/best **2882** |
| vs Metav4 | **0/6，mean −23604** |
| vs shop_v7 | **0/6，mean −22422** |
| vs thomas / alperen / pipe16 | **全部 0/x**（−26k 量级） |
| Slot A | **FAIL** |
| Slot-B collapse | **FAIL**（全面板 0/x） |

结论: **公开 2882 不能转化为该 executable 在我们异构面板上的强度**；与 farm_v4 同类「本地/公开错位」。  
**不投 Kaito v43**；HOLD Metav4。

### 11.3 生产裁决（合并参谋意见）

```text
Metav4 HOLD
Pipe-16 谱系不投
Kaito v43 不投（复核已做）
第二槽按 hedge 逻辑保留，但当前无合格 Slot-B 候选
不重开自研 P92–P100；只对「真正新外部证据」做定点双门
```

---

## 10. 一句话现状

**生产 = Metav4 2687.6，HOLD；公开与自研均未过双门；默认不赌；若外部认为 BT/max 机制下弱第二槽无害且存在未扫到的 shop-safe 强包，欢迎指出具体机制与验证方案。**

**（脚注后）Kaito v43 已按参谋要求 exact 复核：不过门，不投。第二槽 hedge 机制已写入门禁；仍无合格候选。**

### 11.4 P92b 第二轮点名复核（2026-09-27）

| 候选 | Artifact | vs Metav4 | vs shop_v7 | Slot |
|---|---|---:|---:|---|
| **Kaito v48 Fast Routes** | SHA `dadee25a…`=manifest | **0/6 −23600** | **0/6 −22417** | **FAIL** |
| Andrey Breaking the Tie | V12 **API 403**；实测 V21-R1 bootstrap SHA `c6f96a85…` | 0/6 −35788 | 0/6 −33579 | **FAIL**（且非 2883 包） |

- v48 略胜 v43（+1673），但仍被 Metav4/shop/thomas/alperen 全面碾压 → **同属被生产血统压制**  
- 公开 Best（3009/2882/2883）与本地异构面板强度 **系统性脱节**  
- **按约定：HOLD Metav4；不再无限扫 kernel**  
- 除非外部提供 **V12 的 exact main.py 字节**（API 拉不到），否则 Breaking the Tie 线关闭  

**生产裁决（终）:** `HOLD Metav4 56390446`；不投任何 P92/P92b 候选。


