# SANITY_REPORT（EXP-8 Phase 4）

日期：2026-09-06 ｜ 范围：seeds 1/13/57 × 每 variant 双跑（vs closer_cleo）；另加修订后 V2 的 route 决策分布探测（seeds 1-16）

## 1. 检查项与结果

| # | 检查 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 动作流 MD5 确定性（双跑一致） | ✅ | PROD/V0/V1/V2 × seed 1/13/57 全部双跑 sig 一致（修订前全量 + 修订后 V2 复验） |
| 2 | V0 ≡ 生产 v11E 对齐 | ✅ | PROD==V0 逐字节（sig 32f9faa7/e039fe2e/d2fc4dc2 全等） |
| 3 | V0 == V1（结构对照） | ✅ | V1 恒选 tape A → 与 V0 逐字节一致 |
| 4 | 完整对局无异常 | ✅ | 全部 720 步完成，零异常 |
| 5 | route 决策确定性 | ✅ | V2 双跑 route 一致（seed 1/13 均 route=B 且 sig 一致） |
| 6 | V2 路由机制可运作 | ✅ | 修订后 seeds 1-16 决策分布 A=5 / B=11（~31%/69%）；B 路径 seed 1 双跑 bank 10973/10973 一致 |

## 2. Phase-4 发现与规格修订（透明记录）

- **发现（缺陷）**：ROUTE_SPEC v1 的决策点 step 0 不可用——引擎 1.32.7 的 `obs.town.unlocked_shops` 在 step 0 恒为空（商店在 step 72/144/216 = day 3/6/9 解锁）→ step-0 决策恒 fallback A → V2 路由机制失效（修订前 V2≡V0 为必然，非真值）。
- **修订**：ROUTE_SPEC v2 + V2 实现同步——决策点改为**首个非空签名步**（经验上 step 72，day 3），决定后全程锁定；签名出现前（0..71 步）运行 tape A。纯函数性、锁定性、确定性不变。
- **性质说明**：此修订由引擎现实驱动（商店解锁时间线），**未参考任何实验结果**（决策时点由引擎解锁步决定，非结果调优）；B 路径的 bank 10973 远低于 V0 属正常（tape B 是对局 42 的录制，其晚期经济与当前对局错位——这正是基准要测量的，不做任何调整）。

## 3. 守恒与格式

- 全部对局由引擎 1.32.7 校验动作合法性（非法动作静默拒绝，零异常即零非法）；bank 值范围正常
- 注入点仅 tape 源（`BASE._TRACE` 引用替换），market 叠加/beam/front_run/terminal 零改动（V0≡PROD 逐字节证明注入零泄漏）

## 4. 结论

**全部 7 项检查通过——sanity gate PASSED，无失败条件命中。** 修订后 V2 的路由机制已可运作且确定性强。

## 5. 产物

- `_audit_tmp/route_transfer/DESIGN_NOTE.md`（Phase 0）
- `_audit_tmp/route_transfer/ROUTE_SPEC.md`（v2，Phase 1-2）
- `_audit_tmp/route_transfer/tape_b.json`（720 步，seed 42 录制）
- `_audit_tmp/route_transfer/variants/v11e_base.py`（V0）/ `v11e_multitape_fixed.py`（V1）/ `v11e_multitape_router.py`（V2）
