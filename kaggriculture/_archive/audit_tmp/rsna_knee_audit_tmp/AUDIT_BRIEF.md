# Kaggriculture 开源高分 Agent 取证审计简报（GPT 版）

日期：2026-09-06 ｜ 审计人：AtomCode（deepseek-v4-flash） ｜ 全文证据：_audit_tmp/NOTES.md
审计范围：Seyamalam/Kaggriculture、lonespear/kaggriculture、COK-ZhangZiliang/Kaggriculture 三个主 repo（全部 clone + commit history + README + 源码审计），外加 GitHub 全网搜索（307 repo）+ gh CLI 搜索 + web 搜索补充。
证据分级：CODE（源码直证）/ BENCHMARK（本地实验）/ LEADERBOARD（线上结果）/ README_CLAIM（作者声称）/ INFERENCE（代码推断）。禁止将 README claim 当 benchmark evidence。
我的生产基线：v11E（线上 942 Elo，sequential beam + ProductBelief 对手模型），当前恢复提交为纯 v11E（ref 56047543）。

---

## 1. 三个主 repo 的证据质量总览

| Repo | 最强结果 | 证据质量 | 架构 | 一句话 |
|---|---|---|---|---|
| Seyamalam | V18 公开 24-3、rating 600→2053.6；V21 corpus 94/110→100/110、live15 27/30→29/30 | LEADERBOARD（自报逐场表，内部自洽但 era 通胀）+ BENCHMARK（开放回放）+ SELF-PLAY（100 配对 seeds vs 精确 V18，2-1-97 平） | 规则式+专家选择（Hybrid） | 工程纪律最强（SHA 固定、拒绝实验留档、replay-loss 归因 harness），但 V18→V21 是同家族改进 |
| lonespear | v18 内部 league 48-2；线上 921（13-11，24 场） | league = 纯 SELF-PLAY；线上 = LEADERBOARD | 规则式自适应 | **自博弈幻觉教科书**：league 48-2 却线上落定 921，末 10 场对手均值 117,920 vs 我方 103,979 被压分；自己警告 seed 方差 54k-68k |
| COK | V10 597 局 corpus 336→339 W、0 退化 | BENCHMARK（冻结公开动作回放，半独立但非自适应；590/597 相同=弱信号） | 规则式+签名选路 | 公开态纪律最强（显式禁止 replay 查找/身份路由），机制最保守 |

## 2. 关键机制指纹（7 层浓缩）

- **Farm 路线**：A/B 均为 8 牛 6 羊家族（B：24 草莓、10 麦、2 象限、11 手；A：3 象限 12 手）；C 为多路线（V5 低 10C/4S ↔ 高 6C/12S，step-72 公开签名 + Yarn 门选路）。v11E 同 8牛6羊家族 + MELON 排程。
- **劳动力**：B 有"站立即做工"pass（站在就绪格免费行动，不被拖去远处次要任务）+ 小携带量防 shed 溢出（963 units/局丢失的审计教训）。v11E 调度器未见此 pass。
- **资本**：B 有显式价格门控现金储备（reserve = 300 + wheat_px × (动物+1) × 喂养天数——麦价上涨直接收紧买动物；replay 90323915 断粮教训）。v11E 的 _cash_needed 是平值成本模型。
- **市场**（最高优先）：A 有暴露度定向否认排序（_interference_value = 对手暴露度 × 价格，仅把对手重仓商品卖单提前、WHEAT 位保留——**不是** Fix-A 式全量前移）+ 镇消费后首步需求匹配卖；C 有镇消费前 1 步 front-run（需求模型 + 自有 action tape 目标量 + repay 防双卖）；B 是价格阈值 drip 卖（无 per-unit 定价意识）。**三者均无 v11E 的 sequential beam 流动性求值**（v11 942 vs v12 875 = 67 Elo 线上实证）。
- **对手模型**：A 有 _opponent_pipeline（公开农场→供给估计）+ 专家选择；C 有 _meta_* clone 画像 + 市场增量对手卖出推断；B **无**。**v11E 的 ProductBelief/hazard/expected-opponent-sell 是四者中最强**。
- **晚局**：A 有 V21 资本闩锁（step 577 一次性：对手−自己 ≤ −5000 → 停掉 recovery sweep；条件式非全局）+ V20 全局晚段放弃被作者拒绝（26 trace 20/0/32——全局晚段放弃伤强供给对手）；B 有末局全清算 + fill-seed（无对手差距条件）；C 有 step-718 保守补卖（投影 shed、保留既有 SELL、10-cap 感知）。v11E 无对手差距条件式策略。

## 3. v11E Differential

**公开 agent 有、v11E 没有**：
1. 暴露度定向否认排序（A1，源码在 repoA/main.py _apply_market_interference）
2. 安全小麦挤压（A2，作者默认关闭=自判不值）
3. 市场专家选择（A3，v13-v18 模式 + 日滞回）
4. 对手差距条件式晚局策略（A4，V21 闩锁概念）
5. 站立即做工劳动 pass（B1）
6. 价格门控现金储备（B2）
7. 末局 fill-seed（B3，晚生产方向，非 terminal conversion）
8. 肥料套利开链（B5，作者未测）
9. clone-profile → 农场路线切换（C2）
10. step-718 保守补卖清算（C4）

