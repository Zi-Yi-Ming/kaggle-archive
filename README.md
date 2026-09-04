# Kaggle Competitions

我的 Kaggle 竞赛实验归档：记录每个比赛的实验过程、失败教训与方法迁移，而不是只留结果。

## What this archive is

- 可公开的 Kaggle 学习/竞赛归档，共 10 个无奖牌或已完赛的比赛
- 每个比赛目录含：README（结果记录 + 深度复盘）+ 迭代代码 + 提交 CSV
- 重点保留**实验过程、失败记录、方法迁移**——复盘与代码同等重要
- 活跃奖牌赛（kaggriculture / rsna_knee）**赛期内不公开**，赛后归档到此仓库
- 本仓库不包含任何奖牌赛代码、不虚构排名或成绩

## Learning Path

这些比赛按我实际的学习顺序排列，每一阶段解决的问题不同：

```
Baselines & Controls (Titanic)
        ↓  对照线思维、CV 与公开榜脱节、小样本防过拟合
Feature Engineering & Ensembling (House Prices, Spaceship Titanic, S6E8)
        ↓  domain-aware 特征、异构集成、OOF 混合
Time-Series Forecasting (Store Sales)
        ↓  lag/rolling 特征、提交正确性、灾难调试
Computer Vision (Digit Recognizer, Solar Filament)
        ↓  模型归纳偏置匹配、极小样本 patch pipeline
Pretrained NLP (NLP Disaster Tweets, LLM Classification)
        ↓  预训练 > 从零训练小语料、离线权重挂载
Competition / Systems Thinking (kaggriculture — 赛后归档)
        ↓  共享市场博弈、对手状态估计、Elo 赛制策略
```

## Featured Cases

### Titanic — Control-Line Thinking
891 行小样本的经典教训：本地 CV 0.83 与公开榜 ~0.76 脱节后，学会**模型分数必须与规则对照线（性别基线）在相同折上比较**；最终胜出的不是最复杂的模型，而是 4 特征的最简模型。
[→ titanic/](titanic/)

### Store Sales — Submission Correctness
时序赛核心：lag/rolling 特征贡献 +0.04 进头部区间，但两次"本地完全看不出来"的灾难分（提交 id 错位 3.50、测试滞后特征 NaN 塌陷 1.76）证明——**提交正确性与模型质量是两件事**。
[→ store_sales/](store_sales/)

### Smartphone Addiction (S6E8) — OOF Ensemble & Borrowing
69 万行合成表格：单模型调参到顶后，真正的收益来自**异构集成 + 拼接社区公开 OOF 库**（74 模型，rank 归一化解决 log-odds 量纲陷阱，嵌套 CV 防过拟合），公开榜 0.97033。
[→ smartphone_addiction/](smartphone_addiction/)

## Competition Archive

| 比赛 | Metric | Best Score | Best Version | Status |
|---|---:|---|---|---|
| [Titanic](titanic/) | Accuracy | 0.77272 | v4 | Completed |
| [Digit Recognizer](digit_recognizer/) | Accuracy | 0.98778 | CNN | Completed |
| [House Prices](house_prices/) | RMSE (log) | 0.12196 | v4 | Completed |
| [Spaceship Titanic](spaceship_titanic/) | Accuracy | 0.80289 | v2 | Completed |
| [Store Sales](store_sales/) | SMAPE | 0.43884 | v2 | Completed |
| [NLP Disaster Tweets](nlp_getting_started/) | F1 | 0.83174 | v3 | Completed |
| [Smartphone S6E8](smartphone_addiction/) | AUC | 0.97033 | v6 | Completed |
| [LLM Classification](llm_classification/) | LogLoss | —¹ | v1 | Completed |
| [Solar Filament](solar_filament/) | —¹ | —¹ | U-Net | Completed |
| [S6E9 EV Purchase](s6e9/) | AUC | —² | —² | In progress |

¹ 练习赛/无最终成绩记录（以方法验证为主，详见各自 README）。
² 进行中，未提交最终版本。

## Methodology Across Competitions

不同数据规模下我的策略是**条件化的**，不是放之四海皆准的规则：

- **小样本（千行级）**：baseline + 规则对照线 + 警惕过拟合（Titanic：CV 0.83 上不了榜，简单模型胜出）
- **中等规模表格**：domain-aware 特征工程 + 异构混合（House Prices / Spaceship：特征要还原数据背后的真实结构）
- **大规模表格**：异构集成 + OOF 库混合，单模型调参收益趋零（S6E8：+0.004 来自拼 OOF 库而非调参）
- **时间序列**：lag/rolling 特征为主，提交正确性检查优先于模型优化（Store Sales）
- **图像**：匹配模型归纳偏置（CNN > MLP），极小样本用 patch pipeline（Solar：19 张图）
- **NLP**：预训练模型微调 > 从零训练小语料（BERT 语义来自预训练语料，7613 条推文只负责微调）
- **练习赛**：优先验证可迁移技术，不无限冲榜（LLM 赛是为 RSNA 的 distilbert 分支做预演）

## Repository Structure

```
Kaggle/
├── README.md                  # 本文档（landing page）
├── .gitignore                 # data/、模型权重、活跃奖赛已排除
├── <competition>/             # 每场比赛一个目录
│   ├── README.md              # 结果记录 + 深度复盘（四段式）
│   ├── *.py                   # 迭代代码（baseline → 各版本）
│   ├── submissions/           # 提交 CSV 存档（保留最佳版本）
│   └── data/                  # 原始数据（gitignore，不入库）
```

每个比赛 README 的统一结构：
1. **Result** — Metric / Best Score / Best Version / Key Finding
2. 结果记录 — 简介、项目结构、提交记录表
3. 深度复盘 — 心理历程、架构方法演变、失败实验档案、核心经验教训

## Reproducibility

- 原始比赛 `data/` 不入库（GitHub 单文件限 100MB），需要时从 Kaggle 重新下载
- 大型模型权重 / OOF 资产不入库（如 smartphone_addiction 的 `public_oof/`）
- 环境按比赛分别定义，不提供统一 requirements（各比赛依赖差异大）：
  - 表格赛（titanic/house_prices/S6E8 等）：`kaggle` conda 环境，Python 3.11
    （numpy/pandas/sklearn/lightgbm/xgboost/catboost/optuna）
  - CNN 赛（digit_recognizer/solar_filament）：另需 torch（CPU 版镜像）
  - NLP 赛（nlp_getting_started/llm_classification）：另需 transformers，
    distilbert 微调建议在 Kaggle Notebook + GPU 上跑
  - 各比赛 README 的"使用方法"一节写明本赛可复现的命令
- 提交 CSV 保留存档，命令见各比赛 README

## Active Competitions

`kaggriculture`（Featured, Simulation）与 `rsna_knee`（Research, Medical Imaging）
是两个仍在进行的奖牌赛，赛期内代码不公开。赛后（或赛期允许后）归档到本仓库。

---

Last updated: 2026-09-04
