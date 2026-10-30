# Session notes

## [2026-09-27 · H3 过门待授权]

- H3 扩大 80%/+369 vs Metav4、shop 不崩；路径拼错已修；未提交

## [2026-09-27 · P97b 过双门]

- H3/H4 终局杂交 smoke+holdout 过；扩大中；待授权提交

## [2026-09-27 · 铜牌焦虑]

- 9/24 锁榜；last-2 地板 Metav4 ~2428 + Fieldcraft 爬分；禁 re-roll

## [2026-09-27 · 截止 9/24]

- 提交锁在 9/24；此后一周 BT；last-2 锁死勿 re-roll

## [2026-09-27 · 禁 re-roll 2700]

- 2700包若指Metav4：再交=毁2432路径；不交
- lb-2700 补门禁中

## [2026-09-27 · 提交后掉分]

- Fieldcraft 爬分期 + Metav4 live 波动；team=max；不再交

## [2026-09-27 · Fieldcraft 提交]

- 用户授权 → 已交 Slot-B 1 次；等 last-2 确认

## [2026-09-27 · Fieldcraft 交不交]

- 判断：Slot-B 期权值得试1次；非金牌保证；需授权

## [2026-09-27 · Fieldcraft 2887 Slot-B]

- shop 不崩 + Metav4 25% → Slot B 信号，待用户授权
- 其余新包仍是 Pipe-16 族或输 Metav4

## [2026-09-27 · P94 暴力扫包]

- guru TOP2 = Pipe-16 族；其余输 Metav4 或不可提取
- HOLD Metav4+Thomas；无过门冲金弹药

## [2026-09-27 · top200 回落]

- rank 滑 = 相对池；last-2 在则 HOLD；禁恐慌换包

## [2026-09-27 · 持续掉分应对]

- 口径：public 阴跌 ≠ 丢 last-2 ≠ 终榜；HOLD A/B，禁恐慌提交

## [2026-09-27 · lottery mode 定稿]

- 金牌=信息增量机会；证据集内无主动制造路径
- 只盯三源；禁 Best 标题海；A/B HOLD

## [2026-09-27 · P93 Reopen]

- 新包双门全灭（Pipe-16 族 / 废包）；作者无更新
- Metav4 2630 HOLD；无金牌可执行路径

## [2026-09-27 · 状态定位锁定]

- 参谋：STATUS **PASS**；= 研究结束 · 生产锁定 · 等真正新信息
- 冲金仅 external-evidence Reopen；禁 Best 标签无限搜包
- Metav4+Thomas HOLD；只核对 last-2

## [2026-09-27 · FINAL FREEZE + v1 判定]

- GOLDSHOT_V1 = INFRASTRUCTURE_PASS / LEARNING_SIGNAL_UNTESTED（吞吐+coverage FAIL；shop PASS）
- 不是 RL 失败；赛前算力窗口内无法有效检验
- FINAL FREEZE: Metav4 + Thomas HOLD；研究 CLOSED；仅 Reopen 三条件
- 赛后 v2 = fast sim + hierarchical neural macro + league

## [2026-09-27 · Gold Shot v1]

- 吞吐 ~94 SPS → 社区级 RL 门 FAIL
- 预算内多窗口 90 局：vs Metav4 无边；shop 未崩
- **STOP_NO_SIGNAL**；HOLD；Thomas 不替换 Slot B
- `RESEARCH_GOLDSHOT_V1.md`

## [2026-09-27 · 参谋确认 HOLD + Slot-B 修正]

- **Slot-B = Thomas 56358711 @2377.9**，不是空槽；决策=**不主动替换**
- HOLD Metav4 **2658.8**；Team = max(A,B)
- 理由：公开 Elo 阴跌≠退化；final BT 只计最终 active pair episodes；无过门候选
- 优化目标=截止时 active 两 bot，不是 public 小时级波动
- 已写入 STATUS / GPT_SCORE_DROP_BRIEF

## [2026-09-27 · Gold Shot 收口校准]

- v0 = minimal probe STOP；**不是 RL 定论**
- HOLD Metav4；Slot B = **Thomas 不主动替换**（非空）；赛中研究全 CLOSED
- 赛后 hierarchical macro RL 仍开放

## [2026-09-27 · GOLD SHOT v0]

- 宏路由 bandit on Metav4 day6 route：eval 无边 vs Metav4；shop 未崩
- **STOP_NO_SIGNAL**；HOLD；不投 Slot B
- `RESEARCH_GOLDSHOT_V0.md`

## [2026-09-27 · RL meta 解读（参谋）· 仍 HOLD]

- 榜前或有 RL；解释 P46–P69「无稳定 precursor / LOSO 崩」= 非有限 if 表，而是 π(s)
- naive PPO 社区易 plateau → **本周不训 RL、不改 HOLD**
- 赛后：Metav4 skeleton + 高层 policy + population rollouts
- 已写入 `RESEARCH_CLOSED_20260927.md` / STATUS / POST_COMP

## [2026-09-27 · FINAL FREEZE 农场赛研究收口]

