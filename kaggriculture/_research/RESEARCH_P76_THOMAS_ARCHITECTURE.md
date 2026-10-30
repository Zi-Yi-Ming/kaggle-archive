# P76 — thomas_2945 架构拆解（冲牌周·防回落）

**日期:** 2026-09-19  
**源码:** `_external/scan_20260919/extracted/thomas_2945_clean.py`  
生产包: `_push_thomas_2945/main.py`（ref **56358711**）  
**提交:** 无（只读拆解 + 本地消融）  
**动机:** 用户判断 public Elo 可能见顶回落，终榜 Bradley-Terry 在截止后约两周，私榜有掉分风险 → 需要 **知道分从哪来、哪层脆弱**。

---

## 0. 一句话

```text
公开强 tape 底座（V39 / yhay81 shop-router 谱系）
    + 数十层 agent = 包装(agent) 反应式补丁
    + 针对引擎时序 / 市场先到先得 / 物种 ROI 的 v9 层
≠ 从零 RL，也 ≠ 薄皮旋钮 clone
```

本地门禁: vs alperen / R2 / tetsu **各 8/8**。  
榜上: 600 → … → **~2595**（CLI），用户 UI 报 **铜牌**。

---

## 1. 包结构（执行顺序）

文件约 **5760 行 / 862KB / 161 个 def**，大量：

```python
def agent(...):          # 每层重定义
    ...
    return _PARENT(...)
agent.telemetry = REPORT
agent = globals().pop("agent")   # 摘掉名字，下一层再包
```

**后定义的 agent 在最外层**（最后执行、最先看到 obs / 最后改 action）。  
因此调用链是：

```text
最终 agent（最外层，文件末尾）
  → … 中间无数 repair / market / shop 层 …
    → v9 RACE / RACEPX / RACEGATE
      → v9 HERD
        → v9 COURIER
          → … 底座 tape worker + shop router …
```

注意：文件里 **嵌套 `exec('"""E182 …"""')`** 等字面量源，以及 **monkey-patch**（如 `Chassis._sell_lead = _v9_racepx_lead`），不是纯函数管道。

---

## 2. 底座（不是 thomas 独有）

与 alperen / yhay81 / prvsiyan 同源的公开谱系：

| 能力 | 含义 |
|---|---|
| **720-step action tape** | 预计算 farmer/hands 逐步命令表 |
| **Shop-pair / shop-router** | 按本局解锁商店选择路由与生产计划 |
| **Observation repairs** | 除草、还债、卖货、救货等启发式修补 |
| **Hire / production stack** | 每日雇工 + 浇水/喂养/收获节奏 |

研究结论（P37–P40）仍成立：**从零合成 elite tape 很难**；thomas 的增量在「底座之上」。

---

## 3. v9 关键层（作者注释 + 代码）

### 3.1 COURIER（傍晚快递）

| 项 | 内容 |
|---|---|
| **问题** | ~40% 草莓/牛奶日终仍在工人身上；引擎 **先市场、后自动入仓** → 同行第二天早上才卖 |
| **窗口** | hour ≥ **12**；物品 STRAWBERRY / MILK / WOOL / MELON |
| **条件** | 该工人今日剩余命令全是 PASS/移动（移动免费，黎明重生在 shed） |
| **动作** | 走到 shed 邻接格 `(4,4)(5,4)(4,5)(5,5)` → DROP → **当天市场**卖 |
| **经济点** | hour20–次日黎明之间无 town 抽货；傍晚卖吃的是 **次日早晨的报价**，比等自动入仓早一天 |
| **脆弱点** | 依赖引擎结算顺序；若对手也全员 COURIER，优势变小；tape 工人「今天没活」假设被改坏会失效 |

### 3.2 HERD（第10天换物种）

| 项 | 内容 |
|---|---|
| **问题** | 鹅：2 蛋/日 → $50 书；羊：4 毛/3日 → $200；牛：3 奶/2日 → $160 |
| **时点** | tape 的 day-10 鹅购买时刻，**只改物种，不改工人日程** |
| **羊条件** | BAKERY+BRUNCH_SPOT ≤1 且有 YARN_STORE 且 WOOL≥**150** |
| **牛条件** | 蛋店=0 且披萨/冰淇淋/奶昔店 ≥3 且 MILK≥**150** |
| **多余产出** | tape 没计划卖的部分，进 shed 即卖 |
| **脆弱点** | 强依赖 **本局 shop 抽签 + 报价**；商店抽错或价格不到阈值 → 完全不触发（行为=原鹅 tape） |

### 3.3 RACE / RACEPX / RACEGATE（抢卖窗口）

| 项 | 内容 |
|---|---|
| **问题** | 高价货供给一多价格崩；**先卖拿价，后卖砸盘**（premium books ~60 units glut） |
| **观测** | `rival_sold[p] = inv' - inv + town_draw - own_sold`（公开信息，$1 地板以上可还原） |
| **lead** | 对手在你 tape 计划卖出前抛货 → 记「领先步数」 |
| **horizon** | `clamp(最大 lead + 12, 40, 48)`；**自 step 192（day 8）起**才启用预留 |
| **RACEPX** | monkey-patch `Chassis._sell_lead`，改卖出优先级/门控 |
| **RACEGATE** | 统计/限制 reservation units |
| **作者 A/B** | 40/12 镜像强于 6/4 与 32/12；**更深（44/48）有的局赢、对不抢跑对手会亏** → 不是越深越好 |
| **脆弱点** | 依赖「对手也在用 tape 计划卖」的形态；对 **不规律/不卖** 对手，深预留会放弃 town 回血；镜像局（同策略）上 RACE 是主战场 |

