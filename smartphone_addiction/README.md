# Smartphone Addiction — Tabular Playground S6E8

Kaggle 官方月度练习赛(Tabular Playground Series - Season 6 Episode 8):
根据手机使用行为数据(屏幕时间、社交媒体时长、游戏时长、睡眠、通知数等)
预测是否成瘾(addicted_label),二分类,评分指标为 **AUC**。

赛程:2026-08-01 ~ 2026-08-31。数据为合成生成(信号干净、缺失为 MCAR),
训练集 69.1 万行 / 测试集 29.6 万行。

## Result

| Metric | Best Score | Best Version | Status |
|---|---:|---|---|
| AUC | 0.97033 | v6 (OOF blend) | Completed |

### Key Finding

单模型调参到顶后，真正收益来自 OOF ensemble——拼接社区公开 OOF 库（74 模型 + rank 归一化解量纲陷阱 + 嵌套 CV 防过拟合），而非继续微调单模型。

## 项目结构

```
smartphone_addiction/
├── data/                    # train.csv / test.csv / sample_submission.csv
├── submissions/
│   ├── submission_v4.csv           # v4 三模型异构混合(见提交记录表)
│   ├── submission_v6_sel_opt.csv   # v6 公开 OOF 库混合(最佳,0.97033,最终提交)
│   ├── submission_v6_sel_opt_repro.csv  # v6 复现版
│   ├── submission_v7_lrstack_all81.csv  # v7 后续实验(记录在 Kaggle 历史)
│   └── submission_v8_gbdt_stack.csv     # v8 后续实验(记录在 Kaggle 历史)
├── smartphone_baseline.py   # v1: LR/RF 基线 + 单特征对照线 + 5 折 CV
├── smartphone_v2.py         # v2: LightGBM 原生缺失/类别 + n_missing 特征 + 集成
├── smartphone_tune.py       # 调参脚本:15 万行子样本扫描 LGBM 参数
├── smartphone_v3.py         # v3: 调参后 LGBM + 交互特征对比
└── README.md
```

## 提交记录(2026-08-18)

| 版本 | 文件 | 模型思路 | 本地 AUC | 公开榜 |
|---|---|---|---|---|
| v1 | `submissions/submission_baseline.csv` | LR/RF 5 折 CV,RF 0.9303 | 0.9303 | 0.93171 |
| v2 | `submissions/submission_v2.csv` | LightGBM(原生 NaN/类别 + 早停)+ n_missing 特征 | 0.9635 | 0.96518 |
| v3 | `submissions/submission_v3.csv` | 调参后 LGBM(mcs=100);交互特征被 OOF 否决 | 0.96343 | 0.96507 |
| v4 | `submissions/submission_v4.csv` | LGBM+XGB+CatBoost 异构集成(权重混合,Kaggle Notebook 上跑) | 0.964+(Kaggle OOF) | 0.96584 |
| v5 | `submissions/submission_v5.csv` | v4 + 种子平均(3 seeds)+ 0.01 步长权重搜索 | lgb+xgb 0.96424 | 0.96578 |
| **v6** | `submissions/submission_v6_sel_opt.csv` | **公开 OOF 库混合(74+FM5+本地2,rank 归一化 + optuna 权重,精选 14 成员)** | **0.96925** | **0.97033** |

**v6 结论(2026-08-21)**:v5 的种子平均+权重搜索到顶了(混合 OOF 0.96424,
权重搜索找到的就是 0.5/0.5,LR stacking 反而更差 0.96418),真正的杠杆是
**拼接入公开 OOF 库**(`szymonkapiski/s6e8-oof-library-47-models` 74 模型 +
`raykkretzschmar/s6e8-fm-lattice-blend-members` 5 个因子分解机,本地数据在
`public_oof/`):
- **折方案验证**:公开库用 `StratifiedKFold(5, shuffle, random_state=42)`,
  与本地 v4/v5 完全一致,5 折 va_idx 逐折比对全部相等,可直接拼接。
- **对齐验证**:74 个成员重新计算的 OOF AUC 与 manifest 逐位一致(±0.00000)。
- **量纲陷阱**:FM 库成员输出 log-odds(-14~+48)而非概率,直接等权平均会被
  污染(提交概率均值 1.96!)。解法:全部成员统一 **rank 归一化**
  (`rankdata(x)/N`,对 AUC 单调无损),再混合。
