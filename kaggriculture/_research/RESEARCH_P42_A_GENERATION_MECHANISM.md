# P42-A — Generation Mechanism 审计

**日期：** 2026-09-14  
**对象：** rayk「Zero to Top Meta」+ V16/boatlee tape 形态  
**结论类型：** **机制还原**（非算法发明）

---

## Decision

```text
GENERATION = REPLAY_MINING + STABLE_TAPE + MARKET_OVERLAY + H2H_GATES
NOT_GENETIC_NOT_RL_NOT_RANDOM_EVOLUTION
```

---

## 1. Elite 是怎么被「产生」的（rayk 原文路径）

Rayk 在 notebook 开篇写明工作循环：

```text
download current leaders
        ↓
work out which moves repeat
        ↓
turn the repeatable part into a local agent
        ↓
beat it from both seats
```

完整晋升链（Section 9）：

```text
c14  多局重复出现的完整 schedule 才入模
c15  在 schedule 上加 clone-aware premium 抢跑
c16  多 leader 收敛 → 换更强 common-meta field tape
c18  field 固定，只刷 premium market schedule
c27  终局控制器改到 step 717
c45  debt-tracked 两回合 horizon
c68  THUNDER field refresh + 在线 horizon 推断
c70  impact-first 卖出排序
c71  Giovanni market timing 重建
c72  仅当货在 shed 旁且价值≥2000 才提前变现
c92  只修「挡住既定 route 的随机草」
c94  开局 feed 保护 + 肥料一回合抢跑
c95  刷新 top-20 market rhythm
```

**每一步都是：公开对局 tape → 结构蒸馏 → 有界 market overlay → 双 seat 门禁。**

---

## 2. 明确否定的生成方式

| 方式 | 是否使用 |
|---|---|
| 从随机 program 遗传进化 | **否** |
| RL / policy gradient | **否** |
| 手写完整 720 步规则 | **否**（最终打包成 tape） |
| 单局 winner tape 直接抄 | **否**（作者称这是 first mistake） |
| 只追 bank vs starter | **否**（明确说 bank ≠ rating） |

Rayk 原文：

> “A high bank against starter is a smoke test, not a promotion test.”  
> “Kaggle rating rewards wins, not surplus coins.”

---

## 3. 元结构：field 收敛，market 分化

公开 top 队高度收敛：

```text
8-cow / 5–6-sheep
12 hands
three quadrants
~23 strawberry / 31 wheat（成熟期）
```

差异主要在 **market turns**（卖出时点、抢跑、feed 保护），不是再堆动物。

> “The farm stayed fixed, the market moved.”

V16 同构：完整 coupled tape 压缩打包（zlib+b85），sim 对四 elite = 0。

---

## 4. Objective 分裂（本阶段重要实证）

| agent | vs finn mean3 | 本地 vs R2 | 备注 |
|---|---:|---:|---|
| R2 | 183,850 | — | 线上 **2012.7** |
| V16 | 172,660 | **0–0–8** | 新 family |
| rayk C95 | 164,032 | **0–0–8** | 文中 public **2836.8** |

**C95 本地 bank 与 H2H 都输给 R2，但 public Elo 高一个档。**

Rayk 自己写明：C70 已 83-5 对历史对手却卡在 sub-3000——  
**rating 优化的是 close-game 转化，不是 surplus coin。**

含义：

```text
Objective A  bank vs finn     → 筛「有没有 elite 产能」
Objective B  WDL/Elo vs field → 筛「有没有资格替代 R2」
A 强 ≠ B 强（V16/C95 vs R2 已证明）
```

P42-B 若做 search，第一阶段仍可用 bank 找 basin；  
**晋升必须用 field H2H，不能只用 bank。**

---

## 5. 对 P38/P40 失败的统一解释

| 实验 | 结果 | 用本机制解释 |
|---|---|---|
| P38 market grammar + p11 | 21k | 手写旋钮 ≠ 搜索出的 tape |
| P40 从零 coupled 规则 | 44 | 规则空间未覆盖 meta route 几何 |
| P41 V16/C95 | 164–173k | **tape 表示 + 他人 search 产物** |

> **open-loop 是执行表示；generation 是 replay mining + 结构重建 + market 门禁。**

---

## 6. Production

R2 last-2 **冻结**。  
V16 / C95 均 **0/8**，**不 submit**。

C95 高 public Elo 提醒：若目标是冲分，不能只盯「打赢 R2」，还要能打赢 **field 中 close-game 对手**——那是另一套 fitness。

---

## 7. P42-B 建议（尚未开跑）

**不要**自己发明 GA/RL。最小复现应是 rayk 同构：

```text
1. 收集 public leader episode tapes（Kaggle API / 已有 kernel）
2. 蒸馏重复出现的 field schedule（跨对手稳定）
3. 有界 market overlay（时点/抢跑/排序），禁止推翻 field
4. 双 seat + 多 seed + 至少 2 个无关 family 作 veto
5. 打包 tape；用 field H2H 晋升，不用 bank-only
```

成功判据（爬升可见）：

```text
tape 家族在 field 门禁上稳定提升 W-T-L
（不是 bank 44→50 这种噪声）
```

失败判据：

```text
蒸馏 tape + 有界 overlay 仍打不过无关 family
→ 缺的是 tape 源，不是算法
```

---

## Artifacts

```text
RESEARCH_P42_A_GENERATION_MECHANISM.md
_external/p41_extracted/rayk_c92_main.py
_external/p41_extracted/rayk_c94_main.py
_external/p41_extracted/rayk_c95_main.py
_external/p41_extracted/salem_2900_main.py
p41_v16_vs_r2.csv
```
