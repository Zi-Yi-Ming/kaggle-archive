# P92b — 参谋点名候选 exact 复核（v48 + Breaking the Tie）

日期：2026-09-27  
脚本：`_scripts/_p92b_v48_tie.py`、`_p92c_decode_payload.py`  
结果：`_research/p92b_v48_tie.json`  
约束：历史 `scriptVersionId` 拉取 **403 Forbidden**；使用本地 `public_nb` / notebook 内嵌 PAYLOAD exact 产物  

## ① Kaito v48 Fast Routes（优先）

| 项 | 值 |
|---|---|
| 路径 | `_external/public_nb/kaito_v48/main.py` |
| SHA-256 | `dadee25a9840313218384208c53b2c4752f82c3209cc654632e0b96c65e2664a`（= manifest） |
| 宣称 | Fast-Climber Sparse Route Hybrid；notebook Best **3009** |
| 历史 | P79 vs **thomas** 已是 **0/4 −26375** |

**P92b 双门（seeds1–3 × 双座）**

| 对手 | WR | mean margin |
|---|---:|---:|
| **Metav4** | **0/6** | **−23600** |
| **shop_v7** | **0/6** | **−22417** |
| thomas | 0/4 | −26376 |
| alperen | 0/2 | −21755 |
| guru v4 / pipe16 | 0 | −21936 |
| **kaito v43** | **2/2** | **+1673** |

- Slot A: **FAIL**  
- Slot-B collapse: **FAIL**（生产面板全 0/x）  
- 指纹：v48 略胜 v43，但 **同属被 Metav4 血统碾压的一族**；公开 3009 **不能**转化为 vs 生产包强度  

## ② Andrey Breaking the Tie

| 项 | 值 |
|---|---|
| 参谋目标 | **V12** Public=Best **2883** |
| 版本拉取 | `.../341994976` → **403** |
| 实际可加载产物 | notebook PAYLOAD → **V21-R1 teacher bootstrap** |
| SHA | `c6f96a8521dc9aa369b6f27e5b36b9d481e5c1688f50c8ca215c3bb53f1f9eb8`（= notebook EXPECTED_SOURCE_SHA） |
| notebook 自述 | `BOOTSTRAP ONLY: submission.tar.gz has NOT been created` → **不是 V12/2883 提交包** |

**双门（该 bootstrap）**

| 对手 | WR | mean margin |
|---|---:|---:|
| Metav4 | 0/6 | **−35788** |
| shop_v7 | 0/6 | **−33579** |
| thomas | 0/4 | −32907 |

- Slot A: **FAIL**  
- **诚实脚注:** V12 exact **无法经 API 获取**；已测的是当前 notebook 内嵌 bootstrap，且全面弱于生产包。若有人能提供 V12 的 `main.py` 字节，可再跑一次；在此之前 **不能**把 2883 当作可复现 executable。

## ③ 与参谋约定的裁决

> 「若这两个都被双门打掉，赞成彻底回到 HOLD Metav4，不再为了『还有没有 kernel』无限搜索。」

```text
Kaito v48 Fast Routes  — FAIL（exact SHA 校验通过）
Andrey Breaking the Tie — V12 不可得；可得 bootstrap FAIL
→ HOLD Metav4 56390446
→ 不投 v48 / 不投 bootstrap / 不投 Pipe-16 / 不投 Kaito v43
→ 不再无限扫公开高分标题
```

## ④ 累计公开 exact 复核（生产面板）

| 候选 | 声称分 | vs Metav4 | vs shop | 结论 |
|---|---:|---:|---:|---|
| Kaito v43 | 2882 | 0/x | 0/x | 否 |
| **Kaito v48** | **3009** | **0/x −23.6k** | **0/x −22.4k** | **否** |
| Andrey bootstrap | (V12 2883 不可得) | 0/x −35.8k | 0/x −33.6k | 否 |
| haideptry 2965/2950 | 2965/2950 | +50（=Pipe16） | 0/x −16k | 否 |
| guru v4 | — | +50（=Pipe16） | 0/x | 否 |
| one-more-wheat | — | +78 | 0/x | 否 |

**结论：公开 Best 标签与「可加载 executable 在异构生产面板上的强度」系统性脱节。**

## 产物

- `_research/p92b_v48_tie.json`  
- `_research/RESEARCH_P92B_V48_TIE.md`  
- 包：`public_nb/kaito_v48/main.py`、`scan_p92b_versions/extracted/andrey_breaking_tie.py`
