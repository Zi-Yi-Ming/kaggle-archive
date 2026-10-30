# P12.1 — Worker Routing Diagnostic

**Date:** 2026-09-12  
**Method:** paired action accounting, R2 vs B-stack (labor+EOD DROP+shepherd≤3+early/fert sell)  
**Seeds:** 1–2 × both seats  
**No planner buy/sell changes. No R2 edit. No submit.**

---

## Decision

```text
ROUTING_BOTTLENECK_CONFIRMED
```

Specifically from **d6 onward**: PICKUP thrash + move-per-useful ≈2× R2.  
d0–d3 is **not** the problem (B useful ≥ R2).

---

## Windows (mean per day)

| Window | | useful | pickup | move | use% | pku% | mv/useful | cash@end |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **d0–3** | R2 | 38.5 | **3.5** | 41 | 0.31 | **0.03** | 1.1 | $149 |
| | B | **42.2** | 16.0 | **93** | 0.27 | 0.10 | **2.2** | **$496** |
| **d4–6** | R2 | 54.2 | **3.8** | 58 | 0.38 | **0.02** | 1.1 | $822 |
| | B | **63.7** | 18.7 | **121** | 0.31 | 0.09 | **1.9** | $219 |
| **d7–10** | R2 | **82.1** | **7.9** | 102 | 0.36 | **0.04** | 1.2 | **$5,637** |
| | B | 65.9 | **51.1** | 99 | 0.29 | **0.23** | 1.5 | **$164** |
| **d11–15** | R2 | **120.8** | **5.8** | 102 | **0.49** | **0.02** | 0.8 | **$22,817** |
| | B | 67.3 | **50.5** | 83 | 0.34 | **0.23** | 1.2 | $820 |

### Answers

| Question | Answer |
|---|---|
| B 从何时开始落后？ | **d6–d7**（cash 与 useful 同时分叉） |
| 最早 execution gap？ | **MOVE 偏高 + PICKUP 从 d6 起 4–6× R2** |
| d0–d3 B 更差吗？ | **否** — useful 反而更多，cash 更高 |
| routing hypothesis？ | **支持** — 非早期策略缺失，是喂畜期路径/取货效率 |

---

## Key ratios

| Metric | R2 (d7–15) | B (d7–15) |
|---|---:|---:|
| PICKUP / all cmds | **2–4%** | **23%** |
| useful / all cmds | 36–49% | 29–34% |
| move / useful | 0.8–1.2 | 1.2–1.5 |
| FEED/day | 12–16 | 14（不低） |
| PLANT/day | 5–11 | 5（低） |
| HARVEST d10 | **15.5** | 10.2 |

B 的 FEED 绝对次数并不差，但 **PICKUP 空转把 action budget 吃掉**，PLANT/HARVEST 跟不上。

---

## Mechanism (from code + logs)

`animal_care` 让 **actor 0–2 全部** 在 `hungry>0 and wheat_inv==0 and shed.wheat>0` 时去 PICKUP：

- 3 名 shepherd 同时冲向 shed  
- 1 人拿到麦，另外 2 人 PICKUP 失败，下一 step 重试  
- 形成 **pickup stampede** → pku% 0.23  

这不是 tape 问题，是 **角色未去重 + 无 sticky cargo**。

---

## Primitive to test (single variable)

`p12_1_routing/sticky_shepherd.py`:

1. **唯一取麦权**：仅 actor 0 可从 shed PICKUP WHEAT；1–2 只在已持麦时 FEED，否则种地/其它  
2. **Sticky cargo**：`wheat_inv>0` 时禁止再进 shed  
3. **无固定 day route** — 全 state-driven  

B0 = 当前 B stack；B1 = B0 + sticky_shepherd。

Success: Δcash_d10 显著、pku% 降到 &lt;10%、useful↑。  
若 Δcash_d10≈0 → `STOP_ROUTING`。

---

## Artifacts

```text
p12_1_worker_accounting.csv
p12_1_daywise_productivity.csv
p12_1_route_gap.csv
_p12_1_accounting.py
p12_1_routing/sticky_shepherd.py
p12_1_b0_b1.csv
p12_1_routing_ablation.csv
RESEARCH_P12_1_ROUTING.md
```

---

## Intervention (B1 sticky shepherd)

Single variable: only actor 0 PICKUPs from shed; sticky wheat; non-owners never walk to shed for feed.

| Metric | B0 | B1 sticky | R2 |
|---|---:|---:|---:|
| pku% d7–15 | **0.23** | **0.022** | **0.02–0.04** |
| mean bank | ~$8.5k* | $16.0k | $130k+ |
| d10 cash | ~$100 | **$301** | **$17k** |

\*B0 accounting sample included 2 near-bankrupt games; other-seed B3 sample was ~$30k.

### Read

1. Stampede real — pku% now matches R2.  
2. Cash did not follow — Δcash_d10 ≈ +$200.  
3. One B1 game $1 (owner-only too tight).  
4. Effect size not commensurate with $100k+ gap.

---

## Final Decision

```text
ROUTING_EFFECT_TOO_SMALL
```

Pickup waste was a real **symptom** from d6+. Fixing it to R2-level pku% **did not** open d10 or close the money gap.

**STOP_ROUTING.** No more routing code this cycle.

Next (new cycle): decode R2 **d7–d10 revenue events** (what compounds into +$14k on d10), not more pathing.

NO SUBMISSION.
