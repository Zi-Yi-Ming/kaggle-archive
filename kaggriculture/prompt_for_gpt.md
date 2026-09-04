# Kaggriculture v10 代码审查 + v11 设计请求

## 背景

我在打 Kaggle 的 Kaggriculture 比赛（Featured，Elo 赛制双人农场模拟，30天=720回合，胜负看赛季末银行余额）。当前最优提交 v9 Elo ~887-1045。我刚完成 v10 架构升级，本地真实引擎 ablation 显示银行从 83k 单调提升到 91k，但 Elo 效果待验证。

**比赛机制速览**：
- 10x10 地块，初始解锁 NW 象限，可花 1000/2000/4000 买 NE/SW/SE
- 作物 WHEAT(10)/CARROT(20)/TOMATO(50)/STRAWBERRY(100)/MELON(80)；动物 GOOSE(300→EGG)/COW(400→MILK)/SHEEP(500→WOOL)，动物每天需喂 1 WHEAT，连续2天不喂死亡
- 市场动态价格：商品初始库存10000，城镇商店每4回合消费一次，每种商品有独特谷贱曲线（高端品超产即崩到$1）
- 市场订单按列表顺序逐条成交，先卖拿好价；先卖的钱可喂后面的买
- 雇 hand 每天重置需重雇（fib 成本）；每日24回合 farmer 重置回仓库旁
- 引擎版本 kaggle-environments 1.32.7（已含 tomato/carrot/egg 的 scarcity 平衡更新）

**关键认知**：
1. 生产层已收敛：104个队伍共享同一 712 回合 meta field plan（8COW+5SHEEP+6STRAWBERRY，跨3象限）——我直接播放这套 trace（base85压缩的 _TRACE 数组）
2. 生产固定后，卖货层（market layer）是唯一分水岭。Tier6-9 共享同一生产计划，仅卖货不同，独立得分 148k-164k
3. Elo 只看胜负不看银行差额：Cleo（保守原位卖货）银行最低(83k)但头对头全胜其他 Tier——Liquidity dominance 现象
4. v10 假设：在固定 meta plan 下，仅靠"在线估计对手 + liquidity-aware + counterfactual timing"就能系统性提高最终银行

## 我的 v10 架构

```
META FIELD PLAN（固定，_TRACE 播放）
    ↓
Opponent Observer（新增）
  ├─ 市场库存差分反推对手卖出量: Δinv = -镇消费 - 我卖 - 对手卖
  ├─ 对手生产速率估计（动物/作物可见计数 × 手工先验速率）
  ├─ 对手 shed 库存估计 + 不确定性追踪（简单累积差分）
  └─ 对手近期卖出频率（likely_sell_soon）
    ↓
Liquidity-aware 卖货决策（新增）
  Utility = Revenue − PriceDamage + λ·CashUnlock + ρ·OpponentDamage
    ↓
Counterfactual timing（新增，可开关 _V10_COUNTERFACTUAL）
  ├─ hold_bonus: 预测镇消费将推高价格且对手不抛 → 延迟卖
  └─ rush_bonus: 对手即将抛售同商品 → 抢先卖
    ↓
Cleo 原位卖货布局（保留，_SELLS_FIRST=False 保现金流稳定）
```

## Ablation 结果（本地真实引擎，5 seeds × 2 seats）

| 模式 | 平均银行 | 说明 |
|---|---|---|
| A = Cleo 原版 | 83,328 | 基线 |
| B = +对手估计+liquidity | 87,789 | +5.4% |
| C = B+反事实时序 | 91,244 | +9.5% |

单调提升，说明三个模块逐层叠加有效。但 C 在头对头中略输给 A（边缘），提示"银行高≠胜率高"，Elo 赛制下可能另有玄机。

## 代码（cleo_v10.py 全文，875行）

[在此粘贴 cleo_v10.py 完整代码]

## 我的具体问题

1. **Opponent Observer 哪些估计太粗糙？** 我已知：
   - `_CROP_RATE`/`_ANIMAL_RATE` 是手工先验，未按 1.32.7 scarcity 更新校准
   - `shed_est` 是简单累积差分（prod - opp_sold），长期会漂移，无衰减/重锚定
   - `likely_sell_soon` 只看最近6次卖出的均值，未按 day 分段
   - 对手卖出的推断 `opp_sold = -Δinv - drain - mine` 可能被 DROP（$1 floor 不可见损失）污染
   请给出每个估计器的改进方案（具体公式/数据结构/重锚定策略）。

2. **Utility 系数 λ/μ/ρ 全手调，如何系统化搜索？** 有没有比 grid search 更聪明的办法（贝叶斯优化/演进策略），在有限本地对局预算内找到最优系数组合？

3. **Counterfactual timing 的价值方向对吗？** 我预测"下次商店消费后价格变化"来决定 hold/rush。但这个游戏还有"对手下一回合就会卖"的 first-mover 博弈——如何把 P(对手先卖) 显式建模进决策？

4. **Elo 赛制 vs 银行最大化冲突怎么办？** 如果 v10 Elo 验证后发现 91k 银行没转化为 Elo（情况B），说明应该做 P(win|opponent strategy) 的对手策略分类 + matchup-specific policy。请设计这个分类器的特征集和决策框架。

5. **belief state 质量**：我现在的状态是确定性估计（单值+unc），要不要升级成真正的 belief distribution（如粒子滤波/正态分布维护）？在 720 回合×24/天的预算内，哪种复杂度值得？

6. **1.32.7 scarcity 对 tomato/carrot/egg 的影响**：我的 _MP 价格模型还是老的（log/sqrt/linear 参数），需不需要按新引擎重新校准？怎么验证？

请按优先级排序你的建议，并给出 v11 的具体实现设计（数据结构 + 伪代码级别）。
