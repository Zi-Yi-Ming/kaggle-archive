# RSNA 提交时间线对照（Kaggle API 时间按 UTC；本地文件为 Windows 本地时区≈UTC+8）

## Kaggle 提交（本会话 CLI 已拉取）

| ref | date (API) | local≈UTC+8 | publicScore | 本地候选匹配 |
|---|---|---|---|---|
| 56331070 | 2026-09-18 13:19:00 | 2026-09-18 21:19 | 0.679 | latest || submission.csv best=exp003_2fold_SC_mean d=6.23e-08 mtime=2026-09-19 03:00:58.550954103; submission.csv best=exp003_fold0_SC_mean d=2.89e-08 mtime=2026-09-18 08:33:03.409412622; submission_exp003_sc_fold0.csv best=exp003_fold0_SC_mean d=2.89e-08 mtime=2026-09-18 08:33:03.409412622 |
| 56299753 | 2026-09-17 08:25:51 | 2026-09-17 16:25 | 0.685 | BEST || submission.csv best=exp003_fold0_SC_mean d=2.89e-08 mtime=2026-09-18 08:33:03.409412622; submission_exp003_sc_fold0.csv best=exp003_fold0_SC_mean d=2.89e-08 mtime=2026-09-18 08:33:03.409412622; submission.csv best=exp003_2fold_SC_mean d=6.23e-08 mtime=2026-09-19 03:00:58.550954103 |
| 56256422 | 2026-09-15 14:19:11 | 2026-09-15 22:19 | 0.659 | EXP-002 a3 fold0 || submission.csv best=exp002_fold0 d=2.32e-08 mtime=2026-09-15 14:16:47.359055519; submission_exp002_a3_fold0.csv best=exp002_fold0 d=2.32e-08 mtime=2026-09-15 14:16:47.359055519; submission.csv best=exp002_fold0 d=2.32e-08 mtime=2026-09-15 14:01:57.170910358 |
| 56203211 | 2026-09-13 08:40:28 | 2026-09-13 16:40 | 0.667 | EXP-001 5-fold mean || submission.csv best=exp001_mean5 d=8.25e-08 mtime=2026-09-13 08:42:15.876516104; submission_exp001_5fold.csv best=exp001_mean5 d=8.25e-08 mtime=2026-09-13 08:42:15.876516104; submission.csv best=exp001_fold0 d=2.48e-08 mtime=2026-09-12 04:33:14.627388 |
| 56162074 | 2026-09-11 08:38:48 | 2026-09-11 16:38 | 0.663 |  || submission.csv__from_Kaggle best=exp001_fold0 d=2.48e-08 mtime=2026-09-11 11:56:48.613412619; submission.csv best=exp001_fold0 d=2.48e-08 mtime=2026-09-12 04:33:14.627388; submission.csv best=exp001_mean5 d=8.25e-08 mtime=2026-09-13 08:42:15.876516104 |
| 56139481 | 2026-09-10 07:04:13 | 2026-09-10 15:04 | 0.658 | BASELINE fold0 || submission.csv__from_Kaggle best=exp001_fold0 d=2.48e-08 mtime=2026-09-11 11:56:48.613412619; submission.csv best=exp001_fold0 d=2.48e-08 mtime=2026-09-12 04:33:14.627388; submission.csv best=exp001_mean5 d=8.25e-08 mtime=2026-09-13 08:42:15.876516104 |
| 55913420 | 2026-08-31 10:38:30 | 2026-08-31 18:38 | None |  || submission.csv best=exp001_mean5 d=3.22e-01 mtime=2026-08-29 14:44:55.761538506; submission_v3_2epoch.csv best=exp001_mean5 d=3.11e-01 mtime=2026-08-29 13:03:40.791737318 |
| 55909290 | 2026-08-31 06:44:33 | 2026-08-31 14:44 | None |  || submission.csv best=exp001_mean5 d=3.22e-01 mtime=2026-08-29 14:44:55.761538506; submission_v3_2epoch.csv best=exp001_mean5 d=3.11e-01 mtime=2026-08-29 13:03:40.791737318 |
| 55908018 | 2026-08-31 05:26:40 | 2026-08-31 13:26 | 0.495 |  || submission.csv best=exp001_mean5 d=3.22e-01 mtime=2026-08-29 14:44:55.761538506; submission_v3_2epoch.csv best=exp001_mean5 d=3.11e-01 mtime=2026-08-29 13:03:40.791737318 |
| 55734380 | 2026-08-24 05:52:41 | 2026-08-24 13:52 | 0.503 |  || (no near local file) |
| 55732362 | 2026-08-24 04:05:07 | 2026-08-24 12:05 | 0.5 |  || (no near local file) |
| 55709319 | 2026-08-23 07:42:56 | 2026-08-23 15:42 | 0.495 |  || (no near local file) |
| 55668747 | 2026-08-21 12:15:37 | 2026-08-21 20:15 | 0.5 |  || (no near local file) |

