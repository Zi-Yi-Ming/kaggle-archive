# RSNA Knee 冲牌：多源标签 vs 多平面扩容 — 该押哪条

> Generated 2026-09-29 · depth: deep · 7 angles / 90+ sources scanned · workspace: research/rsna-top-strategies/

## Executive summary

1. **标签是主杠杆，不是模型扩容。** 多名 0.93–0.95 选手（45th Archit、81st Raymond、18th 公开方案）明确：图像侧到 0.87 后就顶到标签天花板；Raymond 在 288px 单模型上 0.938→0.949 几乎全靠多源弱标签 + teacher 伪标签 [1][2][3]。
2. **我们 0.721 的真正短板更底层**：报告抽取 key≈0.81、单源 LLM≈0.89，但公开方案的抽取器也只到 0.833 acc / 0.88–0.92 天花板；同时我们 **每 study 只采约 6 张切片（n_clips=2）**，赢家共识是 18→64 张，且切片数比换 backbone 更值钱 [4][5]。
3. **单源 LLM 换标签已经 A/B 过：0.701 vs 规则 0.699 = 平手**（公开测试仅 3 study，噪声内）。说明「换一个 CSV」不够，要做 **多源共识 + 软标签工艺**。
4. **静音必须当 UNK，绝不能是 0.25/0.5。** CheXpert / MAPLEZ 都有实锤：把「未提及/稳定」压成中间概率会显著伤 AUROC；我们 EXP-009/010 塌到 0.58–0.60 与此一致 [6][7]。
5. **损失要按置信度加权**：0.5=未提及，权重用 `2*|p-0.5|`；软目标要离开 0.5（BCE 在 0.5 几乎不训）[2][8]。
6. **多平面 S+C+A 是「组题」不是得分杠杆**。0.937 单平面也能到；多平面融合有人报无效。我们已有 +0.022，保留，但不要再指望继续堆平面 [9]。
7. **224px 够用。** 公开 0.950 单折来自 224 CoAtNet；Qwen VLM@384 也是 0.950。分辨率不是当前主因 [10]。
8. **Gold 58 只能当验证，不能当训练主力，更不能拿来选标签集**（SE≈0.086）；rank-18 做成 fold −1 [2][11]。
9. **推荐优先级**：(A) 多源标签共识 + 置信加权软损失 → Axial 2h A/B；(B) 同步把切片覆盖拉到 ≥18；(C) 赢了再 S+C+A / 小模型 ensemble。**不要**先做多平面继续扩容或加 epoch。
10. 奖牌带公开约 **0.955–0.959**；单模型公开基线已在 0.94+。我们 0.721 → 目标不是微调，而是补标签工艺与采样密度 [12][13]。

## Background & scope

问题：在 GPU 有限、code-comp 必须可重跑的前提下，下一步是押 **多源 LLM 标签共识**，还是押 **当前配方的多平面扩容**。范围覆盖公开榜 0.93–0.96 集群的讨论/方案/数据集卡与软标签文献；不含我们已有 EXP-00x 内部史（已知）。假设公开榜 3 study 噪声大但仍作方向信号；预算约 14h GPU，截止 2026-10-22。

## 一、公开榜真实打法（0.93–0.96）

竞赛形态：12 标签宏 AUC，train 4407 / hidden ~1300，code-comp 离线 ≤9h，$77k [14]。

| 层级 | 代表 | 分数 | 关键做法 |
|---|---|---|---|
| 公开单模型 | CoAtNet 224 2.5D | 0.950 | 标签做好后小模型够用 [10] |
| 公开单模型 | Qwen3.5-2B VLM @384 | 0.950 | 视觉语言模型 [10] |
| 18th 公开方案 | EfficientNet-B3 MIL + Qwen3.6-35B 标签 | 0.903 | 标签抽取是瓶颈 [3] |
| 顶级公开栈 | DINOv2 族 + RadImageNet + CoAtNet Raptor | ~0.941–0.957 | 多架构互补，不是单 backbone [15][16] |
| 奖牌带 | — | 0.955–0.959 | 伪标签 + 多源 + 少量 ensemble [12] |

「Best single-model」讨论里 0.936–0.950 已很常见：小 ResNet 224 = 0.936；CoAtNet-2@352 = 0.940；多折再 +0.002–0.009 [10][17]。

## 二、标签工程：赢家具体怎么做

**天花板。** 仅 58/4407 有专家标；其余靠报告。18th 的 Qwen3.6-35B 抽取器对 gold58 仅 0.833 mean acc / 0.766 F1；「完美读报告」估计 0.88–0.92 封顶（报告与图像不一致，silent report 不可约）[3][18]。

**公开标签源（与我们本地分析一致）：**

