# P84 — 猎新包 vs 生产 Metav4（无提交）

日期：2026-09-20  
生产：`_push_metav4_v13/main.py`（CLI **2778.3**，公榜 ZiYiMing **#145 / 9648 ≈ top 1.49%**）  
脚本：`_scripts/_p84_hunt_vs_metav4.py`  
结果：`_research/p84_hunt_vs_metav4.json`

## 作者公开包

`thomastschinkel` 最新公开仍是 **Metav4 v13**（09-20），**无更新版**。

## 本地门禁 vs Metav4（seeds1–2 × 双座 smoke）

| 候选 | WR vs Metav4 | mean Δ | 结论 |
|---|---:|---:|---|
| guru master-engine v3 | **0/4**（bank 与 Metav4 相同/持平） | 0 | **NO** — 至多同源，不更强 |
| lime0001 score2710 | **0/4** | -6231 | **NO** |
| farming_score_v5 | **0/4** | -4934 | **NO** |
| shop_router v6 | **0/4** | -3972 | **NO** |
| ahmed v45/v46、flexonafft×3、prvsiyan、crystalbaby、dmitrii… | 加载失败 | — | 不可门禁 ≠ 更强 |

**无一候选在本地打赢生产 Metav4。**

## 决策

```text
HOLD last-2 = Metav4 56390446
禁止 re-roll / 禁止交弱包
仅当本地 WR vs Metav4 稳定 ≥~80% 且 Validation 过 + 用户授权 → 才谈提交
```

公开分仍在爬（2714→2778）；**等收敛本身就是当前最优「冲刺」**。  
距 top1% 线 ~2816.7 约 +40；终榜仍看封榜后 BT。