- **选择**:0.98 相关性去冗余 81→14 成员;optuna(softmax 权重)在精选集上
  OOF **0.96925**;嵌套 CV(外层 5 折)验证 optuna 比等权真实 +0.0065,
  非过拟合。
- 公开榜 **0.97033**,比 v4 提升 **+0.00449**,与公开库作者自述的 0.97062
  (54 成员全混合)非常接近,排名进入前列。

**关键结论**:

- **本地 CV 与公开榜几乎一致**(v1: 0.9303 vs 0.93171;v2: 0.9635 vs 0.96518)。
  与 Titanic 的严重脱节(0.83 CV vs 0.76 榜)形成鲜明对比——脱节的主因是
  **样本量太小**(891 行),69 万行的合成数据信号干净可迁移,CV 就是可信的。
- **LightGBM 对缺失值多的表格数据碾压 RF**:原生处理 NaN + 类别特征,
  5 折 OOF AUC 0.9635 vs RF 0.9298(+0.034),且训练速度更快(5 折仅 69 秒)。
- **n_missing 特征**(每行缺失字段数)有真实信号——合成数据的缺失不是随机的。

**v3 尝试(2026-08-18)**:调参 + 交互特征,结论是**两者都没有提升**:
- 参数扫描(15 万行子样本,2 折 OOF):最优仍是 `num_leaves=63, lr=0.05`,
  `min_child_samples=100` 比 v2 的 200 只有 +0.0001 级别的变化(子样本 0.95595 vs 0.95564)。
- 3 个交互特征(屏幕时间×通知数、社交+游戏、周末-平日)在同一 5 折下
  **反而略降**(X16 0.96325 < X13 0.96343)——LightGBM 的树分裂本身就能学交互,
  显式添加在合成数据上没有收益。
- 公开榜验证:0.96507 vs v2 的 0.96518,差 0.0001,纯噪声,**v2 仍是最佳提交**。
- **教训**:到 0.96+ 这个水平,单模型调参和手工特征工程的边际收益已经接近零,
  再往上是多模型异构集成(不同种子/不同库/不同特征视图)的天下。

## 运行环境(2026-08-18 起)

推荐使用新 conda 环境 **kaggle**(Python 3.11,完整现代依赖栈):

```bash
conda activate kaggle
# 或直接调用:C:\Users\Lenovo\.conda\envs\kaggle\python.exe
```

新环境版本:numpy 2.4.6 / pandas 3.0.5 / scikit-learn 1.9.0 / lightgbm 4.7.0 /
xgboost 3.2.0 / catboost 1.2.10 / optuna 4.9.0 / pyarrow 25.0.1 —— 之前 py3.8
的 `.venv` 装不了的 XGBoost / CatBoost / Optuna 现已全部可用。

旧 `.venv`(py3.8)已于 2026-08-18 删除,环境只保留 kaggle 一个(迁移验证过:
titanic_v4 与 smartphone_v2 在新环境下输出与旧环境逐位一致)。

## 使用方法

```bash
# 先激活:conda activate kaggle
# 推荐:最终最佳版本(v6 公开 OOF 库混合,详见提交记录表)
#   v6 依赖 public_oof/(社区 OOF 库,未入库),由 smartphone_v6_final2.py 等生成
# 可独立复现的历史版本:
python smartphone_addiction/smartphone_baseline.py   # v1 基线(RF)
python smartphone_addiction/smartphone_v2.py         # v2(LightGBM,历史最佳,0.96518)
```

### 提交

```bash
# 本机 kaggle CLI 需要绕过系统代理才能连接
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c playground-series-s6e8 \
  -f smartphone_addiction/submissions/submission_v6_sel_opt.csv -m "说明"

# 其他存档提交见 submissions/(v4 为 LGBM+XGB 混合;v7/v8 为后续实验,记录在 Kaggle 历史)
```