| 源 | 对 gold key AUC | 角色 |
|---|---|---|
| 报告规则 / regex | ~0.81 | 基线，已不够 |
| steven v2 | 0.887 | 主源 |
| **steven v4_blend** | **0.893** | 去相关混合后的主源 [2] |
| lixin73 | 0.835 | 去相关第二源（单独弱，混合有用）[2] |
| pilkwang | 0.870 / 含 conf+verdict | 三源共识 + UNK 显式 [19] |

**共识模式（rank-18 已生产化）：** 按 **该类在 gold58 上的可靠性加权投票**；分歧输出为 soft label；第三方 pilkwang 作第三意见 [2][18]。要点是 **去相关**，不是找一个「最强单源」。

**软标签工艺：**
- `0.5` / `UNK` = 未提及 → **mask**，不是负例、不是 0.25 [6][7]
- 损失权重 `2*|p-0.5|`（低置信少训）[2]
- mild 严重度压低；目标锐化离开 0.5 [2][8]
- gold58 做 fold −1 验证，不进训练、不拿来选标签 [2][11]

**我们的 EXP-012 缺了什么：** 静音 mask 做对了；但仍是 **单源 v4_blend**、**无置信度损失加权**、**gold 仍在训练里**、**切片过稀**。这解释了为何 0.701≈0.699。

## 三、模型与采样：什么是表注、什么才加分

- **表注（table stakes）：** 按平面选 series、均匀取切片、多平面均值。0.93 后多平面融合有人报无效 [9]。
- **真加分：** 切片覆盖 18→64；per-finding attention pooling；几何切片顺序；逐 series 窗宽 [5]。
- **backbone 次要：** 224 CoAtNet / 小 ResNet 都能上 0.93–0.95；换 DINOv2/CoAtNet 是后期 [10][16]。
- **横向翻转是负增益**（左右结构标签）[5]。

我们现状：ResNet34 224 2.5D、n_clips=2（约 6 切片）、S+C+A 三平面 mean。平面维度够，**采样密度远不够**。

## 四、推理与 ensemble

- 指标是 12 个 AUC 的均值 → **只看排序**，不必做概率校准 [20]。
- 多折 mean 很常用但 **不是免费午餐**（0.938→0.947，也有 5 折反输单折）[17][21]。
- TTA 约 +0.001 [22]。
- 同配方 blend 相关 0.92，基本没用；要 **异架构**（相关 0.83 时 +0.004）[17][23]。
- Code-comp 要能重跑：权重+薄推理正确；推理可优化到 <10 min [24]。

## 五、软标签为什么塌（我们踩的坑有文献背书）

| 错误 | 后果 | 证据 |
|---|---|---|
| silence=0.25/0.5 当软负例 | 训成全阴性 | MAPLEZ「Use Stable=50%」AUROC 下降；我们 EXP-009 0.586 [7] |
| 全局同一套 uncertain 映射 | 病理间最优映射不同 | CheXpert U-Ones/U-Zeros 因病而异 [25] |
| 过度 label smoothing | 抹掉类间 logit 结构 | Müller NeurIPS’19 [8] |
| 用未校准 LLM 分数 | 校准也无法修非保序噪声 | Ushio ICLR’26 [26] |

## 六、决策：多源标签 vs 多平面扩容

| 选项 | 预期收益 | GPU/小时 | 风险 | 证据强度 |
|---|---|---|---|---|
| **A 多源共识标签 + 置信加权损失** | 高（0.72→0.85+ 路径上的主段） | 标签 CPU + Axial 2h A/B | 中（需正确 UNK/加权） | 高（多名高排名自述 + 18th 方案） |
| **B 继续 S+C+A / 更多平面** | 低–中（我们已有 +0.022；社区不认这是主杠杆） | 7h | 中 | 中 |
| C 更多 epoch | 无 | 2–7h | 已证伪（EXP-011 0.710） | 高 |
| D 换大分辨率 | 低 | 高 | 224 已 0.950 | 高 |
| E 增加切片覆盖 ≥18 | **高且便宜** | 同模型重训 2h | 低 | 高（18→64 > 换 encoder） |

**结论：选 A，但把 E 并进同一次实验。**  
「多源标签」单独不够（我们单源已平手）；必须是 **多源 + UNK mask + `2*|p-0.5|` 加权 + 更多切片**。多平面 S+C+A 在标签变好后再上，作为第二级放大器，而不是现在再灌 7h。

### 建议实验序（GPU 可负担）

