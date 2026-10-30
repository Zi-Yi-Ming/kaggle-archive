# Kaggriculture — resume notes (P51)

## What hung
`_p51_sr_vs_r2.py` aborted by user — state_router import/run is slow (notebook self-smoke + 720-step agent). Not a logic bug.

## Run tomorrow (file-log stdout only)
```
C:\Users\Lenovo\.conda\envs\kaggle\python.exe D:\桌面\Kaggle\kaggriculture\_p51_sr_vs_r2.py
```
Redirect stdout to `_p51_sr_vs_r2.log`, stderr to `$null` (OpenSpiel noise).

## Current best new candidate
**Public State Router** (~174k vs finn 3 seeds). Unknown vs R2. If ≥4/5 paired W vs R2 → expand 8-seed gate; else discard.

## Freeze
R2 last-2 2012.7 / 1997.7. No Kaggle submit.
