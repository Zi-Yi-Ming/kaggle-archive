# Kaggriculture Research — Day 2 Summary

**Date:** 2026-09-12  
**Deadline:** 2026-09-30（还约 18 天）  
**Python:** `C:\Users\Lenovo\.conda\envs\kaggle\python.exe`

---

## Live status (end of day)

| Ref | Agent | publicScore | last-2 |
|---|---|---:|---|
| 56168165 | **Medal R2** (yhay81 shop-router) | **2318.8** | 是 |
| 56181169 | **R2 path twin** (byte-identical) | **1161.6** ↑ | 是 |
| 56167372 | v66 (Kaito-v58 closed-loop) | 1441.8 | 否（被 twin 挤出） |

**Rank:** ~909（团队 8701）

今日配额：已用 1（twin），剩余 4。

---

## Champion

```text
_push_medal/main.py
= yhay81 Shop Router 0909 + aurax7 sell timing (prvsiyan packaging)
= 线上 2300+ 主马
```

v11E frozen，未改。

---

## What we proved today

1. **16-0 对 v11E 是真的**（昨日）；本地强 ≠ 线上 Elo，但 R2 两条都站得住。  
2. **2300+ = 8C/6S shop-router 镜像带**（ashok top-10：d15 胜者 20/20 = 8牛6羊3地）。  
3. **本地 R2 vs R2 十二局全 exact tie** —— 引擎对称；线上 1.5k–5k 分差来自对手代码微差。  
4. **Elite 分差在 d25–29 的 STRAW/MILK/WOOL 实现**；关键步挂单量几乎相同，差在价格×库存×时刻合成。  
5. **共享市场价格 win=lose 每一天**；草莓 d18~232 → d29~108。  
6. **R8–R16 全部不能稳定 ≥5/8 赢 R2**（overlay / hold / tape patch / 草莓时机）。  
7. **Moon 与 R2 对局 6/6 全 tie**（同族）。  
8. **路径依赖合法且有效**：twin 从 600 已爬到 1161。

---

## Failed variants (do not resubmit)

| ID | Idea | Result |
|---|---|---|
| R8–R11 | 终局 dump / premium 前置 | seat 偏或 no-op |
| R12 | 低价 hold milk | 1-5 更差 |
| R13 | C16 @649/717/718 | 窗口错，4-4 |
| R14 | C16 @709–717 | 4-4 +137 |
| R15 | 改 tape 670–671 灌单 | 4-4 +89 |
| R16 | 草莓 d17–20↑ d29↓ | 4-4 +4 |
| v67 | v66 反 shop-router 签名 | 打不过 R2 |

目录：`_push_medal_r4` … `_push_medal_r16`、`_push_v67` 为实验包，**勿再提交**。

---

## Open-source inventory (all screened vs R2)

| Agent | vs R2 |
|---|---|
| Medal R2 | champion |
| Moon | 6 tie（同策略） |
| tetsu-shape | 3-3 seat 偏 |
| tetsu MSF | 3-3 seat 偏 |
| boatlee / Kaito48/43 / v66 | seat 偏或弱 |
| tetsu R3 | 本地可打，线上掉到 ~1k |
| GitHub lonespear/gzmcr/… | 无优势 |

---

## Key data / scripts

| Path | Use |
|---|---|
| `_push_medal/main.py` | **唯一主提交** |
| `_external/public_data/ashok_top10/replays_2026-08-03.parquet` | 268 elite 局 |
| `_external/replays/` | live R2/v66/tetsu replay |
| `_analyze_replays.py` | 结构/卖出汇总 |
| `_deep_r2_curves.py` | 逐日资金曲线 |
| `_ashok_endgame_gap.py` | elite 终局分差 |
| `RESEARCH_R1` … `RESEARCH_R7` + 本文件 | 研究备忘 |

---

## Tomorrow plan

1. 盯 **twin** 是否逼近/超过原 R2；若 twin 更高，last-2 以更高路径为准。  
2. 配额留给：**本地明确打赢当前 R2 的版本**，或 twin 保护性重提。  
3. 研究优先：elite **日内成交价**（非日初报价）反事实；不要再叠第 17 个无信息 overlay。  
4. API 保持低频，避免限流。

---

## One-line

> **开源 shop-router 把我们送到 2300 镜像带；再往上不是换 notebook，而是路径彩票 + 终局成交机制。配额锁死，champion 不乱改。**
