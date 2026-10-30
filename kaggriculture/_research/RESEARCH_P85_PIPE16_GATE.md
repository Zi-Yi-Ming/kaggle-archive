# P85 — 发现 Pipe-16（本地门禁通过，待授权）

日期：2026-09-20  
来源：`nathanjacob/kaggriculture-pipe16-idle-workers`（今日公开）  
包：`_external/scan_p85_new_0920/extracted/pipe16_main.py`  
SHA256：`827ddf2997fa442e…`（与 notebook EXPECTED 一致）  
结果：`_research/p85b_pipe16_gate.json`

## 机制（notebook 自述）

- 底座：**Tschinkel Metav4 v13** + **HybridOpening**（day0–2 空闲工人临时种小麦）  
- 作者 gauntlet：**vs Metav4 50–0**，+~$118/局  
- 与我们本地同向：对 Metav4 **稳定小胜**（多为 **+50**/局量级）

## 本地门禁 vs 生产 Metav4（CLI 曾 2792）

| 对手 | 局数 | 胜率 | mean margin |
|---|---:|---:|---:|
| **Metav4 seeds1–6** | **12/12** | **100%** | **+50** |
| **Metav4 seeds7–12 holdout** | **10/12** | **83%** | +50（2 败为 path/seat 级） |
| **vs Metav4 合计** | **22/24** | **~92%** | **~+50** |
| thomas 2945 | 8/8 | 100% | +2359 |
| alperen | 8/8 | 100% | +5281 |
| 自对战 Validation | DONE/DONE | — | — |

**门禁判定：`PIPE16_LOCAL_GATE_PASS`**  
- 对手是 **当前生产 Metav4**，不是只赢 thomas  
- 优势不大（+50/局）但 **胜率高、可复现**  
- 与作者 50-0 叙述一致  

## last-2 算术（若授权交 1 次）

当前：Metav4 **2792.7** + thomas 2560 / goodpjw ERROR  

```text
提交 Pipe-16 后（若 Error 不占有效槽）:
last-2 = [Pipe-16 新号, Metav4@2792]
队分 = max(爬分, 2792)  → Metav4 是地板
thomas 掉出 last-2（已被 Metav4 超越）
```

| 风险 | 说明 |
|---|---|
| 新 path 从 ~600 爬 | 公开分短期可能仍显示 Metav4（best bot） |
| 本地 +50 ≠ 榜上必超 2792 | 但 WR 92% + 作者对 Metav4 全胜，证据强于 farm_v4 |
| ERROR 占坑 | 提交前确认 Successful 里 Metav4 仍在 |
| 交第二次 | 可能挤掉 Metav4 — **只交 1 次** |

## Decision

```text
PIPE16_GATE_PASS
AWAITING_USER_SUBMIT_AUTH
Metav4 production still FROZEN as backup
```
