# Kaggle Competitions

我的 Kaggle 竞赛记录仓库 —— 收录**无奖牌/练习赛**的完整代码与提交方案。

> 活跃奖牌赛（kaggriculture、rsna_knee）在赛期内不公开，赛后才归档到这里。

## 比赛列表

| 比赛 | 类型 | 截止 | 状态 | 目录 |
|---|---|---|---|---|
| Titanic | Getting Started | - | ✅ 完赛 | [titanic/](titanic/) |
| Digit Recognizer | Getting Started | - | ✅ 完赛 | [digit_recognizer/](digit_recognizer/) |
| House Prices | Getting Started | - | ✅ 完赛 | [house_prices/](house_prices/) |
| Spaceship Titanic | Playground S4E12 | - | ✅ 完赛 | [spaceship_titanic/](spaceship_titanic/) |
| Store Sales | Playground S4E11 | - | ✅ 完赛 | [store_sales/](store_sales/) |
| NLP Getting Started | Getting Started | - | ✅ 完赛 | [nlp_getting_started/](nlp_getting_started/) |
| Smartphone Addiction | Playground S6E8 | - | ✅ 完赛 | [smartphone_addiction/](smartphone_addiction/) |
| LLM Classification Finetuning | Getting Started | - | ✅ 完赛 | [llm_classification/](llm_classification/) |
| S6E9 EV Purchase | Playground S6E9 | 进行中 | 🟡 进行中 | [s6e9/](s6e9/) |
| Solar Filament | Playground S6E6 | - | ✅ 完赛 | [solar_filament/](solar_filament/) |

## 结构约定

每个比赛目录包含：
- `README.md` — 比赛简介、方法、成绩、复盘
- `*.py` / `*.ipynb` — 核心代码（baseline → 迭代版本）
- `submissions/` — 提交 CSV（可选）

## 说明

- `data/` 目录（原始比赛数据）和模型权重不入库（GitHub 单文件限 100MB），需要时从 Kaggle 重新下载
- 各比赛的详细复盘见对应目录的 `README.md`
