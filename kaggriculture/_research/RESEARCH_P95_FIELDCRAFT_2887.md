# P95 — Hak Fieldcraft 2887（首个 Slot-B 信号 · 需授权）

日期：2026-09-27  
包：`_external/scan_p95_again/extracted/fieldcraft_pkg/`（`main.py` + `mirror_plan.py`）  
来源：`hakdevelopment/kaggriculture-2887-score-fieldcraft-agent`  
宣称：submission **56258004** public **2887.4**（notebook 自述 2026-09-21 verified）  
结果 JSON：`_research/p95_again_gates.json` → `fieldcraft_2887_expanded`

## 与 Pipe-16 谱系的本质区别

| | Pipe-16 / guru TOP2 / V54 / auto-top1 | **Fieldcraft 2887** |
|---|---|---|
| vs Metav4 | ~100% +50~97 | **25% mean −1266** |
| vs shop_v7 | **0% −16k** | **66.7% +3058** |
| 结构 | HybridOpening 镜像毒 | **shop 鲁棒 + 异构有胜场** |

## 扩大评估（seeds 见 JSON）

| 对手 | n | WR | mean margin |
|---|---:|---:|---:|
| Metav4 | 16 | **0.25** | **−1266** |
| shop_v7 | 12 | **0.667** | **+3058** |
| Thomas | 8 | 0.25 | −308 |
| alperen | 6 | **1.0** | +8266 |
| pipe16 | 6 | 0.333 | +109 |
| kaito_v48 | 6 | **1.0** | +24000 |

- **field_wr ≈ 0.52** · **collapses = []**  
- **Slot A**（vs Metav4≥60% 且 shop≥50%）→ **FAIL**（25% vs Metav4）  
- **Slot B gate** → **SLOT_B_SIGNAL_AUTH_REQUIRED**

## Slot-B 含义（官方 hedge）

```text
Team final = max(BT(A), BT(B))
提交 Fieldcraft 到 Slot B：
  A = Metav4 HOLD（地板不撤）
  B = Fieldcraft（新路径从 ~600 爬）
  挤掉的是 Thomas（弱槽）
```

| 情景 | 结果 |
|---|---|
| Fieldcraft 池内 BT 超过 Metav4 | 队分/名次可能抬升（公开 2887 标签若可迁移） |
| Fieldcraft BT 低于 Metav4 | team 仍 = Metav4，**公开队分不降** |
| Validation ERROR | 不参战；需先看 Successful 是否仍留 Metav4 |

**风险仍在：** 本地 **H2H 输给 Metav4 75%**；2887 公开分 **不能**直接等价 BT 终榜；与 Metav4 族对局可能在榜上吃亏。

## 同批其它包（P95）

| 候选 | 判定 |
|---|---|
| more-wheat-smarter-sales / auto-top1 | = Pipe-16 族 shop 0% · **否** |
| alperen market-rhythm | 输 Metav4 · shop 仅小胜 · **否** |
| shop-router-0913 | 双输 · **否** |
| Kaito v27 / boatlee / 多数教程包 | 不可提取 / 分析壳 |

## 决策（等待用户）

```text
生产 A = Metav4 56390446 · 继续 HOLD
Slot B = Thomas · 默认不替换
Fieldcraft 2887 = SLOT_B 候选 · 状态 AUTH_REQUIRED
→ 未经你明确授权：不提交
→ 若授权：交 1 次 Fieldcraft，挤掉 Thomas，Metav4 留 last-2
```

**授权话术示例:**  
「明知本地对 Metav4 25%，仍授权将 Fieldcraft 2887 提交 1 次作为 Slot-B hedge」
