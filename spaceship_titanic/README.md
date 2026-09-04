# Spaceship Titanic

Kaggle 经典常驻赛(Getting Started,滚动榜):预测 3000 年的星际乘客是否被
"传送"(Transported)到另一维度的空间站。**二分类**,评分指标为 **Accuracy**。

数据:训练集 8693 行 × 14 列,测试集 4277 行 × 13 列。13 个特征含乘客信息
(HomePlanet / CryoSleep / Cabin / Destination / Age / VIP / 5 项消费额 / Name)
与 **PassengerId**(格式 `组号_组内序号`,同一组 = 同行乘客)。

## 项目结构

```
spaceship_titanic/
├── data/                          # train.csv / test.csv / sample_submission.csv
├── submissions/
│   ├── submission_baseline.csv    # v1 基线(GB,0.79401)
│   └── submission_v2.csv          # v2 特征工程 + LGBM/XGB(当前最佳,0.80289)
├── spaceship_baseline.py          # v1: 填充 + one-hot + LR/RF/GB 3 模型 5 折
├── spaceship_v2.py                # v2: Cabin/组规模/消费聚合特征 + LGBM/XGB 混合
└── README.md
```

## 提交记录(2026-08-19)

| 版本 | 文件 | 模型思路 | 本地 OOF/CV | 公开榜 |
|---|---|---|---|---|
| v1 | `submissions/submission_baseline.csv` | 填充 + one-hot + LR/RF/GB,GB 最优 | 0.7928 | **0.79401** |
| **v2** | `submissions/submission_v2.csv` | Cabin 解析 + 组规模 + 消费聚合 + LGBM/XGB,XGB 最优 | 0.8117 | **0.80289** |

**关键结论**:

- **v2 比 v1 公开榜提升 +0.009**(0.79401 → 0.80289),本地 CV 提升 +0.019
  (0.7928 → 0.8117)——CV 方向一致但公开榜兑现打个折(小样本 + 滚动榜噪声)。
- **v2 提升来源**(三块特征工程 + 模型升级,缺一不可):
  1. **Cabin 解析**:`B/0/P` → 甲板字母 Deck + 左右舷 Side——甲板与传送率强相关;
  2. **GroupSize 组规模**:PassengerId 前缀是组号,同行人数是最强特征之一
     (单独出行 vs 多人同行,传送率差异大);
  3. **消费聚合**:TotalSpend + NoSpend(五项消费全 0)+ CryoSpend
     (冷冻中却有消费的异常组合)——CryoSleep=True 的人消费全 0,
     一致性标记捕捉了真实信号;
  4. **模型升级**:LR/RF/GB → LGBM/XGB,树模型 + 更多特征配合更好。
- **格式坑(踩过)**:该比赛提交文件 `Transported` 列**必须是布尔 `True/False`**
  (样例格式),输出 `0/1` 会被整体判 **0 分**(v1 第一次提交 0.00000 即因此)。
  教训:新比赛提交前先看 `sample_submission.csv` 的格式。
- **环境坑**:xgboost 3.2.0 + numpy 2.x 下类别特征用 `category` dtype 会崩
  (`numpy.bool has no len()`),LGBM 可原生处理但 XGB 需要 `enable_categorical=True`,
  最稳做法是 **LabelEncoder 编码成整数**(树模型效果等价)。

## 使用方法

```bash
# 环境:conda activate kaggle
python spaceship_titanic/spaceship_baseline.py   # v1 基线
python spaceship_titanic/spaceship_v2.py         # v2(当前最佳)
```

### 提交

```bash
# 需先 conda activate kaggle;NO_PROXY 绕过系统代理
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c spaceship-titanic \
  -f spaceship_titanic/submissions/submission_v2.csv -m "说明"
```

## 进阶方向(无截止日期,可慢慢磨)

1. **Name 姓氏解析**:同组乘客共享姓氏,可构造"家庭规模"(GroupSize 的精细化版本,
   区分同行朋友 vs 家人);极端情况下同组 6 人是否整组被传送可作为特征
2. **目标编码/统计编码**:HomePlanet × Destination 组合的传送率(注意防泄漏,
   只用训练集折内统计)
3. **模型**:加 CatBoost 入混合(原生类别)、多种子平均、概率校准
4. **缺失模式**:该赛缺失值非 MCAR(全列 ~2% 缺失,疑似整批数据丢失),
   n_missing 已是特征,可再深挖缺失行本身的规律
