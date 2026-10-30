# rsna_knee 结构（2026-09-25 整理）

- `core/` — 辅助脚本（v2/smoke/colab 等）
- `labels/` — 标签抽取器版本副本（exp005/006；根目录仍保留权威副本与 sha）
- `notebooks/` — 历史 notebook / from_root
- `artifacts/` — fold 产物（resume 权威）
- `submissions/` — 本地提交 CSV
- `_push_exp00X*/` — 上传 Kaggle 的 kernel 包（勿散落）
- `_out/*_pull/` — 从 Kaggle 拉回的日志与权重
- `_dataset_stage/` — Dataset 上传暂存
- `_torch_dataset/` — 离线 torch wheels
- `_archive/` — 历史/冒烟/勿删研究物
- `_workspace/` — 本比赛脚本草稿
- `MEDAL_STRATEGY.md` — 冲奖牌公开策略
- 根目录保留核心训练脚本 `rsna_v3.py`、`rsna_report_labels*.py`、数据 CSV、README
