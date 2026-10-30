# A6 FORENSIC REPORT（EXP-8 Forensic Accounting Investigation）

日期：2026-09-06 ｜ 对象：V2-B seed 1 的 reconciliation −1060 根因调查（一次且仅一次）
**ROOT_CAUSE: CONFIRMED**（两个 accounting-reconstruction primitive 缺陷，均已修复并全量重验证）

## 1. Known failure

- A5 smoke：V2-B seed 1 reconciliation = **−1060**（唯一失败局；V0/V1/V2-A/V2-B-s13 全部精确 0.0）
- A3 case 10 同源（V2-B 类），case 9 step 672 部分同源

## 2. First divergence step

**FIRST_DIVERGENCE_STEP = 73**（V2-B seed 1，seat 0 = 对手 closer_cleo 侧）
- 后续 step 216 出现第二处独立分歧（候选侧 FERTILIZER）

## 3. Engine state（step 73，seat 0）

- 引擎观测：`shed[WHEAT] 17 → 13`（obs(72)→obs(73)），随身 WHEAT 1 → 0 → 4
- step 73 市场订单：`SELL FERTILIZER 4 / HIRE / HIRE`（**无 SELL WHEAT**——4 小麦并非卖出）
- 单位动作：`[PICKUP, WHEAT, 4]`（farmer 从 shed 取 4 小麦到随身）

## 4. Reconstructed state（step 73，seat 0）

- 修复前：`shed[WHEAT] = 17`（未扣 PICKUP 的 4 → 与引擎 13 差 +4）
- 修复后：`= 13`（与引擎逐位一致）

## 5. Exact action causing divergence

- **P1（step 73）**：对手单位动作 `PICKUP WHEAT 4`（shed → 随身）从未被应用到对手的步前状态重建
- **P2（step 216）**：日末入仓 `_drop_inventories_to_shed` 被应用到**市场前** shed（错误），引擎顺序为 units → market → consume → **end_of_day（入仓在后）**——step 216 候选的 `SELL FERTILIZER 1` 因我的重建多出 1 肥料而错判可执行（money +89、market[FERTILIZER] +1、shed −1），引擎侧该 sell 在市场时点 shed=0 而失败（money 8 未动）

## 6. Engine semantics（kaggriculture.py 1.32.7，CODE）

- 引擎每 turn：`_apply_unit_action`（各玩家单位动作）→ `_process_market`（双方订单 lockstep）→ `_town_consume` → `_decay_plants` → `if (step+1)%24==0: _end_of_day`（L935-946）
- `_end_of_day` 内 `_drop_inventories_to_shed`（L843-846）把随身库存入棚（容量上限，溢出丢弃）——**市场处理之后**
- 单位动作只作用于自己（PICKUP 查 `_is_shed_adjacent` + shed 库存）

## 7. Root cause（两个独立 reconstruction 缺陷）

| # | Primitive | 缺陷 | 影响 |
| --- | --- | --- | --- |
| P1 | 对手单位动作流 | `_unit_state_effects` 对双方都用候选的 `act_cur`——**对手的 farmer/hands 动作从未应用到对手状态**（obs_prev_other 已修但 actions 未修） | 对手 PICKUP/DROP/HARVEST/PLANT 等任何单位效果缺失 → 对手 shed 偏差 → 共享市场库存与价格级联 → 候选 money 漂移 |
| P2 | 日末入仓时点 | deposit 在 `_unit_state_effects` 内被加进**步前** shed；引擎实际在市场后入仓 | 市场 SELL/BUY 的可用性检查错看 post-deposit 状态 → 单步 1 单位差异即翻转订单执行 |

## 8. Why V0/V1/V2-A do not trigger it

- P1/P2 是**对手侧与日末边界**的极端场景缺陷：V0/V1/V2-A 的对手（closer_cleo）在这些 seed 上未出现"入棚/取棚量恰好翻转订单执行"的临界情形；V0/V1/V2-A 局与 V2-B 局共享对手，但 route 差异改变了对局状态轨迹，未触发
- 修复后 11/11 局（含 V0/V1/V2-A）reconciliation 全部 0.0 且校验 719/719——正常路径本就不受这两个缺陷实质影响（原 A4 已 9/11 精确）

## 9. Why V2-B seed 1 triggers it

- V2-B 的 tape-B 与当前对局错位 → 候选侧大量失败订单 + 对手侧临界入棚/取棚动作组合（step 73 PICKUP WHEAT 4、step 216 日末 deposit + SELL FERTILIZER 1）
- seed 1 恰好命中；seed 13 的 B 局轨迹未命中（其 recon 原已 0.0）

## 10. Whether case 9 is same primitive

- **case 9 step 672 = 同一 P1**（对手侧 DROP 的 STRAWBERRY/MILK/FERTILIZER/WHEAT/WOOL 全品类缺失——P1 商品无关）
- P2 独立（日末入仓时点），case 9 未命中 P2；**分并记录，不强行合并**

## 修复内容（仅 accounting reconstruction，`executed_ledger.py`）

1. P1：对手步前重建改用对手动作流（`act_other = _ACT_OTHER[seat]`，按 seat 取各自动作）
2. P2：日末入仓从步前重建移出，在市场重放 + consume 后、校验前应用（携带随身库存列表，容量上限）

## 重验证（A6-8，全部通过）

| 局 | reconciliation | 校验 |
| --- | --- | --- |
| V0 s1/13/57 | **+0.0** | 719/719 ×3 |
| V1 s1/13/57 | **+0.0**（≡V0） | 719/719 ×3 |
| V2 s1（B） | **+0.0**（原 −1060） | 719/719 |
| V2 s13（B） | **+0.0** | 719/719 |
| V2 s57（A） | **+0.0** | 719/719 |

- V0 ≡ PROD 行为：seeds 1/13/57 终局 bank 与 production main.py 逐位相等（92247/122623/88415）
- V2 route 不变：s1/s13 → B，s57 → A（ROUTE_SPEC v2 未动）
- 未修改 production / V0/V1/V2 / ROUTE_SPEC / tape / hash / seed；无 tolerance、无 heuristic、无终局反推

---

```
A6 STATUS: PASS
ROOT CAUSE: CONFIRMED
RECONCILIATION: 0
PHASE 5: READY（按协议停在 READY，不自动执行正式 benchmark）
PRODUCTION: UNCHANGED
```
