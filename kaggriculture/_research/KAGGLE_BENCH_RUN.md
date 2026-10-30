# v13 异构 Benchmark — Kaggle Notebook CPU 运行说明

## 为什么用 Kaggle Notebook CPU
- 免费、不耗 GPU 配额（本 benchmark 纯 CPU）
- 环境无代理问题，9h 上限足够（预计 ~1-2h 跑完 520 局）
- 断点续跑：CSV 追加写入，session 断了重跑会自动跳过已完成局

## 步骤 1：新建 Notebook
1. https://www.kaggle.com/code → New Notebook
2. Settings → Accelerator 保持 **None (CPU)**（不要选 GPU，省配额）
3. 建议勾选 Settings → "Turn off internet access"？ **不要勾**——首次要 pip install。装完后如果不需要可忽略。
4. 右上 **Upload**（笔记本编辑器右上 "+" 图标旁）→ 上传 `v13_bench_kaggle.zip`
   （文件会自动出现在 /kaggle/working/ 下）

## 步骤 2：运行以下 cells（复制粘贴）

### Cell 1 — 解压 + 装引擎（固定版本 1.32.7）
```python
# 解压研究包
!cd /kaggle/working && unzip -o v13_bench_kaggle.zip
!ls -la /kaggle/working/*.py | head

# 安装引擎——版本必须锁死 1.32.7(P0 校准基于此版本)
!pip install -q kaggle-environments==1.32.7
```

### Cell 2 — 版本与引擎验证（关键！跑前必须过）
```python
import importlib, sys
import kaggle_environments as ke
print("kaggle-environments:", ke.__version__)
assert ke.__version__ == "1.32.7", "版本必须 1.32.7!"

# 快速冒烟:加载 v11E 跑 1 局,确认引擎机制与本地一致
sys.path.insert(0, "/kaggle/working")
import _pm_pool as P
from kaggle_environments import make
v11 = P.load_agent("v11E")
env = make("kaggriculture", debug=False)
env.configuration["episodeSteps"] = 720
env.configuration["seed"] = 7
env.run([v11, P.load_agent("broker_bea")])
b = env.steps[-1]
print("v11E vs broker_bea 冒烟 bank = [%.0f, %.0f]" % (
    b[0]["observation"]["farms"][0]["money"],
    b[1]["observation"]["farms"][1]["money"]))
# 本地参考(2026-09-05,seed=7): ~[83000-87000, ...]——只验证"能跑通且量级正常"
print("冒烟通过(能跑通即引擎 OK;bank 量级正常)")
```

### Cell 3 — 跑核心 A/B：E vs D（sequential 收益在异构对手上是否复现）
```python
# E(被测) vs 全 pool 13 对手 × 50 局 ≈ 650 局 ~40-60 分钟
!cd /kaggle/working && python _pm_bench.py --agents E --all-opps --n 50
```

### Cell 4 — 跑 D（对照臂）
```python
!cd /kaggle/working && python _pm_bench.py --agents D --all-opps --n 50
```

### Cell 5 — 跑 A(≈v10) 与 closer_cleo(≈v9) 定位（可选,各 vs 高 tier 4 对手 30 局）
```python
!cd /kaggle/working && python _pm_bench.py --agents A,closer_cleo \
    --opp broker_bea --n 30
!cd /kaggle/working && python _pm_bench.py --agents A,closer_cleo \
    --opp ledger_lena --n 30
!cd /kaggle/working && python _pm_bench.py --agents A,closer_cleo \
    --opp melon_mateo --n 30
!cd /kaggle/working && python _pm_bench.py --agents A,closer_cleo \
    --opp rancher_rita --n 30
```

### Cell 6 — 验证结果 + 下载
```python
import pandas as pd
df = pd.read_csv("/kaggle/working/_pm_bench.csv",
                 names=["agent","opp","seed","win","bank_a","bank_b"])
print("总局数:", len(df))
print(df.groupby(["agent","opp"]).size().unstack(fill_value=0))
print(df.head())
# 下载:右下角 Output 面板 → _pm_bench.csv → Download
```

## 步骤 3：把 _pm_bench.csv 发回
- 下载后放回本地 `D:/桌面/Kaggle/kaggriculture/_pm_bench.csv`
- 我这边做 Wilson CI、E-D 差异分解、matchup 矩阵分析

## 注意
- **不要**在 Kaggle 上 import 比赛数据或提交——这纯本地引擎研究,与比赛数据无关
- session 若超时断开:重跑 Cell 1-2 后直接跑 Cell 3/4,CSV 追加续跑(已完成的 seed 自动跳过)
- 若 Cell 3 跑太久,可中途 Ctrl+C,后续重跑会从断点继续
