# RSNA 冲奖牌公开策略汇总（2026-09-25 检索）

来源：Kaggle 讨论区 735304 / 738339 / 733836 + 数据集页（firecrawl 抓取，原文在 `.firecrawl/`）

## 核心共识（0.87→0.95 队列原话）

1. **标签是最大杠杆**，不是 backbone（Archit #36: 0.950 CoAtNet；Raymond #69: 0.938→0.949 全是 label；Nathan #379: 0.74→0.87+ 是 label ceiling）
2. **规则抽取不够**：regex vs gold ≈ **0.81**；LLM 读报告 ≈ **0.89**（stevenleehans）
3. **多源弱标签 → teacher → 伪标签 → student 图像模型**（Raymond）；不同 teacher 擅长不同目标
4. **便宜 LLM 就够**（API 总成本 <$5）；Gemma 4 本地抽取有人报单模型 0.949
5. **软标签要锐化**：挤在 0.5 附近 BCE 学不动；mild 发现要压分（小量积液≠阳性）
6. 模型 224–384 都行：CoAtNet / DINOv2-MIL / 小 ResNet / Qwen3.5-2B VLM@384 单折 0.950
7. 分辨率次要；**224px 小 ResNet + 好标签可到 0.91–0.936**
8. DICOM 必须按 **ImagePositionPatient** 排序（我们已做）
9. OOF 伪标签与 LB 相关较好；ensemble 是最后加厚，不是主因

## 可直接挂载的公开标签

| 数据集 | 要点 |
|---|---|
| **stevenleehans/rsna-knee-llm-report-labels** | 全 4407；`llm_labels_v4_blend.csv` 推荐（+lixin73 GPT 混合）vs gold **0.8927** |
| lixin73/rsna-knee-llm-report-labels-sol56 | 独立 LLM 标签，用于 blend |
| dreaddevelopment/rsna-knee-labels | 另一套 LLM soft labels |
| barun2104/...soft-labels | 旧版；我们验过 **98.7% 死 0.5，慎用** |

注意：steven 页面写明 **「更好 key ≠ 自动更好模型」**，要 A/B。

## 我们 vs 奖牌级

| 项 | 我们 0.721 | 奖牌带 0.94+ |
|---|---|---|
| 标签 | 规则 + plumbing | LLM 多源 blend / teacher 伪标签 |
| 模型 | ResNet34 224 2.5D 3ep | CoAtNet/DINOv2/256–384 + 更长训 |
| 提交 | infer-only 权重（已通） | 同左 + TTA / 少量 ensemble |
| 差距 | — | **~0.22 AUC** |

## 奖牌路线（4 周，按 EV）

### P0 本周（GPU 少也先做）
1. 挂载 **steven v4_blend**，替换/混合我们 pseudo（保留 gold 优先）
2. 用 **A/B harness**：同 Axial fold0 或 S+C+A，对比 labels005 vs v4_blend
3. 锐化：`2·|p-0.5|` 加权或温度锐化；mild 压到 ≤0.4

### P1 刷新 GPU 后
4. **teacher→student**：多源标签训 teacher → 对全量出伪标签 → 重训 student
5. 模型升级单变量：CoAtNet-224 或 DINOv2-MIL，仍 3 平面 fold0
6. 336px 同 140mm 物理裁剪（标签稳定后再做）

### P2 冲 0.90+
7. 多模型互补 ensemble（DINOv2-MIL + CoAtNet + ResNet）
8. TTA、更多 clip、更长训 + 正则
9. 可选 Qwen3.5-2B VLM 微调（有人单折 0.950）

### 明确不做
- 继续堆 EXP-003 式 fold ensemble
- 再扩 OA 词表（EXP-006 已证伪）
- 单独死磕 224→384 分辨率（先标签）

## 来源 URL

- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/738339
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733836
- https://www.kaggle.com/datasets/stevenleehans/rsna-knee-llm-report-labels
- https://www.kaggle.com/datasets/lixin73/rsna-knee-llm-report-labels-sol56
