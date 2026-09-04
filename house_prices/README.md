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
│   └── submission_v4.csv          # v4 等权平均(公开榜最佳,最终版);早期版本见提交记录表
├── house_prices_baseline.py       # v1: log1p 目标 + Ridge/RF/XGB + 5 折 RMSE
├── house_prices_v2.py             # v2: 10 个组合特征 + Ridge/XGB/LGBM 权重混合
├── house_prices_v3.py             # v3: +MSSubClass 类别化等特征 + CatBoost 入队
├── house_prices_v4.py             # v4: XGB+LGBM+CatBoost 等权平均(最终版)
└── README.md
```

## Result

| Metric | Best Score | Best Version | Status |
|---|---:|---|---|
| RMSE (log) | 0.12196 | v4 (equal-weight blend) | Completed |

### Key Finding

小样本上权重搜索选出的极端权重会过拟合 OOF、吃掉真实收益；等权平均本地略逊却最能兑现到公开榜。

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
# 推荐:最终提交版本
python house_prices/house_prices_v4.py         # v4(最终版,XGB+LGBM+CatBoost 等权平均,公开榜 0.12196)
# 历史版本(按需查看演进)
python house_prices/house_prices_baseline.py   # v1 基线(XGB 单模型)
python house_prices/house_prices_v2.py         # v2(组合特征 + 三模型权重混合,公开榜 0.12223)
python house_prices/house_prices_v3.py         # v3(+CatBoost 四模型权重搜索,公开榜 0.12290)
```

### 提交

```bash
# 需先 conda activate kaggle;NO_PROXY 绕过系统代理
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c house-prices-advanced-regression-techniques \
  -f house_prices/submissions/submission_v4.csv -m "说明"
```

> 注:历史版本 `submission_v2.csv` / `submission_v3.csv` 未保留在本地(记录在
> 上方提交表),当前目录的存档提交为最终版 `submission_v4.csv`。

## 进阶方向(无截止日期,可慢慢磨)

1. **特征工程深化**(本比赛最大收益来源):面积/质量组合、街区房价中位数
   (但注意防泄漏,只能用训练集算)、强缺失列构造指标(`PoolQC` 缺失率 99%,
   但"有没有泳池"本身是最强特征之一)、`MSSubClass` 类别化处理
2. **模型**:XGB/LGBM 调参 + CatBoost 加入混合(新环境已装)、多种子平均
3. **残差分析**:v2 混合后看哪些房子的残差系统性大(豪宅/新房/特殊街区),
   针对性地加特征

---

# 🧠 深度复盘(2026-08 完赛归档)

## 1. 心理历程:一次"本地赢了、榜上输了"的反复拉扯

这是我打的第二个表格赛(第一个是 S6E8 手机成瘾)。赛初带着 S6E8 的经验:
**异构混合 > 单模型调参**。v1 用 XGB 单模型跑基线(0.13325),v2 立刻上
"10 个组合特征 + Ridge/XGB/LGBM 权重网格搜索",公开榜直接跳到 0.12223(+0.011),
当时觉得这条路对了——**特征工程 + 权重混合是双杠杆**。

v3 我继续加码:MSSubClass 类别化 + CatBoost(原生类别编码)入队变四模型,
本地 OOF 0.12598 明显优于 v2(0.13008),权重搜出 `{CatBoost:0.7, XGB:0.2...}`
——本地一切都很美。结果公开榜 0.12290 **反而略差于 v2 的 0.12223**。

这是我第一次亲历"本地 CV 更优、公开榜未兑现"的案例(1460 行小样本,
权重搜索 1331 组合对 OOF 的过拟合 + 公开榜噪声,0.0007 级别的差距没法分辨)。
当时的心理是"怎么会?本地明明更优啊"——这促使我做了 v4 的激进实验:
**完全不做权重搜索,三模型等权平均**。结果本地 CV 略差(0.12766),
但公开榜 0.12196 创下全程最佳。

**最终领悟**:小数据上权重搜索选出的极端权重(0.7 压单一模型)会过拟合 OOF、
吃掉真实收益;等权平均本地略逊但最稳、最能兑现到公开榜。这和 S6E8 后期
"权重搜索找到的就是 0.5/0.5"完全呼应——**搜索权重的收益在小样本上可能是幻觉**。

## 2. 架构方法演变:四版本的进化链

```
v1 XGB 基线          (0.13325) → 单模型,确认信号
 │  ↓ 特征工程 + 异构混合(S6E8 经验迁移)
v2 组合特征+三模型权重混合 (0.12223) → +0.011,大跳:特征与混合双杠杆
 │  ↓ 继续加码
v3 +CatBoost 四模型权重搜索 (0.12290) → 本地 0.12598 更优,榜上未兑现(-0.0007)
 │  ↓ 激进实验:放弃权重搜索
v4 三模型等权平均    (0.12196) → 本地略差,公开榜创最佳 —— 最终提交
```

**每个版本切换的动机**:
- v1→v2:S6E8 已验证"异构混合>单模型",直接上组合特征+权重搜索
- v2→v3:相信"更多模型+更细权重=更好",继续堆
- v3→v4:被"本地优榜上差"打脸后,反其道试等权平均,赌"搜索权重在过拟合"
- v4 胜出,验证了赌注

## 3. 失败实验档案(试错记录)

| 实验 | 投入 | 结果 | 教训 |
|---|---|---|---|
| v3 四模型+1331组合权重搜索 | 1天 | 本地 0.12598 最优,榜上 0.12290 反降 | 小样本权重搜索过拟合 OOF |
| CatBoost 单模型 | 半天 | 本地 OOF 0.12726 最强 | 单模型再强也不如混合兑现 |
| 权重搜索极端值 {0.7,0.2,0.1,0} | - | Ridge 权重被压到 0 | 极端权重是过拟合信号 |

## 4. 核心经验教训(武器库)

1. **小样本(千级)权重搜索会过拟合 OOF**:极端权重(0.7 压单模型)是危险信号,
   等权平均最稳、最能兑现(与 S6E8 结论互证)
2. **组合特征(面积×质量等)在房价上收益巨大**:v2 的 +0.011 大半来自 10 个组合特征
3. **CatBoost 原生类别编码在房价上确实最强**(单模型 OOF 0.12726),值得留作混合成员
4. **"本地更优榜上未兑现"在小样本是常态**:0.0007 级差距 = 噪声,别为它重构
5. 参照系:基线 ~0.13,认真做 ~0.12,头部 ~0.11 —— **0.12196 已进"认真做"区间**,离头部还有 0.012 的空间(残差分析+特征深化是主线)
