# RESEARCH CLOSED — Kaggriculture 公开侦察 + 自研（2026-09-27）

**状态:** CLOSED（研究线）  
**生产:** Metav4 **56390446** + Thomas **56358711** 双 HOLD  
**定位:** 研究结束 · 生产锁定 · **金牌 lottery mode = 等信息增量**  
**金牌定稿:** 不是没机会，是 **当前证据集里没有主动制造金牌的办法**  
**依据:** 参谋终裁 + P87–P93 / Gold Shot v0–v1 闭合  

## 核心问题

> **是否有足够强的新信息，值得改变截止时的 active pair？**

**每天只盯三源（极低成本）:** thomastschinkel 真更新 · 真新 adaptive family · Andrey V12 bytes。  
**禁止:** Best 标题无限搜包。

## 关闭范围

| 线 | 状态 |
|---|---|
| 公开 kernel 侦察 / 高分标题扫描 | **CLOSED** |
| 自研 wrapper / flag / 中盘劳力 / 终局微层 | **CLOSED** |
| Slot B 主动填充 | **CLOSED**（门禁保留；Thomas HOLD 不替换） |
| **Gold Shot v0**（day6 bandit） | **CLOSED — STOP_NO_SIGNAL** |
| **Gold Shot v1**（多窗口 + 现金 reward） | **CLOSED — INFRASTRUCTURE_PASS / LEARNING_SIGNAL_UNTESTED** |

**Gold Shot 边界（防误读）:**  
- v0 = 单节点 toy probe 无信号  
- v1 = 吞吐 **FAIL**（~94 SPS）+ coverage **FAIL**（Q 未触发→default≈Metav4）；shop 鲁棒 **PASS**  
- **不得写成 RL / learned policy 失败**；赛前算力窗口内 **无法有效检验** 该假设  
- 赛后 v2：fast sim + hierarchical neural macro + large-scale league（继承 chassis/接口）

## Reopen 条件（全部满足才启动定点双门）

1. **新** 可执行高阶 artifact 出现（作者/社区新发，非重贴旧 SHA）  
2. **或** thomastschinkel 公开 **真正更新**（≠ Metav4 v13）  
3. **或** 获得 **Andrey V12 exact `main.py` 字节**（当前 UNRESOLVED）  

且 Reopen 后仍须：exact SHA 校验 → Slot A 或 Slot B 门禁 → Validation → **用户明确授权**。

## 赛后下一代研究路线（2026-09-27 参谋解读 · 非本周任务）

公开讨论支持：榜前 **至少部分** 策略为 RL（如 #121），与 heuristic 并存。  
这与 P46–P69 **不矛盾**，而是闭环：

```text
有限 replay → 无法恢复 full π(state)
     ↓ P46–P69 已证
在线 state-conditioned policy 可越过 representation/data bottleneck
     ↓ RL 是一种实现手段
≠ naive PPO(env) 端到端 720 步
```

社区证据：naive PPO 易 plateau（规则 agent 150k+ vs PPO 卡几千）；大采样仍未收敛。  
**本周动作：不从零训 RL；HOLD Metav4。**

赛后优先方向（按价值排序）：

1. **Metav4 强规则骨架 + learned high-level policy**（开局/资产/market/route 选择）  
2. 状态抽象 + 层级/宏动作（先 factorize action，再 policy heads）  
3. offline replay 作 warm-start + 在线 simulator 大规模 refinement  
4. population / 对手多样性训练（应对 non-transitive meta）  
5. **不要**再写 deterministic guru-counter / 再拧 Metav4 常量  

基础设施缺口（赛后要建）：env throughput、reward design、action abstraction、validation harness、训练可复现。

## 校准点（详见 STATUS / POST_COMP §2.0）

`3009 v48 → 0/6 vs Metav4` · `2882 v43 → 0/6` · `2965 Pipe-16 → 0% vs shop` · Andrey V12 **unresolved**

## 索引

- `_production/STATUS.md` — FINAL FREEZE  
- `_production/GPT_COUNSEL_BRIEF_20260927.md` — 参谋往来  
- `_research/RESEARCH_P87…P92B_*.md` — 否决证据链  
- `_production/POST_COMP_GITHUB_OUTLINE.md` — 赛后归档结构  

