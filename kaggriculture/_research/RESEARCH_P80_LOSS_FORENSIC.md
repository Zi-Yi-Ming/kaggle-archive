# P80 — thomas 榜上败局 forensic（无提交）

日期：2026-09-26  
数据：`_external/p77_search/loss_replays/` + `thomas_losses.json`  
脚本：`_scripts/_p80_loss_forensic.py`  
深拆：`_research/p80b_loss_deep.json`

生产 CLI：thomas ref 56358711 **2622.0**（UI 铜/银为相对档位波动，非 last-2 丢失）

## 四场败局（座位按 TeamNames=ZiYiMing 校正）

| 对手 | margin | 形态 |
|---|---:|---|
| wadigongren | **-1035** | 近镜像 tape：SELL 量几乎相同；对手 WHEAT/FERT 略多，差距从 day10 起单调扩大 |
| **Thomas Tschinkel** `56358231` | **-812** | **异构**：对手 market SELL 极少（WHEAT 409 vs 我们 17387）却终局更高；day25 后差距拉大 |
| Master_S1ave | **-607** | 异构：对手几乎不走大 market queue；**day28 我们还 +14，day29 被反超 -607** → 末日清算/入账路径差 |
| Maciek Kiryla | **-58** | 纯镜像：SELL/HIRE/动物几乎逐项相同；全程微幅落后（-3~-58） |

共性：
- 四场 **双方终局 shed 全空** —— 不是「货没卖掉」，是 **实现收入/时序** 差
- 败局都很薄（58~1035），符合榜上 Elo 只记胜负、BT 方差大的特征
- **不是**生产计划崩盘，而是 **市场执行层 / 末段入账** 细节

## 机制解读（对齐 P76）

1. **镜像/同族 tape（wadigongren、Maciek）**  
   - 产量与卖出总量对齐，差在 **同 turn 报价先后、WHEAT/FERT 少量前置、queue 位置**  
   - 与 P76：RACE/COURIER 在镜像上更重要 —— 一致  
   - Maciek -58：几乎 path 噪声，**不值得为这种局改生产包**

2. **异构强对手（作者新包、Master_S1ave）**  
   - 对手 **几乎不发大额 market SELL**，却赚到相近或更高的 bank  
   - 可能：更依赖 town-center 节奏、不同变现通道、或 replay 中 orders 形态不同  
   - Master_S1ave：**day29 一日 -600+** → 终局窗口（712–718）/ 日终入仓与结算顺序敏感  
   - 作者包公开源不存在；本地改 thomas **无法保证**对上其私有路径

3. **我们相对弱点（研究假设，未改包）**  
   - 末日大量同质 SELL（D29 全品类 6k–7k）可能 **自砸价格**；对手少卖反而单价更高  
   - COURIER/RACE 在「异构少卖对手」上可能 **过度 reserve 或抢卖**（P76：对不抢跑对手深预留会亏）  
   - 开局 path：wadigongren day10 已 -43 → 早期市场小额差会复利

## 赛制含义（铜牌 UI）

- CLI 仍 **2622**，last-2 = thomas + twin 完整  
- 奖牌 UI 为 **相对档位**，对手池爬分会把你挤到铜 —— **不是策略突然失效**  
- 终榜 = 封榜后 **~2 周 BT**，只认 last-2 对局胜负；公开瞬时分 **不锁奖牌**  
- **冻结 last-2 仍是正解**；公开包 P79 已证明无人本地打赢 thomas

## 研究方向（赛中默认不提交）

| 优先级 | 假设 | 验证方式（仅本地） |
|---|---|---|
| P1 | D29 同质大 SELL 砸价 | 单变量：末日 SELL 上限/分日拆分 vs full thomas，同种子双座看 **W/L** |
| P1 | 镜像 RACE 参数 | P76 已示 RACE 镜像敏感；horizon 40/12 vs 更浅，vs Maciek 类 tape |
| P2 | COURIER 在异构对手上是否负贡献 | no_courier vs thomas_full vs Master_S1ave 类代理（若有） |
| P2 | 早盘 WHEAT/FERT 前置 | 对照 wadigongren 少量差，单变量改 opening market |
| 不做 | 盲交 / 换 last-2 / re-roll thomas | P78–P79 已否 |

**门禁（若做补丁）：** vs 生产 thomas + 镜像 tape + 异构 elite；**胜率 ≥60%** 且 Validation 自对战通过；**需用户明确授权**才讨论是否动 twin 槽。

## 产物

- `_research/p80_loss_forensic.json`
- `_research/p80b_loss_deep.json`
- `_research/RESEARCH_P80_LOSS_FORENSIC.md`（本文）
