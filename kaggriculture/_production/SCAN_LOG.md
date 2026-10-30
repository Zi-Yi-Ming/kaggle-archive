# 每日扫描日志 — 冲牌周

门禁见 `MEDAL_PUSH_2026-09.md` §2。默认结论 `NO_GATE_PASS — no submit`。

---

## 2026-09-18 (D0)

| 候选 | 来源 | 可执行 | 指纹 | vs alperen | vs elite | 结论 |
|---|---|---|---|---|---|---|
| alperen path twin | `_push_alperen_twin/` | 是（与 alperen 同字节） | 同 alperen 族 | n/a（同策略） | n/a | **已提交** |

**今日动作:**  
- CLI 核对 last-2：原 last-2 = V16(977)+farm_v4(1982)，**alperen 被挤出**  
- 用户授权后提交路径孪生  
- kernel push v1 → `submission.tar.gz` → competition submit  
- **ref 56346424** COMPLETE publicScore **600.0**（初始分）  
- 提交后 last-2 = twin(600爬分中)+V16(977)；farm_v4/alperen 原条目掉出  
- 剩余配额 4/日  

**下一步:** 等 twin 收敛；继续扫新 elite；**不再** path 抽卡。

---

## 2026-09-19 (D1) — 状态复查 + 公开扫描

| 项 | 值 |
|---|---|
| twin 56346424 | **1851.4**（自 600 爬升） |
| V16 | 969.7 |
| last-2 team | ≈ **1851** |
| 榜顶 #1 | Majkel1337 3282 |
| 奖牌带 | ~2950+ |
| 结论 | 收敛正常；公开扫描完成静态预筛；**尚未 submit 新候选** |

### CLI 公开 notebook 扫描（votes/date/score）

高优先级已 pull → `_external/scan_20260919/`：

| notebook | agent() | 静态指纹 | 备注 |
|---|---|---|---|
| **thomastschinkel/the-2945-farm…** | Y | shop-router/V 系 + RACE/COURIER/HERD | 文案称 LB **2944.7** 全开源；与 sunil 提取字节相同 |
| sunil123kumar/top-10-public-bots | Y | 同上 | 与 thomas 提取 **同文件** |
| goodpjw melon-2749 | Y | 与 alperen jaccard≈**0.95** | 薄 overlay，novelty 门禁大概率 FAIL |
| ahmed V50 / guru gametheory | Y | shop-router 族 jaccard 0.87–0.88 | 已知族变体 |
| guru master-engine-v3 | Y | 表面差异大，待 H2H | 未证明新 family |
| alperen5252525 ×2 / pilkwang / tetsu sale-timing | **N** | 分析文，无 `agent()` | 不可直接提交 |

| 候选 | 来源 | 可执行 | 指纹 | vs alperen | vs elite | 结论 |
|---|---|---|---|---|---|---|
| thomas_2945 | public nb 2026-09-19 | 待清洗后 H2H | 公开 V39+shop-router 血统 + 独有层 | **未测** | **未测** | **HOLD — 禁止盲交**；下一步本地门禁 |
| twin 56346424 | — | — | alperen 同字节 | — | — | 爬分中 |
| 其余扫描项 | scan_20260919 | 部分 Y | 多为已知族 / 无 agent | — | — | NO_GATE_PASS |

**「暴力学榜前」结论（研究证据）:** 见对话与 P28/P31/P37/P42/P73——私有 top 无公开码；冻结 tape 迁移失败；BC/重组失败。剩余合法路径=公开近奖牌 agent **过完整门禁后再考虑提交**，不是对 top 私有策略做拟合训练。

**下一步:** 清洗 `extracted/*_clean.py` → 本地 vs alperen ≥5/8 双 seat；指纹 novelty；全过再请用户授权。**no submit now**。

### P74 本地门禁（同日续）

| 对手 | 结果 |
|---|---|
| alperen | **8/8** mean +5271 |
| R2 | **8/8** mean +8351 |
| tetsu R3 | **8/8** mean +33570 |

- twin 56346424：**1851.2**（几乎持平，仍在爬）  
- Decision: `LOCAL_GATE_PASS_PENDING_USER_AUTH`  
- farm_v4 警告：本地 8-0 alperen ≠ LB；thomas 作者自述 LB 2944.7 未验证  
- **等待用户是否授权提交 thomas_2945**；授权前 last-2 不动  

| 候选 | 结论 |
|---|---|
| thomas_2945 / sunil 同源 | **本地门禁 PASS**，待授权 |
| goodpjw / ahmed V50 / guru gametheory | 已知族高相似 — NO |
| 无 agent() 的分析 notebook | 不可提交 — NO |

### thomas 提交（用户授权：交 thomas + 预留补交 alperen）

