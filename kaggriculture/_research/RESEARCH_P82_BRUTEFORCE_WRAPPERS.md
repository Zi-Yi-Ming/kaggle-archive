# P82 — 暴力包装网格 vs 生产 thomas（无提交）

日期：2026-09-26  
脚本：`_scripts/_p82_bruteforce_wrappers.py`  
结果：`_research/p82_bruteforce_wrappers.json`、`p82b_cap_escalate.json`  
生产：`_push_thomas_2945` 冻结；CLI ~2629；**本实验不提交**

## 网格结论

| 包装 | vs thomas（升级后） | 判定 |
|---|---|---|
| 多数 cap/delay/split/race_off | 与 prod **完全相同 bank**（包装未触发或无效果） | 无效 |
| **cap_s650_q1000_total3000**（step≥650，单笔≤1000，全日 SELL 总量≤3000） | seeds1–8 双座：**6/16 胜**，WR **0.375**，mean margin **+76** | **未过门禁**（需 ≥0.60） |
| 同包装 vs alperen / R2 / shop_router | 8/8、8/8、6/8 | 仅说明 **thomas 底座**本来就压这些对手 |
| 邻域 total2500/3500、s640/s660、q800 | ≤0.33 WR 或全平 | 无更优邻域 |

### 唯一「像有信号」配置的细读

`cap_s650_q1000_total3000` vs thomas（有效独立信息 ≈ 8 seed）：

| seed | margin | 结果 |
|---:|---:|---|
| 1 | 0 | 平（cap 未改变行为） |
| 2 | +538 | 胜 |
| 3 | -62 | 负 |
| 4 | 0 | 平 |
| 5 | +101 | 胜 |
| 6 | 0 | 平 |
| 7 | +31 | 胜 |
| 8 | 0 | 平 |

- 3 胜 / 1 负 / 4 平；**分差多为数十～数百**，属 path/噪声量级  
- **不能**当作「稳定更强」；farm_v4 教训：本地小赢 ≠ 榜上 +Elo  
- 双座 bank 对称 → 不是 16 个独立样本  

## 新拉 kernels（p82）

anasriaz / salem harvest / tetsu adaptive / ahmed v46 等：提取后 **加载失败或无 agent**，无新可门禁强包。  
公开榜顶仍无私有源（P79 结论不变）。

## 决策（维持）

```text
冻结 last-2 = thomas + twin
不提交任何 P82 包装变体
cap_s650_q1000_total3000: HOLD — 未过 vs thomas 胜率门禁
UI 铜/银 = 相对档位；CLI ~2629 仍在 last-2
```

## 若继续暴力（仅本地）

- 更大 holdout seeds + **异构** elite panel（不止 alperen）  
- 仅当 WR vs **thomas** ≥0.6 且 Validation 自对战通过，才谈用户授权  
- 赛中默认 **不交**

## 产物

- `p82_bruteforce_wrappers.json`
- `p82b_cap_escalate.json`
- `RESEARCH_P82_BRUTEFORCE_WRAPPERS.md`
