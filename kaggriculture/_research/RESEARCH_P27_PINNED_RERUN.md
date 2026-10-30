# P27 — Pinned-Seed Re-evaluation (P24/P25)

**Date:** 2026-09-12  
**Harness:** `p26_harness.py` (`env.info["seed"]` pinned)  
**Opponent:** fallow_finn  
**Determinism check:** seed1 T0 repeat → **bank & action-hash identical** ✅

---

## Decision

```text
R2_DEEP_LOCAL_BASIN
```

在可信 harness 下，**粗粒度 2-step 微扰几乎全负**；不存在可重复的 hill-climb 方向。

---

## 1. R2 reference（pinned）

| seed | bank | shops@final (public) |
|---:|---:|---|
| 1 | **148,548** | PET_CAFE, FARMERS_MARKET, … |
| 2 | 167,824 | PET_CAFE, ICE_CREAM, … |
| 3 | 187,389 | SMOOTHIE, FARMERS_MARKET, … |
| 4 | 174,050 | SMOOTHIE, FARMERS_MARKET, … |
| 5 | 176,747 | YARN, BAKERY, … |
| seed1 repeat | **148,548** | **hash match** |

跨 seed bank $148k–$187k 是 **真 shop-path 差异**，不再是 harness 噪声。

---

## 2. P25 微扰（3 seeds × 4 days × 3 kinds = 36）

| | n | positive | meanΔ | median | best | worst |
|---|---:|---:|---:|---:|---:|---:|
| **ALL** | 36 | **3/36 (8%)** | **−21,987** | −12,664 | **+19** | −76,881 |
| DROP_SELL | 12 | 3/12 | **−370** | ~0 | +19 | −1,316 |
| SKIP_HIRE | 12 | **0/12** | **−39,488** | | | |
| NO_WORK | 12 | **0/12** | **−26,102** | | | |

**全部「正向」仅 +$19** — 等价于无操作噪声，不是可爬山步。

对比未 pin 的 P25（28% positive, best +38k）：**此前正向全是 path/shop 噪声。**

---

## 3. P24 窗口替换（pinned）

| | T1 d9–12 | T2 d0–5 |
|---|---:|---:|
| s1 | −95,942 | −145,815 |
| s2 | −136,257 | −167,824 |
| s3 | −155,175 | −187,389 |

**方向与量级在 pin 后仍成立** — 我们 production 段替换 R2 仍是毁灭性的。

---

## 4. 结论：R2 是否 local-optimal？

| 问 | 答 |
|---|---|
| 2-step 粗微扰有稳定正向？ | **否**（8%，且 +$19） |
| 大窗替换有正向？ | **否**（全 −100k 以下） |
| R2 处于深 basin？ | **是（在本 operator 空间）** |

```text
P24  大块替换 → 灾难
P25  未 pin → 28% 假正向
P27  已 pin → 8% 且无幅度
```

---

## 对路线的含义

**停止** 在 R2 上用同类粗粒度 mutation 手工爬山。

若再碰 trajectory improvement，必须换 **更细 action 空间**（真实 bundle 替换而非删订单），且全部走 `p26_harness`。

否则应转向：

```text
更大 elite corpus / 学习生成 / 外部 top-agent 数据
```

---

## 封存

```text
❌ 未 pin seed 的绝对 bank 比较
❌ P25 旧 28% positive 结论
✅ p26_harness 作为唯一本地评测入口
```

---

## Artifacts

```text
RESEARCH_P27_PINNED_RERUN.md
p27_pinned_rerun.csv
_p27_pinned_rerun.py
```
