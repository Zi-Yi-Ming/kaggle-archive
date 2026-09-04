# Titanic - Machine Learning from Disaster

Kaggle 经典入门赛：根据乘客信息（性别、舱位、年龄等）预测其是否在泰坦尼克号沉船事故中生还。
二分类任务，评分指标为 **Accuracy（准确率）**。

## 项目结构

```
Kaggle/
├── (conda 环境)              # kaggle: Python 3.11,依赖装在 conda(旧 .venv 已删除)
├── data/                   # train.csv / test.csv / gender_submission.csv
├── submissions/            # 提交文件归档（历史提交都在这里）
│   ├── submission.csv      # v1 基线
│   ├── submission_v2.csv   # v2 调参集成
│   ├── submission_v3.csv   # v3 分组特征
│   ├── submission_v4.csv   # v4 最小可靠模型（新基线）
│   ├── submission_v5.csv   # v5 精细调参 + Stacking
│   └── submission_v6.csv   # v6 同舱/同票组大小特征
├── titanic_baseline.py     # v1 基线脚本：一条命令跑通全流程
├── titanic_improved.py     # v2：调参 + 集成 + 修复分箱方法论
├── titanic_v3.py           # v3：姓氏/票号分组特征 + 多 seed 集成
├── titanic_v4.py           # v4：最小可靠模型（Sex+Pclass+人均票价+年龄）
├── titanic_v5.py           # v5：v4 特征 + RF/GBM 精细调参 + Stacking
└── titanic_v6.py           # v6：v4 特征 + CabinCount/TicketCount 组大小
├── README.md
└── eda_overview.png        # EDA 分析图（运行时生成）
```

## 提交记录（2026-08-18）

| 版本 | 文件 | 模型思路 | 公开榜 |
|---|---|---|---|
| control | `gender_submission.csv` | 性别基线（全体女性生还） | **0.76555** |
| v1 | `submissions/submission.csv` | GBM 默认参数 + 基础特征 | 0.76315 |
| v2 | `submissions/submission_v2.csv` | 调参 LR+RF+GBM 投票集成 | 0.76076 |
| v3 | `submissions/submission_v3.csv` | 姓氏/票号分组特征 + 多 seed 集成 | 0.72248 |
| v4 | `submissions/submission_v4.csv` | 最小可靠模型（Sex+Pclass+人均票价+年龄，RF） | **0.77272**（超过性别基线，最佳） |
| v5 | `submissions/submission_v5.csv` | v4 特征 + RF/GBM 精细调参 + Stacking（选用 TunedGBM） | 0.76794 |
| v6 | `submissions/submission_v6.csv` | v4 特征 + 同舱/同票组大小（无目标泄漏，选用 TunedGBM） | 0.74401 |

**复盘结论**：v1/v2 的 5 折 CV 有 0.83+，但公开榜只有 ~0.76，与性别基线持平 —— 891 行小数据上，树模型学到的"聪明特征"（年龄/票价/称呼）很大程度是训练集噪音，没有迁移到测试集。v3 押注的分组特征（37% 测试乘客能映射到训练集票号组）在公开榜上反而负收益。教训：**公开榜只覆盖约一半测试集（209 行），统计噪音极大，CV 分数要打折扣看待；最终以公开榜为裁判，每次提交都要和性别基线对照**。

**v4 方法论修正（2026-08-18）**：放弃"堆特征 + 堆模型"的思路，回归最小可靠模型（Sex + Pclass + 人均票价 + 年龄，RandomForest）。本地对照结果：

| 模型 | RepeatedStratifiedKFold CV (5x3) | 相对性别规则提升 |
|---|---|---|
| 性别基线规则（女性全活） | 0.7867 ± 0.0209 | —（对照线） |
| LogisticRegression | 0.7898 ± 0.0227 | +0.0030 |
| RandomForest | 0.8130 ± 0.0221 | +0.0262 |

- **对照方法**：模型 CV 分数要和"性别基线规则"在**相同折**上的分数比，而不是只看绝对值。v1/v2 的 0.83 之所以骗人，是因为从没和这条对照线比过。
- **提交健康检查**：v4 与性别基线在 418 行测试集上有 33 行差异（92.1% 一致），其中 7 行"男性被预测生还"——这 7 人全是 Pclass 1/2 的儿童（如 2 岁、6 岁、8 岁男孩），符合"儿童优先逃生"的真实规律，属合理信号而非噪音；另有 26 行是三等舱女性被预测死亡（票价低、生存率本就不高）。提交前用这种逐行差异清单能提前发现行序错位、预测方向异常等问题。
- **本地测试**：`titanic_v4.py` 会同时输出以上全部对照数据，跑一次就能看到。

