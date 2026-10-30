# Kaggriculture Workspace

Canonical project: `D:\桌面\Kaggle\kaggriculture`
Last organized: 2026-09-26（B 级清理；赛期 gitignore 不公开）

**生产现状见** `_production/STATUS.md`（截止 2026-09-30；BT 10-01→约10-15）

## Layout
```
_production/     STATUS / MEDAL_PUSH / SCAN_LOG / POST_COMP_GITHUB_OUTLINE
_research/       RESEARCH_*.md + p*.csv + figures/（里程碑写作用）
_scripts/        experiment runners + analysis scripts
_external/       notebooks, extracts, replays, tmp_candidates
reference_agents/ finn + pool
_push_thomas_2945/     PRODUCTION 主力 @~2645–2673 FROZEN（KEEP）
_push_alperen_twin/    last-2 第二槽 path twin（KEEP）
_push_alperen/         历史 alperen（KEEP）
_push_medal/           R2 champion（KEEP）
_push_v16/             历史 last-2（KEEP）
_push_farmv4/          本地强≠LB 对照（KEEP）
_push_tetsu_r3/        historical last-2（KEEP）
_push_v11e_restore/    v11E restore（KEEP）
_push_goodpjw_melon2749/ Validation ERROR 对照（勿交）
_archive/        failed pushes / large traces / historical / submissions
                 └ submissions/root_leaks_20260926/  根目录泄漏归档
```

## Key files
- `_production/STATUS.md`
- `_research/RESEARCH_FINAL_CLOSE.md`
- `_research/p73_top_tape_eval.csv`
- `_archive/submissions/` — root 泄漏的提交包与 timing 元数据
- `_archive/large_traces/` — `_pm_*.jsonl` 历史 trace（约 500MB，只归档不删）

## _archive map
```
failed_pushes/     _push_medal_r*, tetsu_r6, v66_r7, v67（失败实验包，勿提交）
historical_pushes/ _push_v13, _push_wheat
historical/        v13*, _pm_*.py, old notebooks/zips
large_traces/      _pm_*.jsonl + >5MB csv
calibs/            _calib_*.json
logs/              _p*.log/err + misc
build/             _build_*.py + root build/
results/           根目录未进 _research 的结果副本
experiments/       p10_* … p48_traces 等实验包目录
submissions/       提交 tar / manifest / timing / exp260_main.py
audit_tmp/         原根目录与 rsna_knee 下的农场审计材料
tmp_candidates/    原根目录 tmp_* 外部候选
```

## Counts (files on disk)
- _research: 345
- _scripts: 240
- _archive: 694
- _external: 3032
- _push_* kept: alperen/medal/v16/farmv4/tetsu_r3/v11e_restore

## Submit discipline
见 `_production/STATUS.md`：无 new-family gate 不要提交。

## Path notes
- 研究脚本路径多为相对路径；若脚本写死旧根目录散文件路径，改读 `_research/` 或 `_archive/`。
- 本地跑 RSNA resume 时 artifacts 现在在 `rsna_knee/artifacts/`，必要时传 `--artifact-dir`。

## _research sample
- CANONICAL_PATH.txt
- KAGGLE_BENCH_RUN.md
- RESEARCH_CLOSURE_P58_P60.md
- RESEARCH_DAY2_SUMMARY.md
- RESEARCH_FINAL_CLOSE.md
- RESEARCH_FINAL_P9_P40.md
- RESEARCH_H2_BOTTLENECK.md
- RESEARCH_H3_FINAL_GATE.md
- RESEARCH_H3_OPPONENT_SIGNAL.md
- RESEARCH_H5B.md
- RESEARCH_H5_RNG.md
- RESEARCH_P1.md
- RESEARCH_P10_1_EXECUTOR_EXTRACTION.md
- RESEARCH_P10_EXECUTOR.md
- RESEARCH_P11_PLANNER_SEARCH.md
- RESEARCH_P12_1_ROUTING.md
- RESEARCH_P12_PRODUCTION_GAP.md
- RESEARCH_P13_1_MELON.md
- RESEARCH_P13_2_HARVEST.md
- RESEARCH_P13_3_WATER.md
- RESEARCH_P13_4_GENERIC_WATER.md
- RESEARCH_P13_CASH_ENGINE.md
- RESEARCH_P14_1_PORTFOLIO.md
- RESEARCH_P14_2_LIVESTOCK_PORTFOLIO.md
- RESEARCH_P14_PRODUCTION_REGIME.md
- RESEARCH_P15_MULTISTAGE.md
- RESEARCH_P16_1_BRANCH_QUALITY.md
- RESEARCH_P16_SKELETON_BRANCH.md
- RESEARCH_P17_1_CONTINUATION_LIBRARY.md
- RESEARCH_P17_TOP_AGENT_ARCHITECTURES.md
- … +309 more

