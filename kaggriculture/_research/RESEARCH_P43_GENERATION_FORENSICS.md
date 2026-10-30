# P43 — Elite Generation Mechanism Forensics

**日期：** 2026-09-14  
**类型：** 考古 / 机制还原（非优化）  
**源：** rayk Zero-to-Top-Meta、boatlee/salem V16-RC5、跨 elite landmark 对照

---

## Decision

```text
GENERATION = PUBLIC_REPLAY_DISTILLATION
           + STABLE_TAPE_EXTRACTION
           + BOUNDED_MARKET_OVERLAY
           + H2H / BRADLEY-TERRY GATES
NOT_GENETIC_MUTATION_OF_ACTIONS
NOT_IN_POLICY_RL
```

---

## 1. 十二问对照（考古答案）

| # | 问题 | 证据 |
|---|---|---|
| 1 | 初始策略从哪来？ | **公开 leader 的 live episodes**（按 publicScore 匹配 active submission） |
| 2 | 一次 rollout 怎么评？ | 本地 `kaggle-environments` 双 seat 对局 |
| 3 | fitness 是什么？ | **W-D-L / Bradley-Terry**；明确不用 coin surplus |
| 4 | 有 population 吗？ | **有**：自家 c14…C94 谱系 + **重建的公开 live 策略** |
| 5 | 怎么 mutation？ | **结构化 graft / overlay**（整段 market tape、wheat 开局、fert 分裂…） |
| 6 | mutation 粒度？ | **market 轨迹段 / 开局数量 / 1 回合时点**；**不是** 随机改单 action |
| 7 | 改 action / phase / 整段？ | **整段 market schedule** + 有界时点；**field route 基本冻结** |
| 8 | 用 opponent 吗？ | 设计期：对 **重建的公开对手** 做门禁；P42：局内 **无** opponent-identity 自适应 |
| 9 | self-play 吗？ | 主要是 **vs 重建 field / 历史对手**，不是纯 self-play |
| 10 | replay/distillation？ | **核心路径**。V16：3 局 majority vote；rayk：跨对手稳定 tape 蒸馏 |
| 11 | 淘汰机制？ | 4-game / 100-game / 900-game gate；loss-to-family = veto |
| 12 | 搜了多少次？ | rayk 最终一轮：**3,214 local games**；C71 筛 **26** 种 field×market；C94 holdout **900** games |
| 13 | 最终 tape 怎么 export？ | **zlib + base85/base64 压缩的完整 720-step action 表** |

---

## 2. 两个已文档化的 generation loop

### A. rayk（C14 → C95，public ~2836）

```text
download_top_replays（必须匹配 displayed publicScore 的 submission）
        ↓
找跨对手重复的 field schedule（禁止抄单局 winner）
        ↓
蒸馏成确定性 tape / tape router
        ↓
有界 market overlay（premium 抢跑、feed 保护、fert 分裂、impact 排序）
        ↓
双 seat H2H gate + 多 seed + 无关 family veto
        ↓
Bradley-Terry 锦标赛（18 agents × 6 = 918 games；全程 3,214）
        ↓
export 压缩 tape
```

关键失败记录（否定错误 mutation）：

| 尝试 | 结果 |
|---|---|
| Copy a full rival market tape | **Large generalization failure** |
| Buy 6 wheat first | 0-4 回归 |
| Buy 14/19 wheat + resell | 对 Kaito 路线脆 |
| Clone-confidence gate | 抑制有效动作 |
| 持续加大 margin vs 已赢对手 | **不能**推 Elo（C70 83-5 仍卡 sub-3000） |

### B. V16-RC5（boatlee / salem 2900+ 文）

```text
Nikita Lugovoy submission 55440039
  episodes 92165990 / 92185587 / 92223213
        ↓
3 局 majority vote：farmer + hands + market
  field 完全一致；market 决策步 99.91% 一致
        ↓
+ weed repair（挡 PLANT/BUILD 时）
+ 1 回合 premium market lead（MELON/MILK/STRAW/WOOL）
  只挪时点，总意图量不变
        ↓
60/60 双 seat（30 seeds）本地门禁
        ↓
export 压缩 action table
```

---

## 3. 共同结构：「场固定，市移动」

公开 top 收敛 farm：

```text
8 COW / 5–6 SHEEP（V16 为 8C/4S）
12 hands
3 quadrants
STRAW + WHEAT + MELON 混作
```

差异几乎全在 **market turns**（时点、抢跑、排序、feed/fert 保护）。

P42 已证：R2 **局内**不按 opponent 改 sell；  
P43 表明：差异是在 **设计期** 通过 tape 对比与有界 overlay 加上的。

---

## 4. 跨 elite 不可变骨架（seed1, vs finn）

| elite | MELON | MILK | WOOL | FERT | STRAW | land |
|---|---:|---:|---:|---:|---:|---|
| R2 | 249 | 196 | 149 | 30 | 381 | 6,11,18 |
| qeinstein | 249 | 195 | 150 | 28 | 381 | 6,11 |
| rayk_rank | 249 | 196 | 149 | 30 | 382 | 6,11 |
| kaito_v27 | 252 | 216 | 160 | 48 | 336 | 6,10 |
| rayk_c95 | 252 | 216 | 145 | 48 | 336 | 6,10 |

→ **两个 sell-cadence family**（249/196 族 vs 252/216 族），不是 5 条无关 tape。  
→ land 几乎总在 **d6 + d10/11**。  
→ cash：d10 仍低（~3–5k），d12 因 melon 转换跳升。

这更像 **小约束系统**（phase landmarks + cadence family），  
但 P35/P40 已证：**手写该 grammar 不能直接生成 elite**；  
正确用法是：

```text
constraints  →  从真实 tape 蒸馏  →  elite
```

而不是 constraints → 直接 elite。

---

## 5. 对 P25/P27/P40 失败的统一解释

| 实验 | 失败原因（用本机制重述） |
|---|---|
| P25/P27 局部 mutation | 真实搜索不改随机 step，改 **整段 market 时序** |
| P40 从零 coupled grammar | 未进入 **meta farm 几何 + 已验证 cadence** |
| P38 market grammar + p11 | worker/market 未来自 **同一蒸馏 tape** |
| P42 局内 sell repair | elite **局内不自适应**；repair 在设计期 |

---

## 6. 仍未解决 / 下一步边界

**已恢复：** 生成 loop 的算法形状（distill + overlay + gate）。  
**未恢复：** 完整超参（每队 episode 数、候选爆炸比、私有 holdout）。  
**未做：** 按此机制 **复现搜索**（P44，需另开且设止损）。

若做 P44，最小复现应是：

```text
1. 拉取 top submission 的 public episodes
2. majority / 稳定性蒸馏 field tape
3. 只加有界 market overlay
4. 双 seat + 多 seed + ≥2 无关重建 family 门禁
5. fitness = W-L/BT，不用 bank-only
6. 预算与 P40 同级硬停
```

**不要**自创 GA/RL；**不要**动 R2 last-2；**不要** submit。

---

## Artifacts

```text
RESEARCH_P43_GENERATION_FORENSICS.md
p43_landmark_skeleton.csv
_external/p41_candidates/kaggriculture-findings-from-zero-to-top-meta.ipynb
_external/p41_candidates/v16-rc5-*.ipynb
_external/p41_extracted/salem_2900_main.py
_external/p41_extracted/rayk_c95_main.py
```
