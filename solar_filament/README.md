# Solar Filament — 太阳暗条分割（Playground S6E6）

## 比赛简介

Kaggle Playground Series Season 6 Episode 6：太阳暗条（solar filament）图像分割。

- **类型**: Playground（无奖牌）
- **数据**: MAGFiLO 1.0，COCO polygon 标注，2048×2048 灰度图，**仅 19 张训练图**（极小样本分割）
- **目标**: 多类分割（3 类 filament），二值化基线对比

## 核心挑战

**19 张训练图的极小样本分割** —— 这是本赛最大的难点：
- 直接全图训练极易过拟合
- 需要 patch 切片扩样 + 轻量网络 + 混合损失

## 方法

### `solar_v1_unet.py` — U-Net baseline
- 纯 torch 手写轻量 U-Net（无 torchvision/SMP 依赖，本地 CPU 可冒烟）
- 2048² 大图切 **512×512 patch**（每图多 patch 扩样）
- 4 类 filament 合并为二值前景
- 损失：**Dice + BCE 混合**（缓解类别不平衡）
- 本地冒烟：`python solar_v1_unet.py --smoke`；完整训练：`--epochs 30 --patch 512`

### `multiclass_quick.py` — 二值 vs 多类对比
- 3 类 mask（每类一通道）vs 二值 mask 的快速 CPU 冒烟对比
- 验证多类学习是否有增益

### `patch_exp.py` — patch 大小实验
- 对比 128 / 256 patch 的训练信号密度
- 附带 filament 占比分析（`pos_ratio`）

## 实验结果

- 二值 Dice/BCE U-Net 为最终基线
- 多类与二值的差异在 19 图小样本下不显著（CPU 冒烟验证，未跑完整 GPU 训练）

## 复盘

1. **极小样本下 patch 切片是唯一可行的扩样手段**，512 patch 兼顾信号密度与感受野
2. **Dice+BCE 混合损失** 对暗条这种细长稀疏目标（filament 占比常 <5%）比纯 BCE 稳定
3. 该赛定位为 U-Net 分割练手场，未冲榜（Playground 无奖牌），代码沉淀了可复用的纯 torch 分割模板

## 状态

✅ 完赛（无奖牌练习赛，U-Net 分割模板沉淀）
