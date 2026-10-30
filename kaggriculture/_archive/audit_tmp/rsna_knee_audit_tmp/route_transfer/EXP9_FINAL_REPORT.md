# EXP-9 Final Report（结果汇总，不新增实验/统计）

日期：2026-09-07 ｜ 依据：EXP9_PHASE4_REPORT.md（主要 benchmark evidence，740 局原始记录 phase4_bench.jsonl）

```
VERDICT: STOP
TRANSFERABILITY: NOT TRANSFERABLE
PRODUCTION DECISION: STOP
```

## 核心证据（Phase 4 正式 benchmark，740 games / 370 paired matchups）

| 指标 | 值 |
| --- | --- |
| 对手池 | closer_cleo（120）+ 异构 5 对手（各 50），双 seat |
| reconciliation failures | **0 / 740** |
| T1 wins | **0 / 370** |
| closer_cleo Δ | **−47,800/局**（median −45,114，95%CI [−52,009, −43,591]） |
| heterogeneous Δ | **−71,484/局**（median −65,038，95%CI [−75,051, −67,916]） |
| paired p | **< 0.0001**（20,000 resamples） |
| effect size | **d = −2.03（closer_cleo）/ −2.48（heterogeneous）** |
| T1 SELL failure rate | **81.2%**（vs T0 ~4%） |

Phase 3 的 fresh-seed 大规模失败现象在 Phase 4 完整复现（0/370 胜、全体对手一致强负、无 seat/对手依赖）。

## 结论

> 截至 2026-09-07 当前可核验的强 public tape C1（カワシギ / submission 55425101，ladder rank-1 @ 2026-08-15），在 fresh fixed-RNG 环境下**不存在 transferable advantage，且显著弱于冻结的 v11E**。

## 实验状态

```
EXP-8 → STOP / CLOSED
EXP-9 → STOP / CLOSED（Phase 5-7 NOT EXECUTED / NOT REQUIRED——用户选择以 Phase 4 为终局）
EXP-10 → PROPOSED / NOT STARTED
Production → v11E FROZEN
```

## Production 冻结确认（全部未动）

- agent：v11E，Elo = 942.2，recovery submission = 56047543
- engine：kaggle_environments 1.32.7
- production md5：`224a1c47cf9b07624f5faabbb5227891`
- 未修改 production、未提交 Kaggle、未 merge public tape、未 merge repair、未做 hotfix

## FUTURE RESEARCH CANDIDATE（不启动，仅记录）

```
EXP-10: Public Tape + Compatibility Repair
（需下一轮明确实验协议后再启动；不得污染 EXP-9 结论）
```

## 产物清单

`EXP9_PHASE01_REPORT.md`（候选研究 + T1 选择）、`EXP9_PHASE2_REPORT.md`（hands 恢复 + Gate PASS）、`EXP9_PHASE3_REPORT.md`（smoke + Gate PASS）、`EXP9_PHASE4_REPORT.md`（正式 benchmark + STOP）、`EXP9_FINAL_REPORT.md`（本文件）；数据：`phase4_bench.jsonl`（740 局）、`tape_55425101_91889284.json`（T1 artifact）；代码：`phase4_bench.py`/`phase4_agg.py`/`phase3_smoke.py`、复用 `executed_ledger.py`
