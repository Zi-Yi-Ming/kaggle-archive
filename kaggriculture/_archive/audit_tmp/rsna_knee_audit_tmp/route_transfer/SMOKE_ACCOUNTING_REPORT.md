# SMOKE_ACCOUNTING_REPORT（EXP-8 Phase A4/A5）

日期：2026-09-06 ｜ 对象：V0/V1/V2 × seeds 1/13/57（vs closer_cleo，座位按 seed 奇偶），executed-ledger 口径

## 1. Smoke 结果（逐局 issued/executed/failed + reconciliation）

| variant | seed | route | issuedRev | executedSELL | issuedCost | executedCost | failed_u | finalBank | recon |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V0 | 1 | A | 1255 | 1214 | 725 | 36014 | 41 | 92247 | +0.0 |
| V0 | 13 | A | 1252 | 1211 | 725 | 37033 | 41 | 122623 | +0.0 |
| V0 | 57 | A | 1251 | 1204 | 725 | 36291 | 47 | 88415 | +0.0 |
| V1 | 1/13/57 | A | = V0 | = V0 | = V0 | = V0 | = V0 | = V0 | +0.0 |
| V2 | 1 | **B** | 1340 | 380 | 725 | 30048 | 960 | 10973 | **−1060.0** |
| V2 | 13 | **B** | 1241 | 112 | 725 | 9601 | 1129 | 837 | +0.0 |
| V2 | 57 | A | = V0 | = V0 | = V0 | = V0 | = V0 | = V0 | +0.0 |

（V1 ≡ V0 逐位一致 = 结构对照组 ✓；V2 route B 局 failed_u 960-1129 = tape-B 订单大规模失败（issued≠executed 的真实体现））

## 2. A5 Gate 逐项

| 条件 | 结果 |
| --- | --- |
| V0 == production 逐字节 | ✅（此前 smoke 已证，seeds 1/13/57 全 True） |
| V2 route == 原 SANITY | ✅（seed 1/13 → B，seed 57 → A，与 SANITY 一致） |
| 720 steps 完整 | ✅ |
| micro-validation | ⚠️ PARTIAL（A3：8/10 PASS，case 10 FAIL） |
| **reconciliation == 0（每局）** | ❌ **V2 seed 1（B 路线）−1060.0 ≠ 0** |

## 3. 处置（按 A5 规则）

> "如果仍然 reconciliation_error != 0：立即停止。不要加 tolerance。不要继续跑正式 benchmark。先报告新的 accounting gap。"

**STOP：不进入正式 benchmark。**

- **ACCOUNTING STATUS: FAIL**（V2-B 类存在种子相关的重建 gap：seed 1 −1060；seed 13 的 B 局精确——tape-B 与当前对局错位时漂移累积程度因种子而异）
- **PRODUCTION STATUS: UNCHANGED**（main.py 零改动，md5 保持）
- **PHASE 5 STATUS: BLOCKED**

## 4. 已知 gap 描述（不掩盖、不 tolerance）

- 类属：V2-B（tape B 大规模订单失败）场景下 executed-ledger 重建的残余漂移；A3 case 10 与 A4 seed-1 同一类
- 表象：最早漂移 step 73 `shed[WHEAT] 17 vs 13`（重建多 4 小麦入棚）→ SELL 执行量偏差 → money 漂移 −1060
- 未收敛的效应候选：同步 WATER→HARVEST 产量增强、动物产品流边界（case 9 step 672 同类）
- 9/11 局 recon 精确 +0.0；V0/V1 全部精确——生产 tape 路径（V0/V1）与 A 路线（V2 seed 57）完全精确

## 5. 产物

- SMOKE_ACCOUNTING_REPORT.md（本文件）；executed_ledger.py（修复后版本）；ACCOUNTING_AUDIT.md / ACCOUNTING_MICRO_REPORT.md（A0/A3）
- 未修改 production、未调参、未 p-hack、未跑正式局
