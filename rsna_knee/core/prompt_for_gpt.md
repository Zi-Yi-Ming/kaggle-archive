# RSNA Knee 现状完整简报 + 参谋请求（2026-09-04）

请以资深医学影像 Kaggle 竞赛专家 + 提分策略顾问的身份，先完整理解下述情况，再回答文末问题。不要凭空假设数据；需要更多信息时明确列出要什么。**特别提醒：请先诊断"为什么 5 个月才 0.503"，再谈提分——0.503 ≈ 随机(0.5)本身说明训练路径有问题，不是正常 baseline。**

---

## 一、比赛背景

- **比赛**: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection
- **类型**: Research（**发奖牌/积分**）| 参赛 ~2,700 队 | **截止 2026-10-22**（剩 48 天）
- **奖金**: $77,000
- **我的当前排名**: ~2446-2517 / ~2700（接近垫底）
- **指标**: 12 个目标的**宏平均 AUC**（提交 StudyInstanceUID + 12 列置信分数 0~1）

### 数据（关键难点）
- 训练集 4,407 例 MRI（DICOM 多序列）+ 放射报告文本（12 种语言）
- **官方 12 标签列 98.7% 为 NaN，仅 58/4407 例有标注** ← 本赛最大难点
- 标签需自行从报告文本提取；社区方案用 **LLM 生成软标签**（pseudo_* 列）
- 测试集：页面样例仅 3 例，完整测试集通过 Notebook 挂载获得
- `train_series.csv` / `test_series.csv` 有 Study→Series 映射与 Anatomical_Plane（Axial/Sagittal/Coronal）、压脂属性

### 任务形态
12 标签多标签分类（ACL/MCL/半月板×2/OA×3/积液/滑膜炎/Baker 囊肿/挫伤/骨折），医学影像 + 文本双模态。

---

## 二、当前代码版本链（全部已就绪，未真正在 Kaggle 全量验证）

| 版本 | 文件 | 核心 | 状态 |
|---|---|---|---|
| baseline | `rsna_baseline.py` (19K) | 2.5D ResNet34：同一 series 相邻 3 切片 [prev,center,next] 合成 3 通道 clip → study 级 12 sigmoid 头；GroupKFold(by StudyInstanceUID) | 跑通但 ~0.5 |
| v2 | `rsna_v2.py` (24.5K) | 按 Anatomical_Plane 分平面独立建模（每平面一个 ResNet34 + 2.5D clip），测试时按各平面 OOF AUC 加权融合（--fuse weight/mean），缺平面时归一化权重 | 就绪 |
| **v3** | `rsna_v3.py` (41.8K, 921行) | v2 全部 + **离线预训练权重自动扫描** + **软标签内容识别增强** | **就绪待真实验证** |
| v3 fix | `rsna_v3_fix.ipynb` / `rsna_v3_single.ipynb` | v3 单 cell 版 Notebook（上传直接跑） | 就绪 |
| Colab | `rsna_colab.ipynb` / `colab_setup.py` | 弃用（kaggle.json 缺失下载失败） | 已弃 |

### v3 关键实现细节
- **折划分**: `GroupKFold(5, groups=StudyInstanceUID)` 防同一患者泄漏
- **预处理**: DICOM Rescale → 百分位窗口化 → 224² → 同一 series 相邻 3 切片 3 通道 clip
- **模型**: ResNet34 + 12 sigmoid 头；conv1 改 3 通道（channels==3 时沿用预训练权重）
- **损失**: BCEWithLogitsLoss，**valid 掩码只算有标注位置**（缺失标签不污染）
- **软标签**: 按内容识别任意含 `StudyInstanceUID` + `pseudo_*` 列的 CSV（不再依赖文件名白名单），`--pseudo-conf` 置信度阈值过滤
- **权重加载优先级**: ① 离线 .pth（挂载 matteonaccarato/resnet34-imagenet-pth 或 pytorch/resnet34，自动扫描 /kaggle/input）→ ② `--pretrained` 联网 → ③ 随机初始化
- **权重兼容**: model_state_dict / model. / backbone. 前缀均兼容；扫不到权重自动打印挂载目录树诊断
- **参数默认**: `--epochs 2 --batch 8 --lr 3e-4 --n-clips 2 --folds 5 --fuse weight --pseudo-conf 0.0`

---

## 三、真实提交成绩历史（publicScore = LB）

| ref | 日期 | 分数 | 备注 |
|---|---|---|---|
| 55709319 | 2026-08-23 | 0.495 | 早期 |
| 55732362 | 2026-08-24 | 0.500 | |
| 55734380 | 2026-08-24 | **0.503** | **最佳（仍 ≈ 随机）** |
| 55908018 | 2026-08-31 | 0.495 | |
| 55909290 | 2026-08-31 | —（无分） | submission 异常 |
| 55913420 | 2026-08-31 | —（无分） | submission 异常 |

**0.503 ≈ 随机(0.5)——训练基本没学到东西。** 本地 OOF AUC 也 ~0.49-0.50。

---

## 四、报错/失败历史（按时间线，全部已定位）

