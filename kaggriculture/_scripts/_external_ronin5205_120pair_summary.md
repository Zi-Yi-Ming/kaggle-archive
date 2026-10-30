# Ronin5205 120-Pair Benchmark Summary

**Date:** 2026-09-11  
**Engine:** kaggle-environments 1.32.7  
**Baseline:** v11E frozen  
**Candidate:** ronin5205  
**Repo:** `D:\桌面\Kaggle\kaggriculture\_external\ronin5205`  
**Wrapper:** `D:\桌面\Kaggle\kaggriculture\_external\ronin5205\wrapper.py`  
**Module name:** `external_ronin5205_wrapper_unique`

## Experiment Configuration

- Seeds: 1-120 (n=120 independent seeds)  
- 2 games per seed (Ronin5205 seat0 vs v11E seat1; v11E seat0 vs Ronin5205 seat1)  
- Total games: 240  
- Episode steps: 720  
- Loader: importlib.util.spec_from_file_location with unique module names

## Smoke Test

- load_ok: True  
- action_ok: True  
- steps_executed: 720  
- runtime_error: None  
- observation_test: {'seed': 2, 'obs0_keys': ['day', 'farms', 'hour', 'market', 'player', 'private', 'remainingOverageTime', 'step', 'town'], 'obs1_keys': ['day', 'farms', 'hour', 'market', 'player', 'private', 'remainingOverageTime', 'town'], 'has_step_key': True, 'step_value': 0}

## Overall

- games = 240  
- Ronin5205 wins = 98  
- v11E wins = 107  
- ties = 35  
- win rate = 40.8333%  
- 95% Wilson CI = [34.8067%, 47.1488%]  
- mean margin = +162.92  
- median margin = +0.00  
- std margin = +2,634.61  
- min margin = -14,144.00  
- max margin = +13,214.00  
- 95% mean-margin CI = [-170.41, +496.24]

## Seat Split

### Ronin5205 seat 0 (n=120)  
- W-L-T = 57-49-14  
- win_rate = 47.5000%  
- mean margin = +437.02  
- median margin = +0.00

### Ronin5205 seat 1 (n=120)  
- W-L-T = 41-58-21  
- win_rate = 34.1667%  
- mean margin = -111.18  
- median margin = +0.00

## Seed Variance

- seed-net-margin mean = +325.83  
- seed-net-margin std = +3,919.63  
- seed-net-margin min = -14,316.00  
- seed-net-margin max = +20,418.00

## Runtime / Invalid-Action Statistics

- total_runtime_errors = 0  
- total_invalid_actions = 0  
- games_with_invalid_actions = 0

## STEP_DEPENDENCY = True

## Final Verdict

**FAIL**

Ronin5205 does not demonstrate a meaningful advantage over v11E.
