# P88 — 2026-09-27 猛攻扫描：新公开包双门（无提交）

日期：2026-09-27  
脚本：`_scripts/_p88*.py`  
结果：`_research/p88c_clean_gates.json`  
CLI：Metav4 **56390446 = 2695.5**（仍在 last-2）；thomas 2423.0  

## 门禁（硬）

vs **Metav4** ≥60% **且** vs **shop_router v7** ≥50%；holdout + 自对战 + 用户授权才谈提交。

## 新公开扫描（kaggle dateCreated）

| 包 | 自称 | 本地 vs Metav4 | vs shop_v7 | 双门 |
|---|---|---:|---:|---|
| **haideptry/the-2965-master-hybrid-engine** | 2965 | **100% +50** | **0% −16627** | **FAIL — = Pipe-16 克隆** |
| **haideptry/the-2950-peak-farm** | 2950 | 100% +50 | 0% −16627 | FAIL — 同克隆 |
| **dmitrii/one-more-wheat** | Pipe16+1天麦 | **100% +78** | **0% −16797** | FAIL — 病更重 |
| haideptry/countering-big-3 | — | **0% −3105** | 100% +5160 | FAIL — 输 Metav4 |
| haideptry/demystifying-2900 | — | 0% −3105 | 100% +5160 | FAIL — 与上者同包 |
| kenanzhang a1-t31-guard | A1+现金预留 | 0% −7582 | 0% −2556 | FAIL — 全面弱 |
| Ahmed V51/V52 文档 | Lean Flock | 自报 vs thomas13 **28/100** | — | 文档已示弱于 Metav4 |
| **guru master-engine v4** | 新统一引擎 | **100% +50** | **0% −16627** | **FAIL — 也是 Pipe-16 克隆** |
| shiiin9 beat-v48-day6 | V48+两层 | 0% −6202 | 50% −80 | FAIL — 输 Metav4/thomas |
| thomastschinkel 公开 | — | 仍最新 **Metav4 v13** | — | 无更新 |

**关键情报：榜面标题「2965 / 2950」与 guru Master Engine v4 在本地与 Pipe-16 逐 seed bank 完全一致**（149878 / 72902 / 127139）。  
公开分高 ≠ 策略新；是 **同一 HybridOpening 谱系**，异构 shop 仍崩。

**P88 双门总表（可加载候选全灭）**

| 家族 | 代表 | vs Metav4 | vs shop | 结论 |
|---|---|---:|---:|---|
| Pipe-16 谱系 | 2965/2950/guru v4/pipe16 | +50~78 / 100% | **−16k / 0%** | 镜像毒药 |
| shop-safe 弱包 | countering/demystifying | **负** | 赢 | 不能替换 Metav4 |
| 其他 | beat-v48 / a1-t31 / V51 自述 | 负或自报弱 | 中等 | 不过门 |

## 解读

1. 公开冲分叙事集中在 **Metav4 + 开局空闲工人**；本地双门能识破。  
2. **one-more-wheat** 镜像边更大（+78）但 shop 更惨 — 边越大毒越深。  
3. **countering/demystifying** 能打 shop 却打不过 Metav4 — 不能替换生产包。  
4. 作者侧仍无新公开包；私有 56358231 仍无源。  
5. **HOLD Metav4 仍是唯一理性生产决策。**

## 动作

1. **不提交**任何 P88 候选  
2. 继续盯：guru v4 / beat-v48 / prvsiyan lab / crystalbaby / destbreso arena  
3. 缺陷驱动发明仍只认双门  
4. STATUS 与 notes 已同步  

## 产物

- `_external/scan_p88_new/`（拉取的 notebook）  
- `_external/scan_p88_new/extracted_clean/`（可加载 agent）  
- `_research/p88c_clean_gates.json`  
- `_research/RESEARCH_P88_NEW_PUBLIC_HUNT.md`（本文）
