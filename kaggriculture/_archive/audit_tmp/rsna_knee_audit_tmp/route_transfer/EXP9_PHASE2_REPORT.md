# EXP-9 Phase 2 报告：T1（カワシギ 55425101）hands-hash 恢复验证

日期：2026-09-07 ｜ 引擎 kaggle_environments 1.32.7 ｜ production v11E 冻结（md5 224a1c47... 未动）

## A. Artifact provenance

| 项 | 值 |
| --- | --- |
| source | destbreso/kaggriculture-top10-replay-streams（streams.parquet）+ Kaggle 官方 episode replay endpoint |
| submission | **55425101**（rank-1，team カワシギ，ladder 3282.6 @ 08-15 快照） |
| episode | **91889284**（replay JSON 26.6MB：episode-91889284-replay.json） |
| seed | 1579917451（episode replay info 中记录；与 episodes.csv 一致） |
| seat | 1（rewards [36691, 133672]，カワシギ bank 133672 = episodes.csv 记录一致） |
| engine | kaggle_environments 1.32.7（replay 的 module_version 记录） |
| artifact checksum | tape_55425101_91889284.json（720 步完整动作流，已保存） |

## B. Hash semantics

- `hands_h`（streams.parquet）= **十手动作的 8 字节哈希**（数据集作者注释："since only equality is ever asked of it"）——哈希本身**不可逆**，parquet 不含 hands 原文
- **可恢复通道**：Kaggle 官方 replay endpoint（kaggle CLI：`kaggle competitions replay <episode_id>`）合法公开下载，replay JSON 含双方每步完整 action（farmer/hands/market 原文）→ hands 可映射回原始动作 ✓

## C. Recovery result

- **RECOVERED** ✓
- 720/720 steps 完整；每步 action schema 合法（farmer/hands/market）
- farmer/market 与 streams.parquet **逐位一致**（True/True——数据集为同一 episode 的忠实提取，交叉验证通过）
- hands 原文：666/720 步非空（样例 `[["WEST"],["NORTH"],["WEST"],["WEST"],["WEST"]]` 等完整保留）
- seed/episode/submission 三要素全部对上；可独立 deterministic replay；无缺步、无猜测、无插值、无人工修补

## D. Gate

```
PASS → C1 可进入 Phase 3（exact tape replay + smoke）
```

- production v11E 未修改；未跑正式 benchmark；未加 repair/adaptive；未提交 Kaggle
- 恢复全程合法公开（kaggle CLI replay endpoint），无权限绕过

## 下一步（gated，不自动执行）

Phase 3 smoke：T1 = tape_55425101_91889284.json 的 exact replay（720 步原样）vs T0（v11E），8-16 paired seeds 双 seat，deterministic double-run，reconciliation==0。
