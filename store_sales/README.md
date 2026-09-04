# Store Sales - Time Series Forecasting

Kaggle 常驻赛(无截止日期,滚动榜):预测厄瓜多尔 Favorita 超市
**54 家门店 × 33 个商品类别**的日销售额(2017-08-16 ~ 08-31,16 天窗口),
评分指标为 **SMAPE**(对称平均绝对百分比误差)。

数据:训练集 **300 万行**(2013-01-01 ~ 2017-08-15,6 列),测试集 28512 行;
附带门店表(城市/类型/cluster)、油价(dcoilwtico,43 个缺失)、节假日表
(全国/地方、Holiday/Event/Transfer 等)。

## 项目结构

```
store_sales/
├── data/                          # train.csv / test.csv / stores.csv / oil.csv / holidays_events.csv / transactions.csv
├── submissions/
│   ├── submission_v1.csv          # v1 基线(LGBM,0.47986)
│   └── submission_v2.csv          # v2 时序特征 + 3 种子平均(当前最佳,0.43884)
├── store_sales_v1.py              # v1: 日期特征 + 油价 + 节假日 + LGBM log1p
├── store_sales_v2.py              # v2: 滞后/滚动特征 + 节日距离 + 促销滞后 + 3 种子(可断点续跑)
└── README.md
```

## 提交记录(2026-08-19)

| 版本 | 文件 | 模型思路 | 本地验证(时间窗口) | 公开榜 |
|---|---|---|---|---|
| v1 | `submissions/submission_v1.csv` | 日期分量 + store/family + onpromotion + 油价 + 全国节假日,LGBM 回归 log1p(sales) | SMAPE 0.5656 | 0.47986 |
| **v2** | `submissions/submission_v2.csv` | **滞后特征(lag1/7/364 + 滚动均值 r7/r14/r28) + 节日距离 + 促销滞后 + 油价滞后 + 3 种子 LGBM 平均** | SMAPE ~0.491 | **0.43884** |

**关键结论**:

- **v2 公开榜 0.43884, 比 v1 提升 +0.041**(0.47986 → 0.43884), 已进入头部区间
  (头部 ~0.43-0.44, 基线 ~0.55-0.60)。时序专有特征是这 +0.04 的全部来源:
  滞后销售(去年同天 lag364 的季节项 + 滚动均值 r7/r14/r28 的趋势项)让模型
  能"看到"每个 store×family 自己的近期水平, 这是全局日期特征给不了的。
- **v2 踩了两个导致灾难分的坑(本地验证完全看不出来!)**:
  1. **提交 id 错位**(3.49998 分): 特征工程把 train+test 合并后按
     (store,family,date) 排序, 但提交文件的 id 用了原始 test.csv 顺序
     (date,store,family)→ 预测与 id 整份错位洗牌。教训: **只要对数据做过
     重排, 提交 id 必须从重排后的帧里取**, 不能用原始表;
  2. **测试行滞后特征 NaN 塌陷**(1.76111 分): 合并帧里测试行 sales=NaN,
     8/17 之后的滞后特征(lag1/lag7/r7/r14)全 NaN, 模型把 NaN 路由到
     "冷启动"分支 → 8/23 起预测塌成近 0(均值 469 → 33)。修复: 用每组
     训练期最后一天(8/15)的滞后值只回填测试行, 不碰训练行的冷启动 NaN。
     教训: **验证集表现好 ≠ 测试特征没坏**——必须单独检查测试集特征的
     完整性(按日期看预测分布是最快的 sanity check)。
- **本地验证与公开榜的对应**: v2 本地 ~0.491 vs 公开榜 0.43884, 公开榜更好
  (与 v1 相同的规律: 时间窗口验证偏保守); 但两个坑的分数(3.5/1.76)远高于
  本地, 说明"本地好"和"提交对"是两件事。

## 使用方法

```bash
# 环境:conda activate kaggle
python store_sales/store_sales_v1.py   # v1 基线(当前最佳)
```

### 提交

```bash
# 需先 conda activate kaggle;NO_PROXY 绕过系统代理
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c store-sales-time-series-forecasting \
  -f store_sales/submissions/submission_v1.csv -m "说明"
```

注意:本赛**每日提交上限 5 次**(比 playground 更严), 提交前先在本地用
时间窗口验证确认提升, 避免浪费次数。

## 进阶方向(无截止日期,可慢慢磨)

1. **时序专有特征**(本赛最大提升来源):
   - 滞后特征: 每个 (store, family) 过去 7/14/28 天销售额均值(滚动窗口)
   - 同 (store, family) 前一年同周销售额(季节项)
   - 促销记忆: onpromotion 滞后值(促销影响会延续数天)
2. **节假日精细化**: 不用简单的 is_holiday 标记, 而是"距离最近全国节日的天数"
   + 节日前后窗口、Transfer(调休)单独处理
3. **模型**: 多种子平均、分 (store×family) 粒度单独建模的轻量模型、
   或直接对 SMAPE 优化的目标变换(如 log1p 输出后再做 SMAPE 调参)
4. **交易数据**: transactions.csv 可作辅助(不过它对预测销售的作用有限,
   重点是节日销量提升的线索)
