# P90 — 侵入式 flag 突变 + tape 感知注入（无提交）

日期：2026-09-27  
脚本：`_scripts/_p90_flags.py`  
结果：`_research/p90_flags.json`  
生产：Metav4 HOLD  

## 方法

1. 读 `_push_metav4_v13/main.py` 全文，**文本替换模块级常量**后重新 exec（每突变独立命名空间）  
2. **T1 tape-aware**：peek `_IMPL.chassis.routes`，仅当未来 3 步该工人 tape 也是 PASS 才注入；不碰 step0 market、不碰牧场格  
3. 双门：vs Metav4 + vs shop_v7；烟测 seeds1–2 过门则 holdout seeds3–6  

## 结果（已跑完的关键变体）

| 变体 | 改动 | 烟测 vs Metav4 | 烟测 vs shop | holdout vs Metav4 | holdout vs shop | 双门 |
|---|---|---:|---:|---:|---:|---|
| **F7** | `V9_FERT_FIRST_DAY` 14→**10** | **100% +20.5** | 100% +5800 | **50% −15** | 100% +3481 | **holdout 失败** |
| **F9** | RACE margin 12→4, default 40→24 | 100% +7 | 100% | **25% −387** | 100% | 失败 |
| **F10** | RACE margin 24, default 48 | 50% +425 | 100% | **25% −42** | 100% | 失败 |
| T1 | tape-aware 中盘注入 | 0% −1624 | 50% +4446 | — | — | 失败 |
| F1 | 关经济 feed skip | 0% −1602 | 100% | — | — | 父本该层有用 |
| F4/F6/F11 | 关 quote / 放宽 HERD / courier 提前 | **= Metav4 全同** | 100% | — | — | 本 panel 未触发 |

F7 holdout 逐 seed（双座相同）：**−170, −2, +90, +22** → 镜像上是噪声级，**不是稳定边**。

## 结论

1. **Metav4 常量已高度校准** — 多数 flag 不触发或回归；与 nathanjacob「参数全灭」一致。  
2. **烟测 dual-pass ≠ 可提交** — F7/F9 烟测好看，holdout 打回。纪律有效。  
3. **tape 感知也不能把工人拿去种地** — 仍 −1.6k；Metav4 的空闲窗口一动就伤 tape 相位。  
4. 唯一稳定打赢 Metav4 的公开边仍是 HybridOpening，且必崩 shop。  
5. **HOLD Metav4；P90 一律不提交。**

## 下一枪（P91 方向）

| 优先级 | 方向 |
|---|---|
| P1 | F7 更大 holdout（seeds7–20）仅作研究，确认是否真中性 |
| P1 | 终局 712–718 **价格公式分批卖**（公开 inventory 估冲击），双门 |
| P2 | Metav4 vs 高 Elo 公开败局日终 money gap（非 shop） |
| P3 | 盯 thomastschinkel 新公开 |
| 不做 | 提交任何未过 holdout 的 flag 突变 |

## 纪律

**不提交**；HOLD Metav4 56390446；研究 gitignore。

## 产物

- `_scripts/_p90_flags.py`  
- `_research/p90_flags.json`  
- `_research/RESEARCH_P90_FLAGS.md`
