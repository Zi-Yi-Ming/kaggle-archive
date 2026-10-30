# P79 — 穷尽公开候选 vs 生产 thomas（无提交）

日期：2026-09-26  
生产：`_push_thomas_2945/main.py`（ref **56358711**，CLI ~2630）  
脚本：`_scripts/_p79_mass_gate_vs_thomas.py`、`_p79b_*`、`_p79c_*`  
结果：`_research/p79_mass_gate_vs_thomas.json`、`p79b_*`、`p79c_*`、`p79d_*`

## 结论（穷尽后）

| 判断 | 说明 |
|---|---|
| **无公开候选本地 ≥ thomas** | 所有成功跑通的 smoke **胜率均为 0**（仅 evgendvorkin 2/8 例外，仍远弱） |
| **作者新包 56358231** | 公开 kernels 无对应源；不可复用 |
| **榜顶 2957–3282** | 多为私有/未公开 agent；公开 meta 已收敛到 V39/shop-router/thomas 层 |
| **决策** | **继续冻结 last-2，不提交** |

## 成功门禁汇总（vs thomas）

| 候选 | WR | 备注 |
|---|---:|---|
| yhay81 shop-router-0913 | **0/8** | 底座刷新 |
| salemali7 2900 / salem_main | **0/8** / 0/4 | 文案 2900 不成立 |
| evgendvorkin / p71_evo | **2/8** | 最强公开衍生，仍输 |
| prvsiyan moon/rain/top5/main | 0/4 | 同族 |
| kaito v58 / v48 | 0/4 | |
| municef LB2448 | 0/4 | |
| guru master v3 | 0/4 margin 0 | 与 thomas 同 bank（同谱系） |
| flexonafft / tetsu2131 / boatlee | 0/4 | top5 公开包 |
| shop_router v6/v7 | 0/4 | |
| farming_score v2/v4/v5 | 0/4 | |
| thomas 95.5 replay-routing | 0/4 | 作者旧包，远弱 |
| gzmcr / lonespear / sey / cok / pomagrenate / octahedron / rayk c94-c95 / qeinstein / danilchil champ / nusrati / v44y / q30 / day3cow / terminal / score2710 | 0/4 | 外部/历史候选 |

## 无法门禁（加载失败）≠ 更强

Ahmed V45–V50 builder、dmitrii 多文件、pilkwang/reyhanksatria/tetsu market-smart 等 notebook 未抽出可运行 `agent()` 或缺 settings。  
其文案高分多与 **shop-router / V 系 / thomas 同谱系**；无证据表明本地会赢 thomas。

## 公开 vs 私榜

- 公开榜前 20：**2957–3282**（Majkel1337 3282…）
- 你队：**thomas ~2630 银**
- 差距约 **+330 Elo**；公开材料与门禁均未提供可执行「冲金包」

## 工程含义

1. **不要**因文案 2700–3000 盲交（goodpjw/salem/yhay81 已证伪）  
2. **不要** re-submit thomas 期望换 path 回金  
3. last-2 保持 **thomas + twin**；twin 仅占槽不拖分（best-of-2）  
4. 剩余希望：**BT 终榜方差** / 赛后 episode dump 再开 lineage；赛中公开材料已扫尽  

## Loader / harness 经验

- conda env：`C:\Users\Lenovo\.conda\envs\kaggle\python.exe`（kaggle-environments **1.32.7**）  
- notebook extract：截断 `Path("main.py")` / `env.run` 打包尾；IPython+matplotlib stub  
- 同 seed 双座 bank 常对称 → 有效独立信息 ≈ 4 seeds，不是 8 独立样本  
