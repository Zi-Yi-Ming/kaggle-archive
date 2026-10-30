# P26 — Baseline Determinism Audit

**Date:** 2026-09-12  
**Goal:** make R2 T0 a repeatable benchmark before any Δmargin learning.

---

## Decision

```text
BASELINE_NONDETERMINISM_ROOTED_AND_FIXED
```

**根因：`env.configuration["seed"]` 不控制 shop RNG；必须 `env.info["seed"]`。**

---

## 证据

### A. 只设 configuration.seed=1（我们过去的写法）

| rep | info_after | bank | shops @144 |
|---|---:|---:|---|
| 0 | **896223292** | 107,879 | BAKERY, PET_CAFE |
| 1 | **2112374029** | 200,714 | SMOOTHIE, PIZZA |
| 2 | **1035370095** | 198,922 | SMOOTHIE, YARN |

`resolve_episode_seed` **scrub** 掉 configuration seed，并落入 **随机 31-bit** → shop 序列每局不同。

### B. 同时设 env.info["seed"]=1

| rep | info_after | bank | shops |
|---|---:|---:|---|
| 0–2 | 1 | **148,548** | PET_CAFE, FARMERS_MARKET |

**3/3 完全一致。**

### C. seed=99

| rep | bank | shops |
|---|---:|---|
| 0–1 | **145,390** | YARN_STORE, BAKERY |

**确定性成立。**

---

## 引擎机制

```python
# kaggriculture.py shop unlock
seed = env.info.get("seed", 0)
rng = random.Random((seed * 1_000_003) ^ day)
...
town["unlocked_shops"].append(rng.choice(sorted(SHOPS)))
```

```python
# resolve_episode_seed: config seed 被清空
setattr(config, "seed", None)
env.info["seed"] = seed  # 仅当此前 info 已有或 config 可读到时
```

我们的 harness **只写 configuration** → 实际 episode seed 是随机的 →  
R2 在 d144 `SHOP_PLANS` 分叉 → 全轨迹漂移。

---

## 对历史实验的含义

| 实验 | 影响 |
|---|---|
| P25 28% positive | 在 **未固定 shop RNG** 下测得 — **不能** 当作可爬山证据 |
| P19–P22 Δcash/Δmargin | 同样未 pin info.seed — paired 仍同进程内可比，但 **绝对 bank 不可跨 run 比** |
| P24 −113k/−166k | 方向仍大概率成立（量级巨大），但 **精确数字需在 pin seed 下复核** |

---

## 固定 harness

```text
p26_harness.py
  run_game(agent0, agent1, seed)
    → 强制 env.info["seed"] = seed
    → 返回 bank + action hash + shops
```

以后所有 Δbank / mutation / selector 实验 **必须** 走该 harness。

---

## 验证标准（harness 合格）

同 seed 重复：

```text
bank identical
action hash identical
shop sequence identical
```

当前 pin 后已满足。

---

## Artifacts

```text
RESEARCH_P26_DETERMINISM.md
p26_harness.py
p26_determinism_audit.csv
_p26_determinism.py
_p26b_joint_hash.py
_p26c_seed_probe.py
```
