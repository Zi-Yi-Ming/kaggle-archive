# EXP-9 Phase 4 Benchmark Report

日期：2026-09-07 ｜ 引擎 kaggle_environments 1.32.7 ｜ production v11E 冻结（md5 `224a1c47...`，未动，未提交 Kaggle）

## 1. Dataset / Provenance

- **T0** = production v11E（kaggriculture/main.py，md5 `224a1c47cf9b07624f5faabbb5227891`）
- **T1** = tape_55425101_91889284.json（submission 55425101「カワシギ」rank-1 @ 2026-08-15 快照；episode 91889284，seed 1579917451，seat 1）——720 步 **exact replay**（TapeAgent 纯查表，无 repair/fallback/adaptive/route/推断/增删改；失败订单按引擎原生语义执行）
- 来源：destbreso top-10 replay streams + Kaggle 官方 replay endpoint（Phase 2 已核验：farmer/market 与 parquet 逐位一致）

## 2. Experimental Protocol

- 固定 RNG（`env.info["seed"]`）；paired seeds（T0/T1 同 seed/同 opponent/同 seat/同 engine）；seat 按 seed 奇偶（复用 EXP-8 约定）
- 对手池**严格复用 EXP-8**：closer_cleo（Pool A）+ broker_bea/slotter_silas/ledger_lena/melon_mateo/rancher_rita（Pool B）
- 会计：executed_ledger.py（A6 后），硬门 reconciliation == 0

## 3. Sample Size

- 370 paired matchups × (T0+T1) = **740 games**（closer_cleo 120 + 异构 5×50）

## 4. Overall Result

| Pool | n | T0 Bank | T1 Bank | Δ | T1 Win Rate | 95% CI (Wilson) | p |
| --- | -: | ---: | ---: | ---: | ---: | --- | ---: |
| closer_cleo | 120 | 73,952 | 26,152 | **−47,800** | 0/120 (0.0%) | [0.000, 0.031] | <0.0001 |
| heterogeneous | 250 | 101,221 | 29,737 | **−71,484** | 0/250 (0.0%) | [0.000, 0.015] | <0.0001 |

- Paired Δ：closer_cleo median −45,114、std 23,524、95%CI [−52,009, −43,591]、**effect size d = −2.03**；heterogeneous median −65,038、std 28,777、95%CI [−75,051, −67,916]、**d = −2.48**
- 370 matchups 中 T1 胜 0、负 370、平 0

## 5. Seat Breakdown

| Seat | n | Δ (closer_cleo) | T1 Win | Δ (hetero) | T1 Win |
| --- | -: | ---: | ---: | ---: | ---: |
| 0 | 60/125 | −45,928 | 0% | −72,219 | 0% |
| 1 | 60/125 | −49,672 | 0% | −70,748 | 0% |

双 seat 均 0% 胜——无 seat 依赖。

## 6. Opponent Breakdown

| Opponent | n | Δ | T1 Wins | T1 Losses |
| --- | -: | ---: | ---: | ---: |
| broker_bea | 50 | −54,783 | 0 | 50 |
| ledger_lena | 50 | −54,659 | 0 | 50 |
| melon_mateo | 50 | −94,480 | 0 | 50 |
| rancher_rita | 50 | −99,143 | 0 | 50 |
| slotter_silas | 50 | −54,352 | 0 | 50 |
| closer_cleo | 120 | −47,800 | 0 | 120 |

全体对手一致强负——无对手依赖。

## 7. Failure / Execution Analysis

| 项 | T0 | T1 |
| --- | ---: | ---: |
| SELL issued (closer_cleo) | 150,694 | 419,040 |
| SELL executed | 144,591 | 78,904 |
| **SELL failure rate** | **4.0%** | **81.2%** |
| SELL issued (hetero) | 313,690 | 873,000 |
| SELL executed | 301,642 | 163,814 |
| **SELL failure rate** | **3.8%** | **81.2%** |

- **Phase 3 现象在正式规模完全复制**：tape 在 fresh seeds 上 SELL 订单 81.2% 失败（市场/库存状态与录制对局不兼容，含大量超量卖出订单），经济显著劣势
- tape/state mismatch：T1 无自适应层，全部失败按引擎原生语义执行（未 repair）

## 8. Accounting Integrity

```
reconciliation failures = 0（740/740 局 exact 0.00）
```

- 含 T1 大规模失败订单局全部守恒；executed-ledger 正确归因 issued/executed/failed

## 9. Statistical Conclusion

- 正式统计结论：**T1 显著且稳定劣于 T0**——0/370 胜（win rate 0.0%，Wilson CI 上限 0.031/0.015），paired permutation p<0.0001（20,000 resamples），效应量 d = −2.03（closer_cleo）/ −2.48（heterogeneous）——巨大负效应
- 双池、双 seat、全部 6 个对手一致复现；无接近显著、无方向不一致

## 10. Transferability Conclusion

**NOT TRANSFERABLE（不可迁移）**：
- 数据唯一回答：该 public tape（C1）在 fresh fixed-RNG environments 上无 transferable advantage，且为**系统性、大规模劣势**（−48k~−99k/局，依赖对手）
- 根因明确：tape 录制于 seed 1579917451 的特定对局上下文，其动作流（尤其 SELL 节奏/数量）与 fresh seed 的市场/库存状态不兼容 → 81.2% SELL 失败 → 经济坍塌
- 不推断其他 tape 的强弱（仅 C1 可判）；不将"历史强"等同于"当前强"——本实验证实该 tape 当前不可迁移

## 11. Production Decision

```
STOP
```

- T1 显著劣于 T0 → 不进入 candidate evaluation；production v11E 继续冻结
- EXP-9 主结论：截至 2026-09-07 可核验的"最强 public tape"（ladder rank-1 @ 08-15）在 fresh fixed-RNG 上**不能击败 v11E**，且显著更弱

## 处置

- 停在 Phase 4 结束：**不自行进入 Phase 5/6/7**；不修改 production；不提交 Kaggle；不做 repair 实验
- 若后续研究"public tape + compatibility repair 是否值得"→ 另开 EXP-10（不得污染 EXP-9）
- 产物：phase4_bench.jsonl（740 局原始记录）、phase4_bench.py、phase4_agg.py、EXP9_PHASE2/3_REPORT.md、EXP9_PHASE01_REPORT.md