## 本地 submission 与候选预测的最近匹配

- `submission_v3_2epoch.csv` mtime=2026-08-29 13:03:40.791737318 best=exp001_mean5 max_abs_diff=0.31140407
- `submission.csv` mtime=2026-08-29 14:44:55.761538506 best=exp001_mean5 max_abs_diff=0.32167723
- `submission.csv__from_Kaggle` mtime=2026-09-11 11:56:48.613412619 best=exp001_fold0 max_abs_diff=0.00000002
- `submission.csv` mtime=2026-09-12 04:33:14.627388 best=exp001_fold0 max_abs_diff=0.00000002
- `submission_exp001_5fold.csv` mtime=2026-09-13 08:42:15.876516104 best=exp001_mean5 max_abs_diff=0.00000008
- `submission.csv` mtime=2026-09-13 08:42:15.876516104 best=exp001_mean5 max_abs_diff=0.00000008
- `submission.csv` mtime=2026-09-15 14:01:57.170910358 best=exp002_fold0 max_abs_diff=0.00000002
- `submission_exp002_a3_fold0.csv` mtime=2026-09-15 14:16:47.359055519 best=exp002_fold0 max_abs_diff=0.00000002
- `submission.csv` mtime=2026-09-15 14:16:47.359055519 best=exp002_fold0 max_abs_diff=0.00000002
- `submission_exp003_sc_fold0.csv` mtime=2026-09-18 08:33:03.409412622 best=exp003_fold0_SC_mean max_abs_diff=0.00000003
- `submission.csv` mtime=2026-09-18 08:33:03.409412622 best=exp003_fold0_SC_mean max_abs_diff=0.00000003
- `submission.csv` mtime=2026-09-19 03:00:58.550954103 best=exp003_2fold_SC_mean max_abs_diff=0.00000006

## 候选预测源

- exp001_mean5: shape=(3, 12) mean=0.509170 range=[0.1868,0.8209]
- exp001_fold0: shape=(3, 12) mean=0.533960 range=[0.2022,0.8316]
- exp001_fold1: shape=(3, 12) mean=0.482704 range=[0.1522,0.8801]
- exp001_fold2: shape=(3, 12) mean=0.510811 range=[0.1391,0.7790]
- exp001_fold3: shape=(3, 12) mean=0.512302 range=[0.1827,0.8534]
- exp001_fold4: shape=(3, 12) mean=0.506071 range=[0.1522,0.8179]
- exp002_fold0: shape=(3, 12) mean=0.549956 range=[0.2245,0.8564]
- exp003_fold0_SC_mean: shape=(3, 12) mean=0.511874 range=[0.1735,0.8048]
- exp003_fold0_Sagittal: shape=(3, 12) mean=0.531206 range=[0.1539,0.9068]
- exp003_fold0_Coronal: shape=(3, 12) mean=0.492541 range=[0.1708,0.8216]
- exp003_2fold_SC_mean: shape=(3, 12) mean=0.505322 range=[0.1972,0.8392]
- exp003_fold1_Sagittal: shape=(3, 12) mean=0.460625 range=[0.1691,0.8621]
- exp003_fold1_Coronal: shape=(3, 12) mean=0.536915 range=[0.1373,0.8852]
- exp001_lastfold4: shape=(3, 12) mean=0.506071 range=[0.1522,0.8179]

