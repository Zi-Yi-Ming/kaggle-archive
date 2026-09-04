# RSNA Knee Abnormality Detection — baseline 部署说明

**比赛**:https://www.kaggle.com/competitions/rsna-knee-abnormality-detection
**脚本**:`rsna_baseline.py`(2.5D ResNet34 多视图,12 标签,宏平均 AUC)
**截止**:2026-10-22 | **奖金**:$77,000 | 已下载数据:`train.csv`/`test.csv`/`test_series.csv`/`sample_submission.csv`

## 比赛要点(前置认知)

- **数据**:4,407 例训练 MRI(DICOM)+ 放射报告文本(12 种语言);测试集 3 例(样例),
  完整测试集通过挂载获得;`train_series.csv` 记录 Study→Series 映射与平面/压脂属性。
- **标签**:官方 `train.csv` 的 12 个标签列 **98.7% 为 NaN,仅 58/4407 有标注**!
  标签需自行从报告文本提取(社区用 LLM 软标签,见下)。baseline 只在这 58 例上训练,
  OOF AUC 会偏低,主要价值是**跑通流程、拿到合法提交**。
- **指标**:12 个目标的宏平均 AUC(提交 12 列置信分数,0~1)。

## 在 Kaggle Notebook 上运行(推荐)

1. 打开 https://www.kaggle.com/code → **New Notebook**
2. **Settings → Accelerator** 选 **GPU T4**(CPU 跑 4 万张 MRI 切片不可行)
3. **Add Input**:
   - 挂载比赛 **rsna-knee-abnormality-detection**(数据自动出现在 `/kaggle/input/`)
   - (可选)挂载社区软标签数据集 **barun2104/rsna-knee-stratified-folds-and-llm-soft-labels**,
     脚本会自动扫描并填充缺失标签(`train_folds_with_pseudo.csv` 中 `pseudo_*` 列)
   - (推荐)挂载离线预训练权重数据集 **matteonaccarato/resnet34-imagenet-pth**
     (或 `pytorch/resnet34` / `marcshade/resnet-pretrained-weights-imagenet`),
     脚本自动扫描 `/kaggle/input` 下的 `.pth` 并加载 ImageNet 预训练,**无需开 Internet**
4. 上传 `rsna_v3.ipynb`(或 `rsna_v3.py`)到 Notebook,运行最后一个 cell:
   ```python
   !python rsna_v3.py --epochs 3 --batch 16 --n-clips 2 --fuse weight --verbose
   ```
   - 建议先 `--epochs 1 --batch 8` 冒烟跑通(确认 DICOM 能读、不出错),再放大;
   - 9 小时运行上限内可跑 3-5 epoch × 5 折(取决于 GPU 与 clip 数)。
5. 运行完输出 `/kaggle/working/submission.csv` → 右侧 **Submit to Competition** 直接提交

### 脚本行为

| 环节 | 说明 |
|---|---|
| 路径 | 自动扫 `/kaggle/input/*/train.csv`;本地回退 `rsna_knee/` |
| 折划分 | `GroupKFold(5, groups=StudyInstanceUID)`,防同一患者泄漏 |
| 预处理 | DICOM Rescale→百分位窗口化→224²→同一 series 相邻 3 切片合成 3 通道 clip |
| 模型 | ResNet34(ImageNet 预训练,conv1 改 3 通道)+ 12 sigmoid 头 |
| 损失 | BCEWithLogitsLoss,**valid 掩码只算有标注的位置**(缺失标签不污染) |
| 输出 | OOF 宏平均 AUC 报告 + `submission.csv` |

### v3 权重加载优先级(关键改进)

| 来源 | 触发方式 | 说明 |
|---|---|---|
| ① 离线权重 | 挂载 `.pth` 权重数据集,自动扫描 | 无需联网,推荐;结构须与 ResNet34 匹配(缺 conv1/fc 可豁免) |
| ② 联网下载 | `--pretrained` | 需开启 Internet,失败自动回退 |
| ③ 随机初始化 | 默认 | 无任何权重时兜底,精度明显下降 |

## 本地验证(不跑训练)

本地环境无 torchvision/pydicom,仅可做数据层验证:

```bash
python -m py_compile rsna_knee/rsna_baseline.py   # 语法
python -c "import sys; sys.path.insert(0,'rsna_knee'); import rsna_baseline as R; R.resolve_paths(); R.load_labels(R.resolve_paths()[0])"
```

## 后续提升方向(按性价比)

1. **LLM 软标签**(挂载社区数据集即可,脚本已支持自动填充)——把训练样本从 58 例扩到全量,这是最大的提升点;
2. **多平面聚合**:`test_series.csv`/`train_series.csv` 的 `Anatomical_Plane`(Axial/Sagittal/Coronal)
   分平面独立建模再融合,替代现在粗暴的 series 拼接;
3. **更大 backbone**:ConvNeXtV2-Tiny / EfficientNet / RadImageNet 预训练(医学影像专用权重,社区有公开档);
4. **文本分支**:放射报告用 distilbert(参考 nlp_getting_started 经验)与影像特征融合——头部方案都在做双模态。

## 文件

```
rsna_knee/
├── rsna_baseline.py      # baseline 脚本(Kaggle Notebook 上跑)
├── rsna_preview.py       # 数据预览(本地跑,看 CSV/DICOM 结构)
├── README.md             # 本文档
├── train.csv / test.csv / test_series.csv / sample_submission.csv  # 已下载的轻量 CSV
└── (DICOM 影像数据不下载,走 Kaggle 挂载)
```
