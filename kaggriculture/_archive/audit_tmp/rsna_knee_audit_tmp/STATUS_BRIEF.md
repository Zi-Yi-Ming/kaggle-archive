# Kaggriculture 现状简报 v10（2026-09-06，GPT 版）

日期：2026-09-06 ｜ 整理人：AtomCode（deepseek-v4-flash）｜ 完整证据：_audit_tmp/（route_transfer/：DESIGN_NOTE/ROUTE_SPEC v2/SANITY_REPORT/phase5_runner.py/smoke_{v0,v1,v2}.jsonl/3 variants/tape_b.json；ablation_*.jsonl 6×120；bench 三仓库各 120；机制审计三件套）
本轮核心：**EXP-8/Phase-5 Smoke = FAIL（reconciliation 违规），按用户停止规则正式 benchmark 暂停**；等用户选 reconciliation 修复选项（A/B/C）。V0≡生产逐字节通过、V2 路由工作正常——失败在测量口径，不在 treatment。

---

## 1. 生产状态

- 生产 agent = **纯 v11E**（sequential beam + ProductBelief/hazard/transition/shop counter/exact market model），线上 Elo **942.2**，零改动（md5 224a1c47...）
- 恢复性提交 ref **56047543**；engine 1.32.7；fixed-RNG = env.info["seed"]

## 2. 路线历史（已完成阶段）

```
E1/E2/E3 机制移植: 全 FAIL → 候选池清空
EXP-6 完整复刻基准: lonespear(碾压) / Seyamalam(经济持平) / COK(+29% bank 反杀)
EXP-7/Phase-1 因果消融: vs v11E 只有 route selection(E) 有因果证据（+3,681/局净）
EXP-8/Phase 0-4: E 的 v11E 隔离实验前置全过 → READY
EXP-8/Phase-5: Smoke FAIL（reconciliation）→ 正式 benchmark 暂停（本轮）
```

## 3. EXP-8/Phase-5：Smoke 结果（本轮新状态）

**通过项**：V0≡生产 v11E 逐字节（seeds 1/13/57 全 True，treatment 完整性完好）；V2 route 真实发生（seeds 1/2 选 B / seed 3 选 A）；720 步完整无异常。

**失败项（exact reconciliation ≠ 0）**：

| Variant | reconciliation_error |
| --- | ---: |
| V0 | −5,545（seed 3） |
| V1 | −3,054 / −2,646 / −5,545 |
| V2（B 路线） | **−152,916 / −140,176**（终局 bank 仅 7.5k-11k） |
| V2（A 路线） | −5,545 |

**根因（runner 会计口径缺陷，非 treatment 缺陷）**：记账按"发出的订单"（action 流）求和，但引擎对**无现金/无库存订单静默失败**——V0/V1（生产 tape 匹配良好）只差 2.6k-5.5k；**V2 B-route 的 tape B 与当前对局状态错位，订单绝大多数不执行**（意图成本 ~150k 实际未发生）→ 巨大负误差。观测级限制：obs 层无法逐单归因（一步多单 + 引擎内部成交价），executed 口径需 money/shed 状态差推断。附带异常：v0/v1 部分 seed 的 `first_sig_step` 记 0（与 step-0 空签名探测矛盾，runner 记录待查，不影响 route 决策）。

**协议处置**：按用户停止规则（"reconciliation≠0 先停止解释结果" + "立即停止先报告，不要修完继续跑"）→ **正式 benchmark（V0/V1/V2 × 120 × 6 对手）暂停**，未跑任何正式局。未修改 production、未调参、未 p-hack。

**等待用户决策（A/B/C）**：
- **A**：批准修 runner 会计为 executed 口径（money/shed 状态差推断实际成交）→ 重 smoke → 通过后进正式
- **B**：批准调整协议（issued 口径 + 偏差带，reconciliation 作描述性指标而非硬门）
- **C**：维持硬门——executed 口径会计就绪前不进入正式

## 4. EXP-8 前置回顾（Phase 0-4，已完成）

- DESIGN NOTE：v11E 单 tape（`_TRACE`）vs COK 5-route（unlocked_shops 签名→label→tape）；E 机制必要条件 = 公共签名→纯函数映射→早期决定+锁定→多 tape
- ROUTE_SPEC v2：首个非空签名步决定（step 0 恒空，商店 step 72/144/216 解锁，引擎现实驱动的规格修订）+ 全程锁定 + 纯函数哈希 A/B 二分
- SANITY：7 项全过（V0≡PROD 逐字节、V1 结构对照、V2 路由运作 seeds1-16 A=5/B=11、确定性双跑）
- Gate：READY FOR 120-PAIR BENCHMARK（前置全过）

## 5. 已完成证据链（前轮回顾）

- 三仓库全量基准：lonespear（v11E 100% 胜 +36.5k）/ Seyamalam（v11E 70.8% 胜，经济持平）/ COK（COK 100% 胜 +29% bank）
- EXP-7 消融：vs v11E 仅 E 有因果证据（47/120，+11,050/局）；A/B/C 休眠（clone 门从不打开）；D 真 no-op
- 归因修正：COK 的 +29% 主体来自基础策略（tape 主干 + 无条件叠加层），非 meta 市场层

## 6. 下一步候选（按优先级）

1. **EXP-8 Phase-5 恢复**（取决于 reconciliation 决策 A/B/C）
2. Discussion 最新强 tape 对照（739273/737764，当前 live meta 上限；需 Kaggle episode 抓取）
3. 线上 Elo 监控照旧（v11E 942.2 / 恢复提交 56047543；截止 2026-09-23）

## 7. 方法论收获（跨轮累计）

- 机制单拆 3/3 证伪 vs 完整复刻 10 分钟定案 → "先全量基准、再拆机制"顺序正确
- 因果消融方法论：单点禁用 + Full−Ablation + 触发计数 + 动作级 MD5
- **测量口径纪律**：reconciliation 必须区分"发出的订单"与"实际成交"（引擎静默失败无现金/无库存订单）——smoke 抓出会计缺陷即停止，不"修完继续跑"
- 隔离实验规格修订纪律：引擎现实驱动（商店解锁时间线）的修正，未参考结果
- README/historical rating 三次失效；era+环境双重漂移；证据以对局为准
- 基础设施：mp.Pool heredoc 挂起；长链超时须分批；imap 裸 int 种子需 run_one(seed)

## 8. 验收协议（所有实验）

engine 1.32.7、fixed-RNG（env.info["seed"]）、paired seeds 1-120、异构对手池 ≥50 局、守恒审计 + exact reconciliation、Wilson CI + paired 检验（含 permutation）。禁止 p-hacking；证据不足立即停止。
