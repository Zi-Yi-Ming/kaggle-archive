# 大肥鱼多单位编排（P117 实测）— 2026-09-27

## 棋盘与站位
```
开局 5x5 可用地（y0-4, x0-4），其余 LOCKED
农舍/家： (4,4)
雇工出生点： (5,4)(4,5)(5,5)(4,4) 舍边
化肥采集点： (3,3)  ← 从 (4,4) 路径 = WEST, NORTH, COLLECT_FERTILIZER
牧栏： 建在 (3,3)–(4,4) 一带（P 符号）
```

## 日重置（极重要）
```
每天 h00: 全员回 (4,4)，hands 清 0
每天 h01: HIRE×5–10，新雇工在舍边出生 → 然后才干活
```
不需要夜间寻路回家——**引擎日切强制回窝**。

## 角色分工（day0–2 实测）
| 手 | 职责 |
|---|---|
| hand0/1 | 后勤：PICKUP 牲口/麦 → BUILD_PASTURE → PLACE → FEED/CARE/DROP |
| hand2 | 多为 PASS（机动） |
| hand3 | 田区：一路向北/西，PLANT/WATER |
| hand4/5 | 田区：PLANT MELON/WHEAT，走 (1,x)–(2,x) 一带 |

## 上午循环（day1+ h2–h11）
```
h2 WEST → h3 NORTH → h4 COLLECT_FERT @ (3,3) + SELL FERT
h5 EAST → h6 SOUTH → h7 DROP / PICKUP WHEAT
h8–h10 FEED/CARE 牲口
h11 DROP
```

## 下午/晚上
- h12 DROP
- h13–23 PLANT/WATER（角色化）
- d9–12 h13 可 BUILD_COOP（鹅舍）
- d25+ HARVEST 波

## 作物布局（中午快照）
```
d1–5   NW 角瓜+麦，东南牧栏
d6–16  草莓铺满上半 5 行
d17–22 中部番茄/胡萝卜
d23–29 下半开垦（BUY_LAND）后麦+胡萝卜收尾
```

## 为什么 v3 仍 0 分
- day0 tape 执行 OK
- day1+ 的 hands 数量/角色切换仍对不齐（5→6→8→10 人）
- 缺的是「按 live 手数重绑角色」的调度器
- 整局 gold tape 开环可到 40k，说明 **tape 本身是好的**，泛化死在 hands 粘合

## 下一步（赛后 Gold Shot v2 硬需求）
1. 日切回窝 + h1 续聘 作为 OS 内核
2. 角色槽：logistics×2 + field×N，按 hands_n 动态绑
3. 肥点 (3,3) 固定路径
4. 市场窗：h1 采购 / h4–10 卖肥