**v5 尝试（2026-08-18）**：在 v4 同款 4 特征上做 RF/GBM 精细调参（补搜 max_features / subsample）并尝试 Stacking（RF+GBM 基学习器 + LR meta）。本地 CV：TunedGBM 0.8249 > Stacking 0.8238 > TunedRF 0.8210（均远超性别规则 0.7868），但公开榜只有 0.76794，反而低于 v4 的 0.77272。**教训补充**：本地 CV 三个模型只差 ±0.004（209 行公开榜的噪声就比这大），模型之间的 CV 微小差距在公开榜上不可靠——v4 的"简单 RF + 不过度调参"仍是最稳的基线，参数微调对 891 行数据的收益接近零。

**v6 尝试（2026-08-18）**：在 v4 特征基础上加两个【无目标泄漏】的组大小特征——CabinCount（同舱人数）、TicketCount（同票人数），在 train+test 拼接集上统计、完全不碰标签（避开 v3 的组生存率泄漏）。本地 CV 创下新高：TunedGBM 0.8356（相对性别规则 +0.0488），但公开榜只有 **0.74401**，比性别基线还低 0.02，是所有版本最差。**两个附加发现**：(1) v6 初版有个实现 bug——缺失舱位被 `fillna("NONE")` 后当成 1014 人的巨型分组，修正为缺失→0 后 CV 几乎不变（0.8356），说明该退化不影响 CV，但提交时用的是 buggy 版；(2) 修正版预测 25 名男性生还（v4 只有 7 名），模型越"敢"偏离性别规则，公开榜越差。**最终教训**：本地 CV 与公开榜在"特征复杂度"维度上呈负相关——v4 最简单（4 特征）反而最优（0.77272），v6 最复杂（6 特征 + 最深调参）反而最差（0.74401）；这个比赛的公开榜几乎只奖励"女性生还"这条规则，额外特征在该榜上全是负资产。**v4 仍是最终提交**。

## 快速开始

### 1. 准备数据

从 [比赛页面 → Data 标签](https://www.kaggle.com/competitions/titanic/data) 下载
`train.csv` 和 `test.csv`，放进 `data/` 目录。

> 需要先注册 Kaggle 账号并同意比赛规则才能下载。

### 2. 激活环境（可选）

```bash
conda activate kaggle    # 推荐环境:Python 3.11,依赖齐全(旧 .venv 已于 2026-08-18 删除)
# 或直接调用 C:\Users\Lenovo\.conda\envs\kaggle\python.exe 运行，不用激活
```

### 3. 运行基线脚本

```bash
python titanic_baseline.py   # 需先 conda activate kaggle
```

脚本会依次执行：

| 步骤 | 内容 |
|---|---|
| 加载 | 读取 train.csv / test.csv，文件缺失会给出提示 |
| EDA | 打印缺失值、生存率分布，生成 `eda_overview.png` |
| 特征工程 | 提取 Title 称呼、FamilySize 家庭规模、IsAlone、Cabin 甲板号；按分组中位数补全 Age；Age/Fare 分箱；类别特征 one-hot |
| 交叉验证 | 5 折 StratifiedKFold，对比逻辑回归 / 随机森林 / 梯度提升的准确率 |
| 提交 | 用最佳模型预测测试集，生成 `submissions/submission.csv` |

### 4. 提交

在 Kaggle 比赛页面 → **Submit Prediction** → 上传 `submission.csv` → 看 Public Leaderboard 分数。

## 常见问题

**Q: 为什么分数只有 0.78 左右？**
A: 这是正常的 baseline 水平（性别 baseline 是 0.77，全猜 0 是 0.62）。
提升方向：调参（`GridSearchCV`）、加特征（票价分箱细化、名字里的家庭组合）、换模型（XGBoost / 集成投票）。
认真做可以到 0.80+，头部解法在 0.82 左右。

**Q: 想改参数怎么办？**
A: 直接改 `titanic_baseline.py` 里 `make_models()` 中的模型参数，或者用
`from sklearn.model_selection import GridSearchCV` 做网格搜索。

**Q: 我想在 Kaggle Notebook 里跑同一份代码？**
A: 可以。把 `titanic_baseline.py` 的内容粘进 Notebook，数据加载部分改成
`/kaggle/input/titanic/train.csv` 即可（Kaggle 环境自带全部依赖）。

## 进阶路线

1. **调参**：对 RandomForest 的 `n_estimators / max_depth / min_samples_leaf` 做网格搜索
2. **新特征**：票价按 Pclass 分组分箱、提取名字中的家庭姓氏、SibSp/Parch 组合成家族关系网
3. **模型融合**：Stacking（逻辑回归做 meta-learner）或简单投票
4. **阅读经典 Kernel**：比赛页面 Code 标签按票数排序，`Titanic Data Science Solutions` 是最好的入门教程
