# 标签弱项结论（2026-09-19 CPU 审计）

依据：`train.csv` 官方 gold 58 例 + `rsna_report_labels.extract()` 全量 4407 报告。

## 1. 有效覆盖率（决定 macro AUC 上限）

| 标签 | 有效覆盖 | Gold 阳性抓取 | 主要失败模式 |
|---|---:|---|---|
| ACL / MCL | ~72% | 24/24, 9/9 | 可用 |
| Meniscus / Effusion | 69–84% | 大体可用 | 少量 silent |
| PF OA | 61% | 14/21 | 缺 compartment+OA 词 |
| Contusion / Fracture | 37% / 21% | 15/19, 12/18 | gold 可能把 bone bruise 标成 Fracture；退变骨髓水肿被 decoy |
| Medial/Lateral OA | 25%/23% | 9/15, 6/11 | 见下 |
| **Synovitis** | **12%** | **10/27** | **代理分数被丢弃** |

## 2. 根因 A（主因，同一管线 bug）：纠正分数算出来了，却在进 pseudo 表时被丢掉

`extract()` 有两处**故意**在 npos=nneg=0 时写入分数：

1. **Synovitis ← Effusion 代理**
   - `Large effusion` → Synovitis score=**0.5815**, npos=0 → pseudo=**NaN**
   - `Effusion with synovitis`（原文写了 synovitis）→ score=0.845, npos=1 → pseudo=0.845 OK
2. **GLOBAL_OA（全关节 OA）**
   - `Incipient OA of all three compartments`（正确拼写）→ Medial/Lateral/PF OA score=**0.7498**, npos=0 → pseudo=**NaN**
   - `osteoarthritis of the knee` / `tricompartmental osteoarthritis` / `all three compartments show osteoarthritis` → 同样 0.75 后被丢掉
   - `Incipient OA of all three compartmens`（拼写错误）→ GLOBAL_OA 未命中，score 保持 0.28 地板

`report_score_to_target()` 规则：

```python
if npos > 0: return score
if nneg > 0: return score
return NaN   # ← 纠正路径写入的软标签全部死在这里
```

Gold Synovitis 阳性且 pseudo 沉默的 16 例中：**14 例其实有 pseudo_Effusion，12 例 Effusion>0.5**——代理数据都在，只是没写进表。

**修复方向（单变量）**：当 GLOBAL_OA / synovitis-proxy 触发时，给对应目标 `__npos += 1`（或 `report_score_to_target` 认 `res[tgt+"__soft"]=True`）。  
预期：Synovitis 有效覆盖 12% → 接近 Effusion 覆盖；OA×3 从 22–25% 明显抬升。

## 2b. 根因 A2：OA 词表缺口（修完 A 后仍会漏）

| 短语 | 现状 |
|---|---|
| `OA of medial compartment` | 完全不命中：`OA_EVIDENCE` **无 `\bOA\b`** |
| `chondrosis` / `diffuse high grade chondrosis` | 不命中（有 chondropath/chondromalac，无 chondrosis） |
| `Osteophytes are present`（无 compartment） | 不命中（缺全局骨赘语境） |
| `compartmens` 拼写 | GLOBAL_OA / compartment 词表不匹配 |

**修复方向**：`OA_EVIDENCE` 增 `\bOA\b`、`chondros\w*`；`GLOBAL_OA` 增 `all three compartm\w*`、`\bOA\b of (the )?(medial|lateral|three)`；compartment 允许 `compartm\w*`。

## 3. Fracture / Contusion

- `Insufficient fracture...` → Fracture 0.845 OK（词表能抓）
- `bone contusion is noted` → Contusion 0.95 OK
- Gold 可能把 bone bruise 标成 Fracture；与 decoy 策略冲突
- **EXP-002 Contusion 单点改动已伤 LB（0.659）**，不要先动 trauma 侧

## 4. 建议 GPU 顺序（EXP-004 Axial 之后）

1. **EXP-005 soft-label plumbing**：只修「纠正分数被丢弃」——Synovitis 代理 + GLOBAL_OA 进 pseudo 表  
2. **EXP-006 OA lexicon**：只加 `\bOA\b` / chondrosis / compartmens typo  
3. 不要同时改 trauma；每次 lock sha256 + label_manifest，对照 EXP-003 S+C fold0 **0.685**

## 6. 产物路径

- 报告：`_workspace/rsna_label_weakspots/report.md`
- 失败样例：`gold_miss_samples.json`
- 覆盖率：`_workspace/rsna_status_audit/label_coverage.md`
