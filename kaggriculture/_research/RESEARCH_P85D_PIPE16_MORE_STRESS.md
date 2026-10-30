# P85d — Pipe-16 扩大加压（shop_v7 弱点可复现）

日期：2026-09-20  
结果：`_research/p85d_pipe16_more_stress.json`

## 复现：vs shop_router v7

| 对手 | seeds | Pipe-16 | Metav4 对照 |
|---|---|---:|---:|
| shop_v7 | 1–8 | **0/8** | **8/8** |
| shop_v7 | 9–16 | **0/16** | **16/16** |
| **合计** | 1–16 | **0/24+**，mean **-10k~-16k** | **24/24**，mean +2.6k |

弱点**可复现、可对照**，不是种子噪声。

## Pipe-16 对其他公开对手（seeds1–4 / 9–12）

| 对手 | WR | mean |
|---|---:|---:|
| Metav4 | ~95% | +50 |
| shop_router **v6** | 8/8 | +3966 |
| farming_score v5 | 8/8 | +4987 |
| evgendvorkin | 8/8 | +4636 |
| yhay81 0913 | 8/8 | +12639 |
| tetsu / flex / R2 | 8/8 | 很大 |

**不是全面变弱，而是对 shop_v7（aurax7 系 reactive v7）特异性崩盘。**

## 风险判断

| 问题 | 答案 |
|---|---|
| 打 Metav4 强吗？ | 强，~95%，+50/局 |
| 榜上会不会更高？ | **不确定且危险**：若池内有 shop_v7 血统，Pipe-16 会大量丢分 |
| Metav4 更稳吗？ | **是** — 同种子对 shop_v7 全胜，且公开分已 2780 仍在爬 |
| 作者 50-0 vs Metav4 | 只证明镜像/父本；**未覆盖异构漏洞** |

## 结论

```text
PIPE16_STRESS_CONFIRMED_WEAK_VS_SHOP_V7
RECOMMENDATION: DO NOT SUBMIT
HOLD last-2 = Metav4 56390446
```

本地没有「全面稳赢 Metav4 且无致命弱点」的包；Pipe-16 **不满足**「更好策略」的完整门禁。

Metav4 继续爬分 + 封榜 BT 仍是当前最优路径。
