# EXP-9 Phase 3 Smoke Report：T1 exact tape replay vs T0（v11E）

日期：2026-09-07 ｜ 引擎 kaggle_environments 1.32.7 ｜ production 冻结（md5 224a1c47... 未动，未提交 Kaggle）

## 1. 配置

- **T0** = production v11E（kaggriculture/main.py，md5 `224a1c47cf9b07624f5faabbb5227891`）
- **T1** = tape_55425101_91889284.json 的 **720 步 exact replay**（TapeAgent 纯按 obs.step 查表返回 farmer/hands/market 原文，无 repair/fallback/adaptive/route/推断/增删改）
- 对手：closer_cleo（复用 EXP-8 池）；seeds 1-8 paired；seat 按 seed 奇偶（偶→0、奇→1，双 seat 覆盖 4+4）；每局 deterministic double-run（同 agent/seed/seat 连跑两次）
- 会计：executed_ledger.py（A6 后），硬门 reconciliation == 0（严格 exact）

## 2. 结果

| 指标 | 结果 |
| --- | --- |
| production fingerprint | md5 `224a1c47...` match=**True**（T0 未变） |
| **deterministic double-run** | **PASS**（32 局全部：final bank / exec_sell / exec_cost / recon 逐位一致） |
| **720/720 steps** | **PASS**（全部 32 局 len(steps)=720，status DONE） |
| **reconciliation == 0** | **PASS**（32/32 局全部 0.00，exact） |
| **seats** | 双 seat 可执行 ✓（seat 0/1 各 16 局） |
| **hidden repair audit** | PASS（TapeAgent 仅 tape[step] 查表返回，代码层无任何修复逻辑） |
| T1 failed orders | 16/16 局 SELL 大量失败（failed 2830-2839 vs executed 653-662）——tape 录制于 seed 1579917451，fresh seed 上按**引擎原生语义执行失败**，未 repair（设计如此） |

### 逐局（T1 摘要；T0 全部 recon 0.00）

| seed | seat | T0 bank | T1 bank | T1 execSell | T1 failSell | recon(T0/T1) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 92247 | 27478 | 653 | 2839 | 0.00/0.00 |
| 2 | 0 | 80659 | 26985 | 662 | 2830 | 0.00/0.00 |
| 3 | 1 | 47754 | 21835 | 662 | 2830 | 0.00/0.00 |
| 4 | 0 | 97918 | 25127 | 662 | 2830 | 0.00/0.00 |
| 5 | 1 | 64771 | 28655 | 660 | 2832 | 0.00/0.00 |
| 6 | 0 | 109594 | 15975 | 655 | 2837 | 0.00/0.00 |
| 7 | 1 | 23628 | 18645 | 653 | 2839 | 0.00/0.00 |
| 8 | 0 | 61311 | 29693 | 662 | 2830 | 0.00/0.00 |

- **first divergence**：无（T1 为 open-loop tape，无自适应层；全部 32 局 reconciliation==0、无 state-mismatch 类校验失败——executed-ledger 校验 719/719）
- T1 在 fresh seeds 上大幅落后 T0（15,975-29,693 vs 23,628-109,594）——tape 录制的原始对局上下文（seed 1579917451 + 特定对手）不可迁移，SELL 订单因市场/库存状态差异大规模失败——**这是 T1 的实验结果，不是 bug**（按协议不 repair）

## 3. 会计验证

- 32/32 局 `final = initial + Σexecuted_rev − Σexecuted_cost` 精确成立（recon 0.00）
- 含 T1 大规模失败订单局的守恒（executed-accounting 正确归因 issued/executed/failed）

## 4. Smoke Gate

```
deterministic == PASS
720/720 == PASS
accounting reconciliation == 0 == PASS
no hidden repair == PASS
T0 fingerprint unchanged == PASS
both seats executable == PASS

PHASE_3_GATE = PASS
```

## 5. 处置

按协议**停在 Phase 3 → Phase 4 approval gate**，不自行进入正式 benchmark：

> 请求 Phase 4 授权（T1 exact replay × closer_cleo 120 + 异构 ≥50/对手 paired benchmark）

Production v11E 继续冻结；未提交 Kaggle。
