# PHASE5 REPORT（EXP-8 Phase 5 正式 benchmark）

日期：2026-09-06 ｜ 引擎 1.32.7 ｜ 会计层：executed-ledger（A6 修复后）
**VERDICT: STOP（route-selection 迁移在 v11E 语境为强负效应，E 不迁移，production v11E 保持不变）**
**核心证据：V2−V1 = −49,493/局（closer_cleo，0/120 胜，paired-p<0.0001）；−101,971/局（异构池，0/50 胜，paired-p<0.0001）**

## A. 实验设计（v9 预注册，未改动）

- V0 = 纯 v11E 单 tape；V1 = 双 tape 固定（结构对照）；V2 = route selection（ROUTE_SPEC v2，首个非空签名步决定+锁定）
- 120 paired seeds（固定 RNG `env.info["seed"]`，座位按 seed 奇偶），对手：closer_cleo（120）+ 异构池（broker_bea/slotter_silas/ledger_lena/melon_mateo/rancher_rita，各 50）
- 审计：executed-ledger reconciliation（硬门 ==0，无 tolerance）+ 逐步状态校验

## B. 数据完整性

- 1110 局（去重后）| **recon!=0: 0**（会计硬门在全部 1110 局成立）
- V0/V1 × closer_cleo：校验 100%；异构池存在非 money 校验漂移（见 G）

## C. V0 ≡ V1 ≡ production（对照组 sanity）

| 池 | V1−V0 Δbank | wins | paired-p |
| --- | --- | --- | --- |
| closer_cleo | +0.0/局 | 0/120 | 1.0000 |
| heterogeneous | +0.0/局 | 0/50 | 1.0000 |

V1 ≡ V0 逐位一致（双 tape 固定与单 tape 行为相同），V0 ≡ production（行为等价，3 seeds bank 逐位相等）✓

## D. V2（route selection）全统计

| 对比 | 池 | Δbank mean | wins | win 率 CI (Wilson) | paired-p |
| --- | --- | --- | --- | --- | --- |
| V2−V1 | closer_cleo | **−49,493/局** | 0/120 | [0.000, 0.031] | <0.0001 |
| V2−V0 | closer_cleo | **−49,493/局** | 0/120 | [0.000, 0.031] | <0.0001 |
| V2−V1 | heterogeneous | **−101,971/局** | 0/50 | [0.000, 0.071] | <0.0001 |
| V2−V0 | heterogeneous | **−101,971/局** | 0/50 | [0.000, 0.071] | <0.0001 |

## E. Route breakdown（V2 实际路线分布）

| 池 | B 路线 | A 路线 |
| --- | --- | --- |
| closer_cleo | 87/120（72.5%） | 33/120 |
| heterogeneous | 41/50（82%） | 9/50 |

- **V2-A 局 ≡ V0 逐位一致**（Δbank +0.0，33+9 局全部）——router 锁 A 时行为与 base 相同（sanity ✓）
- **V2-B 局 = 全部破坏性来源**：closer_cleo 87 局 Δbank vs V0 **−68,267/局**

## F. Reconciliation 汇总（会计审计）

- 1110/1110 局 reconciliation == 0.0（V0/V1/V2 × 全部对手）——A6 修复后的 executed-ledger 在正式规模上完全守恒
- 守恒审计：每局 `final = initial + Σexecuted_rev − Σexecuted_cost` 精确成立

## G. 已知非 money 校验漂移（如实记录，不影响 VERDICT）

- 异构池 50/50 局 `valid<n`（recon 仍 ==0）：重构状态在个别步与 obs 有 shed/seeds 级漂移（示例：V0×broker_bea seed 1 首分歧 step 240 `shed[COW] 1 vs 0`，valid 717/719）
- 未影响 money 守恒（SELL/BUY 执行量未翻转），属第三类重建边界（对手异常动作组合），与 A3 残留类同源
- closer_cleo 池校验 100%（V0/V1/V2）

## H. Migration Gate A-E（E = route selection 迁移判定）

| 门 | 证据 | 判定 |
| --- | --- | --- |
| E 因果证据（EXP-7） | vs v11E 只有 E 有因果差异（47/120） | 存在 |
| E 在 v11E 语境收益（EXP-8） | V2−V1 −49k/−102k/局，0 胜，p<0.0001 | **强负** |
| B 路线拟合度 | tape-B 重放于 v11E 状态 = 资源浪费（−68k/局） | 不适配 |
| 结论 | route selection 机制本身在 v11E 无迁移价值 | **REJECT** |

## I. VERDICT 与处置

```
VERDICT: STOP（不迁移 E，不采用 V2 路线选择）
PRODUCTION: UNCHANGED（v11E main.py 保持，md5 不变）
PHASE 5: COMPLETE（正式 benchmark 已执行并出具结论）
```

- 未修改 production / V0/V1/V2 / ROUTE_SPEC / tape / seed；无 tolerance、无 heuristic、无终局反推
- EXP-8 结论：COK 的 route-selection（E）在 COK 语境有因果作用，但在 v11E 语境迁移为**强负效应**（tape-B 对 v11E 状态不适配）——E 机制不迁移；v11E 942.2 锚点维持

## J. 产物

- `phase5_bench.jsonl`（1110 局全量原始记录）、`phase5_bench.py`（runner）、`phase5_agg.py`（聚合）、`A6_FORENSIC_REPORT.md`、`ACCOUNTING_AUDIT.md`、`ACCOUNTING_MICRO_REPORT.md`、`SMOKE_ACCOUNTING_REPORT.md`、`executed_ledger.py`
