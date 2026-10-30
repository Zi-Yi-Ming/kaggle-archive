# EXP-10A PLAN（预注册 — v11E Tape Structure Audit）

日期：2026-09-07 ｜ 只读行为审计，production v11E 绝对冻结（md5 `224a1c47...`，Elo 942.2，recovery 56047543，engine 1.32.7）
本文件所有指标/阈值/分类规则在**看到任何实验结果之前**定义。实验完成后不得修改。

## 0. 目标（Q1-Q4）

Q1 同固定 RNG 下 720-step action stream 稳定性；Q2 跨 seed 哪些 action 保持稳定；Q3 哪些 action 依赖 shop/market/own/opponent/day；Q4 v11E 是否呈"deterministic backbone + sparse adaptive points"（无证据则明确报告未发现）。

## 1. 预注册实验配置

- **Phase A（deterministic control）**：seed 7、seat 1、closer_cleo，同一配置跑 20 局，每局 double-run（同配置两次运行）→ 要求 20/20 动作流逐位一致（MD5 对比）
- **Phase B（cross-seed）**：seeds **1-20** × seats **0/1** × closer_cleo（固定 baseline opponent）= **40 games** × 720 steps（40 局全部进入分析，不删局）
- RNG：`env.info["seed"]` 固定注入；座位：candidate seat 0/1 各 20 局
- 每步录制：canonical action + own state + market 快照 + opponent action

## 2. Canonical action encoding

```
MOVE:NORTH/SOUTH/EAST/WEST        (farmer/hand 移动)
PICKUP:<item>:<n>                 PLACE:<item>:<n>     DROP
PLANT:<crop>                      WATER                 HARVEST
FERTILIZE                         FEED                  CARE
COLLECT_FERTILIZER                DIG                   BUILD_COOP/PASTURE
BUY_SEED:<crop>                   BUY_PRODUCT:<item>    SELL:<item>
BUY_ANIMAL:<item>                 BUY_LAND              HIRE
PASS
```
- 每步生成 **one canonical action per unit**（farmer 1 + hands n）+ market orders 列表；按 unit 序拼接为 step 的 canonical string（`farmer|hand1|...|market:[...]`）用于逐位比较
- 同时保存 step/day/action_type/action_detail

## 3. 指标（预定义）

- **M1 exact agreement**：两 seed 的 step 动作逐位一致率（all / movement only / market only / buy only / sell only / hire / land 分列）
- **M2 step entropy**：`H(action|step)` 基于 40 games 该 step 的 action distribution（base-e bits）；报告 mean/median/p90/max；原始 step 级数据保留，不做 smoothing
- **M3 conditional entropy**：`H(action|step,cond)`，cond ∈ {shop_signature, day, market_state, opponent_action, own_state_bucket}；bucket 过细导致样本 <5 时明确报告 sample size
- **Backbone step**：40 games 中 action 完全一致 → `backbone_ratio = #backbone / 720`，按 all/movement/market 分列 + 按 day 分 5 日段
- **动态点（candidate dynamic point）**：`H(action|step) > 0.5 bit`（threshold 预注册；同时报告 0.25/0.75/1.0 敏感度，仅描述性，不选最优）

## 4. Divergence 分析（预定义分类规则）

- **first divergence**：seed pair 首次 action 不同的 step；记录 step/day/action_A/action_B/state 差/shop 差/market 差/opponent 差
- **原因分类优先级（预注册，按此顺序归因；多项同时差异时取先命中者）**：
  1. **SHOP**：该步 obs 的 `unlocked_shops` 集合/顺序不同
  2. **MARKET**：市场价或 inventory 差 > bucket 边界（价格相对基准价偏移 ≥20% 或 inventory 差 ≥5）
  3. **OWN_STATE**：cash bucket / 随身+棚 inventory bucket / 作物格数不同
  4. **OPPONENT**：对手该步动作不同
  5. **UNKNOWN**：以上均不可归因（**绝不硬归因**）
- **divergence episode**：连续 divergence steps 的 runs；统计 number/median/p90/longest——区分"孤立局部修正"vs"级联整链分叉"
- **序列相似度**：Levenshtein edit distance（720 步 canonical 序列，标准 DP）+ normalized distance + longest common prefix/suffix + common action runs

## 5. Own-state bucket 定义（预注册）

- cash：`[0,3000) [3000,10000) [10000,30000) [30000,60000) [60000,120000) [120000,∞)`
- 市场价（商品级）：相对基准价 `[-20%,+20%)` 内 → FLAT；外 → UP/DOWN
- inventory（随身+棚合计）：`0, [1,10), [10,50), [50,∞)`
- shop signature：`unlocked_shops` 的有序 tuple（含重复，如引擎商店抽取可重复）

## 6. Type A-D 归类规则（预注册，凭数据）

- **A Pure Tape-like**：backbone_ratio ≥ 0.95 且动态点 <10 且无稳定 condition
- **B Tape + Sparse Adaptation**：backbone_ratio ≥ 0.80 且动态点少且动态点与明确 state condition 稳定相关
- **C Structured Adaptive Policy**：backbone_ratio < 0.80 且大量 state-dependent branches
- **D Highly Adaptive**：跨 seed 行为高度不同（backbone_ratio < 0.5）
- 证据不足/混合 → `INCONCLUSIVE`（不强行归类）

## 7. Hard Gates（全部通过才继续）

- Gate A：Phase A 20/20 动作流逐位一致；Gate B：40 games 全 720/720；Gate C：executed-ledger reconciliation 0 failures（40 games）；Gate D：production fingerprint md5 不变
- 任一 FAIL → STOP 排查 runner/RNG/telemetry 污染，不继续分析

## 8. 统计纪律

- 40 games 全入最终数据；不删异常 seed、不选 subset、不事后改 threshold、不只报某日/某类 action
- 稳定性↔bank 相关仅观察（Pearson r + 散点），不据此改策略
- **action variability ≠ adaptation**：仅当 action 变化与 observation/state condition 存在稳定对应（同一 condition 下 40 games 中 ≥2/3 动作一致）才称 candidate conditional branch；否则记 action variability

## 9. 边界

- 只做 Phase A + Phase B + 分析 + 报告；发现的有趣 branch 只记 hypothesis 不实现；不 EXP-10、不 tape 移植、不优化、不提交 Kaggle
- 输出目录 `_audit_tmp/exp10a/`：RAW.jsonl / BEHAVIOR.csv / ENTROPY.csv / DIVERGENCE.csv / SUMMARY.md / FINAL_REPORT.md
