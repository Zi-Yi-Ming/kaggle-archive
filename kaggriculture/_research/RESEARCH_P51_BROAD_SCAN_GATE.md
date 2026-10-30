# P51 — Broad External Scan + Local Gate PASS

**日期：** 2026-09-15  
**协议：** pin `env.info["seed"]`，finn 不 wrap，R2 不改  
**状态：** **本地门禁通过；未 submit**

---

## Decision

```text
LOCAL_GATE_PASS_NO_SUBMIT_YET
```

首次出现：**对 R2 8 seed × 双 seat = 8-0-0** 的公开候选。

---

## 广扫结果

| 来源 | 结果 |
|---|---|
| 拉取 notebook | 16+（含 kaito 多版、yhay、boatlee、tetsu、alperen、guru、lime…） |
| 可执行并 vs finn | 3（两两同一 tape 则合并） |
| **过门禁** | **2 unique families** |

### state_router（Thomas 74.5%）
- vs finn ~174k  
- **vs R2 0-0-5 → FAIL**

### 门禁通过候选

| 候选 | 源 | vs finn 8-seed | vs R2 8-seed |
|---|---|---:|---|
| **guru_dynamic** | guruprasaathas *Fully Dynamic Autonomous* | **176,242** | **8-0-0** |
| **alperen_meta** | alperen *MetaCounter R1* | **179,724** | **8-0-0** |
| lime_smart | lime0001 *Score2710* | ≡ alperen（同 tape hash） | — |

---

## Novelty（seed1 vs finn tape）

| | sim_R2 | sim_V16 | sim_kaito | sim_Q | sim_rayk |
|---|---:|---:|---:|---:|---:|
| guru_dynamic | 0.773 | **0.000** | 0.000 | 0.018 | 0.277 |
| alperen_meta | 0.775 | **0.000** | 0.000 | 0.018 | 0.277 |

- **不是** V16 / kaito / Q 拷贝  
- 与 R2 ~0.77（同 meta 路线但非同一 program）  
- 与已知 elite 最近邻 sim 均 **< 0.8**

`p51_novelty.csv`，`p51_local_gate.csv`，`p51_broad_scan.csv`

---

## 与 P43「bank ≠ Elo」一致

| | vs finn mean | vs R2 H2H |
|---|---:|---|
| R2 | ~183k | — |
| alperen_meta | ~180k | **8-0 胜** |

H2H 更强、vs-fin 略低 → 优化目标是 **对局胜负**，不是 surplus coin。

---

## Gate checklist

| 条件 | 状态 |
|---|---|
| local ≥5/8 vs R2 | **8/8 PASS** |
| multi-seed 稳定 | 8 seeds，全胜 |
| 双 seat | 是 |
| novel（sim<0.8） | 是 |
| runtime clean | 是（quiet load + 720 steps） |
| **Kaggle submit** | **未做（按冻结令）** |

---

## Production

last-2 仍为 R2 twin **2012.7** + R2 **1997.7**。

若用户明确要求 submit：用 `alperen_meta` 或 `guru_dynamic` 任一（alperen vs-finn 略高）打包 main.py 提交；仅 **1 次** 替换弱 slot，保留另一 R2 直到评分。

---

## Artifacts

```text
RESEARCH_P51_BROAD_SCAN_GATE.md
_external/p51_candidates_nb/
_external/p51_extracted2/
p51_broad_scan.csv
p51_local_gate.csv
p51_novelty.csv
_p51_broad_scan.py
_p51_local_gate.py
_p51_novelty.py
```
