# Medal Push R2 — Submit Guide

## What this is

`_push_medal/main.py` is a **self-contained Kaggle script** (stdlib only, no internet).

Policy provenance (Apache 2.0):
- Core: **yhay81 Shop Router 0909** (13 tapes + shop-pair routing)
- Sell timing: **aurax7 Reactive Router**
- Packaging: prvsiyan single-file
- Local research tag: Medal R2

**Do not modify v11E.** This is a separate submission candidate.

## Local VERIFIED results (conda `kaggle` env, kaggle-environments 1.32.7)

| Opponent | W-L-T | Mean margin |
|---|---|---:|
| v11E (frozen production baseline) | **6-0-0** | **+51,369** |
| closer_cleo | 6-0-0 | +48,372 |
| tetsu2131 | 6-0-0 | +35,672 |
| fallow_finn (no-op) | 6-0-0 | +160,892 absolute |

All games: seeds 1–3 × both seats, **fresh agent load every game**, 720 steps, no runtime errors.

Independent earlier check (R1): same policy family beat v11E **16-0** with mean +20k..+50k under both fresh and reuse loading.

## How to submit

### Option A — Kaggle notebook (recommended)

1. Create a new **Script** notebook, private.
2. Paste the entire contents of `_push_medal/main.py` as the only code cell / `main.py`.
3. Settings:
   - Competition: **kaggriculture**
   - Internet: **Off**
   - Accelerator: None
4. Save & Run All (must complete without error).
5. Submit to competition.

`kernel-metadata.json` in this folder is already filled for CLI push if you use `kaggle kernels push`.

### Option B — CLI

```powershell
cd D:\桌面\Kaggle\kaggriculture\_push_medal
kaggle kernels push
```

(Requires Kaggle API credentials configured.)

## Expected score movement (HYPOTHESIS)

- Current production: ~2900 (v11E family)
- Gold cut on recent board: ~2911–2967 for lower gold; top gold 3000–3100
- This agent has a **large local absolute-economy edge** over v11E and several public adaptive notebooks
- Realistic first-submit outcome: **material jump if shop-router is not already saturated in the live pool**
- Risk: many public copies → pool may already contain this policy; Elo gain can shrink

If first submit stalls:
1. Keep last 2 submissions active (competition rule).
2. Next lever is **Kaito Fukami** / other public high-vote routers, or a **meta-router** over 2–3 tapes — not PPO yet.

## Files

| File | Role |
|---|---|
| `_push_medal/main.py` | **Submit this** |
| `_push_medal/kernel-metadata.json` | CLI push metadata |
| `_push_medal/_calib.py` | Local calibration harness |
| `_push_medal/calib_results.json` | Raw calibration games |
| `RESEARCH_R1_16game_truth.md` | Why this beats v11E |

## Frozen baseline note

v11E (`cleo_v11_E_backup.py`) was **not modified**.
