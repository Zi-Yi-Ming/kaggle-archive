# ACCOUNTING_MICRO_REPORT（EXP-8 Phase A3）

日期：2026-09-06 ｜ 对象：executed_ledger.py 的 executed-ledger 重建 vs 引擎 1.32.7 终态
VERDICT: **PARTIAL（8/10 PASS；case 9 money 精确但有 1 个 shed 漂移步；case 10 未通过 reconciliation）**

## 1. 测试设计

- 独立测试目录 `_audit_tmp/route_transfer/accounting_micro/`（run_micro.py + micro_results.json）
- crafted agents 定向触发各案例；executed ledger 由 executed_ledger.replay_game 重建（引擎原语重放）
- 每案例检查：reconciliation_error == 0 + 逐步状态校验（money/shed/seeds/market inventory vs obs）+ 期望成交 qty

## 2. 结果表

| # | 案例 | 校验 | recon | 期望 qty | 判定 |
| --- | --- | --- | --- | --- | --- |
| 1 | 正常 BUY（BUY_SEED WHEAT×10） | 719/719 | 0.0 | BUY_SEED 10 | **PASS** |
| 2 | 无现金 BUY（MELON×50 → 37 成交） | 719/719 | 0.0 | BUY_SEED 37 | **PASS** |
| 3 | 无库存 SELL | 719/719 | 0.0 | SELL 0 | **PASS** |
| 4 | 部分 BUY（COW×10 → 7/10） | 719/719 | 0.0 | BUY_ANIMAL 7 | **PASS** |
| 5 | 部分 SELL（8/10） | 719/719 | 0.0 | SELL 8 | **PASS** |
| 6 | 多 unit BUY | 719/719 | 0.0 | BUY_ANIMAL 3 | **PASS** |
| 7 | 多 unit SELL | 719/719 | 0.0 | SELL 5 | **PASS** |
| 8 | BUY+SELL 同步 | 719/719 | 0.0 | SELL 4 + BUY 4 | **PASS** |
| 9 | interleaving（closer_cleo×2） | 718/719 | **0.0** | — | **money PASS**（1 shed 漂移步 672） |
| 10 | **V2-B 错位**（tape B 大规模订单失败） | 416/719 | **−1060.0** | — | **FAIL** |

## 3. 已知会计 gap（不掩盖）

- **case 10（V2-B）**：reconciliation −1060；最早漂移 step 73 `shed[WHEAT] 17 vs 13`（我的重建多 4 个小麦入棚）。tape-B 与当前对局极端错位使重建漂移累积——剩余未建模效应（疑为同步 WATER→HARVEST 产量增强与个别 FEED/动物流边界），导致 SELL 执行量偏差 → money 漂移。
- **case 9 step 672**：shed[STRAWBERRY/MILK/FERTILIZER] 各差 −7/−3/−2（动物产品流重建 gap）；money 不受影响（recon 0.0）。

## 4. 已修复的重建缺口（本轮累计，全部经微测试证伪后定位）

1. obs 索引/城镇消耗时点（consume_step = s−1；报价见 consume 前库存、消耗效应进 obs(s)）
2. 同步 PLANT 回合级 blocked 逻辑（请求>种子 → 整作物丢弃）
3. PLACE 语义（动物从随身库存放格，非 shed；shed-adjacent 为随身→shed 类 DROP）
4. 同步 HARVEST→随身→日末入仓流（含非持续作物收后 tile→None、可变 tile 状态）
5. 对手步前状态从各自 obs(s−1) 重建（obs_prev_other）+ 对手 obs 校验（obs_cur_other）
6. FEED/FERTILIZE 随身库存消耗 + fed_today/fertilizer_available 同步 tile 状态

## 5. 协议处置

- A3 硬门（每案例 reconciliation == 0）**未完全通过**（case 10 违反）→ 按 A5 规则不进入正式 benchmark，先报告本 gap
- 所有原始数据保留：micro_results.json / executed_ledger.py / run_micro.py
