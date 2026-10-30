# P78 — 候选 vs 生产 thomas（本地门禁，无提交）

日期：2026-09-26  
脚本：`_scripts/_p78_gate_vs_thomas.py`  
结果：`_research/p78_gate_vs_thomas.json`  
生产：`_push_thomas_2945/main.py`（ref 56358711，CLI ~2630）

## 结论

| 候选 | vs thomas (seeds1–4×双座) | mean margin | 决定 |
|---|---|---:|---|
| **yhay81 shop-router-0913** | **0/8** | -10425 | **NO** — 底座刷新仍弱于 thomas 层 |
| **salemali7 kaggriculture-2900** | **0/8** | **-40689** | **NO** — 文案 2900 与本地严重不符 |
| **evgendvorkin public evolution** | **2/8** | -4324 | **NO** — V39/V45 衍生，未过 thomas |

## 作者新包 56358231

- 榜上曾赢 thomas -812（样本败局）
- 公开 kernels 搜索 `thomastschinkel`：仅见 2945 Farm / 93.8% state-router / 95.5% replay-routing 等，**未见对应 56358231 的新公开包**
- 56358231 可能为私有提交或 2945 的 path 重开 — **不能当可复用的下一枪**

## 门禁纪律（再次）

- 本地 H2H **只能否决**；以上三者均未达到「稳定 ≥ thomas」
- **不提交**；last-2 冻结 thomas + twin
- 无新 family + 完整门禁 + 用户授权 → 不动 last-2

## Loader 经验

- notebook extract 尾部常有 `Path("main.py")` 打包 / `env.run` 自检 → 必须截断
- salemali7 等展示型 notebook 含 matplotlib/IPython → stub + 只取 `_ACTIONS`/`def agent` 核心
