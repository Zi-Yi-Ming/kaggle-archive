# EXP-10B REPORT — SELL Adaptation 因果消融（V0 vs V1）

日期：2026-09-09 ｜ 只读消融，production v11E 冻结（md5 `224a1c47...` 未动，未提交 Kaggle）

## 结论

```
情况 B：V0 ≈ V1（V0 略负，无证据支持 SELL adaptation 有 alpha）
V0 mean 77,006  vs  V1 mean 77,159  →  冻结 SELL 层反而 +153/局
V0 win 27/120 (22.5%)，paired permutation p (V0≤V1) = 1.0000
→ SELL adaptation 无因果价值证据；按 GPT 协议：别碰它，v11E 保持冻结
```

## 实验设置

- V0 = production v11E（原样）；V1 = 冻结 SELL 重排层（`_EXP10B_FREEZE_SELL`：直接返回 backbone 原序，跳过 beam reorder；其余逐位一致，diff 验证 27 行新增全部在冻结开关）
- 60 seeds × 2 seats × closer_cleo = **120 paired games/臂**（seeds 1-60，固定 RNG）
- Gates：fingerprint PASS、recon 0 failures/240、deterministic spot-check PASS（8 配置双跑逐位一致）

## 关键 forensic 发现（比结果本身更重要）

**EXP-10A 的"SHOP 驱动"归因需要修正**：
1. `_plan_sells`/`_reserve_price`/`_race_factor` 是**死代码**（`_RESERVE={}` 从未填充）——首轮 V1 冻结它们导致 120/120 逐位一致，暴露了这一点
2. `_v11_beam_order` 读取 `unlocked_shops` 但**从未使用**；`agent()` 内 L1485 的 `shops` 是**未定义变量**（NameError 被 `except: return action` 吞掉）
3. 因此 v11E 活路径的 SELL 适应 = **beam reorder，由市场 inventory/prices + cash 驱动，不读 shop**——EXP-10A 的 380/380 SHOP 归因是 shop 抽签与 seed 差异的**共线混淆**（shop 集合随 seed 变 → 首分歧步恰逢 shop 差异，但不是因果）

## 数字

| 指标 | V0 | V1 |
| --- | ---: | ---: |
| mean bank | 77,006 | 77,159 |
| SELL exec/issued | 144,588/150,696 (95.9%) | 144,588/150,696 (95.9%) |
| SELL revenue | 13,273,670 | 13,292,079 (+18,409) |
| first SELL step (median) | 49 | 49 |

- 成交笔数与失败率完全一致（95.9%），差别只在**卖出顺序/时机**带来的实现价差
- mean Δ = −153（V0 视角），stdev 260，V0 胜率 22.5%，p=1.0——V0 的 beam 重排是**轻微负收益**（+18k revenue 总差 / 120 局 ≈ +153/局给 V1）
- 效应极小（Δ 0.2% of bank），但方向一致：SELL 重排层在 120 局上没有显示正因果价值

## 按 GPT 协议的三分叉

**情况 B 命中（且带刺）**：93.6% backbone 是主要 alpha；6% "adaptation" 中真正的 SELL 重排层**不读 shop**、且是轻微负收益。两个直接推论：

1. **别碰它**：v11E 冻结不动（重排层虽微负，但 -153/局在 Elo 噪声内，不值得为它动 production）
2. **修正记录**：EXP-10A 报告的"shop-driven SELL adaptation"表述需要降级为"seed 相关联的可变性，shop 为混淆变量；活路径适应 = 市场驱动的 beam reorder"

## EXP-10C 决定

**不启动**（其前提"SELL adaptation 有价值"不成立）。按时间盒：9/11-9/14 若无价值 → 直接进入 **v11E bottleneck audit**（下一个寻找 942.2→950+ 增量的地方，候选方向：BUY/种子排程、雇工/动物 economics、市场 timing 的 backbone 层面）。

## 产物

`_audit_tmp/exp10b/`：v11e_frozen_sell.py（V1，冻结开关版）、exp10b_collect.py（分批采集器）、v0_a/partial_v0_b/v1_a/partial_v1_b.json（240 局）、collect.log、EXP10B_REPORT.md（本文件）