# 查询分数
NO_PROXY="*" ... kaggle competitions submissions -c playground-series-s6e8
```

注意:**每日提交上限 10 次**(`maxDailySubmissions: 10`),提交前先在本地
确认 CV 提升再提交,避免浪费次数。

## 在 Kaggle Notebook 上跑 v4(异构集成,推荐)

本地 CPU 跑 CatBoost 太慢(单折 2-3 分钟,5 折要分 5 次 300 秒续跑),而 Kaggle
Notebook 有 12 小时运行上限 + 可选 GPU。`smartphone_kaggle.py` 就是为此准备的:

1. 打开 https://www.kaggle.com/code → **New Notebook**
2. 右侧 **Settings → Accelerator** 选 **GPU T4**(CatBoost 快几十倍)
3. **Add Input** → 搜索 **playground-series-s6e8** 挂载比赛数据(**必须挂载**;若忘记挂,脚本会自动用内置 `kagglehub` 下载兜底,但挂载是官方推荐做法)
4. 把 `smartphone_kaggle.py` 内容粘贴进单元格运行
   (或上传文件后执行 `!python smartphone_kaggle.py`)
5. 运行完输出 `/kaggle/working/submission_v4.csv` → 右侧 **Submit to Competition** 直接提交

脚本自动适配:优先扫描 `/kaggle/input/` 下挂载的数据(不依赖固定目录名);若没挂载,
自动用内置 `kagglehub` 下载比赛数据(需联网);本地运行则用本地 `data/`。
检测到 GPU 自动启用,否则 CPU 兜底。实际结果:三模型 5 折 OOF + 权重混合,
**公开榜 0.96584(当前最佳,超过 v2 的 0.96518)**。

> 注:本地 `smartphone_v4.py` 是可断点续跑的版本(每折存 npy,重跑自动跳过),
> CatBoost 已完成 1/5 折;想本地跑完就反复执行 `python smartphone_v4.py` 直到
> 输出提交文件。本地已修复混合权重归一 bug(lgb+xgb 混合 OOF 0.96417 > 单模型最高
> 0.96373),当前磁盘上的 `submission_v4.csv` 为 LGBM+XGB 临时版(合法可提交)。

## 在 Kaggle Notebook 上跑 v5(种子平均 + 权重搜索,推荐)

`smartphone_v5.py` 是 v4 的升级版:每个模型跑 3 个种子(42/7/2026),同折预测平均
消除方差,再用 0.01 步长权重搜索。本地验证:**lgb 种子平均 OOF 0.96374 > 单种子
最佳 0.96343(+0.00031)**;lgb+xgb 种子平均混合 OOF 0.96424 > v4 单种子 0.96417。
完整版(含 CatBoost)必须在 Kaggle Notebook 上跑(GPU):

1. 打开 https://www.kaggle.com/code → **New Notebook**
2. **Settings → Accelerator** 选 **GPU T4**(CatBoost 快几十倍)
3. **Add Input** → 搜索 **playground-series-s6e8** 挂载数据(自动兜底 kagglehub)
4. 把 `smartphone_v5.py` 内容粘贴进单元格运行
   (或上传文件后执行 `!python smartphone_v5.py`)
5. 运行完输出 `/kaggle/working/submission_v5.csv` → **Submit to Competition**
6. 本地可断点续跑:反复 `python smartphone_v5.py --models lgb,xgb` 先补 CPU 快的;
   cat 折文件在本地只完成了 seed42 的 f0,其余留给 Notebook 跑

> 本地已有文件:lgb/xgb 的 3 种子全部 5 折完成(seed42 复用 v4 旧文件,自动复制为
> `_s42_` 命名);脚本子集运行不写提交文件,完整集合完成才写盘。

## 进阶方向(截止 8/31 前可选)

1. **LightGBM 调参**(num_leaves / learning_rate / min_child_samples)
2. **交互特征**:屏幕时间 × 通知数、社交 × 游戏等成瘾强相关组合
3. **XGBoost/CatBoost 多模型集成**(venv 里还没有,需要装)
4. **概率校准 + 加权混合**(v2 的 Blend 是简单平均,加权/搜索权重通常更好)
5. 公开高分解法参考:S6E8 OOF 库(74 个模型的 OOF/test 预测,可直接学习特征与混合思路)

---

# 🧠 深度复盘(2026-08 完赛归档)

## 1. 心理历程:一场"以为在堆特征,实际在找杠杆"的比赛

赛初我的第一反应和大多数表格赛选手一样:**先跑基线确认信号强度**。
v1(LR/RF)5 折 CV 0.9303,公开榜 0.93171——信号干净、CV 可信,这是个"能打"的赛。

第二阶段我犯了一个典型误区:**以为提升要靠特征工程和调参**。
我花了一天做参数扫描 + 3 个交互特征(屏幕时间×通知数、社交+游戏、周末-平日),
结果 OOF 纹丝不动(0.96343 → 0.96325,交互特征反而略降)。
当时的心理是"怎么会没用?LightGBM 不是靠特征吃饭吗?"

这个打击其实是最有价值的转折点。我意识到:**树模型的分裂本身就在学交互**,
手工加交互在合成数据上等于给模型喂它已经会的东西。真正拉开差距的是——
**在 OOF 都到 0.96+ 之后,单模型的一切(调参/特征)边际收益趋近于零,
剩下的杠杆只有两个:异构集成、借力(公开 OOF 库)**。

于是后面每一步都是围绕"杠杆"展开:
v4 三模型异构混合(0.964+)、v5 种子平均+权重搜索(到顶 0.96424)、
v6 拼公开 OOF 库(0.96925,最终 0.97033)。回头看,
**这场比赛的真正赢点是最后一步的"借力思维"——不是自己造更多模型,
而是把社区 79 个现成模型的 OOF 拼进来**。

## 2. 架构方法演变:六个版本的进化链

```
v1 RF 基线          (0.9303)  → 确认信号强度,CV=公开榜(合成数据可信)
 │  ↓ 换对模型:LightGBM 原生处理 NaN/类别