| 项 | 值 |
|---|---|
| ref | **56358711** |
| 方式 | `kaggle competitions submit -f submission.tar.gz`（kernel `-k` 路径 400，文件上传成功） |
| status | COMPLETE |
| publicScore | **600.0**（初始分） |
| last-2 | **thomas(600) + twin(1851)**；V16 / farm_v4 / alperen 原条目均掉出 |
| team 暂 | ≈ **1851**（twin 兜底） |
| 剩余配额 | ~3 |
| 补交 alperen | **预留未执行**，触发条件见 STATUS |

**观察:** 等 thomas 从 600 收敛；对照作者宣称 2944.7 与 farm_v4「本地 8-0 ≠ LB」教训；**默认不加码提交**。

### P75 暴力扫描（同日续）

| 项 | 结果 |
|---|---|
| 批量 pull | 29/30 个公开 nb → `_external/scan_p75_mass/` |
| 哈希去重 | xuanzhang auto-top1 ≡ sunil top-10 ≡ **thomas 2945**（已交） |
|  | ahmed V45 ≡ degnonguidi cloning |
| 快筛 (seed1 双 seat vs alperen) | 多数 extract 失败/IPython/嵌套 future；可跑结果见下 |
| **goodpjw melon-2749** | seed1 **2/2** → 补满门禁 |
| yeshawang agent-evolution | 2/2 但 margin 仅 +76 → 噪声，NO |
| thomas public-state-router (旧) | 0/2 远弱于 alperen → NO |
| sovereign swarm | bank 3000 垃圾 → NO |

**goodpjw 补满门禁（seeds1–4 双 seat）**

| 对手 | 结果 | mean margin |
|---|---|---:|
| alperen | **8/8** | +4299 |
| R2 | **8/8** | +4401 |

- 指纹：与 alperen **Jaccard≈0.96**（薄 melon overlay，已知族）  
- 文案标称 [2749]，**非**新 family；farm_v4 同类风险  
- Episode 情报：twin **108** 局完成；thomas 仅 **1** 局（reward ~72k），Elo 刚开始爬  

**last-2 实时**

| ref | 名称 | publicScore |
|---|---|---:|
| 56358711 | thomas 2945 | **1108.6**（↑ from 600） |
| 56346424 | twin | **1846.6** |

Team 暂 ≈ **1847**（twin 扛）。  

**Decision pending user (暴力模式):** 是否提交 goodpjw（会挤掉 twin）/ 补交 alperen / 继续等 thomas。

### goodpjw 提交结果

| 项 | 值 |
|---|---|
| ref | **56359570** |
| status | **ERROR**（Kaggle 侧失败，无 publicScore） |
| 影响 | 可能占用 last-2 最新槽；twin 1850 已被挤出风险 |
| thomas 同时 | **1325.1** 仍在爬 |
| 剩余配额 | 2 |

**待用户确认:** 是否立刻补交 alperen / twin 抢救 last-2。

### 2026-09-19 实时 — thomas 爆分

| 项 | 值 |
|---|---|
| thomas 56358711 | **2516.0**（600→…→2516） |
| twin 56346424 | 1857.7（last-2 第二槽） |
| goodpjw 56359570 | ERROR 不计分 |
| Team ≈ | **2516** |
| thomas 已完成对局 | 26（Elo 可能未收敛完） |
| 距奖牌 ~2960 | 仍差 ~444 |
| 纪律 | **禁止**任何把 thomas 挤出 last-2 的提交 |

### 2026-09-19 晚 — 银→铜回落观察

| 项 | 值 |
|---|---|
| thomas CLI | **2620.0**（峰 2633.9，Δ≈-14） |
| 近 20 局 | **15W/4L/1T** |
| last-2 | thomas + twin **未变** |
| UI | 用户报银牌后回落铜牌 |
| 判断 | 绝对分几乎未崩；铜银更像 **相对档位/对手池**；**禁止恐慌提交** |

---

## 2026-09-20 (D2)

| 候选 | 来源 | 可执行 | 指纹 | vs alperen | vs elite | 结论 |
|---|---|---|---|---|---|---|
| | | | | | | |

---

## 2026-09-21 (D3)

| 候选 | 来源 | 可执行 | 指纹 | vs alperen | vs elite | 结论 |
|---|---|---|---|---|---|---|
| | | | | | | |

---

## 2026-09-22 (D4)

| 候选 | 来源 | 可执行 | 指纹 | vs alperen | vs elite | 结论 |
|---|---|---|---|---|---|---|
| | | | | | | |

**截止前核对:** last-2 = __________ / __________  

---

## 2026-09-23 (D5 截止)

- [ ] Submissions 页 last-2 已截图/抄录  
- [ ] 无额外提交  
- [ ] 终态写入 STATUS  
