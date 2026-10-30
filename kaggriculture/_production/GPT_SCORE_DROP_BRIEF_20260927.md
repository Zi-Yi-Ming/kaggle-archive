# 掉分专项简报 — 可直接粘贴给 GPT

**日期:** 2026-09-27（CLI 刚查）  
**竞赛:** Kaggle kaggriculture · 提交截止 **2026-09-30** · BT 终榜约 **10-01→10-15**  
**账号:** ZiYi-Ming  

---

## 1. 当前 last-2（CLI Submissions）

| ref | 名称 | status | publicScore |
|---|---|---|---:|
| **56390446** | **Metav4 v13**（thomastschinkel 公开包 + 本地门禁） | **COMPLETE** | **2658.8** |
| 56359570 | goodpjw melon-2749 | **ERROR**（Validation 失败，不参战） | — |
| 56358711 | thomas 2945 farm | COMPLETE | **2377.9** |
| 56346424 | alperen path twin | COMPLETE（已掉出 last-2） | 1772.6 |

- **Team 显示分 ≈ max(last-2) ≈ 2658.8**（Metav4）  
- **槽位:** Metav4 **仍在** last-2；未观察到 last-2 丢失  
- 日配额 5；**只认最新 2 次**；重交同包 = **新路径约从 600 起爬**

---

## 2. Metav4 公开分轨迹（CLI / 会话记录）

```text
提交后爬升 → 峰值约 2792
→ 2710.0
→ 2695.5
→ 2687.6
→ 2669.5
→ 2658.8   ← 当前（持续阴跌）
```

thomas 同步回落（约 2426 → 2378），**不是单包崩溃**，更像 **池变强 / 连续不利匹配 / 相对档位被挤**。

官方机制（赛制页/讨论区共识）:

- 公开分 = **live matchmaking Elo**  
- **最终名次/奖牌 = 截止后 Bradley-Terry**（约两周），只计 **last-2**  
- **不承诺** 截止时 public 分 = 终榜分  
- UI 奖牌为 **相对档位**，他人爬分也会把你视觉上往下挤  

---

## 3. 本地已关闭的「止跌手段」（为什么不敢乱交）

### 3.1 双门标准

```text
Slot A 主力: vs Metav4 ≥60% 且 vs shop_router v7 ≥50% + holdout + Validation + 用户授权
Slot B hedge: 官方 team = max、第二槽无 downside；但仍要求无 0/x 族崩 + 异构面板 + Validation + 授权
```

生产基线: Metav4 vs shop_v7 本地 **~100%**，mean 约 +数千。

### 3.2 公开高分 exact 复核（全部未过门）

| 候选 | 公开 Best 标签 | Exact | vs Metav4 | vs shop_v7 |
|---|---:|---|---:|---:|
| Pipe-16 / haideptry 2965 / 2950 / guru v4 | ~2950–2965 | 克隆同 bank | +50～78 / 高胜率 | **0% −16k** |
| Kaito v43 | 2882 | SHA=manifest | 0% −23.6k | 0% −22.4k |
| **Kaito v48 Fast Routes** | **3009** | SHA=manifest | **0% −23.6k** | **0% −22.4k** |
| Andrey Breaking the Tie V12 | 2883 | **UNRESOLVED**（版本 API 403） | — | — |
| Andrey 可得 bootstrap V21-R1 | — | =notebook | 0% −35.8k | 0% −33.6k |

### 3.3 自研 / Gold Shot v0

- P87–P91: 条件 Hybrid / 中盘劳力 / flag 突变 / 终局微层 — **双门全灭**  
- Gold Shot v0（Metav4 day6 宏 route bandit，30 局）: vs Metav4 **0.125 / mean 0**，shop **1.0 未崩** → **STOP_NO_SIGNAL**（≠ RL 失败）  
- **无任何本地证据**表明存在「现在交上去就能止跌」的包  

---

## 4. 请你（GPT）回答的问题

1. public Elo 从 ~2792 阴跌到 ~2659，而 last-2 仍 COMPLETE：这在 BT 终榜下 **是否仍应 HOLD**？  
2. 截止前 2–3 天，若无可过双门候选，**任何换包** 是否 EV 仍为负？  
3. 若 BT 对 last-2 **分别计分再取队最优（max）**，弱第二槽（thomas ~2378）是否几乎无害？  
4. 是否存在我们逻辑上漏掉的「不破坏 Metav4 地板」的 **合法第二槽** 策略（不是 Pipe-16 谱系）？  
5. 2659 在本池封榜 BT 下，**银区量级是否仍合理期望**？奖牌 UI 相对档位应如何表述？  

---

## 5. 我方当前决策（2026-09-27 外部参谋已确认 HOLD）

```text
PRODUCTION
A = Metav4 56390446 · 2658.8 · HOLD
B = Thomas 56358711 · 2377.9 · 不主动替换（非空槽）
ERROR = goodpjw 56359570 · 不参与 matchmaking
Team = max(A,B) ≈ Metav4

RESEARCH
公开 kernel / 自研 / Gold Shot v0 = CLOSED

SUBMISSION
无 Reopen 证据 → 不投
```

**HOLD 精确理由（非「掉分所以更不能动」）**

1. 公开 Elo 是 live matchmaking rating；阴跌 ≠ Metav4 同幅度退化（thomas 同步回落）。  
2. 终榜 BT 使用**最终仍 active** 的两 bot 之间的有效对局；换包会改 active 集合与历史 episode 是否计入。  
3. 新/重交路径从 ~600 起爬；**无已验证 upside candidate**。  
4. Slot-B 理论空间存在，但**现在没有**过门 candidate；不为 hedge 理论硬塞未验证 bot。  
5. 应优化的是 **截止时 active 的两个 bot 是谁**，不是小时级 public Elo 数字。

**一句话:** 2659 是 live production anchor；**没有**可证据化的止跌包 → HOLD 到死；只对「真正新 external evidence」Reopen。
