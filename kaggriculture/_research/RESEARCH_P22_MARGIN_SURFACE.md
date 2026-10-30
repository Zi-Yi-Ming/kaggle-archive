# P22 — Paired Margin Outcome Surface

**Date:** 2026-09-12  
**Probe:** 7 pool agents — **no mixed W/L** on seeds 1–2. Closest |margin|: **melon_mateo** (~$4k).  
**Paired protocol:** seeds 1–4, days 9–10, tails MAIN/CASH/HERD, seat 0 vs melon_mateo.  
**No NN. No submit.**

---

## Decision

```text
PAIRED_MARGIN_SIGNAL_CONFIRMED
```

**配对 Δmargin 可用且强**；**binary W/D/L 仍饱和**（8/8 全 W，无 flip）。  
→ margin-aware selector 有依据；**P(W) selector 仍无依据**。

---

## Probe（knife-edge 搜索）

| Opponent | W/L | mean \|margin\| |
|---|---|---:|
| **melon_mateo** | W/W | **$4,125** ← 最近 |
| homestead_hana | W/W | $11k |
| rotation_rosa | W/W | $14k |
| wheat_walter | W/W | $16k |
| broker_bea / ledger_lena / slotter_silas | L/L | $87k–$130k |

Pool 内 **无** 真正 50/50 对手。

---

## Paired Δmargin（vs melon_mateo）

定义：`Δ(tail) = margin(tail) − margin(MAIN)`，同 seed、同 day、同对手。

| seed | day | ΔCASH | ΔHERD |
|---:|---:|---:|---:|
| 1 | 9 | +8,381 | +4,063 |
| 1 | 10 | **+23,474** | +7,248 |
| 2 | 9 | +9,454 | +1,769 |
| 2 | 10 | +21,918 | +3,555 |
| 3 | 9 | +16,896 | +8,395 |
| 3 | 10 | +25,014 | +4,432 |
| 4 | 9 | **−6,081** | −3,960 |
| 4 | 10 | +14,271 | −4,908 |

| | |
|---|---|
| **CASH Δmargin&gt;0** | **7/8** |
| **mean ΔCASH** | **+$14,166** |
| HERD Δmargin&gt;0 | 6/8 |
| **outcome flips** | **0/8**（全 W） |

CASH 把相对结果 **稳定往有利方向推**（除 s4d9）。

---

## 关键 caveat

Paired 强制 tail 时，mateo 终局 bank 多为 **$3000**（开局资金）— 与 probe（~$18k）不同，说明 **路径耦合** 或其策略在我们改 tail 后崩了。  
因此：

- Δmargin 是 **对我们自己 bank 的可靠配对信号**  
- **不能** 直接读成「对真实刀锋对手的 P(W) 提升」

---

## 与 P19–P21 衔接

| | |
|---|---|
| P19 | state → 反事实 cash value |
| P20 | cash+5 边界 melon≥3 |
| P21 | W/D/L 饱和 |
| **P22** | **paired Δmargin 可用（7/8，+14k）** |

Selector 阶梯：

```text
fixed MAIN
→ melon rule (P20 cash)
→ margin-aware (P22)   ← 现在可测
→ learned / PPO        ← 仍远
```

---

## 若继续 selector

第一版 **margin-aware rule** 仍可极简：

```text
if melon>=3: CASH
else: MAIN
```

用 **paired Δmargin** 做 hold-out 验证（更多 seed/day），不要再上 W/D/L score。

---

## Artifacts

```text
RESEARCH_P22_MARGIN_SURFACE.md
p22_margin_surface.csv
p22_paired_delta.csv
_p22_probe.py
_p22_margin_surface.py
```
