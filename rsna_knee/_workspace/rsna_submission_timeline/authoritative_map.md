# RSNA 已提交映射（权威）

数据源：Kaggle API `competition_submissions` 的 `url` 字段（提交来源 kernel）+ 本地产物内容匹配。

| ref | date (UTC) | publicScore | source kernel | 判定 |
|---|---|---|---|---|
| 56331070 | 2026-09-18 13:19 | 0.679 | `ziyiming/rsna-exp-003-fold1-s-c-gpu` | EXP-003 S+C fold0+1 ensemble（比 fold0 差） |
| 56299753 | 2026-09-17 08:25 | **0.685** | `ziyiming/rsna-exp-003-s-c-fold0-gpu` | **BEST = EXP-003 S+C fold0** |
| 56256422 | 2026-09-15 14:19 | 0.659 | `ziyiming/rsna-exp-002-a3-fold0-gpu` | EXP-002 a3 fold0 |
| 56203211 | 2026-09-13 08:40 | 0.667 | `ziyiming/rsna-exp-001-fold4-only-gpu` | EXP-001 5-fold Sagittal ensemble |
| 56162074 | 2026-09-11 08:38 | 0.663 | `ziyiming/rsna-exp-001-fold0-probe-gpu` | EXP-001 fold0 single |
| 56139481 | 2026-09-10 07:04 | 0.658 | `ziyiming/rsna-v5-probe-gpu` | BASELINE fold0 |

本地产物内容匹配（max_abs_diff ~1e-8）：

- `submission_exp001_5fold.csv` = exp001 5-fold mean → 已提交 0.667
- `submission_exp002_a3_fold0.csv` = exp002 fold0 → 已提交 0.659
- `submission_exp003_sc_fold0.csv` = exp003 fold0 S+C mean → 已提交 0.685 BEST
- `_out/exp003_fold1_pull/submission.csv` = exp003 fold0+1 S+C mean → 已提交 0.679
- `submission.csv__from_Kaggle` = exp001 fold0 only（不是 5 折）
