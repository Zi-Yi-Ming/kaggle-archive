# RSNA 暴力推进计划（2026-09-20）

原则：可以高频，但 **GPU/提交次数有硬顶**；暴力 = 批量准备 + 串行烧 GPU + 每发可复现，不是乱交。

## 已完成提交

| 分数 | 实验 |
|---|---|
| 0.687 BEST | EXP-004 Axial fold0 |
| 0.685 | EXP-003 S+C fold0 |
| 0.679 | EXP-003 S+C fold0+1 |
| pending | EXP-004 S+C+A fold0 mean fuse（刚交） |

## 硬约束

- GPU 周配额（CLI 曾示约 30h / 刷新 09-26；API 字段另有一套，以 CLI+实跑为准）
- 提交：code competition，约 **5 次/日**
- 公开榜 **3 例**，勿对 ±0.002 过拟合
- 单折实测：Axial 1.81h / S 2–3.6h / C 1.9–2.5h

## 暴力打法（建议执行序）

### Wave A — 融合扫描（低 GPU，多提交）
1. S+C+A mean（已交）
2. 若 <0.687：交 **Axial-only 权重更高** 的 fuse（0.5A+0.25S+0.25C）CPU kernel
3. 若 ≥0.687：锁定多平面，进 Wave B

### Wave B — 标签修复（主 GPU 杠杆）
1. EXP-005 plumbing：GLOBAL_OA + Synovitis 代理进 pseudo 表（改 `rsna_report_labels` + `report_score_to_target`）
2. EXP-006 OA lexicon：`\bOA\b` / chondrosis / compartmens typo
3. 每个变体：**S+C+A fold0 或 best-plane fold0** 重训，单变量
4. 每发 lock sha256 + label_manifest

### Wave C — 平面/训练暴力扫（仍单变量）
1. Axial fold1–2（仅当 Wave A 显示多平面有效）
2. epochs 3→5（Axial-only，便宜）
3. n_clips 2→4
4. 不要同时改 2 个变量

### Wave D — 对标头部（CPU/研究）
- 扫 top public kernels / forum：他们如何做标签与模型
- 若有可用医学预训练 / 更好伪标签源，作为独立 EXP

## 工程模板

- GPU 训练 kernel：`_push_exp00X_*` + 离线 torch wheels + resume artifact
- 提交 fuse kernel：CPU，硬编码/挂载 pred → `submission.csv`
- 提交命令：`kaggle competitions submit -c rsna-knee-abnormality-detection -k <slug> -f submission.csv -v <ver> -m "..."`
- 产物：`rsna_knee/artifacts/` + `_out/*_pull/` + `.agent-memory/rsna-knee-project-state.md`

## 今日剩余可做

1. 等 S+C+A 分数
2. 准备 EXP-005 标签补丁 notebook（CPU 可先本地验证覆盖率）
3. GPU 允许则推 EXP-005 fold0 训练
