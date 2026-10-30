# EXP-10A FINAL REPORT — v11E Tape Structure Audit

日期：2026-09-07 ｜ 只读行为审计 ｜ production v11E 绝对冻结（md5 `224a1c47...`，Elo 942.2，未提交，未改任何代码/配置）
预注册：EXP10A_PLAN.md（seeds 1-20 × seats 0/1 × closer_cleo = 40 games；阈值 0.25/0.5/0.75/1.0；分类规则先定义）— 本报告全部按预注册执行，40 局全入，未删局/未改阈值/未 p-hack

## 0. Gates（全部 PASS）

| Gate | 结果 |
| --- | --- |
| A deterministic control（seed 7 seat 1，20 局 double-run） | **20/20 动作流逐位一致**（MD5 全同，唯一 stream） |
| B 40 games 720/720 | PASS |
| C executed-ledger reconciliation==0 | PASS（0 failures） |
| D production fingerprint | PASS（md5 224a1c47... 不变） |

## 1. Q1 — backbone ratio

**BACKBONE_RATIO(all) = 0.9361**（674/720 步在全部 40 games 中动作逐位一致）。
分族：movement 0.9998（718/720）、**buy 1.0000、hire 1.0000、land 1.0000（100% 固定）**、sell 0.9650（674/720）——**全部可变性集中在 SELL 族**。
按日：Day 1-5: 100% / 6-10: 100% / 11-15: 97.5% / 16-20: 92.5% / 21-25: 86.7% / 26-30: 85%（前期完全固定，末期逐步放开）。

## 2. Q2 — 动态节点占比

**43/720（6.0%）** step 满足 `H(action|step) > 0.5 bit`（预注册阈值）。
敏感度（仅描述性）：0.25→44 步、0.5→43、0.75→23、1.0→20——阈值变化不大，动态节点轮廓稳定。
H mean 0.063、median 0.000、p90 0.000、max 2.377（中位数熵为 0 = 一半以上步完全固定）。

## 3. Q3 — 动态节点触发源

**首分歧归因（380 seed-pairs，预注册优先级 SHOP>MARKET>OWN_STATE>OPPONENT>UNKNOWN）：SHOP = 380/380（100%）**——全部首次分歧步的 `unlocked_shops` 签名不同。
条件熵证据（43 动态点均值）：H_all 1.036 → **H|shop 0.020**（降熵 98%，shop 签名几乎完全解释可变性）；H|market 0.315；H|own 0.641；H|opp 0.786。
动态步动作族：SELL 占绝对主导（4679 次 vs BUY_PRODUCT 120 / BUY_SEED 120）——**动态决策 = 依据商店解锁状态调整 SELL 时机/数量**。
（注：HIRE 720 出现在动态步计数是步内其他订单可变所致，agr_hire=1.0 已证 HIRE 本身完全固定。）

## 4. Q4 — 稀疏局部 or 级联全局

**稀疏局部（sparse/local）**：
- divergence episodes：n=9226、**median 1、p90 1、longest 3**——分歧后 1-3 步内**重新收敛**（分歧是孤立局部修正，不改变整条轨迹）
- LCP（最长公共前缀）median **362**（整局前半段逐位一致）；lev_norm median 0.0375（edit distance 仅 3.75%）、max 0.0583
- 首分歧 step median 362（day 15）、p90 386、max 526——分歧集中在后半程商店解锁后
- 无级联证据：未观察到"早期分歧 → 后续整链分叉"（episode longest=3 否决级联假设）

## 5. Q5 — Type 归类

**B（Tape + Sparse Adaptation）**：
- 证据：backbone 0.936（≥0.80 规则）；动态点少（43/720）且与明确 state condition（shop signature）**稳定相关**（H|shop 0.020、380/380 SHOP 归因）；movement/buy/hire/land 100% 固定
- 非 A（backbone 0.936 < 0.95 规则，动态点 43 ≥ 10）；非 C/D（无可否认的 state-dependent 主结构）
- 结论：v11E = **高度固定的确定性主干 + 稀疏的商店驱动 SELL 自适应点**

## 6. Q6 — 跨 seed 稳定性

**稳定**：整体熵极低（H mean 0.063）；主干 93.6% 跨 40 games 逐位一致；唯一可变族（SELL）由 shop 签名稳定驱动（同一 shop 条件下动作一致率高）；分歧后快速重收敛；序列相似性高（lev_norm 3.75%）。**action variability ≠ adaptation 的判别**：动态点的动作变化可由 shop 条件稳定解释（≥2/3 一致性判据满足，H|shop≈0）→ 属 **candidate conditional branch**，非无规律漂移。

## 7. Q7 — 可实验机制 hypothesis（仅记录，不实现）

- **H1**：v11E 的 SELL 族自适应（时机/数量/排序随 unlocked_shops 组合变化）是可分离的最小自适应机制——未来可做"固定 backbone + 该单点自适应"的消融对照（如冻结 SELL 策略为固定排程 vs 现状），量化其经济价值。
- **H2**：末期（day 21-30，backbone 降至 85%）的更高可变性可能对应商店解锁密度增大，而非策略退化——可通过 day 分段条件熵验证。
- 按协议：以上仅为 hypothesis，不实现、不进入 EXP-10。

## 8. 稳定性 vs 经济结果

modal-agreement 与 final bank 的 Pearson r = **−0.016**（无相关）——稳定性与收益不相关；不做优化依据。

## 9. 决策规则结论

```
backbone 高 (0.936) + 动态点少 (6%) + 动态点与明确 shop condition 稳定相关
→ 下一阶段可研究 "固定 backbone + sparse adaptation"（提出，不执行）
```

- 不实现 adaptive branch、不 EXP-10、不 tape 移植、不优化、不提交 Kaggle
- Production v11E 冻结确认：md5 `224a1c47...`、Elo 942.2、recovery 56047543、engine 1.32.7

## 10. 产物

- `_audit_tmp/exp10a/`：EXP10A_PLAN.md、raw_{seed}_{seat}.jsonl × 40（42MB）、EXP10A_ENTROPY.csv（step 级 H + 5 条件熵）、EXP10A_BEHAVIOR.csv、EXP10A_DIVERGENCE.csv（380 pairs 首分歧+cause+episodes）、EXP10A_SEQUENCE.csv（Levenshtein/LCP/LCS）、EXP10A_SUMMARY.md、EXP10A_FINAL_REPORT.md（本文件）、exp10a_collect.py / exp10a_analyze.py