1. **baseline 0.5 分根因（2026-08-24 定位）**: 挂载的是 `notebooks/` 目录而非 `datasets/` 数据集 → **软标签 + 预训练权重都没加载上，实际只有 58 例在训练**。修复后 v3 支持内容识别 + 目录树诊断。
2. **Colab 弃用（2026-08）**: `/root/.kaggle/kaggle.json` 缺失导致数据下载失败（用户已 Join 比赛但 Colab 侧无凭据），粘贴缩进问题 → 放弃 Colab。
3. **Kaggle GPU 全量跑挂（2026-08-30/31 日志）**: v3 在 Kaggle 上运行 5 折全跑完但**模型完全没学**：loss 卡在 **0.693**、OOF AUC **0.492** ≈ 随机；且 `submission.csv` 只有 **3 行**（样例行数！）导致提交 **400 失败**。
4. **P100 GPU 不兼容（2026-08-30/31）**: Kaggle 分配 P100 GPU 与 torch 2.10 不兼容崩溃；T4 重跑又遇 cap。
5. **GPU 额度耗尽（当前阻塞）**: Kaggle 每周 GPU 额度用完，等月度重置；`rsna_v3.py` 已就绪但无法在 Kaggle 全量验证。
6. 曾尝试 Kaggle API 推 notebook 自动跑（2026-08-29），跑通但受上面问题影响。

---

## 五、GPU 消耗与运行环境

- 数据: 4,407 例 × 每例多个 series × 每 series 数十~上百张 DICOM 切片（训练需遍历全部切片做 clip）
- 运行: Kaggle Notebook GPU（T4 为主），9 小时运行上限
- 估算: baseline/v2/v3 均 2.5D clip（2D backbone 省显存），batch 8-16、n-clips 2 可跑 3-5 epoch × 5 折
- **当前完全阻塞**: GPU 额度耗尽（Kaggle 每周配额），无本地 GPU（本地仅 CPU，且无 torchvision/pydicom 完整环境，只能做数据层验证）

---

## 六、已规划的提分路线（未执行，因为 GPU 阻塞 + 想先听你的诊断）

| 阶段 | 内容 | 状态 |
|---|---|---|
| 阶段 1 | 预训练权重（离线 .pth）+ LLM 软标签全量训练 | v3 代码就绪，**未真实验证** |
| 阶段 2 | 折对齐验证 + epochs 拉满 + TTA | 未开始 |
| 阶段 3 | backbone 升级 ConvNeXtV2 / EfficientNetV2 / RadImageNet | 未开始 |
| 阶段 4 | distilbert 文本分支（影像+报告双模态；已在 LLM Classification 练习赛预演过双塔/离线权重） | 未开始 |
| 阶段 5 | OOF 集成（复用 S6E8 LR stacking 经验） | 未开始 |

---

## 七、请 GPT 参谋的问题

### Q1: 诊断 0.503——为什么模型没学到？
已知信号: loss 卡 0.693（BCE 的"全输出中间值"态）、OOF AUC 0.492、submission 只有 3 行。
请按可能性排序诊断，并给每个一个可执行的验证动作：
- 标签根本没进训练（58 例 vs 软标签的 valid 掩码逻辑）
- 2.5D clip 构造与数据布局不匹配（series 切片顺序/通道）
- DICOM 读取静默失败 → 输入是空白/噪声图
- 学习率/epoch 不足，或 GroupKFold 划分把 58 例切碎到 fold 里没训练样本
- 其他我没想到的

### Q2: 软标签的正确用法
98.7% NaN 的官方标签 + 社区 LLM pseudo 软标签：业界对这个赛的主流做法是什么？
- 直接全量 soft label 当 target 训 BCE？还是先训 58 例真标签再蒸馏？
- pseudo-conf 阈值应该设多少？不同标签的置信度差异怎么处理？
- 有没有"必须看"的公开 kernel/方案？

### Q3: GPU 额度阻塞下怎么推进（最实际问题）
每周配额耗尽、本地无 GPU、10/22 截止。48 天里怎么最大化利用有限 GPU？
- Kaggle 每周额度什么时候重置？有没有办法确认？
- 是不是应该把代码收敛到"一版最可能出分的方案"，一次性跑完 5 折 + TTA + 提交，而不是反复小跑？
- 有没有值得用 CPU/本地先做的前置工作（数据缓存、clip 预生成、折缓存、软标签预处理）来省 GPU 时间？

### Q4: 2.5D 方案本身够不够
2.5D（相邻 3 切片合成通道 + 2D ResNet）对这个赛是主流够用方案，还是明显落后？
- 需要上 3D（如 ResNet3D/Swin3D 或 pretrained 3D）吗？还是先 2.5D 收敛再升级？
- RadImageNet 权重 vs ImageNet 权重，对 MRI 增益多大？
- 分平面独立建模（v2/v3 的 --planes）正确吗？Axial/Sagittal/Coronal 权重怎么融最稳？

### Q5: 48 天的资源分配建议
如果每周只有 ~10-20 小时 GPU，接下来 48 天最优时间线是什么？
- 每周一个完整实验（如 W1 软标签全量、W2 大 backbone、W3 文本分支、W4 集成）？
- 还是集中火力做 1-2 个最高杠杆改动反复验证？

### Q6: 双模态(文本)值不值得做
这个赛有 12 语言放射报告文本。头部方案是否都在用文本？distilbert 文本分支的预期增益 vs 工程成本？
（注：我在另一个赛已验证过 distilbert 离线微调 + 双塔结构，工程风险低）

---

## 输出格式

1. 每问先结论后依据，不要泛泛而谈
2. Q1 给一个"最可能导致 0.503 的三个原因 + 每个的验证动作"
3. 如果有某个我的技术假设是错的，直接指出
4. 最后给一个"如果只做三件事"的明确排序