v2 LGBM+缺失特征    (0.9635)  → +0.034,本赛最大单跳(选对模型 > 一切调参)
 │  ↓ 误入歧途:调参+交互特征
v3 调参+交互        (0.96343) → OOF 否决,交互特征反降——树自己会学交互
 │  ↓ 转向异构集成
v4 LGBM+XGB+Cat    (0.964+)  → 三模型 5 折 OOF 权重混合,集成>单模型
 │  ↓ 消除方差
v5 种子平均+权重搜索 (0.96424) → 到顶:搜索找到的就是 0.5/0.5,LR stacking 更差
 │  ↓ 借力社区
v6 公开OOF库拼接    (0.96925) → 74+5FM+本地2,rank 归一化+optuna 精选 14 成员
 │
 └─ 公开榜 0.97033,接近公开库作者自述的 0.97062(54 成员全混合)
```

**每个版本切换的动机**:
- v1→v2:基线确认后,直接换"最擅长表格缺失"的 LightGBM(不是先调参)
- v2→v3:误以为特征工程是下一杠杆(被否决,但确认了"模型已饱和"的判断)
- v3→v4:确认单模型饱和后,立刻转向多模型异构(杠杆转移)
- v4→v5:集成后先消方差(种子平均),再做权重搜索(发现到顶)
- v5→v6:本地杠杆耗尽 → 外部借力(公开 OOF 库是当时唯一剩的杠杆)

## 3. 失败实验档案(试错记录)

| 实验 | 投入 | 结果 | 教训 |
|---|---|---|---|
| 参数扫描(15万行×2折) | 半天 | num_leaves=63/lr=0.05 已是局部最优,+0.0001 级 | 0.96+ 后调参收益≈0 |
| 3 个交互特征 | 半天 | X16 0.96325 < X13 0.96343 | 树模型自己学交互,手工加无效 |
| v5 权重搜索(0.01 步长) | 1天 | 找到 0.5/0.5;LR stacking 0.96418 更差 | 高基线上权重搜索过拟合 OOF |
| FM 库直接等权平均 | 半小时 | 提交概率均值 1.96(污染!) | log-odds 量纲陷阱,必须 rank 归一化 |

**最痛的一课是 FM 量纲陷阱**:公开库的 FM 成员输出 log-odds(-14~+48)
而非概率,直接等权平均会把整个提交污染到概率均值 1.96(非法输出)。
修复:全部成员统一 rank 归一化(`rankdata(x)/N`,对 AUC 单调无损)。
**任何外部预测库接入前,先验证量纲,再谈混合**。

## 4. 核心经验教训(武器库)

1. **选对模型 > 一切调参**:RF→LGBM 单跳 +0.034,后面所有调参/特征加起来不到 +0.001
2. **合成数据(69万行)CV=公开榜**,可大胆用本地 OOF 决策;小样本(891 行 Titanic)会脱节
3. **树模型自学会交互**:显式加交互特征在合成表格上是负收益
4. **0.96+ 的杠杆在异构集成与借力**,不在单模型
5. **权重搜索会过拟合 OOF**:高基线时等权平均最稳(house_prices v4 再次验证)
6. **拼外部 OOF 库三件套**:折方案对齐验证 → 量纲统一(rank 归一化) → 去冗余(0.98 相关性)再搜索权重
