# P92 — Kaito v43 定点复核（外部参谋触发 · 无提交）

日期：2026-09-27  
脚本：`_scripts/_p92_kaito_v43.py`  
结果：`_research/p92_kaito_v43.json`  
包：`_external/public_nb/kaito_v43/main.py`  

## 外部证据

- 公开 notebook: `kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid`  
- 页面声称 public/best **2882.0**  
- 本地包 SHA-256 = notebook manifest **`69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3`**（63,309 bytes）→ **exact artifact，不是错包**

## 双门 / Slot-B 面板（seeds 见 JSON）

| 对手 | n | 胜率 | mean margin |
|---|---:|---:|---:|
| **Metav4（生产）** | 6 | **0%** | **−23604** |
| **shop_router v7** | 6 | **0%** | **−22423** |
| thomas 2945 | 4 | 0% | −26376 |
| alperen | 4 | 0% | −26198 |
| pipe16 | 4 | 0% | −26149 |

- **Slot A:** vs Metav4 &lt;60%、vs shop &lt;50% → **FAIL**  
- **Slot-B collapse:** 全部 `0/x` → **FAIL**（官方 hedge「无 downside」也救不了：它 BT 不可能超过 Metav4）  
- panel 胜率代理 = **0.0**

## 解读

1. **公开 2882 ≠ 本 executable 在当前异构面板上的强度。** 与 farm_v4（本地 8–0 → LB ~1980）同构，方向相反：这里公开分高、本地对生产族全灭。  
2. 可能来源：匹配池/路径历史、notebook 内「103/128」针对的公开对手集合 **不含 Metav4 级**、或榜面分未收敛到该包真实 BT。  
3. 机制（两分支 shop hybrid、无 classifier）**不能**在本地压过 Metav4/shop/thomas/alperen。  
4. **reopen trigger 已触发并关闭：** 定点复核不过 → 立即回 HOLD。

## 与官方第二槽结论的合并

官方讨论（参谋引用）: team score = last-2 **更好者**；第二槽 = hedge，**无 downside**。  
→ 我们 **接受** Slot-B 门禁可宽于「必须打赢 Metav4」。  
→ 但 Kaito v43 在异构面板 **0/x 崩盘**，连 Slot-B 也不合格。  
→ Pipe-16 谱系同理：镜像 +50 掩盖不了 shop 崩盘，BT proxy 不可能超 Metav4。

## Slot 门禁（更新后，写入生产纪律）

| 门 | 用途 | 条件 |
|---|---|---|
| **Slot A / 主力** | 替换 Metav4 | vs Metav4 ≥60% **且** vs shop_v7 ≥50% + holdout + Validation + **用户授权** |
| **Slot B / hedge** | 第二槽博 BT | 新 lineage；Validation DONE；**无 0/x 族级崩盘**；≥4 个异构对手；local BT proxy 不显著差于 Metav4；有独立证据（公开高分/新机制） |

**当前无任何候选过 A 或 B。**

## 生产裁决

```text
HOLD Metav4 56390446
Pipe-16 谱系不投
Kaito v43 不投
F7/W3 等自研不投
不重开 P92–P100 自研线
继续：盯新公开包 → 定点双门 → 不过则 HOLD
```

## 产物

- `_research/p92_kaito_v43.json`  
- `_research/RESEARCH_P92_KAITO_V43.md`（本文）  
- `_production/GPT_COUNSEL_BRIEF_20260927.md`（需追加本复核脚注）
