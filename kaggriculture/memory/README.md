# kaggriculture — MiMo 记忆归档

本目录收纳 MiMo Desktop（小米 MiMo）会话记忆中属于农场赛（kaggriculture）的部分。原文照录，未作改写。

- 原始位置：`C:\Users\Lenovo\.local\share\mimocode\memory\`
- 归入时间：2026-10-02
- 完整原始副本（含非本赛记忆）：`_workspace/mimo-export/memory/`

比赛状态：**已归档**。提交窗 2026-09-24 关闭，详见 `kaggriculture/ARCHIVE.md` 与 `COMPETITIONS.md`。本目录记忆为归档前的最终决策记录。

## 条目索引

### 1. `ses_ffe5f6f574cc3ffeMY6VNxtxFl__MEMORY.md`

来源：MiMo 会话 `ses_ffe5f6f574cc3ffeMY6VNxtxFl`（标题「你现在是 Kaggriculture 项目的主力 Research Agent。」，1637 条消息，2026-09-11 → 09-19）的会话级记忆。
原始文件名：`memory/sessions/ses_ffe5f6f574cc3ffeMY6VNxtxFl/memory/MEMORY.md`

| 条目 | 内容 |
|---|---|
| Official mechanics (confirmed) | 官方赛制确认：team score 取两个 active submission 的较优者、终局 BT 只计截止时双方仍 active 的 episodes、平局各算半胜、last-2 替换规则 |
| Therefore | 由赛制推出的操作结论：无需为清掉 V16 而重交 alperen、Slot B 可留 V16、禁止弱探索性提交 |
| Production | 生产锁定：alperen_meta ~2262.6 冻结、研究在 P69 关闭、2424 与 2960 不可规划 |
| Reopen only on | 重新开启的三个条件（作者发布可执行更新、可复现的 2400+ 前沿来源且过 reject-gate、新策略族） |
| Watch (passive) | 被动观察项：社区 / notebooks / forks / 作者评论、瞬时高 Elo agent |
| Do not | 禁止项：P70 RE、guru-counter、阈值法、notebook 重新解包；不得把 Elo→winrate 线性映射当决策工具 |
| Post-final | 赛后动作：下载 tournament episode dump 做 lineage hunt、资产化 harness 与失败数据集 |

### 2. `ses_ffe5f45c9d36effeMDpbGKHlG6__notes.md`

来源：MiMo 会话 `ses_ffe5f45c9d36effeMDpbGKHlG6`（标题「这个是什么意思啊，农场的比赛kaggle」，867 条消息，2026-09-19 → 09-26）的会话笔记。
原始文件名：`memory/sessions/ses_ffe5f45c9d36effeMDpbGKHlG6/notes.md`

| 条目 | 内容 |
|---|---|
| [2026-09-23 · 镜像局白饭定位 · H3x 仍最优] | H3x live 77%（23W-7L）卡 1903–1910；赢家多卖约 1000 化肥是主因；收肥插件会打乱 Metav4 物理，纯 H3x +452 但加肥掉到 +20；结论为白饭属配套产线，9/24 焊不上，H3x 不动 last-2 |

### 3. `ses_current_session_id__notes.md`

来源：MiMo 记忆中一个名为 `current_session_id` 的会话目录（MiMo 写入时未解析成真实 id，无法回溯到具体会话）。按内容判定为农场赛。
原始文件名：`memory/sessions/current_session_id/notes.md`

共 29 条按日期编排的推进记录，条目名如下：

| 条目 |
|---|
| [2026-09-27 · H3 过门待授权] |
| [2026-09-27 · P97b 过双门] |
| [2026-09-27 · 铜牌焦虑] |
| [2026-09-27 · 截止 9/24] |
| [2026-09-27 · 禁 re-roll 2700] |
| [2026-09-27 · 提交后掉分] |
| [2026-09-27 · Fieldcraft 提交] |
| [2026-09-27 · Fieldcraft 交不交] |
| [2026-09-27 · Fieldcraft 2887 Slot-B] |
| [2026-09-27 · P94 暴力扫包] |
| [2026-09-27 · top200 回落] |
| [2026-09-27 · 持续掉分应对] |
| [2026-09-27 · lottery mode 定稿] |
| [2026-09-27 · P93 Reopen] |
| [2026-09-27 · 状态定位锁定] |
| [2026-09-27 · FINAL FREEZE + v1 判定] |
| [2026-09-27 · Gold Shot v1] |
| [2026-09-27 · 参谋确认 HOLD + Slot-B 修正] |
| [2026-09-27 · Gold Shot 收口校准] |
| [2026-09-27 · GOLD SHOT v0] |
| [2026-09-27 · RL meta 解读（参谋）· 仍 HOLD] |
| [2026-09-27 · FINAL FREEZE 农场赛研究收口] |
| [2026-09-27 · P92b v48 + Breaking the Tie] |
| [2026-09-27 · P92 Kaito v43 定点复核] |
| [2026-09-27 · P91 F7 扩大 holdout + 终局分批] |
| [2026-09-27 · P90 侵入式 flag + tape 感知] |
| [2026-09-27 · P89 自创策略双门] |
| [2026-09-27 · P88 新公开猛攻] |
| [2026-09-27 · P87 原创双门全败 → HOLD] |

该文件是三个来源中信息密度最高的，覆盖 P87–P97b 的连续实验、Gold Shot v0/v1 的 STOP_NO_SIGNAL 判定、以及 FINAL FREEZE 的最终口径。

## 与其他记忆的关系

项目内 `.agent-memory/kaggriculture-archive-state.md` 与 `.agent-memory/kaggriculture-benchmark-discipline.md` 是 Qoder 导出的早期记忆（截至 2026-09-11 前后），与本目录内容互补：Qoder 侧偏 benchmark 规范与候选筛查，MiMo 侧偏终局赛制与提交决策。