- 外部参谋终裁 + 本地 exact 复核闭合
- **PRODUCTION: Metav4 56390446 HOLD**（CLI ~2687.6）
- 公开 kernel 侦察 **CLOSED**；自研优化 **CLOSED**
- Reopen only: 新高阶 artifact / 作者公开真更新 / Andrey V12 exact bytes（UNRESOLVED 非 FAIL）
- Slot B = hedge 不主动填；不烧配额
- 校准点已写入 STATUS + POST_COMP_GITHUB_OUTLINE §2.0
- 报告: `RESEARCH_P92B_V48_TIE.md` / `STATUS.md` FINAL FREEZE 块

## [2026-09-27 · P92b v48 + Breaking the Tie]

- Kaito v48 Fast Routes SHA=manifest：vs Metav4/shop **0/x −22k～−24k**；略胜 v43 仍全面崩
- Andrey V12 **API 403**；实测 V21-R1 bootstrap（非 2883）：**0/x −34k**
- 参谋约定兑现：**HOLD Metav4，停止无限 kernel 搜索**
- 报告：`RESEARCH_P92B_V48_TIE.md`

## [2026-09-27 · P92 Kaito v43 定点复核]

- 外部 GPT 参谋: Slot-B 可放宽（官方 team=max/hedge）；点名重查 Kaito v43 public 2882
- exact SHA 一致；本地 vs Metav4/shop/thomas/alperen/pipe16 **全 0/x**（−22k～−26k）
- Slot A/B 双失败 → **不投**；reopen 关闭
- 门禁更新: Slot A 严 / Slot B 宽但仍禁族级 0/x
- HOLD Metav4；报告 `RESEARCH_P92_KAITO_V43.md`

## [2026-09-27 · P91 F7 扩大 holdout + 终局分批]

- F7 seeds7–12：**33% −4** → 烟测 100% 是假阳性，无边
- 终局价格分批卖：33% +5.7 噪声
- W3 F7+终局：胜率 66.7% 但 **mean −37** — 不可提交
- **P87–P91 自研+公开扫描双门全灭；HOLD Metav4**
- 报告：`RESEARCH_P91_F7_TERMINAL.md`

## [2026-09-27 · P90 侵入式 flag + tape 感知]

- F7 fert day 14→10：烟测 100%/+20 vs Metav4 + shop 全胜，**holdout 50%/−15 → 不过门**
- F9/F10 RACE 突变 holdout **25%** — 镜像上 race 参数敏感且易回归
- T1 tape-aware 中盘注入仍 **−1.6k** — 空闲窗口一动就伤
- F4/F6/F11 本 panel 未触发（bank=Metav4）
- **烟测 dual ≠ 可提交**；HOLD Metav4
- 报告：`RESEARCH_P90_FLAGS.md`

## [2026-09-27 · P89 自创策略双门]

- 用户要求自进化研发，不只抄包
- 探针：中盘空地多时手几乎不闲；有闲手时钱/种不齐
- A1 中盘空闲手种麦：vs Metav4 **−17k**、thomas **−33k** — PASS≠免费劳力
- A2/A3/E2 卖出守卫：bank **= Metav4**（空转）；E1/E3 微亏
- 双门仍无一过；**HOLD Metav4**
- 结论：公开唯一边=HybridOpening 且必碰 shop 毒点
- 报告：`RESEARCH_P89_SELF_INVENT.md`

## [2026-09-27 · P88 新公开猛攻]

- CLI Metav4 **2695.5**；thomas 2423；HOLD last-2
- haideptry **2965/2950** 本地与 **Pipe-16 逐 seed 同 bank**（+50 / shop −16k）→ 标题党克隆
- one-more-wheat +78 镜像 / shop 更惨
- countering/demystifying 同包：shop 赢、Metav4 输
- **guru v4** 亦 = Pipe-16 克隆（+50 / shop −16k）；beat-v48 输 Metav4
- 作者无新公开；**可加载候选双门全灭 → 不提交，HOLD Metav4**
- 报告：`RESEARCH_P88_NEW_PUBLIC_HUNT.md`

## [2026-09-27 · P87 原创双门全败 → HOLD]

- 用户：「直接来，大胆实验」——跑了条件 Hybrid / 指纹 / 侧位麦 / D29 拆单
- 探针：Metav4 **seeds.WHEAT=0** 早期；tile(2,4)=未来 PASTURE；Pipe-16 买种+抢格才有 +50
- M1 step0 BUY_SEED → vs shop **−21k**；C6 不买种字段层 **钱=Metav4 全同（空转）**
- C13 侧位麦：vs Metav4 −4.7k / shop **−23k** / thomas −5k — 比 Pipe-16 更毒
- C8/C8b D29 拆单：镜像 bank 与 Metav4 **完全相同** — 本 panel 无感
- **双门无一过**；Pipe-16 对照仍 +50 / shop −16k
- 结论：开局边无法在不碰 shop 毒点时复现；**HOLD Metav4 56390446**
- 报告：`RESEARCH_P87_CONDITIONAL_HYBRID.md`
