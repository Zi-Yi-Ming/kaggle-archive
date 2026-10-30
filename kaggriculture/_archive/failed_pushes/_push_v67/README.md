# Kaggriculture v66

一个面向 Kaggle **Kaggriculture** 环境的轻量级、可离线运行的规则智能体。

v66 不依赖神经网络、PyTorch、CUDA、模型权重或在线服务。它只读取官方提供给当前玩家的 observation，组合多条经济路线，并在输出前清洗结构化 action。对手分类和路线分支只使用公开局面，不读取对手私有状态、episode seed 或网络数据；基础行动与合法性清洗会使用当前玩家自己的 private 字段。仓库同时提供已经验证过的上传归档，可以直接复核或提交到 Kaggle。

> 本项目公开的是一个规则策略，不是 PPO、GAE 或其他强化学习模型。本文只报告已有本地验证和历史执行证据，不宣称当前排行榜名次、线上胜率或最优性。

Kaggle 比赛侧公开说明：[Kaggriculture v66 Public Agent](https://www.kaggle.com/code/mohui666/kaggriculture-v66-public-agent)

## 核心特点

- 纯 Python 标准库推理，无第三方运行时依赖。
- 只使用官方给当前玩家的 observation；不读取 episode seed、对手私有状态或网络数据。
- 根据商店序列、双方资金、资产、市场价格和游戏阶段选择路线。
- 在第 72、144 步等阶段重新判断公开局面，而不是从第 0 步盲跑到底。
- 第 713–718 步处理回仓、收获和最终变现。
- `main.py` 对最终联合动作执行合法性清洗。
- 完整提交包约 497 KiB，便于直接上传和复核。

## 策略结构

Kaggriculture 的 action 是三部分组成的结构化对象：

```python
{
    "farmer": ["..."],
    "hands": [["..."], ...],
    "market": [["..."], ...],
}
```

v66 的决策链可以概括为：

```text
observation
    │
    ├─ 基础生产、移动、采购和销售路线
    │
    ├─ 公开局面签名
    │    ├─ 商店出现顺序
    │    ├─ 双方资金和公开资产
    │    └─ 市场库存与价格
    │
    ├─ 阶段性路线选择
    │    ├─ recovery
    │    ├─ known-yarn
    │    ├─ bakery / pizza
    │    └─ curve / clone response
    │
    ├─ 终局回仓与变现
    │
    └─ sanitize_action → Kaggle action
```

策略并不是通用搜索器。它由一个成熟的基础闭环策略和少量严格触发的公开状态分支组成；没有命中分支时会继续使用已验证的基础路线。

## 文件结构

```text
main.py                                  # Kaggle 入口：agent(obs, configuration)
candidate_v66_meta_closed_loop.py        # v66 顶层公开状态路由
candidate_v65_curve_q2_daniel_backbone.py
candidate_v65_curve_q2_known_yarn_repair.py
candidate_v65_curve_cygn_clone.py
candidate_v65_local_combined.py
candidate_v62_composite_bakery_yarn.py
candidate_v60_curve_counter.py
kaggriculture_agent/
└── env/
    └── adapter.py                       # 联合动作规范化与合法性清洗
LICENSE                                  # Apache License 2.0
NOTICE                                   # 上游署名与修改说明
build_submission.py                      # 重新生成 tar.gz
kaggriculture-v66-submission.tar.gz      # 已验证归档
```

虽然依赖文件保留了开发期间的版本名，但它们不是可任选的独立提交：它们共同构成 v66 的最小运行闭包。入口始终是 `main.py:agent`。

## 环境

v66 提交本身只需要 Python 标准库。本地运行官方环境时建议使用已复核版本：

- Python 3.12
- `kaggle-environments==1.32.7`

Linux / macOS：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## 本地冒烟

在仓库根目录运行：

```bash
python - <<'PY'
from kaggle_environments import make
from main import agent

env = make(
    "kaggriculture",
    configuration={"episodeSteps": 720, "seed": 99173},
    debug=True,
)
env.run([agent, "starter"])

final = env.steps[-1]
print("steps:", len(env.steps))
print("statuses:", [player["status"] for player in final])
print("rewards:", [player["reward"] for player in final])
PY
```

成功条件是记录完整 720 步，双方最终状态均为 `DONE`。单局 reward 会随环境版本、seed 和对手变化，不应把它当作通用 benchmark。

## 构建提交包

仓库已经包含 `kaggriculture-v66-submission.tar.gz`。如需从当前源码重新生成：

```bash
python build_submission.py
tar -tzf kaggriculture-v66-submission.tar.gz
```

归档根目录必须包含 `main.py`，同时包含本仓库列出的运行闭包。

## Kaggle 提交

先在比赛网页加入 Kaggriculture、接受规则并完成 Kaggle CLI 登录，然后运行：

```bash
kaggle competitions submit kaggriculture \
  -f kaggriculture-v66-submission.tar.gz \
  -m "Open-source v66 public-observation rule agent"
```

查看提交状态：

```bash
kaggle competitions submissions kaggriculture
```

本仓库公开代码不包含凭据。不要把 Kaggle token、API key 或本地配置加入提交归档。

## 已完成的验证

以下结果仅描述已记录的本地复核，不等同于当前 Kaggle 排行榜表现。

| 检查 | 结果 |
|---|---:|
| 官方环境版本 | `kaggle-environments==1.32.7` |
| 提交包大小 | 509,159 bytes |
| 干净 Python 进程加载 | PASS |
| 固定 seed 完整对局 | 720 steps，双方 `DONE` |
| v66 action 合法性 | 719 次检查，0 非法 |
| 固定 seed 对 starter | `178911 – 3447` |
| 该局环境执行耗时 | 约 9.56 秒 |

另有一组 fresh24 本地双座位循环赛：24 个固定 seed，v66 共参与 144 场，记录为 52 胜、88 平、4 负，points rate 为 0.6667，非法动作、崩溃和超时均为 0。该集合包含 starter 及与 v66 高度相似的派生策略，因此不能解释成线上总体胜率。

历史上 v66 曾成功提交并进入 Kaggle 执行，但这里不把历史单局执行状态表述成当前分数或排名。

## 验证边界与已知限制

- 本地 `PASS` 只说明当前记录的官方环境版本能够加载并完成对局。
- 对 starter 的固定 seed 胜利不能证明广泛泛化能力。
- 固定 seed tournament 不能替代当前线上 ladder。
- 规则中存在精确的公开状态签名；环境或对手分布变化后，某些分支可能不再触发。
- v66 不是学习模型，不会在推理时继续训练或适应未知策略。
- 本仓库不提供当前排名、分数或获胜保证。

## 来源与许可证

基础闭环策略的一部分派生自 Kaito Fukami 的 Kaggle Notebook：

- [238/238 Known Streams | v58 Minimax Closed Loop](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop)

该 Notebook 以 Apache License 2.0 发布。v60–v66 在此基础上增加了公开状态路由、局部经济反制、终局处理和提交级动作清洗。完整署名见 [NOTICE](NOTICE)。

本仓库整体按照 [Apache License 2.0](LICENSE) 发布。

## 免责声明

Kaggle 与 Kaggriculture 是其各自权利人的名称或商标。本项目为独立参赛者的开源实现，不代表 Kaggle 官方，也不提供任何比赛结果保证。
