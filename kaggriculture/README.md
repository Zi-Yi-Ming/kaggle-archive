# Kaggriculture — 农场模拟 Agent 赛

**比赛**:https://www.kaggle.com/competitions/kaggriculture
**类型**:Featured · Simulation(发奖牌/积分)| 队数 ~6500 | **截止:2026-09-23**
**奖金**:$50,000(前 10 名各 $5,000)

## 规则要点

- 双人农场对战,30 天 = **720 回合**,比谁的"资金 + 资产"高;
- 动作:种/浇/施肥/收(作物)、买/喂/养(动物:蛋奶毛)、除杂草、买地扩张、
  动态市场买卖(价格随供需波动);
- 提交:每天最多 5 个 agent,按 Elo 式 rating 匹配对战,仅最新 2 个计入终榜;
  终榜由 Bradley-Terry 锦标赛产生。
- 环境契约(社区解码):
  ```python
  obs    = {"player", "day", "farms": [{farmer:(x,y), money, tiles}], "private": {seeds, shed}}
  action = {"farmer": [命令], "hands": [], "market": [[OP, CROP, QTY], ...]}
  # farmer 命令: NORTH/SOUTH/EAST/WEST/WATER/HARVEST/DIG/PASS/["PLANT", CROP]
  # market 操作: ["BUY_SEED", CROP, QTY] / ["SELL", CROP, QTY]
  # tile: None | {"kind":"PLANT", planted_day, watered_today} | {"kind":"WEED"}
  ```

## 本目录文件

| 文件 | 说明 |
|---|---|
| `kaggriculture_submission.py` | **提交物**——纯 stdlib 单文件 `agent(obs)`,可直接粘贴/上传 |
| `local_sim.py` | 本地模拟器(契约与真实环境一致;数值为假设,不影响提交正确性) |
| `run_local.py` | 本地验证:agent vs 空转对手打满 720 回合 |

## 首版策略(v1,规则式)

1. **市场优先**(每回合免费):清仓卖出 → 按空地块数补种子(优先高 ROI 的 CORN);
2. **farmer 就近行动**:收获成熟作物(0)> 浇水(1)> 除杂草(2)> 播种(3);
3. 移动:先 x 轴后 y 轴走一步;已站在目标则执行动作。

本地基准(seed=42):agent **4742** vs 空转对手 **100**(720 回合,0 非法 action)。

## 下一步方向(按性价比)

1. **真实环境校准**:在 Kaggle 上跑一局真实 obs,把 `CROPS` 价格/产量换成真实值;
2. **动物 + 市场套利**:利用 Yarn/Dairy/Market 商店轮换做库存前跑;
3. **买地扩张**:资金充足时买邻接象限,提高单位回合产出;
4. **对手建模**:rating 匹配下,针对不同对手风格调整激进/保守参数。

## 本地验证

```bash
python run_local.py   # 期望:720 回合 / 0 非法 action / agent 分显著高于空转对手
```
