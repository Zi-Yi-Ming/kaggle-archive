# Kaggriculture Research Report — R1

**Date:** 2026-09-11  
**Status:** VERIFIED local findings  
**Baseline:** v11E frozen (`cleo_v11_E_backup.py`, loaded via `_pm_pool.load_agent("v11E")`)  
**Env:** conda `kaggle` / kaggle-environments 1.32.7  
**Scripts:** `_diag_16game_truth.py`, `_diag_mechanism.py`  
**Artifacts:** `_diag_16game_truth.json`, `_diag_mechanism.json`

---

## 1. Executive answer

**当前最值得解决的核心问题不是“找一个 Kaggle 分数更高的 notebook”，而是：**

> **v11E 的绝对经济产出系统性低于一批公开 Tier-B shop-router / livestock 策略；本地 16-0 是真实对局结果，不是 benchmark artifact。**

证明路径：

1. 先排除 harness / module-cache / state-bleed  
2. 用 closer_cleo 与 self-play 做 control，确认 v11E 本身可运行  
3. 用 fresh-load 复现 16-0  
4. 用 no-op 绝对分与 mid-game structure 定位机制  

---

## 2. What we believed

进入本轮时的合理怀疑（全部成立为“应质疑”而非“已证伪”）：

| Prior belief | Why it was plausible |
|---|---|
| 4×16-0 可能是 harness bug | 仓库刚修过 wrapper module-cache collision（`_audit_8game_integrity.md`） |
| 可能是 state bleed | v11E 有 `_OPP` / `_LAST_STEP` 全局状态；screening 复用 agent 连打 16 局 |
| 可能是 public-score 造假后的弱公开版被高估 | 4 个 candidate 公开 best score 2483–2879，都 ≤ v11E ~2900 |
| 可能只是 matchup accident | ronin5205 正确加载后仅 40.8% WR、margin ≈ 0 |

---

## 3. What we tested

### Experiment A — Truth controls (`_diag_16game_truth.py`)

| Control | Design | Purpose |
|---|---|---|
| C1 | closer_cleo vs v11E, 8 games, fresh load | 已知 v11E 弱点；校准 harness |
| C2 | v11E self-play, 4 games, fresh | 校准 v11E 可运行 |
| C3 | tetsu vs v11E, 8 games, **fresh every game** | 排除 state bleed |
| C4 | tetsu vs v11E, 8 games, **reuse agents** | 与 screening 同策略对照 |
| C5 | prvsiyan vs v11E, 4 games, fresh | 第二 candidate 抽查 |
| C6/C7 | day-boundary bank trajectory | 领先何时出现 |

### Experiment B — Mechanism (`_diag_mechanism.py`)

| Test | Design | Purpose |
|---|---|---|
| Q1 Absolute | each agent vs `fallow_finn` (no-op), 3 seeds | 绝对经济，不依赖对手 |
| Q2 Structure | day 10/15/20/25/29 动物/作物/现金/土地 | mid-game 差异是什么 |
| Q3 Cross-play | tetsu/prv/flex/salem/cleo/ronin 关键 pair | 公共优势 vs RPS vs 专杀 v11E |

---

## 4. What happened

### 4.1 Harness is healthy (VERIFIED)

| Control | Result |
|---|---|
| C1 closer_cleo | 7–1 vs v11E, mean margin **+861** — 与 PM_REPORT 同量级 |
| C2 self-play | margins 0–268，几乎镜像 |
| C3 tetsu FRESH | **8–0**, mean margin **+22,175** |
| C4 tetsu REUSE | **8–0**, mean margin **+22,876** |
| C5 prv FRESH | **4–0**, mean margin **~+47k** |

**结论：16-0 在 fresh 与 reuse 下都成立。不是 module-cache，不是 state-bleed。**

### 4.2 Lead emerges mid-game, not at open (VERIFIED)

tetsu vs v11E seed1 trajectory:

| Day | tetsu | v11E | diff |
|---:|---:|---:|---:|
| 1–8 | 落后或持平 | — | ≤0 |
| 10 | 2,086 | 1,923 | +163 |
| 15 | 21,528 | 16,949 | +4,579 |
| 20 | 45,478 | 35,461 | +10,017 |
| 25 | 82,198 | 62,146 | +20,052 |
| 29 | 91,559 | 66,310 | +25,249 |

这是 **day 10–25 的复利拉开**，不是开局崩溃、不是 seat bias、不是 terminal 读分错误。

