# P94 暴力扫包（2026-09-27 · 冲金准备）

CLI 扫描时 Metav4 **2610.2** / Thomas **2308.7** · last-2 仍在  
动作：全量拉取未测 kernel → exact 提取 → 双门（vs Metav4 + shop_v7）

## 可加载候选双门

| 候选 | vs Metav4 | vs shop_v7 | 判定 |
|---|---:|---:|---|
| **guru TOP 2 Master Engine V4** | 100% **+78** | 0% **−16797** | **= one-more-wheat / Pipe-16 族**（bank 同） |
| a-wonderful-life | 0% −2830 | 100% +5221 | 打 shop 赢、**输 Metav4** |
| countering-big-3 / winning-notebook | 0% −3105 | 100% +5160 | 同上（二者 payload 同族） |

## 不可门禁（分析壳 / 提取失败）

| Kernel | 原因 |
|---|---|
| Kaito v27 Midgame Meta Reset | notebook 为分析/对照，无完整 submission 载荷 |
| boatlee V14 Clone Preemption | 同为分析/参数表，未嵌可加载 agent |
| Rayk Rank Your Agent | 梯子评测 notebook，依赖外部 dataset agents |
| cropsense / farmpilot | 教程式多 cell 拼接语法失败 |
| crystalbaby god-mode | null bytes / 打包异常 |
| destbreso arena / prvsiyan lab / flyfarmer | 无完整 executable agent |

thomastschinkel：**仍无新公开**（Metav4 v13）。

## 结论

```text
暴力扫包结果 = NO DUAL-GATE PASS
guru「TOP 2」标题包 = Pipe-16 谱系换皮（shop 0%）
金牌仍无「过门可执行」candidate
生产: A=Metav4 HOLD · B=Thomas HOLD · 不提交
```

**冲金仍只等信息增量:** 作者真更新 / 真新 frontier exact（过双门）/ Andrey V12 字节。

## 产物

- `_external/scan_p94_violent/extracted/`  
- `_research/p94_violent_gates.json`  
- `_scripts/_p94_violent_gates.py` / `_p94b_targeted_extract.py`