### 3.4 其它后段层（文件后半）

消融脚本之外仍存在（影响终 agent）：

- 多层 R68/R97/R36 等 shop/supply/sale-reservation 修补  
- **CS / HD2**：更晚的动物物种改写（牛→其它）与 credit/sell 记账  
- 终端窗口 planner（E182，step 712–718 物理收尾）  
- 大量 `try/except` + telemetry，**层间失败会静默退回父层**

---

## 4. 与 alperen 的差异（为何本地 8/8）

| 维度 | alperen（MetaCounter 族） | thomas 2945 |
|---|---|---|
| 底座 | shop-router / V 系，含自身 meta 逻辑 | 公开 V39 tape + 更深修补栈 |
| RACE/COURIER/HERD | **无**（代码计数 0） | **有完整 v9 层** |
| 标识符重叠 | — | Jaccard≈0.21（清洗后） |
| 文件大小 | ~289KB | ~862KB |
| 本地 vs 彼此 | 输给 thomas 8/8 | 赢 alperen mean +5k 级 |
| 榜上 | 原条目 2262，已不在 last-2 | last-2 生产分 ~2595 |

差异不在「谁的 tape 更长」，而在 **卖出时序竞争 + 日终物流 + 物种 ROI** 三处引擎真约束。

---

## 5. 私榜回落风险（用户判断 → 工程含义）

官方 Evaluation：

1. 每日可交 5 个，**只计最新 2**  
2. 提交后先跑 **自对战 Validation**，失败 = ERROR  
3. 截止后锁定提交，**再打约两周**，用这些 episode 做 **Bradley-Terry** 出终榜  

因此 public Elo **可能**回落的原因：

| 机制 | 影响 |
|---|---|
| **匹配噪声 / 早期 path** | 26 局时已 2595；样本仍少于「~60 局 90% 收敛」经验值 |
| **对手池变化** | 新强 bot 入场、弱 bot 挤出 → 同胜率 Elo 可能变 |
| **镜像与内战** | 若池内大量同族 tape，RACE 层在镜像上贡献大，但对「异构私有策略」优势可能缩小 |
| **BT 终榜** | 不用 public 瞬时分，用截止后对局重估；**方差大时可上可下** |
| **私榜 ≠ 现金名次** | 奖金只看最终 Top10；铜/银/金以 UI 规则为准 |

**工程应对（在不改 last-2 生产代码的前提下）：**

1. **冻结** `_push_thomas_2945/main.py` — 不改、不重交  
2. 保持 last-2 = thomas + twin，**避免截止前 churn**  
3. 用本报告 + 消融知道：若终榜掉分，更可能是 **匹配/BT 方差或对手族变化**，不是「代码被偷走」  
4. 赛后归档：层消融表写入 CSDN/复盘（符合你的写作偏好：过程与机制，不只报分）  
5. 若赛中必须再交：只允许 **门禁完整的新 family**，且明知会挤掉 twin（不是 thomas，除非新包更强）

---

## 6. 方法论可复刻清单（迁移到下一场比赛）

1. **底座优先**：先拿公开/已验证强策略，再叠薄层  
2. **每层一个引擎事实**：结算顺序、价格崩盘、物种现金流——禁止无假设旋钮  
3. **telemetry 必做**：`courier_trips` / `herd_rewrites` / `leads`  
4. **A/B 钉种子 + 镜像 panel**；记录「更深为何更差」  
5. **Kaggle Validation 当一等公民**：本地 harness 过了 ≠ 榜上能跑（goodpjw ERROR）  
6. **Elite tape 原子性** 与 **有意义的层补丁** 可以同时为真  

---

## 7. 消融实验（seed1–3 × 双 seat，finn 不 wrap）

| 变体 | vs thomas_full | vs alperen |
|---|---|---|
| **full** | — | **6/6** mean margin **+6051** |
| no_courier | 0/6 mean **-544** | 6/6 mean +5780 |
| no_herd | 0/6 mean **0**（未触发） | 6/6 mean +6051（与 full 同 bank） |
| no_race* | 4/6 mean **-38**（噪声级） | 6/6 mean +5835 |
| no_v9_all | 0/6 mean **-965** | 6/6 mean **+5574** |

**解读:**

1. **打 alperen 的主优势不在 v9**：关掉全部 v9 仍 6/6，margin 只少 ~480。  
2. **COURIER** 在本 seed 上有稳定小贡献（~0.5k bank）。  
3. **HERD** 在 seed1–3 **完全没开**（鹅店/价格条件不满足）；梯子上 shop 抽签不同可能偶发触发。  
4. **RACE** 在「打 alperen」panel 上几乎不贡献；作者注释强调它主要在 **镜像/抢卖** 对局有效——这与私榜回落担忧相关：**若终榜池里同族 tape 变多，RACE 可能变重要；若对手是异构私有策略，底座+生产节奏更关键**。  
5. **回落风险工程结论:** public Elo 继续涨时仍可能是 path/对手池方差；BT 终榜可上可下。**正确动作是冻结 last-2，不是改 thomas。**

产物: `_research/p76_ablation_results.json`、`p76_ablation_agents/thomas_*.py`

---

## 8. Artifacts

```text
_research/RESEARCH_P76_THOMAS_ARCHITECTURE.md   ← 本文件
_research/p76_thomas_layer_inventory.txt
_research/p76_ablation_results.json
_scripts/_p76_layer_inventory.py
_scripts/_p76_ablate_thomas.py
_external/scan_20260919/extracted/thomas_2945_clean.py
_push_thomas_2945/main.py
```
