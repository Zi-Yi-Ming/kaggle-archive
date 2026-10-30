# ACCOUNTING_AUDIT（EXP-8 Phase A0）

日期：2026-09-06 ｜ 对象：`_audit_tmp/route_transfer/phase5_runner.py` 会计层 vs 引擎 1.32.7 真实执行语义（先解释，再修）

## 1. 引擎 1.32.7 市场执行语义（CODE，kaggriculture.py）

### 1.1 `_process_market`（L544-628）：per-unit lockstep
- 每步把双方 market 队列截断到 max_orders=10；按位置逐一处理：**先原子单（HIRE/BUY_LAND，按玩家顺序各处理一次，无部分执行），再 SELL/BUY_\* 的逐 unit lockstep 循环**
- lockstep 循环（L583-626）：每个 unit，双方同时按**当前市场库存**报价（`market_price(item, inventory[item])`），然后双方各 `_commit_unit` 一次；成交则 remaining−1，失败则**整单中止**（`order_states[player_id] = None`——失败 unit 之后的剩余 unit 全部不执行）
- **部分执行存在于订单内**：如 10 个 unit 中前 2 个成功、第 3 个失败 → executed=2, failed=8（订单在失败处中止）
- 报价（L596-605）：
  - SELL：`market_price(item, inventory[item])` —— 随已成交 unit 导致的库存变化**逐 unit 变动**
  - BUY_PRODUCT：`market_price(item, inventory[item] − 1)` —— 按买入后库存报价
  - BUY_SEED：固定 `CROPS[item]["seed"]`（WHEAT 10/CARROT 20/TOMATO 50/STRAWBERRY 100/MELON 80）
  - BUY_ANIMAL：固定 `ANIMALS[item]["cost"]`（GOOSE 300/COW 400/SHEEP 500）
- 每步结束 `_refresh_prices(market)`

### 1.2 `_commit_unit`（L652-687）失败条件
| 订单 | 失败条件（返回 False → 整单中止） | 成功效果 |
| --- | --- | --- |
| SELL | `shed[item] <= 0` | shed−1；money += price；inventory[item]+1（仅 price>1 时） |
| BUY_PRODUCT | `money < price` 或 **shed 满（≥ shed_capacity=100）** | money −= price；shed[item]+1；inventory−1 |
| BUY_SEED | `money < price` | money −= price；seeds[item]+1（**不查 shed 容量**） |
| BUY_ANIMAL | `money < price` 或 shed 满 | money −= price；shed[item]+1 |
| HIRE（原子） | `_do_hire`：当日已雇数 → 成本 `FARM_HAND_COST_MULT × _fib(n)`（**fib 递增**，非平值） | hands+1；money −= 成本 |
| BUY_LAND（原子） | 未知象限（LOCKED）或现金不足 | 解锁象限；money −= 4000 |

### 1.3 关键会计事实
1. **obs 价格为动作后状态**（步末 `_refresh_prices` 后）：**不能用作成交价**——SELL/BUY_PRODUCT 的逐 unit 成交价在过程中随库存变动，步末 obs 价只是终态价
2. **executed ≠ issued**：无现金/无库存/shed 满 → 首个失败 unit 起整单中止（部分执行 = 失败前已成交的 unit 数）
3. 引擎对失败订单**静默**（无日志、无回报）
4. money 仅由市场订单改变（单位动作不改 money）；shed 受单位动作（DROP/PICKUP/PLACE）与市场订单双重影响
5. HIRE 成本为 **fib 递增**（当日第 n 雇 = mult × fib(n)）——runner 现用平值 120 是价格错误

## 2. 现有 runner（issued 口径）逐交易类型缺陷

| 订单 | runner 现状（issued 口径） | 缺陷 |
| --- | --- | --- |
| SELL | `qty × obs 步末价` 计收入 | ① 未成交订单也算（无库存静默失败）② 成交价用步末价 ≠ 逐 unit lockstep 价 ③ 部分执行被忽略 |
| BUY_PRODUCT | `qty × obs 步末价` 计成本 | 同上（无现金/shed 满静默失败；lockstep 价 ≠ 步末价） |
| BUY_SEED | `qty × 固定 seed 价` | 价格对（固定），但未成交 qty 也算 |
| BUY_ANIMAL | `qty × 固定 cost` | 价格对，但未成交 qty 也算（无现金/shed 满） |
| HIRE | `120 × qty` | **价格错**（fib 递增）+ 未成交也算 |
| BUY_LAND | `4000 × qty` | 价格对，但未成交也算（现金不足/LOCKED） |

## 3. 修复路径（A1/A2 设计输入）

- **executed ledger 重建** = 用引擎自身函数逐 step 重放市场处理（import `kaggriculture.py` 的 `_parse_order`/`_commit_unit`/`market_price`/`_do_hire`/`_do_buy_land`/`_refresh_prices` + 双方订单队列 + 重建的步前状态），输出每订单 executed/failed qty + 逐 unit 成交价
- **步前状态重建**：`obs(s−1)` + 单位动作效果（DROP/PICKUP/PLACE 对 shed 的影响——单位动作不改 money）→ 喂给重放
- **验证**：重放后的 money/shed/seeds/market inventory 必须 == `obs(s)`（replay 精确性证明；不等即说明重建有 gap → 停止报告）
- 禁止：heuristic allocation、tolerance、issued 口径回退
