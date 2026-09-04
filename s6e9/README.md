# S6E9 — EV Purchase Prediction（Playground S6E9）

## 比赛简介

Kaggle Playground Series Season 6 Episode 9：预测用户是否购买电动汽车（二分类）。

- **类型**: Playground（无奖牌）
- **目标**: 二分类 `Will_Buy_EV`，指标 **AUC**
- **随机基线**: 0.5

## 方法

`cat_quick.py` — CatBoost 快速验证：
- 2 折小样本冒烟（4万行），确认 cat 对混合模型的贡献方向
- 类别特征转 string + `MISSING` 填充，`StratifiedKFold` + `Logloss` + `AUC`

## 当前状态

🟡 进行中（Playground 无奖牌，作为 LGB/XGB/Cat 混合技巧的练手场）