## 关键数值对照

- EXP-003 fold0 SC vs 2fold SC: 0.08449271
- EXP-001 mean5 vs fold0: 0.16008738

## 09-17 / 09-18 缺口
- API BEST 0.685 @ 2026-09-17 08:25 UTC (=16:25 CST)
- API latest 0.679 @ 2026-09-18 13:19 UTC (=21:19 CST)
- local exp003 fold0 submission mtime=2026-09-18 16:33 CST (=08:33 UTC)
- local exp003 fold1 kernel run=2026-09-18 08:49 (API/kernel timezone)
- local exp003_fold1_pull submission mtime=2026-09-19 11:00 CST — pulled after, not necessarily submitted
- No local submission file dated 2026-09-17 was found in rsna_knee/submissions

## 全仓 09-17 附近修改的 csv/log/ipynb
- 2026-09-18 08:33:03.409412622 submissions\submission_exp003_sc_fold0.csv
- 2026-09-16 13:38:15.738067150 _push_exp003\kernel-metadata.json
- 2026-09-16 13:38:15.738067150 _push_exp003\rsna_exp003_sc_fold0_run.ipynb
- 2026-09-18 08:48:57.877642632 _push_exp003_fold1\kernel-metadata.json
- 2026-09-18 08:48:57.876641989 _push_exp003_fold1\rsna_exp003_fold1_run.ipynb
- 2026-09-18 08:32:52.591431141 artifacts\exp_003_sagittal_coronal\config.json
- 2026-09-18 08:32:59.643419743 artifacts\exp_003_sagittal_coronal\fold_assignment.csv
- 2026-09-18 08:33:00.522859097 artifacts\exp_003_sagittal_coronal\test_uid.csv
- 2026-09-18 08:32:53.406248569 artifacts\exp_003_sagittal_coronal\fold0\Coronal\meta.json
- 2026-09-18 08:32:55.108048916 artifacts\exp_003_sagittal_coronal\fold0\Coronal\test_uid.csv
- 2026-09-18 08:32:55.970803499 artifacts\exp_003_sagittal_coronal\fold0\Sagittal\meta.json
- 2026-09-18 08:32:57.549787998 artifacts\exp_003_sagittal_coronal\fold0\Sagittal\test_uid.csv
- 2026-09-18 08:33:03.411510229 _out\exp003_final\rsna-exp-003-s-c-fold0-gpu.log
- 2026-09-18 08:33:03.409412622 _out\exp003_final\submission.csv
- 2026-09-18 08:32:52.591431141 _out\exp003_final\artifacts\exp_003_sagittal_coronal\config.json
- 2026-09-18 08:32:59.643419743 _out\exp003_final\artifacts\exp_003_sagittal_coronal\fold_assignment.csv
- 2026-09-18 08:33:00.522859097 _out\exp003_final\artifacts\exp_003_sagittal_coronal\test_uid.csv
- 2026-09-18 08:32:53.406248569 _out\exp003_final\artifacts\exp_003_sagittal_coronal\fold0\Coronal\meta.json
- 2026-09-18 08:32:55.108048916 _out\exp003_final\artifacts\exp_003_sagittal_coronal\fold0\Coronal\test_uid.csv
- 2026-09-18 08:32:55.970803499 _out\exp003_final\artifacts\exp_003_sagittal_coronal\fold0\Sagittal\meta.json
- 2026-09-18 08:32:57.549787998 _out\exp003_final\artifacts\exp_003_sagittal_coronal\fold0\Sagittal\test_uid.csv
