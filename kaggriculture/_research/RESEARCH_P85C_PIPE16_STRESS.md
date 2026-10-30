# P85c — Pipe-16 加压门禁（关键否决信号）

日期：2026-09-20  
脚本/结果：`_research/p85c_pipe16_stress.json`  
生产：Metav4 CLI ~**2780**（公榜仍在爬）

## vs 生产 Metav4（好消息）

| 批次 | 局数 | 胜率 | mean |
|---|---:|---:|---:|
| seeds1–6 | 12/12 | 100% | +50 |
| seeds7–12 | 10/12 | 83% | +50 |
| **seeds13–30** | **35/36** | **97.2%** | **+50** |
| **合计约** | **~57/60** | **~95%** | **+50** |

机制：HybridOpening 在 Metav4 上多赚约 **$50/局**，几乎每局固定 +50。  
vs thomas / alperen / R2 / prvsiyan / yhay / evg：**全部 8/8**。

## vs shop_router_v7（坏消息 — 红旗）

| 对手 | seeds | Pipe-16 | Metav4 同种子 | thomas 同种子 |
|---|---|---:|---:|---:|
| **shop_router v7** | 1–8 | **0/16**，mean **-16k** | **8/8** mean +3~5k | **8/8** |

HybridOpening **打父本 Metav4 小胜，却输给 Metav4/父系都能稳赢的 shop-router 族**，且分差巨大。

## 解读

| 现象 | 含义 |
|---|---|
| 对 Metav4 +50/局 稳定胜 | 开局空闲工人改造在**镜像/同族**对局有效 |
| 对 shop_router **0/16 惨败** | 开局改动可能破坏与 shop 路由的对齐；**异构池会重罚** |
| 作者 50-0 vs Metav4 | 只证明打父本，**不证明梯子上总胜率更高** |
| farm_v4 教训对照 | 本地「打赢某个对象」≠ 榜上更强；这里更危险：**输给生产包能赢的对手** |

**榜上若遇到较多 shop-router / V 系公开血统，Pipe-16 公开 Elo 可能低于 Metav4，甚至冲不上去。**

## 决策建议

```text
PIPE16_STRESS_FAIL_ON_SHOP_ROUTER
→ 默认：不提交，守 Metav4 last-2
→ 仅当用户明确知情仍要赌「池内镜像多、shop 族少」时才考虑交
```

**我的建议：不交。** Metav4 2780 仍在爬，Pipe-16 对异构公开族有系统性漏洞，交了可能把 last-2 变成「对 Metav4 小赢、对别人大输」的包。

## 产物

- `p85b_pipe16_gate.json`（vs Metav4/thomas/alperen）
- `p85c_pipe16_stress.json`（含 shop_router 惨败）
- `_push_pipe16/`（已打包，**未提交**）
