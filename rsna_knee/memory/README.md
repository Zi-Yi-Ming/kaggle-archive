# rsna_knee — MiMo 记忆归档

本目录收纳 MiMo Desktop（小米 MiMo）会话记忆中属于 RSNA Knee 比赛的部分。原文照录，未作改写。

- 原始位置：`C:\Users\Lenovo\.local\share\mimocode\memory\`
- 归入时间：2026-10-02
- 完整原始副本（含非本赛记忆）：`_workspace/mimo-export/memory/`

比赛状态：**活跃**。`rsna-knee-abnormality-detection`，截止 2026-10-22。最新项目状态见 `.agent-memory/rsna-knee-project-state.md`（更新至 EXP-016），奖牌策略见 `rsna_knee/MEDAL_STRATEGY.md`。

本目录两份记忆是 RSNA 会话 `ses_ffe5f4866fb4fffeopFHD1RpBW`（标题「你现在看一下RSNA的比赛，刚好今天GPU有刷新率」，946 条消息，2026-09-19 → 09-30）下两个子任务的调研日志。

## 条目索引

### 1. `ses_ffe5f4866fb4fffeopFHD1RpBW__T10-public-strategy-research.md`

来源：子任务 T10（公开榜策略调研）。原始路径 `memory/sessions/ses_ffe5f4866fb4fffeopFHD1RpBW/tasks/T10/progress.md`

| 条目 | 内容 |
|---|---|
| §1 Task identity | 调研 0.93–0.96 头部集群的公开策略，产出 `research/rsna-top-strategies/findings/F1.md` |
| §2 Subagent intent | 以一手来源（官方文档、原始 writeup、论文）而非通用建议作答 |
| §3 Files and code sections | 产出 F1.md（14 条 findings），覆盖赛制形状、标签提取上限、公开榜分数阶梯、软标签、侧向性、集成负结果、测量协议、弱列等 |
| §4 Verbatim commands | 实际执行的目录创建、firecrawl 排查、WebFetch 检索命令 |
| §5 Outcome and discoveries | 关键结论：标签提取是真正瓶颈；切片覆盖 18→64 比换 encoder 更重要；禁止水平翻转（5/12 标签与侧向性相关）；gold-58 不能用于训练或选择（泄漏会把 0.9357 打回 0.8568）；最弱列是 lateral meniscus（−0.09）与 MCL（−0.06） |

备注：该任务的直接产出仍在项目目录中，即 `research/rsna-top-strategies/findings/F1.md`（11989 字节），同目录另有 F2–F7 共 6 份 findings，汇总在 `research/rsna-top-strategies/REPORT.md`。本记忆的价值在于记录了 F1.md 的产出意图与工具约束（firecrawl CLI 未安装、Kaggle 页面需 JS 浏览器），结论部分与 F1.md 内容重叠。

### 2. `ses_ffe5f4866fb4fffeopFHD1RpBW__T16-free-gpu-research.md`

来源：子任务 T16（免费 GPU 资源调研）。原始路径 `memory/sessions/ses_ffe5f4866fb4fffeopFHD1RpBW/tasks/T16/progress.md`

| 条目 | 内容 |
|---|---|
| §1 Task identity | 调研可用于实际 PyTorch 训练（ResNet34 224、2–7 小时、pydicom 加载）的免费 GPU |
| §2 Subagent intent | 只考察 Lightning AI Studio 免费额度与 Hugging Face，产出 `_workspace/gpu_scout/findings_lightning_hf.md` |
| §3 Files and code sections | 25 条带出处的证据（L1–L12 Lightning、H1–H7 HF）及 ResNet34/pydicom 适配表 |
| §4 Verbatim commands | firecrawl-cli 的 search 与 scrape 命令 |
| §5 Outcome and discoveries | 关键结论：Lightning 免费额度是一次性的（注册 5 + 绑卡 25，共最多 30，12 个月过期），不是每月 80 小时；免费 Studio 每 4 小时需重启，5–7 小时任务必须做 checkpoint/resume；Hugging Face 没有任何可跑 2–7 小时训练的免费路径（ZeroGPU 每日 5 分钟且仅 Gradio，Jobs 需余额，Spaces GPU 收费，PRO 每月仅 $2 额度） |

该文件内容偏基础设施，但服务对象是 RSNA 的 ResNet34 训练，故归入本赛。其中 Lightning 额度与重启限制、HF 各方案的边界，对任何后续需要免费 GPU 的实验同样适用。

## 与其他记忆的关系

`.agent-memory/rsna-knee-project-state.md` 记录到 EXP-016（2026-09-30），含完整提交映射、0.721 配方、EXP-009 至 EXP-016 的失败与胜出结论。本目录的 T10 是 EXP-013 起「labels >> multiplane」判断的来源，T16 是免费 GPU 路线的可行性结论。三者应一起读。
