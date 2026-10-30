# EXP-9 Phase 0+1 报告：Current Public Tape Benchmark（基础设施审计 + 候选研究）

日期：2026-09-07 ｜ 研究范围：截至 2026-09-07 的 Kaggriculture public meta

## 一、Phase 0：实验基础设施审计（全部可复用，无需重写）

| 项 | 状态 | 说明 |
| --- | --- | --- |
| **production fingerprint** | ✅ | `kaggriculture/main.py` md5 = `224a1c47cf9b07624f5faabbb5227891`（与 cleo_v11_E_backup.py 逐字节一致），冻结 |
| **engine** | ✅ | kaggle_environments 1.32.7（已装入本地 conda kaggle 环境） |
| **可复用 runner** | ✅ | `phase5_bench.py`（mp.Pool 并行 + fixed-RNG `env.info["seed"]` + jsonl 追加，EXP-8 跑过 1110 局）、`phase5_agg.py`（Wilson CI + paired permutation + route breakdown）、`forensic_a6.py`（逐步 diff） |
| **可复用 accounting** | ✅ | `executed_ledger.py`（A6 修复后：引擎原语重放、per-unit lockstep 成交价、reconciliation==0 硬门——EXP-8 1110 局全过，校验 closer_cleo 池 100%） |
| **baseline 方法** | ✅ | fixed-RNG paired seeds 1-120（座位按 seed 奇偶，双 seat 覆盖）+ 对手池（closer_cleo 120 + 异构 5 对手 ×50）+ executed reconciliation 审计 + 守恒复核 |
| **EXP-8 数据** | ✅ | `phase5_bench.jsonl`（1110 局原始记录，可作对手/seed 复用参考） |

> 结论：T0 = v11E 的 benchmark 管线（runner/accounting/统计/对手池）全部就绪，EXP-9 只需接入 T1 动作流。

## 二、Phase 1：Public Tape 候选研究

### 2.1 检索方法（如实记录）

- Kaggle Discussion **739273 / 737764 / 732902** 直接抓取失败（JS 渲染需登录，`web_fetch` 无正文）——**间接证据**（仅经 web search 片段了解生态）
- 替代通道：web_search + `kaggle CLI` 文件核验（`kaggle datasets files/download`，NO_PROXY="*"）——**两个数据集资产已核验存在并下载关键 CSV**

### 2.2 Candidate Public Tape Table

| candidate | source | date | episode/submission | tape 长度 | agent 类型 | reproducible | freshness | evidence |
| --- | --- | ---: | --- | ---: | --- | --- | --- | --- |
| **C1：カワシギ rank-1 stream** | destbreso/kaggriculture-top10-replay-streams | 2026-08-15 快照 | submission **55425101**（rank 1，ladder 3282.6，222 局） | 720 步 ✓（全 1482 局均 720） | 当前 ladder 头名公开提交（replay/tape 类，见 discussion 738727 生态） | 高：streams.parquet 全文 farmer+market 动作 + episodes.csv 含 engine seed | 08-15（快照日；ladder 每日变动） | **强**：真实 ladder rank-1 + 222 局样本 + 1.32.7 |
| **C2：main_v21moon** | dariushafshar/kaggriculture-tape-benchmark-20260824 | 2026-08-24 | 7-agent 池头名（95.4% of 240 局，对 kaitov41 胜率 82.5%） | 720（基准内 20 seeds × 2 seatings） | 公开 tape（作者署名 pool） | 中高：引擎 1.32.7 固定 + seed block 42000 已录，但 **tape 本体需从 agent_provenance.csv 引用 notebook 恢复** | 08-24（**最新独立强度证据**） | **强**：独立 head-to-head 测量（21 pairing × 40 局） |
| C3：candidate_kaitov41 | 同上 | 2026-08-24 | 池内第二（对弱对手 95-100%） | 720 | 公开 tape | 中高（同上，需恢复） | 08-24 | 中：被 main_v21moon 击败（0.825） |
| C4：discussion 739273/737764/732902 引用 | Kaggle Discussion | 未知（页面不可读） | 未知 | 未知 | 未知 | 低（间接） | 未知 | **弱**：仅搜索片段，无法核验 |
| C5："Mutants at the top" 讨论 | Discussion 738727 生态 | 2026-09-01（近 6 日更新） | 无独立 tape 资产 | — | 讨论 | 低 | 09-01 | 弱：讨论非 tape |

### 2.3 T1 选择

> **T1 = C1：カワシギ rank-1 submission 55425101 的 720 步公开 stream**（destbreso 2026-08-15 快照）

选择理由（recent strength > reproducibility > historical rating）：
1. **recent strength**：ladder rank-1（3282.6）是"当前 public meta 中最强"的最直接证据——真实竞技场头名，222 局样本；C2 虽更新（08-24）但为自选 7-agent 池的池内头名（非 ladder）
2. **reproducibility**：streams.parquet 提供全文 farmer/market 动作 + episodes.csv 提供每局 engine seed——exact replay 链路最完整
3. **T1-alt = C2（main_v21moon）**：若 T1 的 hands 动作不可恢复（见 2.4）或首轮结果需要独立复核，改用 C2（其独立测量是 08-24 最新的强度证据，但 tape 需从 notebook 恢复）

**Freshness caveat（诚实声明）**：截至 2026-09-07 未发现 08-24 之后可核验的新 tape 资产（09-01 讨论为间接证据）。不假装有更新的强 tape。

### 2.4 Provenance / Reproducibility 判定

- **NO RELIABLE PUBLIC TAPE？——否**：存在可靠资产（两个 dataset 文件已核验、CSV 内容已读、engine seeds 已录）
- **已核验**：episodes.csv（1483 行：submission/episode_id/rank/team/ladder/seat/opponent/bank/seed/turns，rank-1 = 55425101 共 222 局全 720 步）；pairwise_win_rates.csv（21 pairing × 40 局，engine 1.32.7，seed0=42000）
- **关键 caveat（Phase 2 必须核验）**：destbreso 的 streams.parquet 中 hands 动作为 **8 字节 hash（hands_h，"only equality is ever asked of it"）**——**hands 原文可能不可恢复** → 若 T1 使用 hands，exact replay 需改从 Kaggle episode replay endpoint 抓取原文（数据集作者即如此采集），或选择 hands 全 PASS 的局；若无法恢复则 T1 的 exact-replay reproducibility 降级，转 T1-alt
- 待办（Phase 2 前置）：下载 streams.parquet + boards.csv（需 pyarrow），核验 55425101 一局的完整动作流格式与 hands 可恢复性

## 三、Phase 2-4 前置清单（下一步，gated）

1. 下载 streams.parquet/boards.csv，核验 55425101 的 720 步流（farmer/market 全文 + hands 可恢复性）
2. 若 hands 不可恢复 → 从 Kaggle episode replay endpoint 抓取该 submission 的原始 episode 动作
3. 建立 T1 exact replay（720 步原样、不 repair、不 fallback——失败即按引擎真实行为执行，记录为 research finding）
4. Smoke（8-16 paired seeds 双 seat，deterministic double-run，reconciliation==0）→ 通过后正式 benchmark（closer_cleo 120 + 异构 ≥50/对手，复用 EXP-8 池）
