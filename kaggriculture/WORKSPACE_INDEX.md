# Workspace Index — kaggriculture/

整理日期：2026-09-18  
**不要删除 champion 与 research notes；实验包可归档但勿提交。**

规范路径：`D:\桌面\Kaggle\kaggriculture`  
详细整理日志：`D:\桌面\Kaggle\_workspace\organize_log.jsonl`

---

## 目录结构（整理后）

```
kaggriculture/
├── main.py / cleo_v11_E_backup.py / _pm_pool.py   # 运行时入口与 pool（留在根目录）
├── local_sim.py / run_local.py / kaggriculture_submission.py
├── README.md / INDEX.md / WORKSPACE_INDEX.md / RECON_REPORT.md
├── _production/          # STATUS：alperen FROZEN
├── _research/            # RESEARCH_*.md + p*.csv + figures/
├── _scripts/             # 实验脚本与分析脚本
├── _external/            # notebook / extract / replay / tmp_candidates / root_public_agents
├── reference_agents/     # finn + pool
├── elite_corpus/ experiments/ benchmark/
├── _push_alperen/        # 当前主提交包（KEEP）
├── _push_medal/          # R2 champion（KEEP）
├── _push_v16/            # last-2 伙伴包（KEEP）
├── _push_farmv4/         # farmv4（KEEP）
├── _push_tetsu_r3/       # 历史 last-2（KEEP）
├── _push_v11e_restore/   # v11E restore（KEEP）
└── _archive/             # 失败包 / 大 trace / 历史 / 提交物
    ├── failed_pushes/    # medal_r4–r16, tetsu_r6, v66_r7, v67
    ├── historical_pushes/# v13, wheat
    ├── historical/       # v13*, _pm_*.py, chunk, zip/ipynb
    ├── large_traces/     # _pm_*.jsonl (~500MB，只归档不删)
    ├── calibs/ logs/ build/ results/
    ├── experiments/      # p10_* … p48_traces
    ├── submissions/      # 根目录泄漏的 tar/manifest/timing/exp260_main.py
    ├── audit_tmp/        # 原根目录与 rsna_knee 下的农场审计材料
    └── tmp_candidates/   # 原根目录 tmp_* 外部候选
```

---

## 必留（生产 / 研究主线）

| 路径 | 说明 |
|---|---|
| `main.py` / `cleo_v11_E_backup.py` / `_pm_pool.py` | v11E frozen baseline + pool loader |
| **`_push_medal/`** | **当前主马 R2，提交用 main.py** |
| `_push_alperen/` | last submitted alperen（~2262） |
| `_push_v16/` | last-2 伙伴 |
| `_push_tetsu_r3/` / `_push_v11e_restore/` | 历史可复用包 |
| `_production/STATUS.md` | 提交门槛与冻结状态 |
| `_research/RESEARCH_*.md` + `p*.csv` | 全部研究备忘与结果 |
| `_scripts/` | 可复跑实验/分析脚本 |
| `_external/` | 公开 notebook、replay、extract |

---

## 提交状态（勿盲目再交）

见 `_production/STATUS.md`：

```text
last-2: alperen + V16 — team ≈ 2262
门槛: 本地 vs 当前 R2 ≥5/8 且无 seat 撕裂
NO submit without new-family gate
```

---

## Python

```text
C:\Users\Lenovo\.conda\envs\kaggle\python.exe
```

Kaggle CLI 低频使用，避免限流。

---

## 路径注意

- 研究结果多在 `_research/`；若旧脚本写死根目录散文件路径，改为读 `_research/` 或 `_archive/`。
- `_pm_pool.py` 必须留在项目根目录（脚本按相对路径 import）。
- RSNA 的 fold artifacts 现在在 `rsna_knee/artifacts/`，与农场无关。
