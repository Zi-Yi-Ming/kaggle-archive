# P41 — External Elite Discovery（第五族 + 生成机制）

**日期：** 2026-09-14  
**类型：** Elite Discovery / Generation Mechanism（**不是** R2 优化）  
**协议：** pin seed，finn 不 wrap

---

## Decision

```text
FIFTH_FAMILY_FOUND_BUT_LOSES_TO_R2_0_OF_8
NO_SUBMIT
```

| 发现 | 结果 |
|---|---|
| 新完整 program（vs finn mean3） | **172,660** |
| sim vs R2/kaito/Q/rayk | **全部 0.000** |
| 是否第五个 160k+ family | **是** |
| 本地 vs R2（8 seed，双 seat） | **0–0–8** |
| 门禁 ≥5/8 vs R2 | **FAIL** |
| 是否 submit | **否** |

---

## 信息侦察结果

从 Kaggle public kernels 拉取高票/高分 notebook：

| kernel | 价值 |
|---|---|
| boatlee / salemali7 **V16-RC5 / 2900+** | **完整 open-loop tape agent** |
| rayk findings-from-zero-to-top-meta | 生成方法叙述（与 rayk_rank 同源） |
| flexon / pilkwang / master-engine | 抽取失败或非完整 agent |

**可运行第五族：** `salem_2900_main.py` ≡ boatlee V16（压缩 action table）

---

## 数字

### vs finn（绝对产能）

| agent | s1 | mean3 |
|---|---:|---:|
| R2 | 181,389 | 183,850 |
| kaito_v27 | 174,341 | ~175k |
| **V16 (new)** | 169,294 | **172,660** |
| qeinstein | 162,690 | ~170k |
| rayk_rank | 163,494 | ~163k |

### V16 vs R2（head-to-head，双 seat）

| seed | V16 | R2 | 胜者 |
|---:|---:|---:|---|
| 1 | 82k | 125k | R2 |
| 2 | 60k | 83k | R2 |
| 3 | 82k | 128k | R2 |
| 4 | 46k | 65k | R2 |
| 5 | 62k | 77k | R2 |
| 11 | 85k | 115k | R2 |
| 12 | 86k | 105k | R2 |
| 13 | 147k | 164k | R2 |

**W-T-L = 0-0-8。**  
V16 是 elite **对弱基线** 的产能，但 **直接对抗** 输给 R2 一截。

---

## 生成机制（本阶段核心知识）

V16 的实现形态：

```text
_ACTIONS = json.loads(zlib.decompress(base64.b85decode(...)))
agent(obs) → 查表 replay 720-step coupled actions
```

**Elite 可以是「压缩的完整 open-loop 轨迹表」，而不是手写规则。**

这解释了 P38/P40 失败：

| 表示 | 生成方法 |
|---|---|
| open-loop tape（P35 已观察） | **≠** 手写 grammar（P38/P40） |
|  | **=** 搜索/进化/优化出来的轨迹，再打包提交 |

与用户判断一致：  
**「open-loop 是表示形式 ≠ open-loop 是生成方法。」**

---

## 对研究链的更新

```text
P37  elite 不可重组
P39  worker/market 不可拆迁移
P40  从零 coupled 规则合成 → max 44
P41  外部发现第五族（172k, sim=0）+ tape-table 生成形态  ← HERE
     但 0/8 输给 R2 → 不替换 production
```

---

## Production

**不变。** last-2 仍为 R2 twin 2012.7 + R2 1997.7。  
V16 **不**满足 ≥5/8，**不 submit**。

---

## 下一步（仅当继续）

1. 继续扫 public kernels / discussions，找 **≥R2 且 sim 低** 的 tape-table agent  
2. 研究 rayk「Zero to Top Meta」生成过程（search 怎么跑的）  
3. **不要**把 V16 当「更强 R2」微调  

**P41 对 medal 未开门禁；对「elite 如何被产生」打开了入口。**

---

## Artifacts

```text
RESEARCH_P41_ELITE_DISCOVERY.md
_external/p41_candidates/*.ipynb
_external/p41_extracted/salem_2900_main.py
p41_external_eval.csv
p41_v16_vs_r2.csv
```
