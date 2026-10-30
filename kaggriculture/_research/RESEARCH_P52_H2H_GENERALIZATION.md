# P52 — H2H Generalization Gate

**日期：** 2026-09-15  
**协议：** 8 seeds × 双 seat；finn 不 wrap；候选不改；**未 submit**

---

## Decision

```text
CROSS_ELITE_STRONG_SUBMIT_OK
```

**不是 R2-counter。** 两个候选对 **全部 5 个已知 elite** 均为 **8-0-0**（elite 池合计 **40-0-0**）。

---

## alperen_meta

| opponent | W-D-L | class |
|---|---|---|
| R2 | **8-0-0** | STRONG |
| V16 | **8-0-0** | STRONG |
| kaito_v27 | **8-0-0** | STRONG |
| qeinstein | **8-0-0** | STRONG |
| rayk_rank | **8-0-0** | STRONG |
| finn | 8-0-0 | STRONG |
| **elite pool** | **40-0-0** | **5/5 STRONG** |

vs finn 8-seed mean **179,724**。

---

## guru_dynamic

| opponent | W-D-L | class |
|---|---|---|
| R2 / V16 / kaito / Q / rayk | 各 **8-0-0** | STRONG |
| elite pool | **40-0-0** | 5/5 |
| finn | 8-0-0 | 176,242 |

与 alperen **不同 tape**（P51 hash），同一泛化模式。

---

## 判定

| 问题 | 答案 |
|---|---|
| 只克 R2？ | **否** |
| 跨 elite 稳定？ | **是（40-0-0）** |
| novel vs 已知 elite？ | 是（sim_V16/kaito/Q=0，R2~0.77） |
| 是否值得动 last-2？ | **按你预设标准：是** |

R2 twin 本地与 R2 同 policy，H2H 同量级，未单列。

---

## 未做

- Kaggle submit（等你明确授权）  
- 更多广扫  
- 改 R2 / last-2  

---

## Artifacts

```text
RESEARCH_P52_H2H_GENERALIZATION.md
p52_h2h_generalization.csv
_p52_h2h_gen.py
```

---

## 最终输出

```text
P52 DECISION:
CROSS_ELITE_STRONG_SUBMIT_OK

alperen_meta: 40-0-0 vs elite pool, finn mean 179724
guru_dynamic: 40-0-0 vs elite pool, finn mean 176242

SUBMISSION:
未执行（待授权）

NEXT:
授权后仅提交 1 次（建议 alperen_meta），保留另一 R2 slot。
```
