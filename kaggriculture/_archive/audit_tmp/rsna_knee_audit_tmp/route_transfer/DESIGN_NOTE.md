# ROUTE TRANSFER DESIGN NOTE（EXP-8 Phase 0）

日期：2026-09-06 ｜ 来源：EXP-7/Phase-1（唯一 MIGRATION CANDIDATE = E route selection）＋ 本次只读源码审计（未修改任何代码）

## 1. v11E 单 tape 是什么（CODE）

- `_TRACE`（main.py 内嵌）：720 步开环动作表，每元素 `{farmer, hands, market}`；末步 farmer=`["PASS"]`
- 执行入口：`_base_agent`（L266）L275 `action = copy.deepcopy(_TRACE[step])` → `_front_run` → `_terminal_liquidation`（step≥717 走 `_terminal_action`）
- `agent`（L1377）只覆盖 market 层：keep（tape 订单减 _RESERVE SELL）+ `_plan_sells` + beam 排序
- **无选择逻辑**：全游戏同一 tape，无 per-game 初始化（模块常量），无 route 概念
- 单位动作（farmer/hands）100% 来自 tape；market 由 tape 提供 base 订单 + 活叠加

## 2. COK 多 tape 是什么（CODE，repoC HEAD 7ef67eac）

- 5 条 route tape：`_V7_CURRENT_ROUTES` = {`10c4s_3q`, `8c6s_3q`, `6c8s_3q`, `6c12s_4q_first_yarn`, `6c12s_4q_second_yarn`} → `_ACTIONS_*`（内嵌 720 步表）；另有 `_V7_LEGACY_ROUTES`（前 72 步布局变体）+ 并行 `_V7_*_SALES` 卖出计划
- 选择逻辑：`_select_route`（L1255）→ `_public_shops`（L1028 读 `obs["town"]["unlocked_shops"]`）→ `_v7_route_label`（纯函数：YARN_STORE 在 shop 前 1/2/3 位 → first_yarn/second_yarn/6c8s_3q；奶支持在前 3 → 10c4s_3q；否则 8c6s_3q）→ label → route tape
- 覆盖层：`_v8_route_label`（L1174）对 "6c8s_3q" 特殊情况用距离阈值缓存决策（third_yarn_milk，一次锁定）；`_v10_should_use_v5`（L1127）v5 专家 route 门（单调只关）；`_v7_legacy_layout`（前 72 步）选 legacy 变体
- **锁定行为**：`state["label"] = _v8_route_label(...)` 每步重算（shops 解锁会改 label → 允许 route 切换），但第三方决策缓存一次、v5 门单调

## 3. E 的"机制必要条件" vs "COK 实现细节"

| 必要条件（E 的抽象内核） | COK 实现细节（迁移时可替换/省略） |
| --- | --- |
| ① 一个**公共可观察签名**作为 route 输入（unlocked_shops） | 具体 label 集合（5 个）与语义（YARN_STORE/奶判定） |
| ② 签名 → **label/route 选择**（纯函数映射） | 距离阈值缓存（third_yarn_milk）、v8 特例 |
| ③ 每局**早期决定 + 有效锁定**（label 重算但单调/缓存） | v5 专家 route 门（_v10_should_use_v5 + _v10_v5_route） |
| ④ 候选 route = **多个 720 步 tape** | legacy 布局变体（_v7_legacy_layout） |
| ⑤ 并行卖出计划（route 决定 tape 也决定卖出节奏） | _V7_*_SALES 的具体排程 |

## 4. 迁移设计含义（对 v11E）

- v11E 迁移"多 tape + route"的最小注入 = 只换 **tape 源**：`_base_agent` 读的 `_TRACE` 替换为路由选定的 tape；其余（market 叠加/beam/front_run/terminal）零改动
- tape B 来源 = v11E 自己在参考局录制的动作流（同一策略家族，**不引入 COK 内容**）
- route 输入 = 与 COK 相同的公共字段 `obs.town.unlocked_shops`（引擎 1.32.7 同构）
- V1（fixed）= 双 tape 存在但恒选 tape A（= 生产 tape）→ 预期与 V0 动作流逐字节一致（结构对照组）
- V2（router）= 签名（unlocked_shops）→ 哈希映射 → tape A/B，**开局一次决定、全程锁定**（比 COK 的每步重算更保守，锁定的确定性更强）

## 5. 实验基线确认（HEAD）

- engine = kaggle_environments 1.32.7；fixed-RNG = `env.info["seed"]`；paired seeds 1..120；obs 动作后状态语义（state(s)−state(s−1)）
- 对手池：EXP-6 基准对手为 v11E（对 v11E 变体无意义）→ Phase 5 对手 = 验收协议池（closer_cleo 家族 + broker_bea/slotter_silas/ledger_lena/melon_mateo/rancher_rita 异构），120 seeds 配对
- 生产 main.py 未改动（md5 保持 224a1c47...）

## 6. 风险与预注册

- 选择规则为纯函数（unlocked_shops → tape），预注册于 ROUTE_SPEC，**不按结果调参**
- 若 V1 与 V0 动作流不一致 → sanity FAIL（结构注入泄漏）→ 停止
- 若 V2 路由决策非确定性 → sanity FAIL → 停止