1. **EXP-013（优先）**：多源 soft 标签（steven v4_blend ×0.5 + lixin73 ×0.2 + pilkwang ×0.3，按类再乘 gold58 可靠性）→ silence→mask → loss weight `2*|p-0.5|`；训练 **Axial fold0，n_clips≥4（≥12 切片）**。对照 EXP-012 0.701 / 规则 0.699。
2. 若 ≥0.71：同样标签 **S+C+A fold0**，weights+infer，对照 0.721。
3. 仍涨：加 1 个去相关模型（CoAtNet 或 DINOv2 小）做 equal blend，而不是再堆同架构 fold。
4. 停止项：再扩 OA 词表、再加 epoch、整表硬编码 CSV、silence 当 0.25。

## Open questions

- 0.93–0.96 集群无完整公开 write-up（榜/讨论页 JS 墙）；0.957 栈细节来自公开 notebook 推断 [15]。
- 社区没有「同标签下 S+C+A vs 单平面」的干净消融表；「多平面无效」有反例也有我们 +0.022 的正例。
- Gold58 是否应在最终模型中重新纳入训练，公开方案不一致（验证期排除是共识）。
- pilkwang / steven / lixin73 的最优类权重需我们自己在 gold58 上估（注意 SE 大）。

## Sources

[1] Kaggle discussion 735304 — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304 (accessed 2026-09-29)
[2] stevenleehans/rsna-knee-llm-report-labels — https://www.kaggle.com/datasets/stevenleehans/rsna-knee-llm-report-labels (accessed 2026-09-29)
[3] Yash Bishnoi, RSNA competition writeup (rank 18) — https://huggingface.co/blog/bishnoiyash/rsna-competetion (2026-08, accessed 2026-09-29)
[4] Bishnoi writeup (label ceiling / extractor 0.833) — https://huggingface.co/blog/bishnoiyash/rsna-competetion (accessed 2026-09-29)
[5] mathischmp/challenge_rsna (slice 18→64, laterality) — https://github.com/mathischmp/challenge_rsna (accessed 2026-09-29)
[6] CheXpert (silence ≠ negative) — https://arxiv.org/html/1901.07031v1 (AAAI’19, accessed 2026-09-29)
[7] MAPLEZ (Stable=50% hurts) — https://arxiv.org/html/2403.04024v2 (MedIA’24, accessed 2026-09-29)
[8] Müller et al., When do label smoothing help — https://arxiv.org/abs/1906.02629 (NeurIPS’19, accessed 2026-09-29)
[9] Kaggle discussion 735304 (multi-plane fusion ineffective for some) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304 (accessed 2026-09-29)
[10] Kaggle discussion 735304 (single-model 0.950 @224) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304 (accessed 2026-09-29)
[11] Kaggle discussion 738339 / gold58 holdout — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/738339 (accessed 2026-09-29)
[12] Leaderboard band — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/leaderboard (2026-09-29)
[13] Kaggle discussion 735767 — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735767 (accessed 2026-09-29)
[14] Competition overview / code-comp 9h — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection (accessed 2026-09-29)
[15] fuadmuhammad rsna-knee-fast-parent-0-957-v2 — https://www.kaggle.com/code/fuadmuhammad/rsna-knee-fast-parent-0-957-v2 (accessed 2026-09-29)
[16] beraterolelk 0.941 SOTA DINOv2+RadImageNet — https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet (accessed 2026-09-29)
[17] Kaggle discussion 735304 / 740610 (folds, blends) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304 (accessed 2026-09-29)
[18] Bishnoi writeup (multi-source fusion) — https://huggingface.co/blog/bishnoiyash/rsna-competetion (accessed 2026-09-29)
[19] pilkwang/rsna-knee-llm-labels — https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels (accessed 2026-09-29)
[20] Bishnoi writeup (ranking metric, fold mean) — https://huggingface.co/blog/bishnoiyash/rsna-competetion (accessed 2026-09-29)
[21] Kaggle discussion 740375 (fold not always better) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/740375 (accessed 2026-09-29)
[22] Kaggle discussion 735304 (TTA +0.001) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304 (accessed 2026-09-29)
[23] Kaggle discussion 735304 (same-recipe blend corr 0.92) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304 (accessed 2026-09-29)
[24] Prateek / discussion 743374 (inference 40→10 min) — https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/743374 (accessed 2026-09-29)
[25] CheXpert uncertainty mapping — https://arxiv.org/html/1901.07031v1 (accessed 2026-09-29)
[26] Ushio et al., ICLR 2026 soft-label calibration — https://arxiv.org/html/2505.20761v1 (accessed 2026-09-29)
[27] Lukasik et al. label smoothing ≈ symmetric noise — https://arxiv.org/abs/2003.02819 (ICML’20, accessed 2026-09-29)
[28] nartaa/rsna-knee-hpo-assets — https://www.kaggle.com/datasets/nartaa/rsna-knee-hpo-assets (accessed 2026-09-29)
