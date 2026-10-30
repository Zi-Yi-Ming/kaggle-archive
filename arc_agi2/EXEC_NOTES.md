# ARC Prize 2026 - ARC-AGI-2 执行记录（低投入高赔率策略）

会话日期：2026-10-05。账号：ziyiming（已加入比赛）。

## 一、比赛状态（2026-10-05 实测，Kaggle API）

- 比赛：arc-prize-2026-arc-agi-2，Featured，$700,000（Progress $275k + Grand $275k + Bonus $150k）
- 时间线：Start 2026-03-25；Entry/Merger Deadline 2026-10-26；Final Submission Deadline 2026-11-02 23:59 UTC；Winners 2026-12-04。今天距 Final 还有 28 天。
- 规模：2445 teams / 10356 entrants / 22520 submissions。账号 2026-10-05 已加入（userHasEntered=True）。
- 提交限制：每日 1 次（实测 submission-limits：remaining today 1）。最终最多选 2 个 Final Submission。
- 赛制：Code Competition，必须 Kaggle Notebook 提交；CPU/GPU ≤12h；禁联网；允许外部公开数据与预训练模型；文件名 submission.json；每个 test output 预测 2 个 attempt，任一完全匹配得 1 分，按 task test output 平均。本比赛可用 L4x4（96GB）机型，提交 rerun 时 L4x4 GPU 配额按 2 倍计。
- 数据：test 240 tasks / 259 outputs（隐藏）；evaluation 120 tasks / 172 outputs（公开带 solutions）；training 1000 tasks。
- 榜首：Tufa Labs 83.61（2026-10-03）；2nd rabbithole 80.56；3rd Yi-Chia Chen 77.22；4th nvbanana 76.67；5th _hans 60.42。
- medal 参考（2026-10-05 leaderboard 前 600 名实测）：rank 10≈42.6，rank 20≈33.9，rank 50≈32.6，rank 100≈32.2，rank 122≈32.2，rank 200≈31.8。Top 10（gold）≈43+，silver（~5%）≈32.2，bronze（~10%）≈31.8。

## 二、公开方案 Top 5（均有真实 Kaggle LB 证据）

| # | 方案 | 作者/来源 | 公开 LB | 完整开源 | Kaggle 可跑 | 备注 |
|---|---|---|---|---|---|---|
| 1 | arc-highscore-lb3389-replica（v38 perfpatch） | qiuqiuh（Kaggle notebook，Apache-2.0） | Best 31.81（V1）；Public 30.56；15 versions | 是（9 cells，arc_loader/decoder/solver/starter） | 是：BYOD docker + sorokin patch kernel + sorokin/qwen3_4b_grids15_sft139 + L4x4，全量约 25-30 min | 即 ARC Prize 2025 冠军 NVARC 方案的公开复刻+吞吐补丁 |
| 2 | fork-of-nvarc-plus-adaptive（ARC2 NVARC+ v1） | ghazarosbarseghyan91（Apache-2.0） | 31.81（V1）；55 min 交互 | 是（20 cells，混合 GRPO/MCTS/JEPA + Qwen3.8 27B） | 是（额外挂 foysalemonshanto/qwen3-8-27b-fp8-repacked-v1） | 与 #1 同父本，混合更多组件，分数相同、复杂度更高 |
| 3 | reproduce-nvarc-2025-results | rokaiyasomapti | 32.22（见 discussion 743880） | 是 | 是 | NVARC 原始方案的复现，LP 略高但方差大（同源 23.33 vs 32.22） |
| 4 | twin-lb33-verbatim / nvarc-plus-ckpt | dajaistewart / dalezhong | 31.53 / 30.14 | 是 | 是 | LB33.89 血统的 verbatim 拷贝与 ckpt 变体 |
| 5 | MindsAI & Tufa Labs 2025（3rd, 15.42%） | jcole75/arc_2025_mindsai（GitHub, 全开源, HF 权重） | 2025 私榜 15.42 | 是 | 是（4×L4 ~11h） | 2025 季军完整方案，与 2026 榜首 Tufa Labs 同团队血统 |

公开可验证天花板 = 31.81~32.2（NVARC 血统）。榜首 83.61 的方案未公开（预计 Final 后开源，写 prize 条款要求开源）。

## 三、选定方案（决策）

选定 #1：**qiuqiuh 的 arc-highscore-lb3389-replica（v38）= 原始 LB33.89 baseline 的最小性能补丁**。

理由：
1. 真实 LB 证据链最完整：31.81（该 notebook Best）、30.56/28.47（两个独立复刻）——不是文章/截图。
2. 代码量最小（9 cells / 4 个 writefile），"最小改动复现"成立；rerun 约 25-30 min，远低于 12h 限制。
3. 依赖全部公开合法：Apache-2.0 notebook + Apache-2.0 模型（7.27GB, Qwen3-4B grids SFT）+ 公开 patch kernel；无联网需求（BYOD 镜像已装 unsloth/flash-attn）。
4. 与榜首 Tufa Labs 同技术血统（NVARC TTT），是当前公开界面的实际上限。
5. 无规则冲突：不碰私有数据、不绕限制、不多账号。

## 四、复现设计

- Kernel A（提交版）：对 qiuqiu v38 notebook 的字节级忠实拷贝，slug ziyiming/arc2-nvarc-v38-replica。
- Kernel V（验证版）：同一代码，仅把交互模式的 debug 4-key 过滤器改为全 120 eval keys（rerun 模式下两版代码路径完全一致，不影响提交），用于在公开 eval 集上实测复现成绩。
- 提交：`kaggle competitions submit -c arc-prize-2026-arc-agi-2 -k ziyiming/arc2-nvarc-v38-replica -v <ver> -m "..."`（CLI 支持代码赛提交，触发 rerun）。
- 方差注意：worker 中 scoring-augment seed = `hash(bk) % 1024**2`，Python hash 每进程随机是 run-to-run 方差来源（社区讨论已指出）。Submission B 可用 PYTHONHASHSEED=0 固定（合法的小变化）。

## 五、方案原理（复现代码已读透）

per task：重置 LoRA→augment(n=16) 得 128 条训练样本 TTT 1 epoch（lr 5e-5, seed 42）→augment(n=2) 得 16 条增强推理样本→turbo DFS（12 个 ARC token、max_score=-ln0.2）→每个候选 grid 用 calc_scores（8 条增强样本 teacher-forced NLL）重排→score_kgmon / score_full_probmul_3 选 top-2→submission。4 worker 并行（4×L4）。v38 perfpatch 只把全词表 logits 归一化留在 GPU、仅回传 12 个 ARC token 的 NLL。