### 4.3 Absolute economy ranking vs no-op (VERIFIED)

| Agent | mean bank vs fallow_finn |
|---|---:|
| salemali7 | 167,091 |
| prvsiyan | 164,472 |
| ronin5205 | 154,127 |
| flexonafft | 153,931 |
| tetsu2131 | 150,175 |
| closer_cleo | 144,652 |
| **v11E** | **109,312** |

**v11E 对无操作对手的绝对产出最低**，比 top candidates 低约 **35–50%**。

这解释了为什么 ronin5205 与 v11E 接近（双方绝对分都在 15 万级，竞争后 margin≈0），而 top5 notebook 仍能 16-0（绝对经济再高一档，竞争后仍能拉开 2 万+）。

### 4.4 Structure: livestock / YARN_STORE vs crop-heavy v11E (VERIFIED)

tetsu vs v11E：结构接近，但 tetsu 更早清 MELON、保留更多 WHEAT/STRAWBERRY 产能，终局 liquidate 更干净。

prvsiyan vs v11E 差异更大：

| Day | prv animals | v11E animals | prv money | v11E money |
|---:|---|---|---:|---:|
| 15 | 17 (SHEEP 11) | 14 (COW 8 SHEEP 6) | 23,481 | 15,970 |
| 20 | 17 | 14 | 60,472 | 30,373 |
| 25 | 17 | 14 | 89,180 | 50,500 |
| 29 | liquidating | still 37 plants | 105,913 | 52,751 |

prvsiyan 重仓 **SHEEP → WOOL → YARN_STORE**，现金复利更快；v11E 更偏 STRAWBERRY/MELON，中后期产能转化更慢。

### 4.5 Cross-play is a partial order, not a single v11E-killer (VERIFIED, n=4/pair)

| Pair | Result | Mean margin |
|---|---|---:|
| prvsiyan vs tetsu | prv 4–0 | prv +39k |
| tetsu vs ronin5205 | tetsu 4–0 | tetsu +24k |
| tetsu vs closer_cleo | tetsu 4–0 | tetsu +16k |
| prvsiyan vs closer_cleo | prv 4–0 | prv +56k |
| flex vs salem | flex 4–0 | flex +17k |
| flex vs closer_cleo | flex 4–0 | flex +45k |
| salem vs closer_cleo | salem 4–0 | salem +23k |

初步强度序：

```text
prvsiyan  >  tetsu2131  >  ronin5205 ≈ closer_cleo ≈ v11E
flexonafft > salemali7  >  closer_cleo
```

**不是“专门打 v11E 的 matchup bug”**：同一套 agent 也碾压 closer_cleo 与彼此中的弱者。  
**也不是完整 RPS**：目前看到的是偏序优势，不是循环。

### 4.6 Provenance correction (RECONSTRUCTED)

`prvsiyan_main.py` 自述：

- 主策略与 13 条 action tape 来自 **yhay81 / Shop Router 0909**
- sell timing / shed projection 来自 **aurax7 / Reactive Router**
- prvsiyan 本人是 “lossless single-file packaging only”

因此公开强策略的真正上游是 **yhay81 shop-router + aurax7 reactive router**，不是 prvsiyan 原创。  
adaptivity tier 仍是 **Tier B**（shop-pair 路由 + 观测 repair），不是 RL。

---

## 5. What changed in our beliefs

| Old belief | New belief | Evidence grade |
|---|---|---|
| 16-0 可能是 artifact | **16-0 是真实本地 H2H** | VERIFIED |
| state bleed / module cache 是主因 | **已排除** | VERIFIED |
| public score 低 ⇒ 不能打 v11E | **Kaggle Elo 与本地绝对经济脱节** | VERIFIED |
| v11E ~2900 ⇒ 本地最强 | **v11E 绝对经济在测试集中垫底** | VERIFIED |
| 突破口是 PPO/meta-agent | **公开 shop-router / livestock 路线已足够超过 v11E** | VERIFIED (local) |
| closer_cleo 击败 v11E 说明市场 slot 脆弱是主因 | **closer_cleo 只是 H2H 小胜；真正大优势来自绝对经济** | VERIFIED |

---

## 6. What is actually proven

