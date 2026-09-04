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

---

# 🧠 深度复盘(进行中)

## 1. 心理历程:一个"验证混合技巧"的轻量练习场

这个赛是在 kaggriculture(奖牌赛)间隙开的,定位很明确:**Playground 无奖牌,
不值得全力投入,但可以用它验证"LGB/XGB/CatBoost 混合"这套在 S6E8/house_prices
里沉淀的技巧能不能快速迁移**。所以赛初只做了最轻量的动作:
`cat_quick.py` 用 2 折小样本(4 万行)跑 CatBoost 冒烟,确认 cat 对混合的
贡献方向——先花最小成本判断"这条路值不值得走",而不是一上来就堆完整 pipeline。

当时的背景判断:S6E8 已经证明"异构混合 > 单模型",house_prices 证明
"小样本权重搜索会过拟合"。S6E9 是 69 万行级的合成数据(和 S6E8 同属
Tabular Playground),大概率适用同样的结论——先用 cat 冒烟验证,再决定
要不要完整跑三模型混合。

## 2. 方法:复制 S6E8 的成熟模式

```
cat_quick.py(当前唯一脚本)
 ├── StratifiedKFold(2, shuffle, seed 42) 小样本冒烟(4 万行)
 ├── 类别特征 → string + fillna("MISSING")  ← 复用 S6E8 的缺失处理经验
 ├── CatBoost Logloss + AUC
 └── 目的:先确认 cat 贡献方向,再决定是否补 lgb/xgb 完整混合
```

**设计动机**:从 S6E8 学到"缺失非随机、类别要显式处理",从 house_prices 学到
"异构混合最稳"——S6E9 直接套用,不重新发明轮子。

## 3. 尚未做的(等 cat 冒烟结果)

| 待验证 | 预期 |
|---|---|
| cat vs lgb/xgb 单模型对比 | 合成表格上 lgb/cat 通常接近 |
| 三模型异构混合 | S6E8 验证过 +0.004~0.005 级收益 |
| 种子平均 | 消除方差,+0.0003 级 |
| 公开 OOF 库拼接 | S6E8 的终极杠杆(若社区发布) |

## 4. 待沉淀教训(赛后再补)

- 本赛定位是"技巧验证场",核心看混合/种子平均的结论能否复现 S6E8
- 若 cat 冒烟显示贡献方向明确,值得补全混合;若贡献微弱,停止投入(和 S6E8
  手机成瘾赛"不再投入"的决策逻辑一致)
- 完赛后按本仓库标准格式补:心理历程 + 架构演变 + 失败档案 + 武器库
