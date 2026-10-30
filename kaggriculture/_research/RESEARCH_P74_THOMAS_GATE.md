# P74 — 公开扫描 + thomas_2945 本地门禁（冒烟/扩展）

**日期:** 2026-09-19  
**提交:** **无**（仅本地评测）  
**候选:** `thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots`  
提取: `_external/scan_20260919/extracted/thomas_2945_clean.py`  
（与 sunil top-10 提取 **字节相同**）

---

## 候选自述

- 文案称 ladder agent 全开源，LB **2944.7**  
- 结构: 公开 V39 / shop-router 血统 + **RACE / RACEPX / COURIER / HERD / CARROT** 层  
- 相对 `_push_alperen/main.py`：RACE/HERD/COURIER 在 alperen 中 **计数为 0**；标识符 Jaccard ≈ **0.21**（清洗后）  
- 作者署名 thomastschinkel；Apache-2.0 notices 与 alperen 同源社区谱系

---

## 本地门禁结果（finn 不 wrap，`env.info["seed"]` 钉种子，每局 fresh load）

| 对手 | 局数 | 胜 | mean margin | seat0 胜 | seat1 胜 | status |
|---|---:|---:|---:|---:|---:|---|
| **alperen** | 8 (seed1–4 × 双 seat) | **8/8** | **+5,271** | 4/4 | 4/4 | 全 DONE |
| **R2** (`_push_medal`) | 8 | **8/8** | **+8,351** | 4/4 | 4/4 | 全 DONE |
| **tetsu R3** (`_push_tetsu_r3`) | 8 | **8/8** | **+33,570** | 4/4 | 4/4 | 全 DONE |

样本 bank（vs alperen）: seed1 150597 vs 148286；seed2 79681 vs 70076；seed3 77444 vs 71206；seed4 74815 vs 71885。  
vs tetsu margin 更大（2.8万–3.9万）——tetsu 本地明显弱于 alperen/R2。

**观察:** 双 seat 胜率对称、无撕裂；margin 为正但 **不是** alperen 对弱 elite 那种 20k+ 碾压。  
同 seed 双 seat 出现相同 bank 对（仅座位对调）——本地 pin seed 下引擎对称，**不能**当作额外独立样本；有效独立信息约等于 4 seed × 对手。

---

## 与 farm_v4 教训对照（关键）

```text
farm_v4:  local 8-0 vs alperen+R2 → LB 仅 1854 / 1982
thomas:   local 8/8 vs alperen + 8/8 vs R2 → LB 未知（作者称 2944.7）
```

**本地 dominance ≠ 榜上 medal。** 历史已烧过一次。  
thomas 与 farm_v4 的差异点（尚未被 LB 证实）：

1. 作者公开宣称 **自己提交过 2944.7**（farm_v4 是我们本地新造）  
2. 含 alperen 没有的 RACE/HERD/COURIER 机制层  
3. notebook 体量更大（~856KB clean vs alperen 289KB）

---

## 门禁清单

| 条件 | 状态 |
|---|---|
| 可执行 `agent()` | 通过（syntax_ok after strip magic） |
| vs alperen ≥5/8 双 seat | **通过 8/8** |
| vs ≥2 elite ≥5/8 | **alperen + R2 + tetsu 均 8/8** |
| 无 seat 撕裂 | 通过 |
| 指纹非已知薄弱 overlay | **部分**：同属 shop-router/V 大谱系，但含独有层；非 goodpjw 那种 0.96 薄皮 |
| 本地 mean bank ≥150k | 部分 seed 达到，非稳定 180k |
| 用户授权提交 | **未授权 — 不交** |

---

## Decision

```text
P74_LOCAL_GATE_PASS_PENDING_USER_AUTH
NOT_A_BLIND_SUBMIT
```

- 公开扫描里 **唯一值得谈提交** 的是 thomas/sunil 同源 2945 包  
- goodpjw / ahmed V50 / guru gametheory → 已知族高相似，**NO**  
- alperen5252525 等无 `agent()` → **不可提交**  
- 若授权提交：last-2 将变为 V16 + thomas（twin 掉出）—— **twin 爬分会被打断**，需用户知情

---

## Artifacts

```text
_external/scan_20260919/
_research/p74_thomas_vs_alperen_smoke.json
_research/p74_thomas_gate_expanded.json
_scripts/_p74_prescreen_scan.py
_scripts/_p74_extract_agents.py
_scripts/_p74_gate_thomas_smoke.py
_scripts/_p74_gate_expanded.py
```
