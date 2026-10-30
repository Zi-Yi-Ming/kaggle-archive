# P34 — Elite Trajectory Geometry

**Date:** 2026-09-12  
**Elites:** R2, kaito_v27, qeinstein, rayk_rank（seed1, pinned, vs finn）  
**Caveat:** P33-C 只证明 **R2** 是 open-loop；**不能**推出所有 elite 都是。

---

## Decision

```text
PHASE_LANDMARK_STRUCTURE_SUPPORTED
```

Action 几乎不同，但 **里程碑顺序 / 相位骨架** 高度一致（kaito 为慢变体）。

---

## 1. Temporal landmarks

| Landmark | R2 | kaito | qeinstein | rayk |
|---|---:|---:|---:|---:|
| field_filled | 0 | 20 | 0 | 0 |
| first_animals2 | 0 | 0 | 0 | 0 |
| melon5 | 0 | 0 | 0 | 0 |
| animals8 | **6** | 7 | **6** | **6** |
| sell_2k | **6** | 7 | **6** | **6** |
| cash_5k | **10** | **10** | **10** | **10** |
| melon_convert | **10** | **20** | **10** | **10** |
| cash_20k | **12** | 15 | **12** | **12** |
| **L1 dist vs R2** | 0 | **35** | **0** | **0** |

**R2 / qeinstein / rayk 里程碑日完全重合；kaito 为延迟 convert 变体。**

---

## 2. Shared motif order

```text
field fill + animals + melon plant @d0
    → animals≥8 @d6–7
    → sell≥2k @d6–7
    → cash≥5k @d10
    → melon convert @d10（kaito@d20）
    → cash≥20k @d12（kaito@d15）
    → late sell ramp d16–29
```

---

## 3. Event density（day-bin）

| bin | R2 sell_val | kaito | qeinstein | rayk |
|---|---:|---:|---:|---:|
| d0–5 | 3k | 2k | 4k | 5k |
| d6–10 | 52k | 20k | 29k | 29k |
| d11–15 | 218k | 19k | 23k | 26k |
| d16–20 | **3.6M** | 58k | 50k | 45k |
| d21–29 | **11.9M** | 113k | 96k | **10.2M** |

- 全员 **hire 随日递增**（过夜清空）  
- R2/rayk 晚期 sell_val 巨大（含空挂 cap）；kaito/qeinstein 温和 — **变现风格不同，相位相同**

---

## 4. Coupled days（sell_val≥1k 且 WATER+HARVEST≥20）

| Policy | n coupled days |
|---|---:|
| R2 | 24 |
| kaito | 22 |
| qeinstein | 24 |
| rayk | 23 |

**中后期生产与变现重叠** — 与 P33-A「market×worker 耦合」一致。

---

## 5. 低维生成结构（假设）

```text
P0 BOOT      d0–1   开地/种长作物/起步畜
P1 EXPAND    d0–6   动物≥8
P2 CONVERT   d6–10  首次大卖 + melon 窗
P3 SCALE     d10–20 现金 5k→20k+
P4 END       d21–29 高频卖出 / 终局
```

kaito：P2 后移到 ~d20。

---

## 6. 勿过度解读

| | |
|---|---|
| 里程碑重合 ≠ 相同 action | 已证 sim≈0 |
| R2 open-loop ≠ 全体 elite open-loop | **必须单独测 kaito/Q/rayk 的 f(day,hour) acc** |
| seed1 一条轨迹 | 需多种子复核 landmark 稳定性 |

---

## 下一步（若做 trajectory generator）

```text
initial env
  → phase skeleton (BOOT/EXPAND/CONVERT/SCALE/END)
  → per-phase coupled market+worker program
  → repair
```

优先级：

1. **Phase skeleton generator**（★★★★）  
2. 多 seed landmark 稳定性（★★★）  
3. 非 R2 elite 的 open-loop acc 复核（★★★）  
4. RL / neural BC（★☆）

---

## Artifacts

```text
RESEARCH_P34_TRAJECTORY_GEOMETRY.md
p34_temporal_landmarks.csv
p34_event_density.csv
p34_regimes.csv
_p34_geometry.py
```
