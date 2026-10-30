# 奖牌候选表（Medal Candidate Table）

创建：2026-09-07 ｜ 比赛截止 2026-09-23 ｜ 规则：本地 120 paired 显著增益 → 独立第二套 seed 复现 → Kaggle canary → Elo 证据；**本地赢 ≠ 线上会涨**（Fix-A 教训）

| Candidate | Local Δ | Replication | Online Elo | Decision |
| --- | ---: | --- | ---: | --- |
| v11E（production，md5 `224a1c47...`） | baseline | ✅ | **942.2** | 冻结基准（recovery ref 56047543） |
| v14 | — | — | ~895.7-900.0 | ❌（ref 56036718） |
| v15 | — | — | 869.8 | ❌（ref 56046351） |
| v12（sequential 移除） | negative | ✅ | 874.8 | ❌（线上实证 sequential 必须保留） |
| Fix-A | positive local | ❌ | 891.7 | ❌（本地固定 RNG 假阳性教训） |
| EXP-10B（V0 vs V1 SELL 冻结消融） | ⏳ | ⏳ | — | ⏳ 实验中（audit，不提交） |
| EXP-10C（shop→SELL timing/quantity，视 10B 结果） | ? | ? | ? | 未启动 |

## 门控（每个候选必须走完）

```text
Candidate → 120 paired → fail accounting → STOP
                        → no significant gain → DISCARD
                        → significant gain → 2nd independent seed set
                              → fail → DISCARD
                              → replicate → Kaggle canary → Elo ↑ ? → 决定
```

## 时间盒（截止 9/23）

- 9/9-9/11：EXP-10B（SELL adaptation 因果价值）
- 9/11-9/14：有价值→EXP-10C（一次只拆一个变量）；无价值→v11E bottleneck audit
- 9/14-9/17：最多 2 个候选独立验证
- 9/17-9/20：线上 canary（一次一个变量，记录 submission/seeds/opponents/Elo/rank）
- 9/20-9/22：冻结最终候选，截止前不换策略
