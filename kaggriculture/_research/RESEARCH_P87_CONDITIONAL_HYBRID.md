# P87 — 原创条件层：从 Pipe-16 失败里拆出来的发明

日期：2026-09-27  
脚本：`_scripts/_p87_conditional_hybrid.py`、`_p87b_diag_and_fingerprint.py`、`_p87c_inventions.py`  
结果：`_research/p87_conditional_hybrid.json`、`p87b_diag.json`、`p87c_inventions.json`  
生产：Metav4 ref **56390446** HOLD；**不提交**

## 门禁（硬）

| 条件 | 阈值 |
|---|---|
| vs 生产 Metav4 | WR ≥ **60%** |
| vs shop_router v7 | WR ≥ **50%**（禁止 Pipe-16 式 0/x） |
| Validation 自对战 | DONE |
| 提交 | 仅用户明确授权；一次；保 Metav4 last-2 |

## P87 分层结果（seeds1–3 × 双座）

| 变体 | 改动 | vs Metav4 | vs shop_v7 | 双门 |
|---|---|---:|---:|---|
| M0 | 纯 Metav4 | 0%（镜像） | **100%** +6328 | 基线 |
| M1 | 仅 step0 `BUY_SEED WHEAT 1` | 0% −11 | **0% −21570** | **市场单刀就炸 shop** |
| M4 | 空闲手条件字段注入 | 0% +0（**未触发或无效**） | 100% +6328 | 无增益 |
| M3 | 仅 day2 晚卖 | 0% +0 | 100% +6328 | 无增益 |
| M14 | M1+M4 合体 | **100% +52** | **0% −13825** | **Pipe-16 同病** |

## 诊断：Metav4 真实动作（seed1–2）

| step | Metav4 hands | Pipe-16 hands | 解读 |
|---:|---|---|---|
| 0 | market `[BUY WHEAT20, SELL WHEAT15]` | 同 + `BUY_SEED WHEAT1` | **改 market 即毒** |
| 2 | h1=`PASS` | h1=`WEST` | 空闲手确实存在 |
| 5 | h1=`PASS` | h1=`PLANT WHEAT` | 可注入 |
| **29** | h2=**`BUILD_PASTURE`** | **hands 仅 `[CARE]`** | **牧场时间线被拆** |
| 49–57 | h0=`PASS` | walk/harvest/drop | 晚段可改 |

终局对照（seed1）：Metav4 vs shop **150127–147262**（胜）；Pipe16 vs shop **72902–82768**（负约 1 万）。  
同一 shop，Metav4 赢、Pipe-16 大输 → **伤害来自 HybridOpening 的结构改动，不是 shop 本身不可战胜**。

## 对手指纹（step48，Metav4 vs shop）

双方农场早期特征高度相似（plants/crops/animals 几乎同构，money 都很低）：  
→ **day0–2 用「像不像 Metav4」区分 shop 族不可靠**。  
市场 inventory 双方共享；可试 **ΔWHEAT** 与 shop 解锁（YARN_STORE）做开关，但样本极少。

## 发明（P87c，待门禁）

| ID | 假设 | 动作 |
|---|---|---|
| **C6 pasture-safe** | 杀死 shop 的是 day1 `BUILD_PASTURE→WATER` + 牧场重建时序 | 只动 day0–2 **空闲 h1** 种麦；**不碰** day1 牧场；day2 只 walk/water/harvest；晚卖 cap≤8 |
| **C7 mkt-fp** | step1–3 共享 ΔWHEAT 与 YARN 解锁可识别镜像 | 仅在指纹安全时启用 C6 |
| **C8 d29-stagger** | P80：末日大额同质 SELL 砸价 / 终局入账差 | step≥696 单笔 SELL cap 250 |
| **C9 / C10** | 组合 | C6+C8 / C7+C8 |

## 纪律

1. **HOLD Metav4 56390446**；Pipe-16 `_push_pipe16/` 仍 **不提交**  
2. 任何新包：双门 + holdout + 自对战 + **用户授权**  
3. 不 re-roll；研究目录 gitignore；赛后才公开 GitHub  

## P87d/e 种子探针 + 快速双门（2026-09-27）

### 探针（seed1）

| 点 | Metav4 | Pipe-16 |
|---|---|---|
| seeds.WHEAT @step0–24 | **恒 0** | step1 起 **1**（step0 BUY_SEED） |
| tile (2,4) @step48 | **PASTURE** | **PLANT WHEAT**（牧场被抢） |
| money @step24 | 11 | 1 |
| money @step48 | 100 | 81 |

结论：无麦种则 `PLANT` 空转；Pipe-16 的 +$50 **绑定** step0 买种 + 抢牧场格 + day2 重建。

### P87e 双门（seeds1–2 烟测）

| 变体 | vs Metav4 | vs shop_v7 | vs thomas | 双门 |
|---|---:|---:|---:|---|
| C0 Metav4 | 0% +0 | **100% +5797** | 100% | 基线 |
| C8 D29 cap | 0% +0（与 C0 同 bank） | 100% +5797 | 100% | **终局层无感** |
| C8b D29 front | 0% +0 | 100% | 100% | 无感 |
| C13 侧位麦 | 0% **−4685** | 0% **−23691** | 0% | **毒** |
| C14 侧位+D29 | 0% −4685 | 0% −23691 | 0% | 毒 |
| P16 对照 | **100% +50** | 0% **−16627** | 100% | 经典病 |

**无一过门。** C8 与纯 Metav4 终局 bank 相同 → 这两局 D29 大额 SELL 改写未改变入账（或父本已无 ≥400 单笔可 cap）。

### 发明结论（诚实）

1. **step0 改 market = 对 shop 即死**（M1 −21k）  
2. **不买种的字段层 = 空转**（C6/C7 钱与 Metav4 全同）  
3. **侧位种麦 + 改手路线 = 比 Pipe-16 更毒**（工人被打乱）  
4. **D29 拆单/抢卖在 Metav4 镜像上无增益**  
5. **Pipe-16 式开局边无法在「不碰 shop 毒点」的前提下复现**

→ 冲金若靠公开包再包装，概率已很低。剩余窗口应：**守 Metav4 last-2** + 盯新公开包 + 高 Elo 败局尸检（非 shop）。

## 纪律（现在）

1. **HOLD Metav4 56390446**；`_push_pipe16/`、一切 P87 变体 **不提交**  
2. 双门未过 = 不讨论交包  
3. 研究目录 gitignore；赛后 GitHub  
4. 下一步：Metav4 vs **榜顶/作者私有路径** 的公开败局；新 notebook 扫描  

## 产物

- `_research/p87_conditional_hybrid.json`
- `_research/p87b_diag.json` / `p87d_seed_probe.json`
- `_research/p87c_inventions.json` / `p87e_fast_gates.json`
- 脚本 `_scripts/_p87*.py`
