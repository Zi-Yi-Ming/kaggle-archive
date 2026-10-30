# P81 — thomas 单变量本地消融（无提交）

日期：2026-09-26  
脚本：`_scripts/_p81_local_patch_ablation.py`  
结果：`_research/p81_local_patch_ablation.json`  
前提：P80 败局 forensic；生产 `_push_thomas_2945` 冻结，**本实验不改生产包、不提交**

## 结果表（seeds1–4 × 双座；同 seed 双座 bank 对称 → 有效信息≈4 seed）

| 变体 | vs thomas_prod | vs shop_router_v7 | 解读 |
|---|---|---|---|
| **late_sell_cap** (step≥700, 单笔 SELL≤2000) | **0W / 8平** m=0 | 6/8 与 prod 相同 | 末日单笔 SELL **本来就 ≤2000**，包装未改变行为 |
| **no_race** | **4/8** m=-44 | 6/8 m=+4122 | 与 P76 一致：RACE 近噪声；**不优于 prod** |
| **no_courier** | **0/8** m=-414 | — | COURIER **有正贡献**，关掉更差 |
| **no_herd** | **8平** m=0 | — | 本 panel HERD **未触发**（同 P76） |
| **thomas_prod** | — | **6/8** m=+4297 | 生产包仍明显强于公开 shop-router v7 |

## 结论

1. **没有**任何本地单变量在 vs thomas 上达到「稳定更强」（需 ≥60% 胜率且对手多样）  
2. **不要**关 COURIER；HERD 在这些 seed 上本来就没开；RACE 关与不关都到不了门禁  
3. P80 的「末日大 SELL 砸价」用 cap=2000@step700 **未证实**——要么阈值不对，要么瓶颈在 **报价时序/queue** 而非单笔数量  
4. 镜像局 -58 级分差 = path 噪声，**不值得**为它冒险换 last-2  
5. 铜牌 UI ≠ last-2 丢失；CLI 仍约 **2622**，公开包 P79 无人打赢 thomas  

## 工程决策（维持）

```text
冻结 last-2 = thomas + twin
不提交任何 P80/P81 研究变体
09-30 前：无完整门禁 + 用户授权 → 不动
```

## 若赛后再挖（非本场冲刺）

- 更早/更紧的 sale window 消融（对照 dmitrii 思路，但是 **对 thomas 底座**）  
- RACE horizon 网格 + **异构**对手（作者包若赛后开源）  
- 终榜 episode dump：作者 56358231 实际行动 vs 我们 thomas  

## 产物

- `p81_local_patch_ablation.json`
- `RESEARCH_P80_LOSS_FORENSIC.md`
- `RESEARCH_P79_MASS_GATE_VS_THOMAS.md`
