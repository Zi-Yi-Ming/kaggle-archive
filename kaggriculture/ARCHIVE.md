# Kaggriculture 归档（2026-09-25）

提交窗已关（最后提交日 2026-09-24）。此后约一周 BT 匹配 → 终榜。本目录转入归档态。

## 最终 last-2（锁定）

| ref | 名称 | public | 备注 |
|---|---|---:|---|
| 56520531 | **Shepherd Herd Safe** | 1938.4↗ | 本地 vs Metav4 **100% +1797**，shop 100%；全场最强 |
| 56517304 | **2965 V59.2** | 2041.0 | 本地 +529 vs Metav4；保底 |

- 队分 = max(Shepherd, 2965)；铜线（前10%）**2292**，银 **2480**，金 **2707**
- 全榜 **9956** 队；我方 ZiYiMing 曾达 rank ~200，回落至 ~1585（2036 时点）
- 终榜由 **Bradley-Terry** 约一周真局产生，public 只是预览

## 曾用/对照包（不进 last-2）

| 包 | 说明 |
|---|---|
| `_push_h3x_term642/` | H3x 终局 start=642，本地 +508，live 曾 2030+ |
| `_push_h3plus_term624/` | H3+ start=624，+348 |
| `_push_h3pp_term636/` | H3++ start=636，+428 |
| `_push_h3_term_greedy/` | H3 start=648，+369；Fieldcraft/Metav4 系时代 |
| `_push_metav4_v13/` | 生产地板参考，+0 镜像 |
| `_push_fieldcraft_2887/` | Slot-B 对冲，已挤出 |
| `_push_thomas_2945/` | 早期银牌主力（历史） |

## 研究结论（赛后复盘用）

1. **大肥鱼（2944）架构**：多单位农场 OS + 收肥白饭 + 日结雇工 + 83% 市场 tape / 18% 手部自适应。见 `INTEL_GOLD_CHOREO.md`、`INTEL_GOLD_COMMENT_PARSED.md`
2. **偷招全负**：禁 day0 卖、卖肥插件、hand 规则、时间刀、牲口滴灌——都会打碎 Metav4/Shepherd 耦合
3. **可迁移的只有局部旋钮**：终局 start 624/636/642 系列（H3x 642 最优 +508）
4. **Shepherd Herd Safe** 是公开可得最强（+1797）；叠 H3x 终局反而掉到 +1283
5. **shop 毒**：V/Pipe/2950/2965 族对 shop_v7 −13k～−16k；Shepherd/H3x/Metav4 系 shop 安全

## 目录说明

- `_push_*` 最终提交包（只读）
- `_research/` 实验 JSON + 金情报 MD
- `_scripts/` P1–P170 实验脚本
- `_external/` 公开扫描/回放（p101_replays 金队 12 场、p139_h3x_live 20 场）
- `_archive/` 失败推送、大 trace、审计
- `_production/STATUS.md` 过程状态（含大量历史，勿再编辑为活跃）

## GitHub

远端 `Zi-Yi-Ming/kaggle-archive`。奖牌赛代码赛期不公开；赛后按 `POST_COMP_GITHUB_OUTLINE.md` 精选里程碑再推。
