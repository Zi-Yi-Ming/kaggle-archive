# ROUTE_SPEC（EXP-8 Phase 1-2：E 机制抽象）

日期：2026-09-06 ｜ 预注册于任何 benchmark 之前。本规格只描述机制，不涉及优化/调参。

## 1. Mechanism 一句话

> 在 agent 的 tape 源选择层注入"公共可观察签名 → 候选 tape"的一次性锁定映射；除 tape 源外
> 不改变 agent 的任何其他行为。

## 2. Inputs

| 输入 | 来源 | 说明 |
| --- | --- | --- |
| `unlocked_shops` | `obs["town"]["unlocked_shops"]`（引擎 1.32.7 公共字段，与 COK `_public_shops` 同源） | 对局开局时的已解锁商店列表；纯公共信息，对手不可见差异（双方同场共享） |
| `player` / `seat` | `obs["player"]` | 每座独立的锁定状态（V2 需要每座各自的 route 决定） |
| `step` | `obs["step"]` | 仅 step==0（首调用）执行决定；之后锁定 |

## 3. Candidate routes

| 候选 | 内容 | 来源 |
| --- | --- | --- |
| **tape A** | 生产 v11E 的 `_TRACE`（720 步 {farmer, hands, market}） | main.py 内嵌（不改动） |
| **tape B** | v11E 在参考局（seed 42 vs closer_cleo）录制的 720 步动作流 | Phase 3 录制（同策略家族，非 COK 内容） |

（迁移设计允许扩展到 N 条 tape；本实验最小化 = 2 条。）

## 4. Selection rule（纯函数，预注册）

```python
def route_for(obs):
    shops = obs.get("town", {}).get("unlocked_shops", None)
    if not isinstance(shops, (list, tuple)) or len(shops) == 0:
        return "A"                       # fallback = tape A（畸形/缺失签名）
    key = tuple(sorted(str(s) for s in shops))
    h = 0
    for ch in "|".join(key):
        h = (h * 31 + ord(ch)) & 0x7FFFFFFF
    return "A" if (h % 2) == 0 else "B"  # 签名哈希 → 二分
```

- 无 threshold、无 tie-break（二元决定）、fallback = tape A
- 规则为纯函数：同一 obs 必得同一 route

## 5. Statefulness

- **每局一次决定 + 全程锁定**（修正 v1：Phase-4 探测发现引擎的 `unlocked_shops` 在 step 0 恒为空（商店在 step 72/144/216 = day 3/6/9 解锁）→ step-0 决策恒 fallback A、路由机制失效。修订为**首个非空签名步决定**：`route_for` 在 `len(unlocked_shops)>0` 的首步执行一次并锁定，之后不再重算、不允许 switch；签名出现前的步（0..71）运行 tape A。引擎现实驱动，未参考任何实验结果的修正）
- 状态按 `(seat)` 键存；step==0 时重置为未决定

## 6. Determinism

- `route_for` 是 `obs` 的纯函数；`obs` 由 seed+engine 唯一确定 → 同 seed+engine+环境 ⇒ 同 route 决策
- 锁定后 tape 源固定 → 动作流由"选定 tape + 原有叠加层"唯一确定 ⇒ 同 seed 必得逐字节一致动作流
- V1（fixed）：恒选 tape A（= 生产 tape）→ 预期与 V0 动作流逐字节一致（结构对照组）
- V2（router）：首个非空签名步决定后锁定 → 与 V1 的差异仅来自 route 决策（签名前 0..71 步同为 tape A）

## 7. 注入点（实现约束，Phase 3）

- 仅替换 `_base_agent` 读取的 tape 源（生产 main.py 的模块全局 `_TRACE` 引用 → 变体模块持有的 tape A/B）
- 不动：market 叠加（keep/_plan_sells/beam）、`_front_run`、`_terminal_liquidation`、`_terminal_action`、hazard/ProductBelief/transition/shop counter/exact market model
- 不引入：H4 / 城镇需求 / meta front-run / 牛编排 / COK 任何策略内容

## 8. 指标与比较（Phase 5 预注册）

- 主指标：paired bank delta；比较 V1−V0（multi-tape 结构效应）/ V2−V1（route 选择效应）/ V2−V0（总迁移效应）
- 记录：route selected / switch count（应为 0）/ route score（无——二元决定）/ per-day bank / realization price / production & market actions
- 统计：mean/median bank delta、Wilson CI、paired permutation、effect size
