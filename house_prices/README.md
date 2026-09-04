# House Prices - Advanced Regression Techniques

Kaggle 经典常驻赛(Getting Started,无截止日期):根据 79 个房屋特征
(面积、质量、地下室、车库、年代等)预测房价 **SalePrice**。
回归任务,评分指标为 **RMSE**(预测 log 房价 与 实际 log 房价 之差)。

数据:训练集 1460 行 × 80 列,测试集 1459 行;19/79 个特征含缺失值。

## 项目结构

```
house_prices/
├── data/                          # train.csv / test.csv / sample_submission.csv
├── submissions/
│   ├── submission_baseline.csv    # v1 基线(XGB)
│   ├── submission_v2.csv          # v2 组合特征 + 三模型混合
│   ├── submission_v3.csv          # v3 +CatBoost 四模型混合
│   └── submission_v4.csv          # v4 等权平均(公开榜最佳,最终版)
├── house_prices_baseline.py       # v1: log1p 目标 + Ridge/RF/XGB + 5 折 RMSE
├── house_prices_v2.py             # v2: 10 个组合特征 + Ridge/XGB/LGBM 权重混合
├── house_prices_v3.py             # v3: +MSSubClass 类别化等特征 + CatBoost 入队
├── house_prices_v4.py             # v4: XGB+LGBM+CatBoost 等权平均(最终版)
└── README.md
```

## 提交记录(2026-08-18)

| 版本 | 文件 | 模型思路 | 本地 OOF/CV RMSE | 公开榜 |
|---|---|---|---|---|
| v1 | `submissions/submission_baseline.csv` | log 目标 + Ridge/RF/XGB 5 折,XGB 最优 | 0.1345 | 0.13325 |
| v2 | `submissions/submission_v2.csv` | 10 个组合特征 + Ridge/XGB/LGBM 权重混合 | 0.13008 | 0.12223 |
| v3 | `submissions/submission_v3.csv` | +MSSubClass 类别化等 4 特征 + CatBoost 入队四模型混合 | 0.12598 | 0.12290 |
| **v4(最终)** | `submissions/submission_v4.csv` | **XGB+LGBM+CatBoost 等权平均(不做权重搜索)** | 0.12766 | **0.12196** |

**关键结论**:

- **v2 比 v1 公开榜提升 0.011**(0.13325 → 0.12223),主要来自两块:
  1. **组合特征**(v2 新增 10 个):总面积 `TotalSF`、质量×面积 `QualArea`、
     总浴室数、房龄/翻新年龄、门廊总面积、`HasPool/HasGarage/HasBsmt` 指标
     —— 都是原始列直接计算,无泄漏;
  2. **异构混合**:Ridge + XGB + LGBM 三模型 5 折 OOF,权重网格搜索
     (0.1 步长,归一,最小化 OOF RMSE)得到 `{Ridge:0.2, XGB:0.5, LGBM:0.3}`,
     混合 OOF 0.13008 明显优于单模型最优 0.13322——和 S6E8 的结论一致:
     **异构模型混合 > 单模型调参**。
- **CV 与公开榜方向一致**(本地 0.13008 → 榜上 0.12223),1460 行虽小但
  信号比 Titanic 干净,CV 可信度尚可。
- 参照系:基线 ~0.13-0.15,认真做 ~0.12,头部 ~0.11。**0.12223 已进入"认真做"区间**。

**v3 尝试(2026-08-18)**:新增 MSSubClass 类别化 / QualSF / Has2ndFlr / HasFireplace,
CatBoost(原生类别编码)入队变四模型混合。本地:CatBoost 单模型 OOF 0.12726 最强,
四模型混合 0.12598(权重 `{CatBoost:0.7, XGB:0.2, LGBM:0.1, Ridge:0}`)明显优于
v2;但公开榜 0.12290 **略差于 v2 的 0.12223**(差 0.0007)。**教训**:又一次小样本下
"本地 CV 更优、公开榜未兑现"的案例——0.0007 级别差距部分来自权重搜索(1331 组合)
对 OOF 的轻微过拟合 + 公开榜噪声;**v2 仍是最佳提交**,v3 的 CatBoost 结论保留
(CatBoost 原生类别在房价上确实最强,后续可在 v2 基础上把它换进去再验)。

**v4(最终版,2026-08-18)**:XGB + LGBM + CatBoost 三模型**等权平均**,完全不做
权重搜索。本地 OOF 0.12766(比 v3 加权混合的 0.12598 略差),但公开榜 **0.12196
创最佳**(胜过 v2 0.12223 / v3 0.12290)。**最终教训**:小数据上权重搜索选出的
极端权重(0.7 压单一模型)会过拟合 OOF、吃掉真实收益——等权平均本地 CV 略逊,
但最稳、最能兑现到公开榜。**v4 为最终提交**。

## 使用方法

```bash
# 环境:conda activate kaggle(或直接用 C:\Users\Lenovo\.conda\envs\kaggle\python.exe)
python house_prices/house_prices_baseline.py   # v1
python house_prices/house_prices_v2.py         # v2(当前最佳)
```

### 提交

```bash
# 需先 conda activate kaggle;NO_PROXY 绕过系统代理
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c house-prices-advanced-regression-techniques \
  -f house_prices/submissions/submission_v2.csv -m "说明"
```

## 进阶方向(无截止日期,可慢慢磨)

1. **特征工程深化**(本比赛最大收益来源):面积/质量组合、街区房价中位数
   (但注意防泄漏,只能用训练集算)、强缺失列构造指标(`PoolQC` 缺失率 99%,
   但"有没有泳池"本身是最强特征之一)、`MSSubClass` 类别化处理
2. **模型**:XGB/LGBM 调参 + CatBoost 加入混合(新环境已装)、多种子平均
3. **残差分析**:v2 混合后看哪些房子的残差系统性大(豪宅/新房/特殊街区),
   针对性地加特征