1. **VERIFIED** — local harness + v11E load 正确（closer_cleo 7–1、self-play 镜像）。  
2. **VERIFIED** — tetsu/prvsiyan 对 v11E 在 fresh-load 下稳定大胜。  
3. **VERIFIED** — 优势在 day 10–25 复利形成。  
4. **VERIFIED** — v11E 对 no-op 的绝对分显著低于 top candidates。  
5. **VERIFIED** — prvsiyan/tetsu/flex/salem 也碾压 closer_cleo，不是只打 v11E。  
6. **VERIFIED** — prvsiyan 当前是测试集中最强（压 tetsu 4–0）。  
7. **RECONSTRUCTED** — prvsiyan ≈ yhay81 Shop Router + aurax7 sell timing。  
8. **UNKNOWN** — 这些 agent 在 Kaggle 真实匹配池中的 Elo 是否仍高于生产 v11E。  
9. **UNKNOWN** — 本地 `cleo_v11_E_backup.py` 与线上 2900 提交是否 byte-identical。  
10. **CLAIMED** — top leaderboard 使用 PPO/meta-agent（dzjiann 等，无代码）。

---

## 7. What remains uncertain

1. **本地 v11E vs 线上 2900**  
   本地它是最弱绝对经济；线上 2900 可能来自：更早 meta、不同匹配池、或我们未复原的提交版本。

2. **为什么 Kaggle best score 没体现这个鸿沟**  
   可能：公开 notebook 不是最终提交；Elo 人口相对；匹配对手不同；本地引擎配置有差。

3. **是否需要 PPO/meta-agent**  
   当前证据说明：先拿到 shop-router 级绝对经济，再谈 meta。PPO 是 top-private 的路径，不是超过 v11E 的必要条件。

4. **YARN_STORE/SHEEP 是否是唯一机制**  
   tetsu 不是重 SHEEP 也能 16-0，说明还有 crop-mix / liquidation / repair 贡献。需要 ablation。

5. **这些公开 agent 是否已在对手池中**  
   若 Kaggle 池里已有大量 shop-router，提交同策略可能没有 2 万 margin 那么好看。

---

## 8. Mechanism hypothesis (HYPOTHESIS, high confidence)

```text
v11E tape
  → 作物向（STRAWBERRY/MELON）
  → 中后期库存转化慢
  → 绝对产出 ~109k vs no-op

shop-router / livestock
  → 早期锁定 YARN_STORE / SHEEP 或等价高周转
  → day 10–25 现金复利
  → 绝对产出 ~150–167k vs no-op
  → 对 v11E 仍有 20k+ 竞争后 margin
```

closer_cleo 路径不同：它靠 sell-slot 破坏 v11E 市场控制器，绝对分并不突出，所以 H2H 只小胜。

---

## 9. Best next experiment

**优先级 1 — 把“绝对经济”做成可部署策略，而不是继续搜 notebook。**

设计一个最小可测 research agent `shop_router_lite`（不改 v11E）：

1. 开局观测前两家店  
2. 若含 `YARN_STORE` → SHEEP/WOOL 路线，否则回退到 best crop route  
3. 保留 prvsiyan 的 weed-repair + terminal liquidate  
4. 与 v11E / closer_cleo / ronin / tetsu / prv 各 8–16 局  

成功标准：

- vs v11E mean margin > +5k 且 WR > 70%  
- vs fallow_finn mean bank > 140k  
- 与 prvsiyan 不至于 0–8 崩盘  

**优先级 2 — provenance 扩展**

下载/执行 yhay81 Shop Router 0909 与 aurax7 Reactive Router 原版，确认 prvsiyan 是否只是包装、是否有更强后继。

**优先级 3 — ablation**

在 prvsiyan 上关掉：SHEEP 重仓 / YARN_STORE 优先 / liquidate / sale-advance，量化各自贡献。

**优先级 4 — 不要现在做**

全量 PPO、960 matchup meta-agent。在绝对经济基线超过 v11E 之前，这些是高成本低信息量。

---

## 10. Research stance

- 不修改 v11E。  
- 不把 CLAIMED 写成 VERIFIED。  
- 不把 4 局 cross-play 写成最终排行榜。  
- 16-0 已从 “SCREENING_ADVANCE” 升级为 **本地 VERIFIED 对 v11E 优势**；Kaggle Elo 外推仍是 UNKNOWN。

---

## 11. One-line takeaway

> **v11E 不是被神秘 RL 打败的；它在本地已经被公开的 shop-router / livestock 绝对经济路线稳定击败。下一步应复制该机制并做受控 ablation，而不是先上 PPO。**