**v11E 有、公开 agent 没有**：sequential beam（流动性排序）、最强对手模型（Belief/hazard/expected-sell）、fixed-RNG 异构池实验纪律。

## 4. 自博弈偏差审计（本次审计的核心）

- **Seyamalam**：2053.6 为实赛（era 通胀）；V21 增量 = 开放回放 corpus（BENCHMARK）+ 100 配对 seeds 同家族（SELF-PLAY）；live15 实赛切片最可信但极小（仅 2 席变化）。中等偏差。
- **lonespear**：league 48-2 = 纯自博弈；线上 921 = 实赛。**"内部 league 碾压但线上被压分"就是自博弈幻觉的直接证据**。
- **COK**：冻结公开动作回放（半独立：真实公开动作但非自适应、确定性对手）。
- **我方教训（实证）**：Fix-A 本地 closer_cleo 录播 +228/局，线上 v11E+FixA = −50 Elo。**自家族录播/共享 ladder 基准系统性高估市场排序型改动。** 因此任何移植候选的验收一律要求 fixed-RNG 异构池 paired，禁止只用 self-play。

## 5. Top 10 移植候选评分（Priority = Evidence×Gain×Compat×Testability/Risk，各 0-5）

| # | 机制 | 来源 | Evid | Gain | Compat | Risk | Test | 得分 |
|---|---|---|---|---|---|---|---|---|
| 1 | 对手差距条件式晚局策略（V21 概念） | A | 3 | 2 | 3 | 3 | 5 | **30** |
| 2 | 末局 fill-seed（晚生产） | B | 2 | 2 | 3 | 2 | 4 | 24 |
| 3 | step-718 保守补卖清算 | C | 2 | 1 | 3 | 1 | 4 | 24 |
| 4 | 暴露度定向否认排序 | A | 2 | 2 | 3 | 3 | 5 | 20 |
| 5 | 肥料套利 | B | 1 | 4 | 3 | 3 | 5 | **20** |
| 6 | 站立即做工 | B | 2 | 2 | 2 | 2 | 4 | 16 |
| 7 | 价格门控现金储备 | B | 2 | 2 | 2 | 2 | 4 | 16 |
| 8 | 市场专家选择 | A | 2 | 2 | 2 | 3 | 4 | 11 |
| 9 | clone-profile 路线切换 | C | 2 | 2 | 1 | 4 | 4 | 4 |
| 10 | 安全小麦挤压 | A | 0* | 2 | 2 | 4 | 4 | 0 |

*作者默认关闭 = 自判不值得。

## 6. 推荐实验（isolated、fixed-RNG paired、异构池验收）

- **Exp 1 肥料套利（优先，上限最大）**：Phase 0 决定性测量 = 统计 v11E 每局 FERTILIZE 次数 vs COLLECT_FERTILIZER 次数 vs 期末 shed 肥料 vs 可施肥窗口覆盖率。若供应盈余且施肥不足 → **动作是瓶颈**，买肥料无效即停（lonespear FERTILIZE_PRI 平跑佐证）；若 shed 耗尽 → 供应瓶颈 → 做 BUY_PRODUCT FERTILIZER 处理臂。验收：异构池收入增益 > 支出，95% CI 不含 0，浇水覆盖不饿死。
- **Exp 2 资本闩锁**：step 577 一次性 opp−own ≤ −5000 → 关闭 premium front-run 至 719，其余精确 v11E。验收：池 CI 不含 0 + 零胜转负 + 守恒。
- **Exp 3 暴露度定向排序**：post-beam 按 _opp_est×price 排序、WHEAT 位保留、暴露阈值。风险旗标：仅在前两项干净后跑，验收含"不复现 Fix-A −50 失败模式"。
- **Exp 4 fill-seed**：按剩余天数买短周期种子填空位。验收：池 CI 不含 0。
- **Exp 5 劳动/资本微调**：先静态查 v11E 是否已有站立即做工；再测动物断粮率，罕见则跳过。
- 公共协议：engine 1.32.7、env.info["seed"] fixed-RNG、paired seeds 1-120、座次交替、ledger 守恒 + exact reconciliation、Wilson CI + paired 检验。

## 7. 最终结论

**无 A 级强移植候选。** 公开 repo 里没有"抄了就能涨 Elo"的东西；有 4 个机制值得按上述 isolated 实验研究，其中**肥料套利是唯一可能有量级级收益的方向**（lonespear 声称：若 $1 地板肥料使作物产量翻倍成立，则所有 acreage 上限都是在半产量下测的——需重测），且其决定性测量 30 分钟内可完成。禁止直接移植任何公开机制（C 级：路线切换、小麦挤压、任何全量 market-list 排序改动）。
