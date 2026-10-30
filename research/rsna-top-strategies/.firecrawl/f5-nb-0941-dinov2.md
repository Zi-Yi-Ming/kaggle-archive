menu

[Skip to\\
\\
content](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#site-content)

[![](https://www.kaggle.com/static/images/site-logo.svg)](https://www.kaggle.com/)

Create

search​

- [explore\\
\\
Home](https://www.kaggle.com/)

- [emoji\_events\\
\\
Competitions](https://www.kaggle.com/competitions)

- [leaderboard\\
\\
Benchmarks](https://www.kaggle.com/benchmarks)

- [smart\_toy\\
\\
Game Arena](https://www.kaggle.com/game-arena)


- [code\\
\\
Data Hub](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#)

expand\_more


- [format\_list\_bulleted\\
\\
More](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#)

expand\_more


menu

[Skip to\\
\\
content](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#site-content)

[![](https://www.kaggle.com/static/images/site-logo.svg)](https://www.kaggle.com/)

search​

[Sign In](https://www.kaggle.com/account/login?phase=startSignInTab&returnUrl=%2Fcode%2Fberaterolelk%2F0-941-sota-rsna-knee-dinov2-radimagenet) [Register](https://www.kaggle.com/account/login?phase=startRegisterTab&returnUrl=%2Fcode%2Fberaterolelk%2F0-941-sota-rsna-knee-dinov2-radimagenet)

[Berat Erol ÇELİK's profile](https://www.kaggle.com/beraterolelk) Berat Erol ÇELİK  · 3d ago · 506 views

arrow\_drop\_up24

Copy & Edit
20

file\_downloadDownload

![bronze medal](https://www.kaggle.com/static/images/medals/competitions/bronzel@2x.png)

more\_vert

# 🩻 \[0.941 SOTA\] RSNA Knee DinoV2 & RadImageNet

## 🩻 \[0.941 SOTA\] RSNA Knee DinoV2 & RadImageNet

[Notebook](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet/notebook) [Input](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet/input) [Output](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet/output) [Logs](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet/log) [Comments (1)](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet/comments)

historyVersion 8 of 8chevron\_right

## Runtime

play\_arrow

9m 50s · GPU T4 x2

## Input

COMPETITIONS

![](https://www.kaggle.com/competitions/154281/images/thumbnail)

RSNA Knee Abnormality Detection

DATASETS

![](https://storage.googleapis.com/kaggle-datasets-images/11745616/19120128/cc223f1e84453683e79c7eadc05020ff/dataset-thumbnail.png?t=2026-08-23-17-26-52)

Knee MRI - Max-Span Dense Corpus

![](https://storage.googleapis.com/kaggle-datasets-images/11746763/19122845/cc223f1e84453683e79c7eadc05020ff/dataset-thumbnail.png?t=2026-08-23-17-24-21)

Knee MRI - Native 384 Corpus

![](https://storage.googleapis.com/kaggle-datasets-images/11752181/19134209/cc223f1e84453683e79c7eadc05020ff/dataset-thumbnail.png?t=2026-08-23-17-23-29)

Knee MRI - Native 384 Dense Corpus

![](https://storage.googleapis.com/kaggle-datasets-images/new-version-temp-images/default-backgrounds-37.png-8955132/dataset-thumbnail.png)

knee mri fold weights

trending\_flat

See All

MODELS

![](https://storage.googleapis.com/kaggle-organizations/3837/thumbnail-2.png)

DINO v2 · dinov2 · V1

NOTEBOOKS

![](https://storage.googleapis.com/kaggle-avatars/thumbnails/default-thumb.png)

RSNA Knee E11 train

![](https://storage.googleapis.com/kaggle-avatars/thumbnails/default-thumb.png)

RSNA Knee E13 train

## Tags

[GPU](https://www.kaggle.com/code?tagIds=16580-GPU)

## Language

Python

## Table of Contents

[🩻 \[0.941 SOTA\] RSNA Knee: DinoV2 Small + RadImageNet ResNet50 + Meniscus Specialist](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#notebook-container) [Bend the Knee to the Dinosaurs](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Bend-the-Knee-to-the-Dinosaurs) [Credits](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Credits) [Bend the knee to the dinosaurs — a knee MRI ensemble, taken apart](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Bend-the-knee-to-the-dinosaurs-%E2%80%94-a-knee-MRI-ensemble,-taken-apart) [What the score rewards, and why it shapes everything below](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#What-the-score-rewards,-and-why-it-shapes-everything-below) [The pipeline](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#The-pipeline) [What changed in this build](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#What-changed-in-this-build) [0\. Run configuration](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#0.-Run-configuration) [Exploratory analysis](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Exploratory-analysis) [Stage 1 — the report extractor](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Stage-1-%E2%80%94-the-report-extractor) [Stage 1 (continued) — DINO: read the study, combine the members](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Stage-1-(continued)-%E2%80%94-DINO:-read-the-study,-combine-the-members) [Stage 2 — A5: attention-pooling folds at 45%](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Stage-2-%E2%80%94-A5:-attention-pooling-folds-at-45%25) [Stage 3 — RadImageNet: reference, twin E10 and E13](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Stage-3-%E2%80%94-RadImageNet:-reference,-twin-E10-and-E13) [Stage 4 — CoAtNet: Raptor views, residual checkpoints, final routing](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Stage-4-%E2%80%94-CoAtNet:-Raptor-views,-residual-checkpoints,-final-routing) [Diagnostics — is the routing doing anything?](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet#Diagnostics-%E2%80%94-is-the-routing-doing-anything?)

![Profile picture for undefined](https://storage.googleapis.com/kaggle-competitions/kaggle/154281/logos/thumb76_76.png?GoogleAccessId=web-data@kaggle-161607.iam.gserviceaccount.com&Expires=1790751927&Signature=WkujBz5GGOVEoi2vFNHJ6YFU%2Bw2PIwnXn4bxi%2F0c%2BNGdMGsDH9XyqCptPm6AEHs18MkNTx0NlEKwB4K086jNKkuI%2FwOLA9SBHnzVUvS9YBP9brPsE246s%2BPks2EirE86QBQr0w%2FRm%2BhUCyBUEon8F4DJPWmgBLw3YuFWtPNnGXXsi1fkAiqT7Q%2BZnsgzXfPNQ7NwA7oZeKTbnYWN5dbSYd%2FGBGQpAovR3W4jeVaDpucliIx74g25P5Bnnt%2F%2FrYVKilMXte85wn3F4XoyOjkyncPQR3mCDfKbkxyxDVlBIQPA%2BurwUK5VhL531C66HXEP2XC5LOTKcfuo%2BDT38rjOAg%3D%3D&t=2026-07-14-02-42-13)

Competition Notebook

[RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)

Best Score

[0.941 V3](https://www.kaggle.com/code/beraterolelk/0-941-sota-rsna-knee-dinov2-radimagenet?scriptVersionId=349998619)

\_\_notebook\_\_

Loading \[MathJax\]/extensions/Safe.js

linkcode

🩻 Verified Public AUC: 0.941 SOTA🏆 DinoV2 + RadImageNet + Meniscus

Curated by [Berat Erol ÇELİK (@beraterolelk)](https://www.kaggle.com/beraterolelk)

# 🩻 \[0.941 SOTA\] RSNA Knee: DinoV2 Small + RadImageNet ResNet50 + Meniscus Specialist

Multi-modal knee MRI abnormality detection pipeline evaluating 12 binary findings. Combines self-supervised vision features from DINOv2 with medical embeddings from RadImageNet and specialized residual attention blocks.


[⚡ \[0.94650\] EV Purchase GM Ensemble](https://www.kaggle.com/code/beraterolelk/lb-0-94650-ev-purchase-gm-ensemble) [🔬 \[0.947 LB\] BioHub DeepCenter Tracker](https://www.kaggle.com/code/beraterolelk/0-947-lb-biohub-deepcenter-ilp-tracker) [📦 ARC-AGI 5000 Tasks](https://www.kaggle.com/datasets/beraterolelk/arc-agi-5000-synthetic-reasoning-tasks)

**🩻 Open Medical AI & Grandmaster Resources:**
Accelerate your computer vision and machine learning pipelines with our curated open benchmark assets:


- ⭐ [Kaggle Grandmaster Winning Solutions (2015-2026)](https://www.kaggle.com/datasets/beraterolelk/kaggle-grandmaster-winning-solutions-2015-2026) — 650+ winning solution architectures breakdown.
- ⭐ [50+ Winning Feature Engineering Recipes](https://www.kaggle.com/datasets/beraterolelk/kaggle-tabular-winning-feature-engineering-recipes) — Feature transforms from top Kaggle competitions.
- ⭐ [Kaggle Grandmaster Tabular Hyperparameter Zoo](https://www.kaggle.com/datasets/beraterolelk/kaggle-grandmaster-tabular-hyperparameters-zoo) — 48+ Optuna tuned configurations for GBDTs.

_If this 0.941 SOTA DinoV2 pipeline helps your RSNA research, please leave an upvote ⭐!_

linkcode

# Bend the Knee to the Dinosaurs [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Bend-the-Knee-to-the-Dinosaurs)

Inference-only submission.

## Credits [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Credits)

[Pilkwang](https://www.kaggle.com/datasets/pilkwang/rsna-knee-weights) · Sofia Anjenje · Antoine G. · prvsiyan · Marwan Mahmoud · dreaddevelopment / Roman Tamrazov · [renta0426](https://www.kaggle.com/code/renta0426/rsna-knee-0-937-weak-label-dinov2-meniscus-resid) · [Anvith Pothula](https://www.kaggle.com/code/anvithpothula/rsna-base)

linkcode

# Bend the knee to the dinosaurs — a knee MRI ensemble, taken apart [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Bend-the-knee-to-the-dinosaurs-%E2%80%94-a-knee-MRI-ensemble,-taken-apart)

**Public score 0.941.** Same weights, same arithmetic, same attribution as the
release it is built from. What changed is that you can now read it.

## What the score rewards, and why it shapes everything below [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#What-the-score-rewards,-and-why-it-shapes-everything-below)

Macro ROC-AUC over twelve binary findings. Two consequences worth carrying
through the whole notebook:

- **Only ordering counts, per column.** Any monotone transform is free and
invisible. Several appear below and none of them changes a score by itself —
they matter only where they feed a blend.
- **Ties are expensive.** A study nobody could score gets a constant, and a
block of identical constants earns half credit against every study it ties
with. The EDA section measures how close this data comes to that failure.
- **Every finding counts equally.** A finding positive in 4% of studies is
worth exactly as much as one positive in 40%.

## The pipeline [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#The-pipeline)

| Stage | Model | Contribution |
| --- | --- | --- |
| 1 | DINOv2/v3 slot attention, multi-member | base ordering |
| 2 | A5 attention-pooling folds | 45% against stage 1 |
| 3 | RadImageNet ResNet-50 + heads, twin E10 / E13 / E11 layouts | 0.50 reference, 0.15 second pass, 0.40 calibrator |
| 4 | CoAtNet: four Raptor views, plus private resgated e4/e6/e8 at 0.40 | 0.60–1.00 of the final blend, per finding |

Stage 1 also ships a hand-written multilingual report extractor. It only runs
when the released weight package is absent, so in a normal Kaggle run it is
inert — but it is the most interesting code in the notebook, because it is what
produced most of the labels these weights were fitted on.

## What changed in this build [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#What-changed-in-this-build)

**One config cell.** Eleven fusion weights, previously scattered across four
stages as literals — one of them written `0.40000000000000002`, another
duplicated into an assertion 40 lines later — now live in a single `RUN` dict.
The stages read from it, and the drift guards still fire if code and config
disagree.

**An EDA section.** Four cells on what a study contains, how the twelve
findings are distributed and co-occur, what the underlying reports look like
(including which languages a monolingual extractor would silently drop), and
why every crop in this pipeline is measured in millimetres rather than pixels.

**Diagnostics at the end.** Per finding: how much the two arms actually
disagree, and how large the biggest tie block is. Together they say whether the
outer weights are doing anything at all.

**Three presets.**`probe22` is the 0.941 submission. `parent` is the flat 0.60
routing it came from (0.939). `halfway` sits between them. The config cell
explains the trade.

linkcode

## 0\. Run configuration [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#0.-Run-configuration)

In \[1\]:

linkcode

```
# =============================== RUN CONFIG =================================
# Every fusion weight in this pipeline, in one place. Defaults reproduce the
# 0.941 submission ("probe #22") exactly.
#
# Read the outer weights below before you change anything. They are the whole
# story of this notebook's score.
import os

PRESET = os.environ.get("RSNA_PRESET", "probe22")

RUN = {
    "a5_w": 0.45,                 # A5 folds against the DINO base
    "rad_alpha": 0.50,
    "rad_e13_member_w": 0.50,
    "rad_second_alpha": 0.15,
    "rad_twin_alt_w": 0.500001,
    "rad_cal_w": 0.40,
    "coat_private_alpha": 0.40,   # private resgated e4/e6/e8 inside the Raptor arm

    # Outer weight given to the CoAtNet/Raptor arm against the transformer
    # stack (DINO + A5 + RadImageNet), per finding.
    #
    # The parent scored 0.939 with 0.60 across the board. Probe #22 raised five
    # findings, and put Lateral Meniscus at 1.00 — meaning three of the four
    # stages are discarded entirely for that column. That bought +0.002 on the
    # public split.
    #
    # "probe22"  - as submitted (0.941 public)
    # "parent"   - the flat 0.60 routing the probes started from (0.939 public)
    # "halfway"  - the probe weights pulled halfway back to 0.60
    "coatnet_w": {"__default__": 0.60, "ACL": 0.75, "Medial Meniscus": 0.80,
                  "Lateral Meniscus": 1.00, "Lateral OA": 0.75, "Fracture": 0.75},

    # Relative weights of the Raptor views inside the CoAtNet arm.
    "raptor_view_w": {"maxspan-v5": 0.55, "native384dense-v10": 0.10,
                      "maxspan-v5-reverse": 0.15, "native384-v8": 0.20},

    # Horizontal-flip TTA on the RadImageNet second pass (the E11 slot layout).
    #
    # The cache is already laterality-normalised - every right knee has been
    # flipped so that all knees present as left. Mirroring a second time is
    # therefore NOT a neutral augmentation: for coronal and axial slots the
    # image width IS the medial-lateral axis, so the flipped view puts the
    # medial compartment where the lateral one belongs. For sagittal slots
    # width is anterior-posterior, so a flip is harmless there.
    #
    #   "off"       - no flip pass (default; reproduces 0.941)
    #   "sagittal"  - flip only the sagittal slots, leave coronal/axial alone
    #   "all"       - flip every slot, as the public top notebook does
    "rad_flip_tta": "off",
    # Findings allowed to take the flipped vote. The four medial/lateral
    # findings are excluded by default because a mirrored coronal slot is
    # actively misleading about which compartment is which.
    "rad_flip_findings": ["ACL", "MCL", "PF OA", "Effusion", "Synovitis",\
                          "Baker's", "Contusion", "Fracture"],

    # Optional fifth view: the v8 checkpoint read back to front. It shares a
    # volume recipe with native384-v8, and after the arm grouping below that
    # means it costs GPU passes only - not one more decode of every study.
    # None leaves it off; 0.10 is a sane first try.
    "raptor_extra_arm_w": None,
}

_PROBE22 = dict(RUN["coatnet_w"])
if PRESET == "parent":
    RUN["coatnet_w"] = {"__default__": 0.60}
elif PRESET == "halfway":
    RUN["coatnet_w"] = {name: (0.60 + weight) / 2 if name != "__default__" else 0.60
                        for name, weight in _PROBE22.items()}
elif PRESET == "probe22+v8rev":
    RUN["raptor_extra_arm_w"] = 0.10
elif PRESET == "probe22+flip":
    # Sagittal-only flip, side-agnostic findings only.
    RUN["rad_flip_tta"] = "sagittal"
elif PRESET == "probe22+flipall":
    # What the public top notebook does: flip everything, apply to all twelve.
    RUN["rad_flip_tta"] = "all"
    RUN["rad_flip_findings"] = list(RUN["coatnet_w"]) and [\
        "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",\
        "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",\
        "Contusion", "Fracture"]
elif PRESET != "probe22":
    raise RuntimeError(f"unknown RSNA_PRESET {PRESET!r}; use probe22, parent, halfway, "
                       f"probe22+v8rev, probe22+flip or probe22+flipall")

def coat_w(label):
    return float(RUN["coatnet_w"].get(label, RUN["coatnet_w"]["__default__"]))

print(f"[config] preset={PRESET} private_alpha={RUN['coat_private_alpha']}", flush=True)
print("[config] outer CoAtNet weight per finding:",
      {k: v for k, v in RUN["coatnet_w"].items() if k != "__default__"} or "flat 0.60",
      flush=True)
```

```
[config] preset=probe22 private_alpha=0.4
[config] outer CoAtNet weight per finding: {'ACL': 0.75, 'Medial Meniscus': 0.8, 'Lateral Meniscus': 1.0, 'Lateral OA': 0.75, 'Fracture': 0.75}
```

linkcode

## Exploratory analysis [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Exploratory-analysis)

Read-only, a couple of minutes, no effect on the submission. Skip to stage 1 if you only want the pipeline.

In \[2\]:

linkcode

```
# ============================ EDA — setup ==================================
# Everything below is read-only and runs in a couple of minutes. It exists to
# answer three questions before any model runs:
#   what is actually in a study, how are the findings distributed, and what do
#   the reports look like — because the labels behind every weight here were
#   read out of those reports.
import warnings
from pathlib import Path as _EdaPath

import matplotlib.pyplot as plt
import numpy as _eda_np
import pandas as _eda_pd

warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.size": 9})
_EDA_INK = "#2f6f9f"
_EDA_WARM = "#c8622d"

_EDA_ROOT = next((p for p in (
    _EdaPath("/kaggle/input/competitions/rsna-knee-abnormality-detection"),
    _EdaPath("/kaggle/input/rsna-knee-abnormality-detection"))
    if (p / "test.csv").is_file()), None)

_EDA_TARGETS = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",\
                "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",\
                "Contusion", "Fracture"]

if _EDA_ROOT is None:
    print("[eda] competition data not attached; skipping", flush=True)
    _EDA_TRAIN = _EDA_TRAIN_SERIES = _EDA_TEST_SERIES = None
else:
    _EDA_TRAIN = _eda_pd.read_csv(_EDA_ROOT / "train.csv", dtype={"StudyInstanceUID": str})
    _EDA_TRAIN_SERIES = _eda_pd.read_csv(_EDA_ROOT / "train_series.csv",
                                         dtype={"StudyInstanceUID": str,
                                                "SeriesInstanceUID": str})
    _EDA_TEST_SERIES = _eda_pd.read_csv(_EDA_ROOT / "test_series.csv",
                                        dtype={"StudyInstanceUID": str,
                                               "SeriesInstanceUID": str})
    _eda_gold = _EDA_TRAIN.dropna(subset=[c for c in _EDA_TARGETS\
                                          if c in _EDA_TRAIN.columns])
    print(f"[eda] {len(_EDA_TRAIN):,} training studies, "
          f"{len(_EDA_TRAIN_SERIES):,} training series, "
          f"{len(_EDA_TEST_SERIES):,} test series", flush=True)
    print(f"[eda] {len(_eda_gold):,} studies carry all twelve labels; the rest are "
          f"supervised only by what a text model read out of the report", flush=True)
```

```
[eda] 4,407 training studies, 24,371 training series, 15 test series
[eda] 58 studies carry all twelve labels; the rest are supervised only by what a text model read out of the report
```

In \[3\]:

linkcode

```
# ==================== EDA 1 — what is inside a study =======================
# A study is a bag of series, and no two bags match. Everything downstream —
# the whole "slot" idea — exists to turn that variable bag into a fixed tensor.
if _EDA_TRAIN_SERIES is not None:
    frame = _EDA_TRAIN_SERIES
    per_study = frame.groupby("StudyInstanceUID").size()
    planes = frame["Anatomical_Plane"].value_counts()
    combos = (frame.assign(
        combo=frame["Anatomical_Plane"].astype(str) + " / " +
              _eda_np.where(frame.get("Fat_Suppression", 0) > 0, "fat-sat", "no fat-sat"))
        ["combo"].value_counts())

    figure, axes = plt.subplots(1, 3, figsize=(13, 3.4))
    axes[0].hist(per_study, bins=range(int(per_study.min()), int(per_study.max()) + 2),
                 color=_EDA_INK)
    axes[0].set_title(f"Series per study (median {per_study.median():.0f})")
    axes[0].set_xlabel("series")
    axes[1].bar(planes.index.astype(str), planes.values, color=_EDA_INK)
    axes[1].set_title("Acquisition plane")
    axes[2].barh(combos.index[::-1], combos.values[::-1], color=_EDA_INK)
    axes[2].set_title("Plane x fat suppression")
    plt.tight_layout()
    plt.show()

    print("Coverage of the six slots the models expect, over training studies:")
    wanted = [("Sagittal", 1), ("Sagittal", 0), ("Coronal", 1),\
              ("Coronal", 0), ("Axial", 1), ("Axial", 0)]
    rows = []
    for plane, fat in wanted:
        have = frame[(frame["Anatomical_Plane"] == plane) &\
                     (frame.get("Fat_Suppression", 0) == fat)]
        rows.append({"slot": f"{plane} {'fat-sat' if fat else 'no fat-sat'}",
                     "studies with it": have["StudyInstanceUID"].nunique(),
                     "share": have["StudyInstanceUID"].nunique() /
                              frame["StudyInstanceUID"].nunique()})
    coverage = _eda_pd.DataFrame(rows)
    print(coverage.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\nA slot no study fills is a column of zeros fed to the encoder; a study "
          "that fills none of them can only be given a constant, and under ROC-AUC "
          "a block of identical constants earns half credit against everything it "
          "ties with. That is the cheapest score leak in this whole pipeline.")
```

![](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results___files/__results___7_0.png)

```
Coverage of the six slots the models expect, over training studies:
               slot  studies with it  share
   Sagittal fat-sat             4150  0.942
Sagittal no fat-sat             4266  0.968
    Coronal fat-sat             4248  0.964
 Coronal no fat-sat             3406  0.773
      Axial fat-sat             4407  1.000
   Axial no fat-sat              857  0.194

A slot no study fills is a column of zeros fed to the encoder; a study that fills none of them can only be given a constant, and under ROC-AUC a block of identical constants earns half credit against everything it ties with. That is the cheapest score leak in this whole pipeline.
```

In \[4\]:

linkcode

```
# ================== EDA 2 — the findings, and how they co-occur ============
# Twelve binary findings, scored as twelve separate AUCs and averaged. That
# framing matters: a rare finding counts exactly as much as a common one, so
# the rare columns are where a submission is won or lost.
if _EDA_TRAIN is not None and set(_EDA_TARGETS).issubset(_EDA_TRAIN.columns):
    gold = _EDA_TRAIN.dropna(subset=_EDA_TARGETS)
    if len(gold):
        prevalence = gold[_EDA_TARGETS].mean().sort_values()
        figure, axes = plt.subplots(1, 2, figsize=(13, 4.2))
        axes[0].barh(prevalence.index, prevalence.values, color=_EDA_INK)
        axes[0].set_xlabel(f"prevalence among {len(gold)} fully-labelled studies")
        axes[0].set_title("How often each finding is positive")
        for y, (name, value) in enumerate(prevalence.items()):
            axes[0].text(value + 0.005, y, f"{value:.2f}", va="center", fontsize=8)

        matrix = gold[_EDA_TARGETS].astype(float).corr()
        image = axes[1].imshow(matrix, cmap="RdBu_r", vmin=-1, vmax=1)
        axes[1].set_xticks(range(len(_EDA_TARGETS)))
        axes[1].set_xticklabels(_EDA_TARGETS, rotation=90, fontsize=7)
        axes[1].set_yticks(range(len(_EDA_TARGETS)))
        axes[1].set_yticklabels(_EDA_TARGETS, fontsize=7)
        axes[1].set_title("Co-occurrence between findings")
        axes[1].grid(False)
        figure.colorbar(image, ax=axes[1], shrink=0.8)
        plt.tight_layout()
        plt.show()

        pairs = (matrix.where(_eda_np.triu(_eda_np.ones(matrix.shape), 1).astype(bool))
                 .stack().sort_values(ascending=False))
        print("Most correlated pairs:")
        for (left, right), value in pairs.head(5).items():
            print(f"  {left:<18} + {right:<18} {value:+.2f}")
        print("\nThe three osteoarthritis compartments move together, which is why "
              "the calibrator downstream groups them. Findings that co-occur are "
              "also findings an ensemble tends to get right or wrong together — "
              "worth remembering before reading any per-finding weight as skill.")
    else:
        print("[eda] no fully-labelled studies found in train.csv", flush=True)
```

![](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results___files/__results___8_0.png)

```
Most correlated pairs:
  Medial OA          + Baker's            +0.48
  Medial Meniscus    + Medial OA          +0.42
  Lateral Meniscus   + Lateral OA         +0.42
  Lateral Meniscus   + Medial OA          +0.41
  Lateral OA         + Baker's            +0.40

The three osteoarthritis compartments move together, which is why the calibrator downstream groups them. Findings that co-occur are also findings an ensemble tends to get right or wrong together — worth remembering before reading any per-finding weight as skill.
```

In \[5\]:

linkcode

```
# ==================== EDA 3 — the reports behind the labels ================
# Almost every label used to fit these weights was read out of a free-text
# report by a text model. This notebook ships a hand-written multilingual
# extractor for exactly that job, so it is worth seeing what it is reading.
if _EDA_TRAIN is not None and "Report" in _EDA_TRAIN.columns:
    reports = _EDA_TRAIN["Report"].fillna("").astype(str)
    words = reports.str.split().str.len()

    # Cheap language fingerprints, using stems the extractor itself keys on.
    probes = {
        "English": r"\btear\b|\bmeniscus\b|\beffusion\b",
        "Spanish/Portuguese": r"\brotura\b|\bmenisco\b|\bderrame\b",
        "Italian": r"\blesione\b|\bmenisco\b|\bversamento\b",
        "French": r"\bd.chirure\b|\bm.nisque\b|\b.panchement\b",
        "German": r"\briss\b|\bmeniskus\b|\berguss\b",
        "Turkish": r"\byirtik\b|\bmenisk.s\b|\befuzyon\b",
    }
    lowered = reports.str.lower()
    hits = {name: int(lowered.str.contains(pattern, regex=True, na=False).sum())
            for name, pattern in probes.items()}

    figure, axes = plt.subplots(1, 2, figsize=(13, 3.6))
    axes[0].hist(words[words < words.quantile(0.99)], bins=60, color=_EDA_INK)
    axes[0].set_title(f"Report length (median {words.median():.0f} words)")
    axes[0].set_xlabel("words")
    order = sorted(hits, key=hits.get, reverse=True)
    axes[1].bar(order, [hits[k] for k in order], color=_EDA_WARM)
    axes[1].set_title("Reports matching each language's finding vocabulary")
    axes[1].tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.show()

    empty = int((words == 0).sum())
    print(f"{empty:,} studies have no report at all "
          f"({empty / max(len(reports), 1):.1%}) — those can only be supervised by "
          f"the images.")
    print("The counts overlap because clinical vocabulary is shared across "
          "languages; they are a rough shape, not a classifier. The point is that "
          "a monolingual extractor silently drops whole slices of the training set, "
          "and a dropped study is not a wrong label — it is no label.")
```

![](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results___files/__results___9_0.png)

```
0 studies have no report at all (0.0%) — those can only be supervised by the images.
The counts overlap because clinical vocabulary is shared across languages; they are a rough shape, not a classifier. The point is that a monolingual extractor silently drops whole slices of the training set, and a dropped study is not a wrong label — it is no label.
```

In \[6\]:

linkcode

```
# ============= EDA 4 — geometry, and why the crop is in millimetres ========
# Pixel spacing varies across scanners, so a fixed pixel crop would show a
# different amount of knee per study. Every stage here crops in millimetres
# instead. This is what that variation looks like.
import pydicom as _eda_dicom

if _EDA_ROOT is not None:
    series_root = (_EDA_ROOT / "test_series" if (_EDA_ROOT / "test_series").is_dir()
                   else _EDA_ROOT / "train_series")
    spacings, rows_cols, sampled = [], [], 0
    for study_dir in sorted(series_root.iterdir())[:120]:
        if not study_dir.is_dir():
            continue
        for series_dir in sorted(study_dir.iterdir()):
            files = sorted(series_dir.glob("*.dcm"))
            if not files:
                continue
            try:
                header = _eda_dicom.dcmread(str(files[len(files) // 2]),
                                            stop_before_pixels=True, force=True)
                spacings.append(float(header.PixelSpacing[0]))
                rows_cols.append((int(header.Rows), int(header.Columns)))
                sampled += 1
            except Exception:
                continue
        if sampled > 400:
            break

    if spacings:
        spacings = _eda_np.array(spacings)
        figure, axes = plt.subplots(1, 2, figsize=(13, 3.6))
        axes[0].hist(spacings, bins=50, color=_EDA_INK)
        axes[0].set_title(f"In-plane pixel spacing over {sampled} series")
        axes[0].set_xlabel("mm per pixel")
        sizes = _eda_pd.Series([f"{r}x{c}" for r, c in rows_cols]).value_counts().head(8)
        axes[1].barh(sizes.index[::-1], sizes.values[::-1], color=_EDA_INK)
        axes[1].set_title("Most common matrix sizes")
        plt.tight_layout()
        plt.show()

        crop_mm = 140.0
        pixels = crop_mm / spacings
        print(f"A {crop_mm:.0f} mm crop spans {pixels.min():.0f} to {pixels.max():.0f} "
              f"pixels across these series — a {pixels.max() / pixels.min():.1f}x range. "
              f"Cropping a fixed number of pixels instead would hand the model a "
              f"different anatomical field of view per scanner, which is the kind of "
              f"artefact a model will happily learn to read as signal.")
```

![](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results___files/__results___10_0.png)

```
A 140 mm crop spans 398 to 896 pixels across these series — a 2.3x range. Cropping a fixed number of pixels instead would hand the model a different anatomical field of view per scanner, which is the kind of artefact a model will happily learn to read as signal.
```

linkcode

### EDA 6 — scanners and sites [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#EDA-6-%E2%80%94-scanners-and-sites)

In \[7\]:

linkcode

```
# ============== EDA 6 — scanners, sites, and the leak in the folds =========
# MRI intensity is not calibrated. A scanner leaves a fingerprint, and a model
# given random folds will happily learn to recognise the scanner instead of the
# knee. That inflates any offline score and none of it survives a private split
# drawn from different sites.
import pydicom as _site_dicom

if _EDA_ROOT is not None:
    root = (_EDA_ROOT / "train_series" if (_EDA_ROOT / "train_series").is_dir()
            else _EDA_ROOT / "test_series")
    makers, models, fields, sampled = [], [], [], 0
    for study_dir in sorted(root.iterdir())[:250]:
        if not study_dir.is_dir():
            continue
        series_dirs = [d for d in sorted(study_dir.iterdir()) if d.is_dir()]
        if not series_dirs:
            continue
        files = sorted(series_dirs[0].glob("*.dcm"))
        if not files:
            continue
        try:
            header = _site_dicom.dcmread(str(files[len(files) // 2]),
                                         stop_before_pixels=True, force=True)
        except Exception:
            continue
        makers.append(str(getattr(header, "Manufacturer", "unknown")).strip() or "unknown")
        models.append(str(getattr(header, "ManufacturerModelName", "unknown")).strip()
                      or "unknown")
        try:
            fields.append(float(getattr(header, "MagneticFieldStrength", 0) or 0))
        except Exception:
            fields.append(0.0)
        sampled += 1

    if sampled:
        maker_counts = _eda_pd.Series(makers).value_counts()
        model_counts = _eda_pd.Series(models).value_counts().head(10)
        figure, axes = plt.subplots(1, 2, figsize=(13, 3.8))
        axes[0].barh(maker_counts.index[::-1], maker_counts.values[::-1], color=_EDA_INK)
        axes[0].set_title(f"Manufacturer over {sampled} sampled studies")
        axes[1].barh(model_counts.index[::-1], model_counts.values[::-1], color=_EDA_WARM)
        axes[1].set_title("Scanner model (top 10)")
        axes[1].tick_params(axis="y", labelsize=7)
        plt.tight_layout()
        plt.show()

        field_counts = _eda_pd.Series([f for f in fields if f > 0]).value_counts()
        print("Field strengths present:",
              ", ".join(f"{value:.1f}T x{count}" for value, count in field_counts.items()))
        top = model_counts.iloc[0] / sampled
        print(f"The single most common scanner model covers {top:.0%} of the sample.")
        print("\nThe training path in this notebook groups folds by md5(report text), "
              "which deduplicates identical reports but does nothing about the "
              "scanner. Manufacturer + model + matrix size + pixel spacing is a "
              "serviceable site key and costs nothing to compute from headers you "
              "are already reading. Grouping on it is what makes an offline number "
              "mean something.")
```

![](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results___files/__results___12_0.png)

```
Field strengths present: 1.5T x144, 3.0T x90, 1.2T x2
The single most common scanner model covers 23% of the sample.

The training path in this notebook groups folds by md5(report text), which deduplicates identical reports but does nothing about the scanner. Manufacturer + model + matrix size + pixel spacing is a serviceable site key and costs nothing to compute from headers you are already reading. Grouping on it is what makes an offline number mean something.
```

linkcode

### EDA 7 — series depth against what the sampler asks for [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#EDA-7-%E2%80%94-series-depth-against-what-the-sampler-asks-for)

In \[8\]:

linkcode

```
# =============== EDA 7 — how much of each series the model actually sees ====
# The CoAtNet arm asks for a fixed number of slices per slot (18 sagittal
# fat-sat, 14 sagittal, 12 coronal fat-sat, 8 coronal, 12 axial) and then
# samples 62 three-slice windows from the 64-slice stack. Whether that is
# generous or lossy depends on how long the series actually are.
if _EDA_TRAIN_SERIES is not None and "n_slices" in dir():
    pass

if _EDA_ROOT is not None:
    root = (_EDA_ROOT / "test_series" if (_EDA_ROOT / "test_series").is_dir()
            else _EDA_ROOT / "train_series")
    lengths = []
    for study_dir in sorted(root.iterdir())[:200]:
        if not study_dir.is_dir():
            continue
        for series_dir in sorted(study_dir.iterdir()):
            if series_dir.is_dir():
                lengths.append((series_dir.parent.name, series_dir.name,
                                len(list(series_dir.glob("*.dcm")))))
    if lengths:
        counts = _eda_np.array([n for _, _, n in lengths])
        asks = {"Sagittal fat-sat": 18, "Sagittal": 14, "Coronal fat-sat": 12,
                "Coronal": 8, "Axial": 12}
        figure, axes = plt.subplots(1, 2, figsize=(13, 3.6))
        axes[0].hist(counts[counts < _eda_np.percentile(counts, 99)], bins=50,
                     color=_EDA_INK)
        for name, ask in asks.items():
            axes[0].axvline(ask, color=_EDA_WARM, linestyle="--", linewidth=0.8)
        axes[0].set_title("Slices per series (dashed = what a slot asks for)")
        axes[0].set_xlabel("slices")

        shares = [(counts >= ask).mean() for ask in asks.values()]
        axes[1].bar(list(asks), shares, color=_EDA_INK)
        axes[1].set_ylim(0, 1)
        axes[1].set_title("Share of series long enough to fill their slot")
        axes[1].tick_params(axis="x", rotation=20)
        plt.tight_layout()
        plt.show()

        print(f"Median series length {_eda_np.median(counts):.0f} slices; "
              f"{(counts < 12).mean():.1%} are shorter than twelve.")
        print("Where a series is shorter than its slot, the sampler repeats "
              "slices, so several of the 62 windows are duplicates and the "
              "attention pooling sees the same evidence more than once. Where a "
              "series is much longer, the sampler is skipping anatomy — and a "
              "meniscus tear visible on two slices can fall between samples "
              "entirely. That is the mechanism behind the max and top-2 window "
              "pooling used for the focal findings upstream.")
```

![](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results___files/__results___14_0.png)

```
Median series length 30 slices; 0.0% are shorter than twelve.
Where a series is shorter than its slot, the sampler repeats slices, so several of the 62 windows are duplicates and the attention pooling sees the same evidence more than once. Where a series is much longer, the sampler is skipping anatomy — and a meniscus tear visible on two slices can fall between samples entirely. That is the mechanism behind the max and top-2 window pooling used for the focal findings upstream.
```

linkcode

## Stage 1 — the report extractor [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Stage-1-%E2%80%94-the-report-extractor)

Inert when the weight package is attached. Included because it is what labelled the training data: sentence splitting, negation and laterality windows, and finding vocabulary across several languages.

In \[9\]:

linkcode

```
from __future__ import annotations
import re
import unicodedata
TARGETS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
_PRE = str.maketrans({'ı': 'i', 'İ': 'i', 'I': 'i', 'ß': 'ss', 'đ': 'd', 'Đ': 'd', 'ø': 'o', 'Ø': 'o', 'æ': 'ae', 'Æ': 'ae'})

def normalize(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = text.translate(_PRE).lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join((ch for ch in text if not unicodedata.combining(ch)))
    text = text.replace('\xad', '')
    text = re.sub('[_\\-/\\\\]+', ' ', text)
    text = re.sub('[ \\t]+', ' ', text)
    return text
_SENT_SPLIT = re.compile('(?<=[.;!?])\\s+|\\n+')

def unwrap(text: str) -> str:
    if not isinstance(text, str):
        return ''
    out = []
    for line in text.split('\n'):
        s = line.strip()
        if out and out[-1] and (not re.search('[.;:!?>*•]$', out[-1])) and (len(out[-1].split()) >= 4) and s and (not s[:1].isupper()):
            out[-1] = out[-1] + ' ' + s
        else:
            out.append(s)
    return '\n'.join(out)

def clauses(text: str):
    norm = normalize(unwrap(text) if FEATURES['unwrap'] else text)
    raw = [c.strip() for c in _SENT_SPLIT.split(norm) if c and c.strip()]
    merged = []
    for i, c in enumerate(raw):
        if c.endswith(':') and len(c.split()) <= 14 and (i + 1 < len(raw)):
            merged.append(c + ' ' + raw[i + 1])
        merged.append(c)
    out = []
    for c in merged:
        out.append(c)
        if len(c.split()) > 25:
            out.extend((p.strip() for p in c.split(',') if len(p.split()) > 2))
    return out
FEATURES = {'unwrap': True, 'directional_negation': True, 'oa_inherit': True, 'graded_pathology': True, 'synovitis_backoff': True}

def _rx(*alts: str) -> re.Pattern:
    return re.compile('|'.join(alts))
PRE_NEG = _rx('\\bno\\b', '\\bnot\\b', '\\bwithout\\b', '\\bnegative for\\b', '\\babsence\\b', '\\bno evidence\\b', '\\bfree of\\b', '\\bnone\\b', '\\bneither\\b', '\\bnor\\b', '\\bsin\\b', '\\bno hay\\b', '\\bausencia\\b', '\\bausentes?\\b', '\\bno se\\b', '\\bpas de\\b', '\\bsans\\b', '\\baucune?\\b', '\\bgeen\\b', '\\bzonder\\b', '\\bniet\\b', '\\bkeine?[nmrs]?\\b', '\\bohne\\b', '\\bnicht\\b', '\\bkein\\b', '\\bnema\\b', '\\bbez\\b', '\\bnisu\\b', '\\bnije\\b', '\\bδεν\\b', '\\bχωρις\\b', 'ουδεν', '\\bουτε\\b', '\\bбез\\b', '\\bне\\b', 'липсва', '\\bняма\\b')
POST_NEG = _rx('\\byok\\b', '\\byoktur\\b', 'izlenmemekte', 'saptanmadi', '\\bdegil\\b', 'gozlenmemekte', 'mevcut degil', 'eslik etmiyor', '\\bizlenmedi\\b', 'izlenmemistir', 'saptanmamistir', 'gorulmemistir', '\\bnema znakova\\b', 'bez znakova')
NEGATION = _rx(PRE_NEG.pattern, POST_NEG.pattern, '\\bunremarkable\\b')
NEG_WINDOW = 90

def _negated(clause: str, start: int, end: int) -> bool:
    for m in PRE_NEG.finditer(clause):
        if m.end() <= start and start - m.end() <= NEG_WINDOW:
            if not re.search('\\b(but|however|ancak|fakat|pero|maar|aber|no i|ali|ωστοσο|αλλα|но)\\b', clause[m.end():start]):
                return True
    for m in POST_NEG.finditer(clause):
        if m.start() >= end and m.start() - end <= NEG_WINDOW:
            return True
    return False
NORMALITY = _rx('\\bnormal', '\\bintact\\b', '\\bpreserved\\b', '\\bwithin normal limits\\b', 'limites normales', '\\bconservad', '\\bintegr', '\\bnormales\\b', '\\bdoga(l|ll)\\b', 'korunmus', '\\bnormaldir\\b', 'olagan', '\\buredn', '\\bocuvan', '\\bodrzan', '\\bintakt', '\\bprimjeren', '\\bodrzanog kontinuiteta', '\\bodržan', 'φυσιολογικ', 'ακεραι', 'δεν παρατηρουνται', 'δεν σημειωνονται', 'unauffallig', 'regelrecht', '\\bo\\.?b\\.?\\b', 'нормал', 'запазен', 'съхранен', '\\bбез особености\\b', 'интактн', '\\bgaaf\\b', '\\bnormaal\\b')
NORMAL_PHRASE = _rx('\\bsin alteracion', '\\bsin cambios\\b', '\\bsin particularidad', '\\bsin hallazgos\\b', '\\bsin lesion', '\\bsin signos de (rotura|lesion)', '\\bcontinu[oa]s?\\b', '\\bcontinuidad conservada\\b', '\\bno abnormalit', '\\bno significant abnormalit', '\\bunremarkable\\b', '\\bno evidence of (tear|injury|abnormalit)', '\\bohne auffalligkeit', '\\bkein nachweis\\b', '\\bohne befund\\b', '\\bgeen afwijking', '\\bzonder afwijking', '\\bsans anomalie', "\\bpas d[e']anomalie", '\\bbez osobitosti\\b', '\\bbez znakova (rupture|lezije)\\b', '\\bbez patoloskih\\b', 'χωρις αλλοιωσ', 'χωρις παθολογ', 'δεν παρατηρουνται (αξιολογα|παθολογ)', '\\bбез особености\\b', '\\bбез патологич', '\\bбез данни за\\b', '\\bozel bir ozellik yok', '\\bpatolojik bulgu (yok|izlenmemis)')
UNCERTAIN = _rx('\\bpossible\\b', '\\bprobable\\b', '\\bsuspicious\\b', '\\bsuspected?\\b', 'cannot (be )?exclude', '\\bmay\\b', '\\bquestionable\\b', '\\bequivocal\\b', '\\br/o\\b', '\\bdd\\b', '\\blikely\\b', '\\bsuggest', '\\bcompatible with\\b', '\\bposible\\b', 'sin criterios categoricos', '\\bdudos', '\\bsugier', '\\bmuhtemel\\b', '\\bolasi\\b', '\\bsupheli\\b', '\\bizlenim', '\\bdusundur', '\\bmoguce\\b', '\\bvjerojatno\\b', '\\bsumnja\\b', '\\bmoze odgovarati\\b', 'πιθαν', 'υποπτ', '\\bmoglich', '\\bverdachtig', '\\bfraglich', '\\bv\\.?a\\.?\\b', '\\bwohl\\b', '\\bвъзможно\\b', '\\bвероятно\\b', 'суспект', '\\bmogelijk\\b', '\\bverdacht\\b')
```

In \[10\]:

linkcode

```
TEAR = _rx('\\btear', '\\btorn\\b', '\\brupture', '\\bdisruption\\b', 'discontinuit', '\\bavuls', '\\bmacerat', '\\bbuckethandle\\b', 'bucket handle', '\\brotura\\b', '\\broturas\\b', '\\bruptura', '\\bdesgarro', '\\broto\\b', '\\bdechirure', '\\bdechire', '\\bscheur', '\\bruptuur', 'gescheurd', '\\briss\\b', 'einriss', '\\bruptur', 'zerreiss', '\\blasion', '\\bausriss', '\\byirtik', '\\byirtig', '\\bkopma\\b', 'butunluk kaybi', '\\brupturu\\b', 'devamsizlik', '\\brupture\\b', '\\bdevamliligi secilememis', '\\bpuknuce', '\\bprekid\\b', '\\bpukotin', '\\bruptur', 'ρηξη', 'ρηξις', 'ρηγμα', 'ασυνεχεια', 'руптура', 'разкъсв', 'разрив', 'скъсв', '\\bлезия\\b')
DEGEN = _rx('degenerat', '\\bmucoid\\b', '\\bmyxoid\\b', '\\bfray', '\\bfissur', 'dejeneratif', '\\bmukoid\\b', 'degenerativn', 'εκφυλ', 'дегенерат', '\\bμυξοειδ', '\\bμυξωδ', '\\bmeniskopat', '\\bmeniscopath', '\\bmuco ?ide\\b', 'aufgefasert', '\\bdejenerasyon\\b')
INJURY = _rx('\\binjur', '\\bsprain', '\\blesion', '\\blasion', '\\bedema\\b', '\\boedema\\b', '\\bodem\\b', '\\bedem\\b', '\\bοιδημα', '\\bодем', '\\bедем', '\\bstrain\\b', '\\bhigh signal\\b', '\\bsignal alteration\\b', '\\bhiperintens', '\\bhyperintens', 'aumento de senal', 'alteracion de senal', 'cambio de senal', '\\bsignalanhebung', '\\bsignalalteration', 'verhoogd signaal', 'sinyal artis', 'αυξημενο σημα', 'повишен сигнал', '\\besguince\\b', '\\bthicken', '\\bzadebljanje\\b', '\\bverdikking\\b', '\\bdistenzij', '\\blaksite\\b', '\\blaxity\\b', '\\bpartial\\b', '\\bparcijaln', '\\bparcial', '\\bpartiel', '\\bpartiell')
_GRADE_RX = re.compile('(?:grade|grad|grado|grau|derece|stupnja|stupanj|βαθμ|степен|icrs|outerbridge)[\\s:]*(?:grade\\s*)?([1-4]|iv|iii|ii|i)\\b')
_ROMAN = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4}

def _grade_of(clause: str):
    best = None
    for m in _GRADE_RX.finditer(clause):
        v = m.group(1)
        n = _ROMAN.get(v, None) if not v.isdigit() else int(v)
        if n is not None and (best is None or n > best):
            best = n
    return best
ANAT = {'ACL': _rx('anterior cruciate', '\\bacl\\b', 'cruzado anterior', '\\blca\\b', 'croise anterieur', 'voorste kruisband', '\\bvkb\\b', 'vorderes kreuzband', 'vorderen kreuzband', 'vordere kreuzband', 'on capraz', '\\bocb\\b', 'anterior capraz', 'prednji krizni', 'prednjeg krizn', 'προσθι[οα][^ ]* χιαστ', 'προσθιου χιαστου', 'χιαστο[^ ]* συνδεσμ', '\\bχιαστ\\w*', 'предна кръстна', 'предната кръстна', 'предна кръста', 'cruciate ligaments', 'ligamentos cruzados', 'ligaments croises', 'kruisbanden', 'kreuzbander', 'capraz baglar', 'krizn[a-z]* ligament[a-z]*', 'χιαστοι συνδεσμ', 'χιαστων συνδεσμ', 'кръстните връзки', 'кръстни връзки'), 'MCL': _rx('medial collateral', '\\bmcl\\b', 'tibial collateral', 'colateral medial', 'colateral interno', '\\blcm\\b', 'collateral medial', 'collateral interne', 'mediale collaterale', 'binnenband', '\\b(mediale|laterale) banden\\b', '\\bcollaterale banden\\b', 'innenband', 'mediales? kollateral', '\\bic yan bag', 'medial kollateral', '\\biyb\\b', 'medyal kollateral', 'medijalni kolateraln', 'medijalnog kolateraln', 'εσω πλαγι', 'εσωτερικο πλαγι', '\\bπλαγι\\w* συνδεσμ', '\\bπλαγιοι\\b', 'медиален колатерал', 'вътрешна странична', '\\bколатерал\\w*', '\\bcolaterales\\b', '\\bcollateraux\\b', '\\bcollateralen\\b', '\\bkolateralni\\b', 'collateral ligaments', 'ligamentos colaterales', 'ligaments collateraux', 'collaterale banden', 'kollateralbander', 'seitenbander', 'yan baglar', 'kolateraln[a-z]* ligament[a-z]*', 'πλαγιοι συνδεσμ', 'πλαγιων συνδεσμ', 'колатерални връзки', 'страничните връзки'), 'Medial Meniscus': _rx('medial meniscus', '\\bmm\\b(?= tear)', 'medial menisc', 'menisco medial', 'menisco interno', 'menisque medial', 'menisque interne', 'mediale meniscus', 'binnenmeniscus', 'innenmeniskus', 'medialen? meniskus', 'innenmeniskushinterhorn', 'medyal menisk', '\\bic menisk', 'medijalni meniskus', 'medijalnog meniskusa', 'medijalnom meniskusu', 'medijaln\\w* menisk\\w*', '\\bmedijalnog meniska\\b', 'medijalni menisk', 'εσω μηνισκ', 'μηνισκ[^ ]* του εσω', 'εσω διαμερισμα[^.]{0,40}μηνισκ', 'медиалния менискус', 'медиален менискус', 'вътрешния менискус', 'oba meniska', 'both menisci', 'ambos meniscos', 'beide menisci', 'her iki menisku', 'amfoteroi\\w* mhnisk', 'αμφοτερ\\w* μηνισκ', 'двата менискуса', 'medial (and|&) lateral menisc'), 'Lateral Meniscus': _rx('lateral meniscus', 'lateral menisc', 'menisco lateral', 'menisco externo', 'menisque lateral', 'menisque externe', 'laterale meniscus', 'buitenmeniscus', 'aussenmeniskus', 'lateralen? meniskus', 'aussenmeniskushinterhorn', 'lateral menisk', '\\bdis menisk', 'lateralni meniskus', 'lateralnog meniskusa', 'lateralnom meniskusu', 'lateraln\\w* menisk\\w*', '\\blateralnog meniska\\b', 'εξω μηνισκ', 'μηνισκ[^ ]* του εξω', 'εξω διαμερισμα[^.]{0,40}μηνισκ', 'латералния менискус', 'латерален менискус', 'външния менискус', 'oba meniska', 'both menisci', 'ambos meniscos', 'beide menisci', 'her iki menisku', 'αμφοτερ\\w* μηνισκ', 'двата менискуса', 'medial (and|&) lateral menisc')}
OA_EVIDENCE = _rx('osteoarthrit', '\\barthros', '\\bgonarthros', '\\bosteoarthros', 'chondropath', 'chondromalac', 'condropat', 'condromalac', '\\bchondros', '\\bchondrosis\\b', 'chondral (loss|defect|ulcer|thinning|injury|fissur|wear)', 'cartilage (loss|thinning|defect|fissur|wear|damage|heterogeneity|irregularit)', '(loss|thinning|fissur|defect|ulcer|erosion|denudation) of[^.]{0,20}cartilage', 'articular cartilage[^.]{0,30}(loss|thin|fissur|defect|erosion|wear|irregular)', 'osteophyt', 'osteofit', 'osteofyt', 'osteofito', 'osteophyten', 'spurring', 'joint space narrowing', 'pinzamiento articular', 'reduced joint space', 'kikirdak kayb', 'kikirdak incelme', 'kondropati', 'kondral', 'kikirdak dejener', 'eklem aralig\\w* daral', 'eklem mesafesi daral', 'kikirdak kalinlig\\w* azal', 'kraakbeen', 'gonartrose', 'artrose', '\\bknorpel', 'arthrose', 'gonarthrose', 'hrskavic', 'hondromalac', 'artroz', 'osteoartrit', 'artrotsk', 'artrotick', '\\boa promjen', '\\boa\\b', 'degenerativne promjene hrskav', 'χονδρ[^ ]*παθ', 'αρθριτ', 'αρθρωσ', 'οστεοφυτ', 'χονδρομαλακ', 'αρθρικου χονδρου', 'εξαλειψη του αρθρικου χονδρου', 'διαβρωση του αρθρικου χονδρ', 'λεπτυνση[^.]{0,30}χονδρ', 'φθορα[^.]{0,20}χονδρ', 'артроз', 'хондропат', 'остеофит', 'хрущял[^.]{0,40}(изтън|увред|дефект|липс)', 'изтъняване[^.]{0,30}хрущял', 'хондромалац', 'ulcera[s]? condral', 'cartilago[^.]{0,25}(perdida|adelgaz)', 'icrs grade', 'icrs\\b', 'outerbridge', '\\bdenudation\\b', 'denudacij', 'erozivne promjene', '\\berosion of[^.]{0,20}cartilage', 'kraakbeenlijden', 'kraakbeenverlies')
TF_SITE = _rx('compartment', 'compartimento', 'compartiment', 'kompartman', 'kompartiment', 'kompartment', 'odjelj', 'διαμερισμα', 'компартм', '\\bотдел', 'femorotibial', 'tibiofemoral', 'femoro tibial', 'femorotibiaal', 'femorotibijaln', 'феморотибиал', '\\bft zglob', 'tibiofemoraln', 'condyle', 'condilo', 'kondyl', 'kondil', 'condyl', 'κονδυλ', 'кондил', '\\bplateau', '\\bplato\\b', 'platillo', 'meseta', 'плато', 'tibiaplateau', 'tibijaln\\w* plato', 'tibyal plato', 'tibia plato', 'κνημιαι', 'μηριαι', 'weightbearing', 'weightbaring', 'zona de carga', 'dragende deel', 'agirlik tasiyan', '\\bfemur\\b', '\\btibia\\b', '\\bfemoral\\b', '\\btibial\\b', '\\bfemura\\b', '\\btibije\\b', '\\bmesarthrio\\b', 'μεσαρθριο')
PF_SITE = _rx('patellofemoral', 'femoropatellar', 'femoropatelar', 'patelofemoral', 'retropatellar', 'retrorotulian', 'trochlea', 'troclea', 'troklea', 'trochlear', 'trohlej', 'τροχιλ', '\\bpatella', '\\bpatellar', 'rotulian', '\\brotula\\b', '\\bpatele\\b', 'patellofemoraal', 'femoropatellair', 'επιγονατιδ', 'μηροεπιγονατιδ', 'пател', 'феморопател', 'anterior compartment', 'compartimento anterior', 'prednj\\w* odjeljk', '\\bfp zglob', '\\bpf zglob', '\\bfaset', '\\bfacet', 'patellofemoraln')
SIDE_MEDIAL = _rx('\\bmedial\\w*', '\\bmedyal\\w*', '\\bmedijaln\\w*', '\\bmediaal\\w*', '\\bmediale\\w*', '\\binterno\\b', '\\binterna\\b', '\\binternos\\b', '\\binterne\\b', '\\binnen\\w*', '\\bic\\b', '\\bunutarnj\\w*', '\\bεσω\\w*', '\\bεσωτερικ\\w*', '\\bмедиал\\w*', '\\bвътреш\\w*', '\\bbinnen\\w*', '\\bmediaal\\b', '\\bmediales?\\b')
SIDE_LATERAL = _rx('\\blateral\\w*', '\\bexterno\\b', '\\bexterna\\b', '\\bexternos\\b', '\\bexterne\\b', '\\bdis\\b', '\\blateraln\\w*', '\\baussen\\w*', '\\bbuiten\\w*', '\\bεξω\\w*', '\\bεξωτερικ\\w*', '\\bлатерал\\w*', '\\bвъншн\\w*', '\\bvanjsk\\w*')
SIDE_ANTERIOR = _rx('\\banterior\\w*', '\\bant\\b', '\\bon\\b', '\\bprednj\\w*', '\\bvorder\\w*', '\\bvoorste\\b', '\\bπροσθι\\w*', '\\bпредн\\w*', '\\banteriyor\\w*', '\\bavant\\b', '\\banterieur\\w*')
GLOBAL_OA = _rx('tri ?compartment', 'all three compartment', 'global(ised)? (oa|osteoarthrit)', '\\bgonarthros', '\\bgonartros', '\\bgonarthrose', '\\bgonartrose', 'gonartro', 'goanrtrot', 'gonartrot', 'osteoarthritis of the knee', 'artrosis (de |)(la )?rodilla', 'knee osteoarthrit', '\\bdiz osteoartrit', '\\bgonartroz', 'artroza koljena', 'οστεοαρθριτιδα', 'αρθριτιδα του γονατος', 'εκφυλιστικη οστεοαρθριτ', 'артроза на колянната', 'гонартроз', 'degenerative joint disease', '\\bdjd\\b', 'three compartments', 'compartmens', 'compartments')
DIRECT = {'Effusion': _rx('\\beffusion', 'joint fluid', 'intra ?articular fluid', '\\bhydrops\\b', '\\bhemarthros', '\\bhaemarthros', 'derrame articular', '\\bderrame\\b', 'liquido articular', 'hemartrosis', 'epanchement', 'gewrichtsvocht', '\\bvocht\\b', 'gewrichtseffusie', 'opzetting van suprapatell', 'gelenkerguss', '\\berguss\\b', 'gelenksergu', 'gelenksflussigkeit', 'eklem\\w* ic\\w* sivi', 'efuzyon', 'eklem sivisi', 'eklem mesafesinde sivi', 'sivi (miktari|artisi|birikimi)', 'sivi artis', '\\bsivi\\b[^.]{0,25}artmis', '\\bizljev', '\\bizliv', 'zglobn[^ ]* tekucin', '\\bhidrops\\b', 'αρθρικ[^ ]* υγρ', 'υγρου ενδαρθρικα', 'ενδαρθρικ[^ ]* υγρ', 'ποσοτητα υγρου', 'ενδαρθρικ', 'αρθρικη συλλογη', 'υγρο στην αρθρωση', 'υγρου στην αρθρωση', 'συλλογη υγρου', 'ενθαρθρικ', 'ставен излив', 'излив', 'ставна течност', 'синовиална течност'), 'Synovitis': _rx('synovit', 'sinovit', 'synovial (thickening|proliferation|hypertroph)', 'thicken\\w* synovial', 'hypertroph\\w* of the synovium', 'synoviale? (verdikking|proliferatie)', 'verdikkingen van (het )?synovium', 'synovialitis', 'synovialis(verdickung|proliferation)', 'reizsynovial', 'sinovijalitis', 'sinovitis', 'zadebljanje sinovij', 'proliferacij\\w* sinovij', 'sinovijaln\\w* proliferacij', 'υμενιτιδα', 'συνοβιτιδα', 'υμενικ[^ ]* υπερτροφ', 'αρθρικου υμεν', 'παχυνση[^.]{0,20}υμεν', 'υμενα', 'синовит', 'синовиал[^ ]* (задебел|пролифер)', '\\bpannus\\b', '\\bhoffit', 'sinovyal\\w* (kalinlas|proliferas)', 'sinovyal hipertrof', '\\bartrit\\b', '\\barthritis\\b'), "Baker's": _rx('baker', 'popliteal cyst', 'quiste popliteo', 'quistes popliteos', 'kyste poplite', 'popliteale? cyst', 'poplitealzyste', 'bakerzyste', 'popliteal kist', '\\bbakerova\\b', 'poplitealn[^ ]* cist', 'popliteal\\w* cist', 'κυστη baker', 'πολυχωρη συνοβιακη κυστη', 'κυστη του baker', 'συνοβιακη κυστη', 'κυστη τυπου baker', 'киста на бейкър', 'бейкърова киста', 'поплитеална киста', 'бекеров', 'gastrocnemio ?semimembranos', 'gastrocnemius semimembranosus burs'), 'Contusion': _rx('\\bcontusion', 'bone bruise', 'bone marrow (o?edema|contusion)', 'marrow o?edema', '\\bkontuz', 'medular bone o?edema', 'osseous contusion', 'contusion osea', 'edema oseo', 'edema de medula osea', 'contusiones oseas', 'oedeme osseux', 'contusion osseuse', 'botcontusie', 'botoedeem', 'beenmergoedeem', 'botmergoedeem', 'knochenmarkodem', 'knochenodem', 'knochenmarksodem', 'kontusion', 'kemik kontuzyonu', 'kemik iligi odemi', 'kemik odemi', 'kemik iliginde odem', 'kontuzyonel kemik', 'kemik iligi odemleri', 'kostani edem', 'edem kosti', 'kontuzij', 'kostane srzi[^.]{0,20}edem', 'οστεομυελικ[^ ]* οιδημα', 'οστικο οιδημα', 'μυελικο οιδημα', 'οστικο μωλωπ', 'костномозъчен едем', 'костен едем', 'контузионен', 'костно мозъчен едем'), 'Fracture': _rx('\\bfractur', '\\bfract\\b', '\\bfractura', '\\bfracturas\\b', '\\bfractuur', '\\bbreuk\\b', '\\bfraktur', '\\bbruch\\b', '\\bkirik\\b', '\\bkirigi\\b', '\\bkiri[kg]\\w*', '\\bprijelom', 'impresijsk[^ ]* fraktur', 'impaktcij', 'καταγμα', 'καταγματ', 'фрактур', 'счупван', 'фисур', 'insufficiency fracture', 'stress fracture', 'avulsion fracture', 'subchondral fracture', 'subkondral kiri', 'impaction (fracture|injury)', 'osteochondral (fracture|impaction)', '\\bsegond\\b', 'impactiefractuur', 'subchondrale impression', 'subchondraler? impress')}
DECOY = {'Fracture': _rx('microfractur', '\\bfracture (risk|prophyla)'), "Baker's": _rx('meniscal cyst', 'quiste meniscal', 'parameniscal')}
PAIRED = {'ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus'}
OA_TARGETS = ['Medial OA', 'Lateral OA', 'PF OA']
PLURAL_MENISCI = _rx('\\bmenisci\\b', '\\bmeniscos\\b', '\\bmenisques\\b', '\\bmenisken\\b', '\\bmeniskusi\\b', '\\bmenisk\\w*ler\\b', '\\bμηνισκοι\\b', '\\bμηνισκων\\b', '\\bменискуси\\b', '\\bменискусите\\b', '\\bmenisci\\w*\\b')
ANY_SIDE = _rx(SIDE_MEDIAL.pattern, SIDE_LATERAL.pattern)
STEM_MENISCUS = _rx('menisc\\w*', 'menisk\\w*', 'μηνισκ\\w*', 'мениск\\w*')
STEM_CRUCIATE = _rx('cruciate', 'cruzado', 'croise', 'kruisband', 'kreuzband', 'capraz bag\\w*', 'krizn\\w*', 'χιαστ\\w*', 'кръстн\\w*', '\\bacl\\b', '\\blca\\b', '\\bvkb\\b', '\\bocb\\b', '\\bacb\\b')
STEM_COLLATERAL = _rx('collateral\\w*', 'colateral\\w*', 'kollateral\\w*', 'collaterale\\w*', 'kolateraln\\w*', 'yan bag\\w*', 'πλαγι\\w*', 'колатерал\\w*', 'странич\\w*', 'innenband\\w*', 'binnenband\\w*', '\\bmcl\\b', '\\blcm\\b', '\\biyb\\b')
STEM_FRACTURE = _rx('fractur\\w*', 'fraktur\\w*', 'fractuur\\w*', '\\bfract\\b', 'kiri[kgğ]\\w*', 'prijelom\\w*', 'lom kosti', '\\bbreuk\\w*', '\\bbruch\\w*', 'καταγμα\\w*', 'καταγματ\\w*', 'фрактур\\w*', 'счупван\\w*', 'fisur\\w* (osea|oseas|kost)', 'fissur\\w* kost')
```

In \[11\]:

linkcode

```
def _near(clause: str, stem_rx: re.Pattern, qual_rx: re.Pattern, window: int=55):
    for m in stem_rx.finditer(clause):
        lo = max(0, m.start() - window)
        hi = min(len(clause), m.end() + window)
        if qual_rx.search(clause[lo:hi]):
            return True
    return False
STEM_RULES = {'ACL': (STEM_CRUCIATE, SIDE_ANTERIOR), 'MCL': (STEM_COLLATERAL, SIDE_MEDIAL), 'Medial Meniscus': (STEM_MENISCUS, SIDE_MEDIAL), 'Lateral Meniscus': (STEM_MENISCUS, SIDE_LATERAL)}

class _Matcher:

    def __init__(self, phrase_rx, stem=None, side=None, window=55):
        self.phrase_rx = phrase_rx
        self.stem = stem
        self.side = side
        self.window = window

    def search(self, clause):
        m = self.phrase_rx.search(clause)
        if m is not None:
            return m
        if self.stem is not None and _near(clause, self.stem, self.side, self.window):
            return self.stem.search(clause)
        return None
ANAT_MATCH = {t: _Matcher(ANAT[t], *STEM_RULES[t]) for t in PAIRED}
DIRECT_MATCH = {t: _Matcher(_rx(rx.pattern, STEM_FRACTURE.pattern) if t == 'Fracture' else rx) for t, rx in DIRECT.items()}
SEV_LOW = _rx('\\bsmall\\b', '\\bminimal\\b', '\\btrace\\b', '\\bmild\\b', '\\bslight\\b', '\\btiny\\b', '\\bscant\\b', '\\bdiscrete\\b', '\\blow ?grade\\b', '\\bincipient\\b', '\\bleve\\b', '\\bminim', '\\bpeque', '\\bfina\\b', '\\bfino\\b', '\\bligero\\b', '\\bescaso\\b', '\\bdiscreto\\b', '\\bhafif\\b', '\\baz miktarda\\b', '\\bsilik\\b', '\\bmanj\\w*', '\\bblago\\b', '\\bdiskretn', '\\bmalo\\b', '\\bpocetn', '\\bgering', '\\bdiskret', '\\bkleine?r?\\b', '\\bwenig\\b', '\\bzarte?\\b', '\\bbeperkte?\\b', '\\bgeringe\\b', '\\bweinig\\b', '\\blichte?\\b', '\\blicht\\b', '\\bηπι', '\\bμικρ', '\\bελαχιστ', '\\bαρχομεν', '\\bминимал', '\\bлек', '\\bмалк', '\\bнеголям')
SEV_HIGH = _rx('\\blarge\\b', '\\bmarked\\b', '\\bmassive\\b', '\\bsevere\\b', '\\bextensive\\b', '\\bmoderate\\b', '\\bgross\\b', '\\bsignificant\\b', '\\babundant\\b', '\\btense\\b', '\\bcomplete\\b', '\\bfull ?thickness\\b', '\\bhigh ?grade\\b', '\\badvanced\\b', '\\bmoderad', '\\bimportante\\b', '\\bsevera?\\b', '\\bmarcad', '\\bcuantios', '\\bespesor total\\b', '\\bcompleta?\\b', '\\bbelirgin\\b', '\\byaygin\\b', '\\bileri\\b', '\\bciddi\\b', '\\bbol\\b', '\\bkomplet', '\\bopsezan\\b', '\\bveliki\\b', '\\bizrazit', '\\bznacajn', '\\bumjeren', '\\buznapredoval', '\\bpotpun', '\\bkompleksn', '\\bausgepragt', '\\bdeutlich', '\\bmassiv', '\\bmassig', '\\bgross', '\\buitgebreid', '\\bgevorderd', '\\bveel\\b', '\\bmatige?\\b', '\\bvolledig', '\\bμετρι', '\\bμεγαλ', '\\bεκτεταμεν', '\\bευμεγεθ', '\\bσοβαρ', '\\bπληρη', '\\bголям', '\\bизразен', '\\bзначим', '\\bумерен', '\\bобилен', '\\bпълн')
GRADE_HIGH = re.compile('grade?[ao]?\\s*(3|4|iii|iv)\\b|icrs grade (iii|iv|3|4)|stupnja iv|stupnja iii|\\bgrado (3|4)\\b|\\bgrad (3|4)\\b|\\bgrade (3|4)\\b')
DEGENERATIVE_MARROW = _rx('subchondral', 'subcondral', 'subkondral', 'supkondraln', 'subchondraln', 'υποχονδρι', 'υπαρθρικ', 'субхондрал', 'subchondrale?', 'subartikuler', '\\bcyst', '\\bquist', '\\bzyste\\b', '\\bcistic', 'reactive', 'reactivo', 'degenerative', 'degenerativ', 'reaktiv', '\\bcisti\\b')
TRAUMA = _rx('\\bbruise\\b', '\\bcontusion', '\\bkontuz', '\\btrauma', '\\bimpaction\\b', '\\bpivot shift\\b', '\\bkissing\\b', '\\bacute\\b', '\\bagudo\\b', '\\bakut', '\\bpivot kaymasi\\b', '\\bcontusion osseuse\\b', '\\bbone bruise\\b', '\\bbotcontusie\\b', '\\bконтузион', '\\bμωλωπ', '\\bkontuzij', '\\bimpaktcij', '\\bimpakcij', '\\bfall\\b', '\\binjury\\b', '\\bimpression\\b')
SYNOVIAL_PROXY = _rx('bursit', 'burzit', '\\bbursa\\b[^.]{0,30}(fluid|distend|sivi|tekucin|opzetting)', 'suprapatellar (bursitis|effusion|recess)', 'suprapatellar bursa', 'suprapatellar bursada', 'suprapatelarno', 'suprapatellaire recessus', 'hoffa', 'hoffit', 'plica', 'plika', 'πλικα', 'fat pad[^.]{0,20}(edema|oedema)', 'kapsul', 'capsul', 'καψ', 'капсул', '\\bpannus\\b', '\\bsinov', '\\bsynov')

def _polarity(clause: str, span=None) -> str:
    if UNCERTAIN.search(clause):
        return 'uncertain'
    if span is None or not FEATURES['directional_negation']:
        if NEGATION.search(clause):
            return 'negative'
    elif _negated(clause, span[0], span[1]):
        return 'negative'
    if NORMALITY.search(clause):
        if TEAR.search(clause) or GRADE_HIGH.search(clause):
            return 'positive'
        return 'negative'
    return 'positive'

def _severity(clause: str) -> float:
    high = SEV_HIGH.search(clause) is not None
    low = SEV_LOW.search(clause) is not None
    if high and (not low):
        return 1.0
    if low and (not high):
        return 0.45
    if high and low:
        return 0.8
    return 0.75

def _grade(n_pos, n_neg, n_unc, best):
    if n_pos or n_unc:
        score = min(0.97, 0.5 + 0.45 * best + 0.015 * min(n_pos, 3))
        conf = min(1.0, 0.55 + 0.15 * n_pos)
    elif n_neg:
        score = max(0.04, 0.2 - 0.04 * n_neg)
        conf = min(0.9, 0.45 + 0.12 * n_neg)
    else:
        score, conf = (0.28, 0.05)
    return (score, conf)

def _paired_weight(clause: str, meniscus: bool) -> float:
    g = _grade_of(clause) if FEATURES['graded_pathology'] else None
    tear = TEAR.search(clause) is not None
    if meniscus:
        if tear:
            base = 1.0
        elif g is not None:
            base = 0.95 if g >= 3 else 0.3
        elif DEGEN.search(clause):
            base = 0.35
        else:
            base = 0.45
    elif tear:
        base = 1.0
    elif g is not None:
        base = 0.85 if g >= 2 else 0.3
    elif DEGEN.search(clause):
        base = 0.4
    else:
        base = 0.55
    if SEV_HIGH.search(clause) and (not SEV_LOW.search(clause)):
        base = min(1.0, base * 1.2)
    elif SEV_LOW.search(clause) and (not SEV_HIGH.search(clause)):
        base *= 0.7
    return base

def _score_paired(cls, tgt):
    anat_rx = ANAT_MATCH[tgt]
    path_rx = _rx(TEAR.pattern, DEGEN.pattern, INJURY.pattern)
    meniscus = 'Meniscus' in tgt
    n_pos = n_neg = n_unc = 0
    best = 0.0
    for c in cls:
        hit = anat_rx.search(c)
        if hit is None and meniscus and PLURAL_MENISCI.search(c) and (not ANY_SIDE.search(c)):
            hit = PLURAL_MENISCI.search(c)
        if hit is None:
            continue
        pm = path_rx.search(c)
        if pm is None and _grade_of(c) is None:
            if NORMAL_PHRASE.search(c) or (NORMALITY.search(c) and (not NEGATION.search(c))):
                n_neg += 1
            continue
        span = (pm.start(), pm.end()) if pm is not None else None
        pol = _polarity(c, span)
        if pol == 'positive':
            n_pos += 1
            best = max(best, _paired_weight(c, meniscus))
        elif pol == 'negative':
            n_neg += 1
        else:
            n_unc += 1
            best = max(best, 0.45 * _paired_weight(c, meniscus))
    s, cf = _grade(n_pos, n_neg, n_unc, best)
    return (s, cf, n_pos, n_neg)

def _score_clauses(cls, anat_rx, path_rx=None, decoy_rx=None, context_penalty=None, context_bonus=None):
    n_pos = n_neg = n_unc = 0
    best = 0.0
    for c in cls:
        m = anat_rx.search(c)
        if not m:
            continue
        if decoy_rx is not None and decoy_rx.search(c):
            continue
        if path_rx is not None and (not path_rx.search(c)):
            if NORMAL_PHRASE.search(c) or (NORMALITY.search(c) and (not NEGATION.search(c))):
                n_neg += 1
            continue
        pol = _polarity(c, (m.start(), m.end()))
        if pol == 'positive':
            n_pos += 1
            w = _severity(c)
            if context_penalty is not None and context_penalty.search(c):
                w *= 0.45
            if context_bonus is not None and context_bonus.search(c):
                w = min(1.0, w * 1.35)
            best = max(best, w)
        elif pol == 'negative':
            n_neg += 1
        else:
            n_unc += 1
            best = max(best, 0.3)
    s, c = _grade(n_pos, n_neg, n_unc, best)
    return (s, c, n_pos, n_neg)

def _score_oa(cls):
    acc = {t: {'pos': 0, 'neg': 0, 'unc': 0, 'best': 0.0} for t in OA_TARGETS}
    g_pos, g_neg, g_best = (0, 0, 0.0)
    for c in cls:
        m = OA_EVIDENCE.search(c)
        if not m:
            continue
        pol = _polarity(c, (m.start(), m.end()))
        sev = _severity(c)
        tf_med = _near(c, TF_SITE, SIDE_MEDIAL, 45)
        tf_lat = _near(c, TF_SITE, SIDE_LATERAL, 45)
        pf = PF_SITE.search(c) is not None
        hits = []
        if tf_med:
            hits.append('Medial OA')
        if tf_lat:
            hits.append('Lateral OA')
        if pf:
            hits.append('PF OA')
        if not hits:
            if pol == 'positive':
                g_pos += 1
                g_best = max(g_best, sev if GLOBAL_OA.search(c) else sev * 0.7)
            elif pol == 'negative':
                g_neg += 1
            continue
        for t in hits:
            if pol == 'positive':
                acc[t]['pos'] += 1
                acc[t]['best'] = max(acc[t]['best'], sev)
            elif pol == 'negative':
                acc[t]['neg'] += 1
            else:
                acc[t]['unc'] += 1
                acc[t]['best'] = max(acc[t]['best'], 0.3)
    out = {}
    for t in OA_TARGETS:
        a = acc[t]
        pos, neg, unc, best = (a['pos'], a['neg'], a['unc'], a['best'])
        if not (pos or unc) and g_pos and FEATURES['oa_inherit']:
            if neg:
                score, conf = _grade(0, neg, 0, 0.0)
                score = max(score, 0.35)
                conf *= 0.7
            else:
                score, conf = _grade(g_pos, 0, 0, g_best * 0.92)
                conf *= 0.75
        else:
            score, conf = _grade(pos, neg + g_neg, unc, best)
        out[t] = (score, conf, pos, neg)
    return out

def extract(report: str) -> dict:
    cls = clauses(report)
    out = {}
    for tgt in PAIRED:
        s, c, npos, nneg = _score_paired(cls, tgt)
        out[tgt] = s
        out[tgt + '__conf'] = c
        out[tgt + '__npos'] = npos
        out[tgt + '__nneg'] = nneg
    for tgt, (s, c, npos, nneg) in _score_oa(cls).items():
        out[tgt] = s
        out[tgt + '__conf'] = c
        out[tgt + '__npos'] = npos
        out[tgt + '__nneg'] = nneg
    for tgt in ('Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture'):
        if tgt == 'Contusion':
            s, c, npos, nneg = _score_clauses(cls, DIRECT_MATCH[tgt], None, DECOY.get(tgt), context_penalty=DEGENERATIVE_MARROW, context_bonus=TRAUMA)
        else:
            s, c, npos, nneg = _score_clauses(cls, DIRECT_MATCH[tgt], None, DECOY.get(tgt))
        out[tgt] = s
        out[tgt + '__conf'] = c
        out[tgt + '__npos'] = npos
        out[tgt + '__nneg'] = nneg
    if FEATURES['synovitis_backoff'] and out['Synovitis__npos'] == 0 and (out['Synovitis__nneg'] == 0):
        proxy = sum((1 for c in cls if SYNOVIAL_PROXY.search(c) and _polarity(c) == 'positive'))
        eff = out['Effusion']
        prior = 0.3 + 0.3 * max(0.0, (eff - 0.5) / 0.45) + 0.06 * min(proxy, 3)
        out['Synovitis'] = min(0.72, prior)
        out['Synovitis__conf'] = 0.18
    return out
```

linkcode

### EDA 5 — auditing the extractor against the gold labels [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#EDA-5-%E2%80%94-auditing-the-extractor-against-the-gold-labels)

In \[12\]:

linkcode

```
# ============ EDA 5 — how good are the labels these weights were fitted on? =
# The extractor above is what supervised almost every weight in this notebook.
# Fifty-eight studies carry gold labels, which makes them the only honest way
# to ask how well it reads a report. This is the most important table in the
# notebook and it takes seconds to produce.
try:
    _aud_gold = _EDA_TRAIN.dropna(subset=_EDA_TARGETS)
    _aud_reports = _EDA_TRAIN[_EDA_TRAIN["StudyInstanceUID"].isin(\
        _aud_gold["StudyInstanceUID"])][["StudyInstanceUID", "Report"]]
    _aud_pred = read_labels(_aud_reports)
    _aud_truth = _aud_gold.set_index("StudyInstanceUID")[_EDA_TARGETS]

    rows = []
    for finding in _EDA_TARGETS:
        truth = _aud_truth[finding].reindex(_aud_pred.index).astype(float)
        keep = truth.notna()
        truth = truth[keep].astype(int)
        guess = (_aud_pred.loc[keep.index[keep], finding] > 0.5).astype(int)
        tp = int(((truth == 1) & (guess == 1)).sum())
        fp = int(((truth == 0) & (guess == 1)).sum())
        fn = int(((truth == 1) & (guess == 0)).sum())
        tn = int(((truth == 0) & (guess == 0)).sum())
        rows.append({"finding": finding, "positives": int(truth.sum()),
                     "precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1),
                     "agreement": (tp + tn) / max(len(truth), 1),
                     "mean confidence": float(
                         _aud_pred.loc[keep.index[keep], finding + "__conf"].mean())})
    _AUDIT = _eda_pd.DataFrame(rows).set_index("finding")
    print(_AUDIT.to_string(float_format=lambda v: f"{v:.3f}"))

    figure, axis = plt.subplots(figsize=(9, 4))
    y = _eda_np.arange(len(_AUDIT))
    axis.barh(y - 0.2, _AUDIT["recall"], height=0.4, color=_EDA_INK, label="recall")
    axis.barh(y + 0.2, _AUDIT["precision"], height=0.4, color=_EDA_WARM, label="precision")
    axis.set_yticks(y)
    axis.set_yticklabels(_AUDIT.index)
    axis.set_xlim(0, 1)
    axis.legend(loc="lower right")
    axis.set_title("Report extractor against gold labels")
    plt.tight_layout()
    plt.show()

    weak = _AUDIT.nsmallest(3, "recall")
    print("\nWorst-read findings:", ", ".join(weak.index))
    print("A missed finding is not a wrong label so much as a lost study: the "
          "weighting scheme downstream scales a study's influence by the "
          "extractor's confidence, so a finding it reads poorly is a finding "
          "the network barely learns. No amount of blending downstream recovers "
          "that. Fifty-eight studies is far too few to trust any single row here, "
          "but a finding sitting near the bottom on both precision and recall is "
          "worth reading reports for by hand.")
except NameError:
    print("[eda] extractor not defined yet; run the stage 1 cells above", flush=True)
except Exception as error:
    print(f"[eda] label audit skipped: {type(error).__name__}: {error}", flush=True)
```

```
[eda] extractor not defined yet; run the stage 1 cells above
```

linkcode

## Stage 1 (continued) — DINO: read the study, combine the members [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Stage-1-(continued)-%E2%80%94-DINO:-read-the-study,-combine-the-members)

In \[13\]:

linkcode

```
from __future__ import annotations
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '4')
import gc
import hashlib
import json
import re
import time
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
import pydicom
import torch
import torch.nn as nn
import torch.nn.functional as F

def _cuda_execution_probe(index):
    dev = torch.device(f'cuda:{index}')
    try:
        major, minor = torch.cuda.get_device_capability(index)
        probe = nn.Conv2d(3, 4, kernel_size=3, padding=1).eval().to(dev)
        with torch.inference_mode():
            out = probe(torch.zeros((1, 3, 16, 16), device=dev))
            if tuple(out.shape) != (1, 4, 16, 16):
                raise RuntimeError(f'unexpected CUDA probe shape {tuple(out.shape)}')
        torch.cuda.synchronize(index)
        print(f'cuda:{index} probe PASS (compute {major}.{minor})')
        del probe, out
        torch.cuda.empty_cache()
        return True
    except Exception as exc:
        print(f'cuda:{index} probe FAIL ({type(exc).__name__}: {exc}); using CPU fallback')
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return False
DEVS = []
if torch.cuda.is_available():
    DEVS = [torch.device(f'cuda:{i}') for i in range(torch.cuda.device_count()) if _cuda_execution_probe(i)]
if not DEVS:
    DEVS = [torch.device('cpu')]
print(f'devices: {[str(d) for d in DEVS]}')
T0 = time.time()
SEED = 2026
np.random.seed(SEED)
torch.manual_seed(SEED)
TARGETS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
CROP_MM = 130.0
CACHE_IMG = 336
GROUP = 3
N_GROUP_MAX = 1
CACHE_FRACTION = 0.45
CACHE_BUDGET_MAX_GB = 24.0
CACHE_BUDGET_GB = 12.0
TEST_SHARE = 0.3
HDR_THREADS = 16
PIX_THREADS = 12
ORDER_THREADS = 32
ORDER_BUDGET_S = 5400
RUNS = [{'name': 'r224', 'img': 224}, {'name': 'r336', 'img': 336}]
EPOCHS = 10
BATCH_STUDIES = 8
AUG_ROT_DEG = 8.0
AUG_SCALE = 0.08
AUG_SHIFT = 0.05
AUG_INTENSITY = 0.1
LAT_MIN_OFFSET_MM = 20.0
SLICE_BAND = (0.2, 0.8)
RULES_NATIVE = {'order': 'normal', 'lat': 'centre', 'slot_fallback': False, 'decode_fill': 'nearest'}
RULES_LEGACY = {'order': 'dominant_axis', 'lat': 'corner_x', 'slot_fallback': True, 'decode_fill': 'zero'}
RULES = dict(RULES_NATIVE)
LEGACY_LAT_OFFSET_MM = 5.0
LR_HEAD = 0.001
LR_BACKBONE = 8e-06
UNFREEZE_LAST = 6
WEIGHT_DECAY = 0.02
EVAL_BATCH = 8
TIME_BUDGET = 8.0 * 3600
SLOTS_RECOVERED = [('SAG_FLUID_FS', 'Sagittal', True, True), ('COR_FLUID_FS', 'Coronal', True, True), ('AX_FLUID_FS', 'Axial', True, True), ('SAG_FLUID_NOFS', 'Sagittal', True, False), ('COR_T1', 'Coronal', False, False), ('SAG_T1', 'Sagittal', False, False)]
SLOTS_PUBLIC = [('SAG_FLUID', 'Sagittal', None, True), ('COR_FLUID', 'Coronal', None, True), ('AX_FLUID', 'Axial', None, True), ('SAG_STRUCT', 'Sagittal', None, False), ('COR_STRUCT', 'Coronal', None, False), ('AX_STRUCT', 'Axial', None, False)]
SLOT_SCHEME = os.environ.get('SLOT_SCHEME', 'recovered')
SLOTS = SLOTS_PUBLIC if SLOT_SCHEME == 'public' else SLOTS_RECOVERED
N_SLOT = len(SLOTS)
POOL_PARTS = {'cls_mean': 2, 'cls_mean_focal': 3}
SLOT_PRIOR_TABLE = {'ACL': (0, 3, 5), 'MCL': (1, 4), 'Medial Meniscus': (0, 1, 3, 4), 'Lateral Meniscus': (0, 1, 3, 4), 'Medial OA': (1, 4, 5), 'Lateral OA': (1, 4, 5), 'PF OA': (0, 2, 5), 'Effusion': (0, 2), 'Synovitis': (0, 2), "Baker's": (0,), 'Contusion': (0, 1, 2), 'Fracture': (0, 1, 2, 4, 5)}
SLOT_PRIOR_STRENGTH = 0.55
FATSAT_OPTS = {'FS', 'FATSAT', 'FAT_SAT', 'FSAT'}
_SEP = re.compile('[_\\-.]')
_FATSAT_RX = re.compile('\\bfs\\b|fatsat|fat sat|\\bstir\\b|\\bspair\\b|\\bspir\\b|\\bwe\\b|water excit|\\btirm\\b|\\bsting\\b|\\bfatsup\\b')
_T1_RX = re.compile('\\bt1\\b|\\bt1w\\b')
_T2_RX = re.compile('\\bt2\\b|\\bt2w\\b')
_PD_RX = re.compile('\\bpd\\b|\\bpdw\\b|proton|\\bdp\\b|dens')
```

```
cuda:0 probe PASS (compute 7.5)
cuda:1 probe PASS (compute 7.5)
devices: ['cuda:0', 'cuda:1']
```

In \[14\]:

linkcode

```
def log(msg):
    print(f'[{time.time() - T0:7.1f}s] {msg}', flush=True)

def find_root():
    for c in [Path('/kaggle/input/competitions/rsna-knee-abnormality-detection'), Path('/kaggle/input/rsna-knee-abnormality-detection'), Path('data'), Path('.')]:
        if (c / 'test.csv').is_file() and (c / 'test_series').is_dir():
            return c
    base = Path('/kaggle/input')
    if base.is_dir():
        for depth1 in sorted((p for p in base.iterdir() if p.is_dir())):
            for cand in [depth1] + sorted((p for p in depth1.iterdir() if p.is_dir())):
                if (cand / 'test.csv').is_file():
                    return cand
    raise FileNotFoundError(f'competition mount not found (cwd {Path.cwd()}); expected a directory holding test.csv and test_series/')

def find_dinov2(variant='small'):
    base = Path('/kaggle/input')
    if not base.is_dir():
        return None
    hits = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('train_series', 'test_series')]
        if 'config.json' in files and 'dinov2' in root.lower():
            hits.append(Path(root))
    for h in hits:
        if variant in str(h).lower():
            return h
    return hits[0] if hits else None
LABEL_COLS = TARGETS + [t + '__conf' for t in TARGETS]

class LabelSourceError(RuntimeError):
    pass

def find_label_table():
    base = Path('/kaggle/input')
    cands = []
    if base.is_dir():
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ('train_series', 'test_series')]
            cands += [Path(root) / f for f in files if f.startswith('report_labels') and f.endswith('.csv')]
    cands += [p for p in (Path('data/derived/report_labels_v2.csv'),) if p.is_file()]
    for c in cands:
        try:
            head = pd.read_csv(c, nrows=1)
        except Exception:
            continue
        if 'StudyInstanceUID' in head.columns and all((t in head.columns for t in TARGETS)):
            return c
    return None

def label_mount_attached():
    base = Path('/kaggle/input')
    if not base.is_dir():
        return False
    return any(('label' in p.name.lower() for p in base.iterdir() if p.is_dir()))

def read_labels(train_df):
    n = len(train_df)
    lab = pd.DataFrame([extract(r) for r in train_df['Report'].fillna('')])
    lab['StudyInstanceUID'] = train_df['StudyInstanceUID'].values
    lab = lab.set_index('StudyInstanceUID')
    src = find_label_table()
    if src is None:
        if label_mount_attached():
            raise LabelSourceError('LABEL SOURCE: a label dataset is mounted but no usable table was found in it. Falling back to the lexicon here would train on the weaker labels and say so only in a log line, so the run stops instead.')
        log(f'LABEL SOURCE: lexicon, {n} studies (no table mounted)')
        return lab
    tab = pd.read_csv(src).set_index('StudyInstanceUID')
    missing = [c for c in LABEL_COLS if c not in tab.columns]
    if missing:
        raise LabelSourceError(f'LABEL SOURCE: {src} is missing {len(missing)} expected columns (first: {missing[0]!r}). Refusing to fall back silently.')
    hit = lab.index.intersection(tab.index)
    if not len(hit):
        raise LabelSourceError(f'LABEL SOURCE: {src} shares no StudyInstanceUID with train.csv.')
    log(f'LABEL SOURCE: {src.name} covers {len(hit)} of {n} studies, lexicon for the remaining {n - len(hit)}')
    lab.loc[hit, LABEL_COLS] = tab.loc[hit, LABEL_COLS].values
    return lab
ROOT = find_root()
log(f'input root: {ROOT}')
IMG = CACHE_IMG

def available_gb():
    try:
        with open('/proc/meminfo') as fh:
            info = {k.strip(): v for k, v in (l.split(':', 1) for l in fh if ':' in l)}
        return int(info['MemAvailable'].split()[0]) / 1024 ** 2
    except Exception:
        return CACHE_BUDGET_GB / CACHE_FRACTION

def plan_cache(n_study, n_test=0):
    avail = available_gb()
    budget = min(avail * CACHE_FRACTION, CACHE_BUDGET_MAX_GB)
    n_total = n_study + max(n_test, int(TEST_SHARE * n_study))
    per_slice = n_total * N_SLOT * IMG * IMG
    afford = int(budget * 1024 ** 3 // max(per_slice, 1))
    groups = max(1, min(N_GROUP_MAX, afford // GROUP))
    log(f'memory: {avail:.1f} GB available, {budget:.1f} GB to the cache; sizing for {n_study} train + {n_total - n_study} test studies -> {groups} group(s) of {GROUP} = {groups * GROUP} slices per slot' + (f' (wanted {N_GROUP_MAX})' if groups < N_GROUP_MAX else ''))
    return groups
N_GROUP = plan_cache(len(pd.read_csv(ROOT / 'train.csv')), len(pd.read_csv(ROOT / 'test.csv')))
CACHE_SLICES = GROUP * N_GROUP
log(f'cache layout: {N_GROUP} groups x {GROUP} slices = {CACHE_SLICES} per slot')
```

```
[    0.1s] input root: /kaggle/input/rsna-knee-abnormality-detection
[    0.2s] memory: 29.5 GB available, 13.3 GB to the cache; sizing for 4407 train + 1322 test studies -> 1 group(s) of 3 = 3 slices per slot
[    0.2s] cache layout: 1 groups x 3 slices = 3 per slot
```

In \[15\]:

linkcode

```
HDR_TAGS = ['SeriesDescription', 'SequenceName', 'ScanOptions', 'ScanningSequence', 'RepetitionTime', 'EchoTime', 'Laterality', 'PixelSpacing', 'Rows', 'Columns', 'RescaleSlope', 'RescaleIntercept', 'ImagePositionPatient', 'ImageOrientationPatient']

def _hdr_vec(s, n):
    if not isinstance(s, str):
        return None
    try:
        v = [float(x) for x in s.split('|')]
    except ValueError:
        return None
    return np.array(v) if len(v) >= n else None

def side_from_geometry(h):
    cx = {}
    for r in h.itertuples(index=False):
        ipp = _hdr_vec(getattr(r, 'ImagePositionPatient', None), 3)
        iop = _hdr_vec(getattr(r, 'ImageOrientationPatient', None), 6)
        ps = _hdr_vec(getattr(r, 'PixelSpacing', None), 2)
        rows, cols = (getattr(r, 'Rows', None), getattr(r, 'Columns', None))
        if ipp is None or iop is None or ps is None or (not rows) or (not cols):
            continue
        try:
            c = ipp[:3] + iop[:3] * ps[1] * float(cols) / 2 + iop[3:6] * ps[0] * float(rows) / 2
        except (TypeError, ValueError):
            continue
        cx.setdefault(r.StudyInstanceUID, []).append(float(c[0]))
    out = {}
    for st, xs in cx.items():
        m = float(np.median(xs))
        out[st] = None if abs(m) < LAT_MIN_OFFSET_MM else 'R' if m < 0 else 'L'
    return out

def side_from_corner_x(h):
    out = {}
    for st, g in h.groupby('StudyInstanceUID'):
        xs = []
        for r in g.itertuples(index=False):
            ipp = _hdr_vec(getattr(r, 'ImagePositionPatient', None), 3)
            if ipp is not None and np.isfinite(ipp).all():
                xs.append(float(ipp[0]))
        if not xs:
            out[st] = None
            continue
        x = float(np.median(xs))
        out[st] = None if abs(x) < LEGACY_LAT_OFFSET_MM else 'R' if x < 0 else 'L'
    return out

def lat_of(h, tag=''):
    geo = side_from_corner_x(h) if RULES['lat'] == 'corner_x' else side_from_geometry(h)
    d, n_tag, n_geo, n_none, n_disagree = ({}, 0, 0, 0, 0)
    for st, g in h.groupby('StudyInstanceUID'):
        v = [str(x).strip().upper() for x in g['Laterality'].dropna()]
        if RULES['lat'] == 'corner_x' and 'ImageLaterality' in g.columns:
            v += [str(x).strip().upper() for x in g['ImageLaterality'].dropna()]
        v = [x[0] for x in v if x and x[0] in ('L', 'R')]
        side = v[0] if v else None
        if side is not None:
            n_tag += 1
            if geo.get(st) is not None and geo[st] != side:
                n_disagree += 1
        else:
            side = geo.get(st)
            n_geo += side is not None
            n_none += side is None
        d[st] = side
    log(f'{tag}laterality: {n_tag} from the tag, {n_geo} from geometry, {n_none} unresolved; tag and geometry disagree on {n_disagree} ({n_disagree / max(n_tag, 1):.1%} of the tagged)')
    return d

def probe(item):
    split, study, series, path = item
    row = {'split': split, 'StudyInstanceUID': study, 'SeriesInstanceUID': series, 'dir': path}
    try:
        files = sorted((e.name for e in os.scandir(path) if e.name.endswith('.dcm')))
        row['files'] = files
        row['n_slices'] = len(files)
        if not files:
            return row
        ds = pydicom.dcmread(os.path.join(path, files[len(files) // 2]), stop_before_pixels=True, force=True)
        for t in HDR_TAGS:
            v = getattr(ds, t, None)
            if v is None:
                row[t] = None
            elif isinstance(v, (list, tuple)) or type(v).__name__ == 'MultiValue':
                row[t] = '|'.join((str(x) for x in v))
            else:
                row[t] = str(v)
    except Exception as exc:
        row['err'] = str(exc)[:120]
    return row

def walk(split):
    base = ROOT / split
    items = []
    if not base.is_dir():
        return pd.DataFrame(columns=['split', 'StudyInstanceUID', 'SeriesInstanceUID', 'dir', 'files', 'n_slices'] + HDR_TAGS)
    for study in os.scandir(base):
        if study.is_dir():
            for series in os.scandir(study.path):
                if series.is_dir():
                    items.append((split, study.name, series.name, series.path))
    with ThreadPoolExecutor(max_workers=HDR_THREADS) as pool:
        rows = list(pool.map(probe, items))
    return pd.DataFrame(rows)

def annotate(df):
    desc = df['SeriesDescription'].fillna('') + ' ' + df['SequenceName'].fillna('')
    desc = desc.str.lower().str.replace(_SEP, ' ', regex=True)
    opts = df['ScanOptions'].fillna('').str.upper().str.split('|')
    opts_fs = opts.apply(lambda ts: any((t.strip() in FATSAT_OPTS for t in ts)))
    df['fatsat'] = desc.str.contains(_FATSAT_RX) | opts_fs
    tr = pd.to_numeric(df['RepetitionTime'], errors='coerce')
    te = pd.to_numeric(df['EchoTime'], errors='coerce')
    gre = df['ScanningSequence'].fillna('').str.upper().str.contains('GR')
    t1, t2, pdw = (desc.str.contains(_T1_RX), desc.str.contains(_T2_RX), desc.str.contains(_PD_RX))
    df['weight'] = np.where(t1 & ~t2 & ~pdw, 'T1', np.where(t2 & ~pdw, 'T2', np.where(pdw, 'PD', np.where(gre, 'GRE', np.where(tr < 800, 'T1', np.where(te > 60, 'T2', np.where(tr >= 800, 'PD', 'UNK')))))))
    df['fluid'] = np.isin(df['weight'], ['PD', 'T2'])
    df['px'] = pd.to_numeric(df['PixelSpacing'].fillna('').str.split('|').str[0].replace('', np.nan), errors='coerce')
    return df
```

In \[16\]:

linkcode

```
def pick_slots(series_df, plane_map):
    series_df = series_df.copy()
    series_df['plane'] = series_df['SeriesInstanceUID'].map(plane_map)
    out = {}
    for study, g in series_df.groupby('StudyInstanceUID'):
        chosen = {}
        for name, plane, fluid, fs in SLOTS:
            sel = (g['plane'] == plane) & (g['fatsat'] == fs)
            if fluid is not None:
                sel &= g['fluid'] == fluid
            cand = g[sel]
            if len(cand) == 0 and RULES['slot_fallback'] and (fluid is False):
                cand = g[(g['plane'] == plane) & ~g['fatsat']]
            if len(cand):
                chosen[name] = cand.sort_values('n_slices', ascending=False).iloc[0]
        out[study] = chosen
    return out
```

In \[17\]:

linkcode

```
ORDER_TAGS = [(32, 50), (32, 55), (32, 19)]
DECODE_FAILED = []

def _natural_key(name):
    return tuple((int(x) if x.isdigit() else x.lower() for x in re.split('(\\d+)', str(name))))

def _order_dominant_axis(rec):
    files, d = (rec['files'], rec['dir'])
    rows = []
    for pos, f in enumerate(files):
        ipp = inst = None
        try:
            ds = pydicom.dcmread(os.path.join(d, f), force=True, stop_before_pixels=True, specific_tags=['ImagePositionPatient', 'InstanceNumber'])
            raw = getattr(ds, 'ImagePositionPatient', None)
            if raw is not None and len(raw) >= 3:
                c = np.asarray(raw[:3], dtype=np.float64)
                if np.isfinite(c).all():
                    ipp = c
            n = getattr(ds, 'InstanceNumber', None)
            if n is not None:
                inst = float(n)
        except Exception:
            pass
        rows.append((f, ipp, inst, pos))
    placed = [r for r in rows if r[1] is not None]
    need = max(2, int(0.8 * len(rows)))
    if len(placed) >= need:
        xyz = np.stack([r[1] for r in placed])
        axis = int(np.argmax(np.ptp(xyz, axis=0)))
        spare = float(np.nanmedian(xyz[:, axis]))
        rows.sort(key=lambda r: (float(r[1][axis]) if r[1] is not None else spare, r[2] if r[2] is not None else float('inf'), r[3]))
    elif sum((r[2] is not None for r in rows)) >= need:
        rows.sort(key=lambda r: (r[2] if r[2] is not None else float('inf'), r[3]))
    else:
        rows.sort(key=lambda r: _natural_key(r[0]))
    return ([r[0] for r in rows], True)

def order_slices(rec):
    if RULES['order'] == 'dominant_axis':
        return _order_dominant_axis(rec)
    files, d = (rec['files'], rec['dir'])
    keyed = []
    for f in files:
        k = None
        try:
            ds = pydicom.dcmread(os.path.join(d, f), force=True, stop_before_pixels=True, specific_tags=ORDER_TAGS)
            iop = np.asarray(ds.ImageOrientationPatient, dtype=float)
            ipp = np.asarray(ds.ImagePositionPatient, dtype=float)
            k = float(np.dot(ipp, np.cross(iop[:3], iop[3:])))
        except Exception:
            try:
                k = float(ds.InstanceNumber)
            except Exception:
                k = None
        keyed.append((k, f))
    if any((k is None for k, _ in keyed)):
        return (files, False)
    return ([f for _, f in sorted(keyed, key=lambda t: t[0])], True)

def read_slot(rec, n_slice=None, out_size=None):
    n_slice = GROUP if n_slice is None else n_slice
    out_size = IMG if out_size is None else out_size
    files, d, px = (rec.get('ordered') or rec['files'], rec['dir'], rec['px'])
    n = len(files)
    if n == 0:
        return None
    lo, hi = (int(SLICE_BAND[0] * (n - 1)), int(SLICE_BAND[1] * (n - 1)))
    idx = np.unique(np.linspace(lo, hi, n_slice).astype(int)) if hi > lo else np.array([n // 2])
    while len(idx) < n_slice:
        idx = np.append(idx, idx[-1])
    planes = []
    for i in idx[:n_slice]:
        try:
            ds = pydicom.dcmread(os.path.join(d, files[int(i)]), force=True)
            a = ds.pixel_array.astype(np.float32)
            sl = float(getattr(ds, 'RescaleSlope', 1) or 1)
            ic = float(getattr(ds, 'RescaleIntercept', 0) or 0)
            a = a * sl + ic
        except Exception:
            a = None
        planes.append(a)
    got = [k for k, p in enumerate(planes) if p is not None]
    if RULES['decode_fill'] == 'zero':
        if not got:
            DECODE_FAILED.append(rec.get('SeriesInstanceUID', d))
        planes = [np.zeros((out_size, out_size), np.float32) if p is None else p for p in planes]
        got = list(range(len(planes)))
    if not got:
        DECODE_FAILED.append(rec.get('SeriesInstanceUID', d))
        return None
    if len(got) < len(planes):
        DECODE_FAILED.append(rec.get('SeriesInstanceUID', d))
        for k, p in enumerate(planes):
            if p is None:
                planes[k] = planes[min(got, key=lambda j: abs(j - k))]
    shp = planes[0].shape
    planes = [p if p.shape == shp else np.zeros(shp, np.float32) for p in planes]
    vol = np.stack(planes)
    if px and np.isfinite(px) and (px > 0):
        want = int(round(CROP_MM / px))
        h, w = shp
        if 16 < want < min(h, w):
            cy, cx = (h // 2, w // 2)
            half = want // 2
            vol = vol[:, max(0, cy - half):cy + half, max(0, cx - half):cx + half]
    lo_v, hi_v = np.percentile(vol, [1, 99])
    vol = np.clip((vol - lo_v) / max(hi_v - lo_v, 1e-06), 0, 1)
    t = torch.from_numpy(np.ascontiguousarray(vol)).unsqueeze(0)
    t = F.interpolate(t, size=(out_size, out_size), mode='bilinear', align_corners=False)
    return (t.squeeze(0) * 255).round().clamp(0, 255).to(torch.uint8)
```

In \[18\]:

linkcode

```
def normalise_laterality(img, plane, lat):
    if lat != 'R':
        return img
    if plane in ('Coronal', 'Axial'):
        return torch.flip(img, dims=[-1])
    return torch.flip(img, dims=[0])
```

In \[19\]:

linkcode

```
ORDER_CACHE = os.environ.get('RSNA_ORDER_CACHE') or None

def build_cache(slot_map, plane_map, lat_map, tag):
    studies = sorted(slot_map)
    sidx = {s: i for i, s in enumerate(studies)}
    cache = np.zeros((len(studies), N_SLOT, CACHE_SLICES, IMG, IMG), np.uint8)
    mask = np.zeros((len(studies), N_SLOT), np.float32)
    log(f'{tag}: cache {cache.shape} = {cache.nbytes / 1024 ** 3:.1f} GB')
    jobs = [(st, k, plane, slot_map[st][name]) for st in studies for k, (name, plane, _, _) in enumerate(SLOTS) if name in slot_map[st]]
    n_job = len(jobs)
    t_ord = time.time()
    n_slice_total = sum((len(j[3]['files']) for j in jobs))
    log(f'{tag}: ordering {len(jobs)} slot-series ({n_slice_total} slice headers)')
    ok = done = 0
    CHUNK_O = 1024
    seen = {}
    if ORDER_CACHE and Path(ORDER_CACHE).is_file():
        try:
            import json as _json
            seen = _json.loads(Path(ORDER_CACHE).read_text())
        except (OSError, ValueError):
            seen = {}
        hit = 0
        for _, _, _, rec in jobs:
            e = seen.get(rec['SeriesInstanceUID'])
            if e and len(e['files']) == len(rec['files']):
                rec['ordered'] = e['files']
                ok += int(e['good'])
                hit += 1
        jobs = [j for j in jobs if 'ordered' not in j[3]]
        log(f'{tag}: {hit} slot-series ordered from {ORDER_CACHE}, {len(jobs)} to read')
    with ThreadPoolExecutor(max_workers=ORDER_THREADS) as pool:
        for c0 in range(0, len(jobs), CHUNK_O):
            block = jobs[c0:c0 + CHUNK_O]
            for (_, _, _, rec), (files, good) in zip(block, pool.map(lambda j: order_slices(j[3]), block)):
                rec['ordered'] = files
                ok += int(good)
                done += 1
                if ORDER_CACHE:
                    seen[rec['SeriesInstanceUID']] = {'files': files, 'good': bool(good)}
            budget = min(ORDER_BUDGET_S, max(60.0, (TIME_BUDGET - (time.time() - T0)) * 0.35))
            if time.time() - t_ord > budget:
                log(f'{tag}: ordering budget spent at {done}/{len(jobs)}; the rest keep file order')
                break
    if ORDER_CACHE and done:
        import json as _json
        _t = Path(ORDER_CACHE).with_suffix('.tmp')
        _t.write_text(_json.dumps(seen))
        _t.replace(Path(ORDER_CACHE))
    log(f'{tag}: ordered {ok}/{n_job} by geometry ({n_job - ok} kept arbitrary) in {time.time() - t_ord:.0f}s')
    jobs = [(st, k, plane, slot_map[st][name]) for st in studies for k, (name, plane, _, _) in enumerate(SLOTS) if name in slot_map[st]]
    log(f'{tag}: decoding {len(jobs)} slot-series')
    n_failed_before = len(DECODE_FAILED)
    CHUNK = 512
    done = 0
    with ThreadPoolExecutor(max_workers=PIX_THREADS) as pool:
        for c0 in range(0, len(jobs), CHUNK):
            block = jobs[c0:c0 + CHUNK]
            for (st, k, plane, _), img in zip(block, pool.map(lambda j: read_slot(j[3], CACHE_SLICES, IMG), block)):
                done += 1
                if img is None:
                    continue
                cache[sidx[st], k] = normalise_laterality(img, plane, lat_map.get(st)).numpy()
                mask[sidx[st], k] = 1.0
            if done % 4096 < CHUNK:
                log(f'  {tag} {done}/{len(jobs)}')
            if time.time() - T0 > TIME_BUDGET:
                log(f'  {tag}: time budget reached during decode')
                break
    n_failed = len(DECODE_FAILED) - n_failed_before
    log(f'{tag}: {int(mask.sum())}/{len(jobs)} slots filled' + (f'; {n_failed} series had a slice that would not decode' if n_failed else ''))
    gc.collect()
    return (studies, cache, mask)
```

In \[20\]:

linkcode

```
class SlotHead(nn.Module):

    def __init__(self, dim, n_slot, n_out, hidden=256, p=0.2, prior=False):
        super().__init__()
        self.proj = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, hidden), nn.GELU())
        self.slot_emb = nn.Parameter(torch.randn(n_slot, hidden) * 0.02)
        self.query = nn.Parameter(torch.randn(n_out, hidden) * 0.02)
        self.drop = nn.Dropout(p)
        self.out = nn.Linear(hidden, n_out)
        self.hidden = hidden
        p_ = torch.zeros(n_out, n_slot)
        if prior and n_slot == len(SLOTS) and (n_out == len(TARGETS)):
            for t, slots in SLOT_PRIOR_TABLE.items():
                if t in TARGETS:
                    p_[TARGETS.index(t), list(slots)] = SLOT_PRIOR_STRENGTH
        self.prior = prior
        if prior:
            self.register_buffer('slot_prior', p_)

    def forward(self, x, mask):
        h = self.proj(x) + self.slot_emb
        att = torch.einsum('bsh,oh->bos', h, self.query) / self.hidden ** 0.5
        if self.prior:
            att = att + self.slot_prior.unsqueeze(0)
        att = att.masked_fill(mask.unsqueeze(1) < 0.5, -10000.0).softmax(-1)
        ctx = self.drop(torch.einsum('bos,bsh->boh', att, h))
        return (ctx * self.out.weight.unsqueeze(0)).sum(-1) + self.out.bias
```

In \[21\]:

linkcode

```
class Model(nn.Module):

    def __init__(self, backbone, dim, pool='cls_mean', prior=False):
        super().__init__()
        self.backbone = backbone
        self.pool = pool
        self.head = SlotHead(dim * POOL_PARTS[pool], N_SLOT, len(TARGETS), prior=prior)
        self.register_buffer('mean', torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))

    def forward(self, imgs, mask, img_size=None):
        B, S = imgs.shape[:2]
        x = imgs.reshape(B * S, *imgs.shape[2:]).float().div_(255.0)
        if img_size is not None and img_size != x.shape[-1]:
            x = F.interpolate(x, size=(img_size, img_size), mode='bilinear', align_corners=False)
        x = (x - self.mean) / self.std
        out = self.backbone(pixel_values=x).last_hidden_state
        patch = out[:, 1:]
        parts = [out[:, 0], patch.mean(1)]
        if self.pool == 'cls_mean_focal':
            k = max(1, patch.shape[1] // 8)
            parts.append(patch.topk(k, dim=1).values.mean(1))
        feat = torch.cat(parts, dim=1).reshape(B, S, -1)
        return self.head(feat, mask)
```

In \[22\]:

linkcode

```
def build_model(unfreeze_last, source=None, variant='small', pool='cls_mean', prior=False):
    from transformers import AutoModel
    p = source if source is not None else find_dinov2(variant)
    if p is None:
        raise FileNotFoundError('DINOv2 weights not attached')
    bb = AutoModel.from_pretrained(str(p))
    n_layer = len(bb.encoder.layer)
    for prm in bb.parameters():
        prm.requires_grad = False
    for blk in bb.encoder.layer[max(0, n_layer - unfreeze_last):]:
        for prm in blk.parameters():
            prm.requires_grad = True
    for prm in bb.layernorm.parameters():
        prm.requires_grad = True
    dim = bb.config.hidden_size
    trainable = sum((p.numel() for p in bb.parameters() if p.requires_grad))
    log(f'backbone: {n_layer} blocks, last {unfreeze_last} trainable ({trainable / 1000000.0:.1f}M params), feature dim {dim * POOL_PARTS[pool]}')
    return Model(bb, dim, pool=pool, prior=prior)
```

In \[23\]:

linkcode

```
FINGERPRINT_TOL = 0.002

def fingerprint(model, dev, img_size, n_slot=None, group=None, seed=None):
    n_slot = N_SLOT if n_slot is None else n_slot
    group = GROUP if group is None else group
    seed = SEED if seed is None else seed
    g = torch.Generator().manual_seed(seed)
    imgs = torch.randint(0, 256, (2, n_slot, group, img_size, img_size), generator=g, dtype=torch.uint8).to(dev)
    mask = torch.ones(2, n_slot, device=dev)
    mask[1, -1] = 0.0
    was_training = model.training
    model.eval()
    with torch.no_grad():
        out = model(imgs, mask, img_size).float().cpu().numpy()
    if was_training:
        model.train()
    return out

def check_fingerprint(model, dev, img_size, expected, tol=FINGERPRINT_TOL, tag=''):
    got = fingerprint(model, dev, img_size)
    exp = np.asarray(expected, np.float32)
    if got.shape != exp.shape:
        raise WeightsError(f'{tag}fingerprint shape {got.shape} != stored {exp.shape}: the architecture is not the one these weights were fitted to')
    d = float(np.abs(got - exp).max())
    if d > tol:
        raise WeightsError(f'{tag}fingerprint differs by {d:.4g} (tolerance {tol:g}). The weights load but do not compute what they computed when fitted - preprocessing, resolution or architecture has moved between the two runs.')
    log(f'{tag}fingerprint matches within {d:.2g}')
    return d

class WeightsError(RuntimeError):
    pass

def find_weights(name='manifest.json'):
    import json
    base = Path('/kaggle/input')
    if not base.is_dir():
        return None
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('train_series', 'test_series')]
        if name not in files:
            continue
        try:
            man = json.loads((Path(root) / name).read_text())
        except (OSError, ValueError):
            continue
        if isinstance(man.get('members'), list) and man['members']:
            missing = [m['file'] for m in man['members'] if not (Path(root) / m['file']).is_file()]
            if missing:
                raise WeightsError(f"{root} holds a manifest listing {len(man['members'])} members but {len(missing)} of their files are absent (first {missing[0]!r})")
            return Path(root)
    return None
TTA_OVERLAP = True
TTA_POOL = 'prob'
PUBLIC_FRONTIER_TARGET_POOL = {'Fracture': 'max', 'Contusion': 'max', 'Medial Meniscus': 'max', 'Lateral Meniscus': 'max', 'ACL': 'top2', 'MCL': 'top2', "Baker's": 'max'}
TTA_TARGET_POOL = {**PUBLIC_FRONTIER_TARGET_POOL, 'Synovitis': 'original_mean'}
# No-extra-pass diversity branch: smooth focal pooling is evaluated from
# the same no-jitter public-member windows already used by the parent.
LEGACY_FOLD_SOFTPOOL_BETA = {
    'ACL': 6.0, 'MCL': 6.0,
    'Medial Meniscus': 8.0, 'Lateral Meniscus': 8.0,
    "Baker's": 8.0, 'Contusion': 8.0, 'Fracture': 10.0,
}
LEGACY_FOLD_SOFTPOOL_ALPHA = {
    'ACL': 0.20, 'MCL': 0.20,
    'Medial Meniscus': 0.25, 'Lateral Meniscus': 0.25,
    "Baker's": 0.20, 'Contusion': 0.20, 'Fracture': 0.15,
}
LEGACY_MEMBER_WEIGHT_BY_TARGET = {'Lateral Meniscus': 15.0, 'Medial OA': 2.5, 'Lateral OA': 15.0, 'Contusion': 5.0}

def window_starts(n_slice, group, overlap=None):
    overlap = TTA_OVERLAP if overlap is None else overlap
    if overlap and n_slice >= group:
        return list(range(n_slice - group + 1))
    return [g * group for g in range(max(n_slice // group, 1))]

def apply_target_window_pool(values, probs, logits, original_probs, mapping, target_idx):
    for target, mode in mapping.items():
        j = target_idx[target]
        if mode == 'max':
            values[:, j] = probs[:, :, j].max(0).values
        elif mode == 'mean':
            values[:, j] = probs[:, :, j].mean(0)
        elif mode == 'logit_mean':
            values[:, j] = torch.sigmoid(logits[:, :, j].mean(0))
        elif mode == 'original_mean':
            values[:, j] = original_probs[:, :, j].mean(0)
        elif mode in ('top2', 'top3'):
            k = min(int(mode[3:]), probs.shape[0])
            values[:, j] = probs[:, :, j].topk(k, dim=0).values.mean(0)
        else:
            raise ValueError(f'unknown TTA pooling mode for {target}: {mode}')
    return values

def legacy_fold_soft_window_pool(original_probs, target_idx):
    values = original_probs.mean(0).clone()
    for target, beta in LEGACY_FOLD_SOFTPOOL_BETA.items():
        j = target_idx[target]
        x = original_probs[:, :, j]
        weight = torch.softmax(float(beta) * x, dim=0)
        values[:, j] = (weight * x).sum(0)
    return values

@torch.no_grad()
def predict_member(model, cache, mask, idx, dev, img_size, group=None, pool=None, starts=None, jitter=False, jitter_seed=SEED, return_public_frontier=False):
    group = GROUP if group is None else group
    pool = TTA_POOL if pool is None else pool
    starts = window_starts(cache.shape[2], group) if starts is None else list(starts)
    if not starts:
        raise ValueError('predict_member was given no windows to average over')
    target_idx = {t: j for j, t in enumerate(TARGETS)}
    unknown = (set(TTA_TARGET_POOL) | set(PUBLIC_FRONTIER_TARGET_POOL)) - set(target_idx)
    if unknown:
        raise ValueError(f'unknown target(s) in TTA_TARGET_POOL: {unknown}')
    jitter_gen = torch.Generator(device=dev)
    jitter_gen.manual_seed(int(jitter_seed) % (2 ** 63 - 1))
    model.eval()
    out, public_frontier_out, public_soft_out = ([], [], [])
    for b in range(0, len(idx), EVAL_BATCH):
        sel = idx[b:b + EVAL_BATCH]
        m = torch.from_numpy(mask[sel]).to(dev)
        win_probs, win_logits, win_original_probs = ([], [], [])
        for st in starts:
            rows = torch.from_numpy(np.ascontiguousarray(cache[sel, :, st:st + group])).to(dev)
            views = [rows] + ([augment(rows, generator=jitter_gen)] if jitter else [])
            view_probs, view_logits = ([], [])
            for view in views:
                with torch.autocast('cuda', enabled=dev.type == 'cuda'):
                    z = model(view, m, img_size).float()
                view_logits.append(z)
                view_probs.append(torch.sigmoid(z))
            win_logits.append(torch.stack(view_logits).mean(0))
            win_probs.append(torch.stack(view_probs).mean(0))
            win_original_probs.append(view_probs[0])
        probs = torch.stack(win_probs)
        logits = torch.stack(win_logits)
        original_probs = torch.stack(win_original_probs)
        v = torch.sigmoid(logits.mean(0)) if pool == 'logit' else probs.mean(0)
        v = apply_target_window_pool(v, probs, logits, original_probs, TTA_TARGET_POOL, target_idx)
        out.append(v.cpu().numpy())
        if return_public_frontier:
            public_v = apply_target_window_pool(original_probs.mean(0), original_probs, logits, original_probs, PUBLIC_FRONTIER_TARGET_POOL, target_idx)
            public_frontier_out.append(public_v.cpu().numpy())
            public_soft = legacy_fold_soft_window_pool(original_probs, target_idx)
            public_soft_out.append(public_soft.cpu().numpy())
    primary = np.concatenate(out) if out else np.zeros((0, len(TARGETS)), np.float32)
    if not return_public_frontier:
        return primary
    public_frontier = np.concatenate(public_frontier_out) if public_frontier_out else np.zeros((0, len(TARGETS)), np.float32)
    public_soft = np.concatenate(public_soft_out) if public_soft_out else np.zeros((0, len(TARGETS)), np.float32)
    return (primary, public_frontier, public_soft)
BUILD_LOCK = threading.Lock()
STATE_LOCK = threading.Lock()
LEGACY_BUNDLE_FILE = 'rsna_20260807_v1.pt'
LEGACY_WEIGHT = 0.5

def find_legacy_bundle():
    base = Path('/kaggle/input')
    if not base.is_dir():
        return None
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('train_series', 'test_series')]
        if LEGACY_BUNDLE_FILE in files:
            return Path(root) / LEGACY_BUNDLE_FILE
    return None

def legacy_group_members():
    return {}

def _run_member(path, m, dev, Cte, Mte, idx, starts, jitter):
    t0 = time.time()
    with BUILD_LOCK:
        if 'state' in m:
            state, fp = (m['state'], None)
        else:
            ck = torch.load(Path(path) / m['file'], map_location='cpu', weights_only=False)
            state, fp = (ck['model'], ck.get('fingerprint'))
        model = build_model(int(m['config']['unfreeze_last']), variant=m['config']['variant'], pool=m['config'].get('pool', 'cls_mean'), prior=bool(m['config'].get('prior', False))).to(dev)
        model.load_state_dict(state)
        if fp is not None:
            check_fingerprint(model, dev, IMG, fp, tag=f"{m['id']}: ")
        else:
            log(f"  {m['id']}: no stored fingerprint (legacy bundle) -- accepted at reduced weight")
    t_ready = time.time()
    jitter_seed = SEED + int(hashlib.sha256(str(m['id']).encode()).hexdigest()[:8], 16)
    public_member = 'state' not in m
    predicted = predict_member(model, Cte, Mte, idx, dev, IMG, starts=starts, jitter=jitter, jitter_seed=jitter_seed, return_public_frontier=public_member)
    if public_member:
        p, public_p, public_soft = predicted
    else:
        p, public_p, public_soft = (predicted, None, None)
    t_done = time.time()
    del model, state
    gc.collect()
    if dev.type == 'cuda':
        with torch.cuda.device(dev):
            torch.cuda.empty_cache()
    passes = len(starts) * (2 if jitter else 1)
    return (p, public_p, public_soft, (t_ready - t0, (t_done - t_ready) / max(passes, 1)))

def _combine(per_member):
    all_ids = sorted({s for m in per_member for s in m['ids']})
    pos = {s: i for i, s in enumerate(all_ids)}
    acc = np.zeros((len(all_ids), len(TARGETS)), np.float64)
    tot = np.zeros(len(TARGETS), np.float64)
    for m in per_member:
        target_weight = m.get('target_weight')
        w = np.asarray(target_weight if target_weight is not None else [float(m.get('weight', 1.0))] * len(TARGETS), dtype=np.float64)
        if w.shape != (len(TARGETS),) or np.any(w < 0):
            raise ValueError(f"invalid target weights for {m.get('id')}: {w}")
        r = pd.DataFrame(m['pred']).rank(pct=True).to_numpy()
        acc[[pos[s] for s in m['ids']]] += r * w[None, :]
        tot += w
    if np.any(tot <= 0):
        raise ValueError(f'at least one target has no ensemble vote: {tot}')
    return (all_ids, acc / tot[None, :])

def combine_public_members_by_fold(per_member, pred_key='pred'):
    # Raw-average the four members within each fold, rank each fold,
    # then give all five folds equal weight.
    all_ids = sorted({study for member in per_member for study in member['ids']})
    position = {study: i for i, study in enumerate(all_ids)}
    groups = {}
    for i, member in enumerate(per_member):
        fold = member.get('fold')
        key = f'fold_{fold}' if fold is not None else f'member_{i}'
        groups.setdefault(key, []).append(member)
    fold_ranks, diagnostics = ([], [])
    for key, members_in_fold in sorted(groups.items()):
        matrices = []
        for member in members_in_fold:
            values = np.full((len(all_ids), len(TARGETS)), np.nan, np.float64)
            values[[position[study] for study in member['ids']]] = np.asarray(member[pred_key], np.float64)
            if np.isnan(values).any():
                raise WeightsError(f"{member.get('id')}: incomplete {pred_key} coverage")
            matrices.append(values)
        raw_fold_mean = np.mean(matrices, axis=0)
        fold_ranks.append(pd.DataFrame(raw_fold_mean).rank(method='average', pct=True).to_numpy(np.float64))
        diagnostics.append({'ensemble_group': key, 'members': len(members_in_fold)})
    if len(fold_ranks) != 5:
        raise WeightsError(f'legacy branch requires five folds, found {len(fold_ranks)}')
    return all_ids, np.mean(fold_ranks, axis=0), pd.DataFrame(diagnostics)

def blend_legacy_frontier_and_soft(frontier_rank, soft_rank):
    output = np.asarray(frontier_rank, np.float64).copy()
    for j, target in enumerate(TARGETS):
        alpha = float(LEGACY_FOLD_SOFTPOOL_ALPHA.get(target, 0.0))
        if alpha:
            output[:, j] = (1.0 - alpha) * frontier_rank[:, j] + alpha * soft_rank[:, j]
    return output

def infer_from_package(path, dev=None):
    man = json.loads((Path(path) / 'manifest.json').read_text())
    members = man['members']
    log(f'weights package: {len(members)} member(s) from {path}; {len(DEVS)} device(s)')
    test_df = pd.read_csv(ROOT / 'test.csv')
    test_series = pd.read_csv(ROOT / 'test_series.csv')
    plane_map = dict(zip(test_series['SeriesInstanceUID'], test_series['Anatomical_Plane']))
    hte = annotate(walk('test_series'))
    log(f'test header pass: {len(hte)} series')
    groups = {}
    for m in members:
        groups.setdefault(m['pixel_group'], []).append(m)
    groups.update(legacy_group_members())
    per_member, public_frontier_members = ([], [])
    est = {'fixed': None, 'win': None}

    def bank(m, ids, pred, starts, jitter, public_pred=None, public_soft=None):
        if float(np.std(pred)) < 1e-09:
            log(f"  {m['id']}: degenerate predictions; not banked")
            return
        with STATE_LOCK:
            per_member.append({'id': m['id'], 'fold': m.get('fold'), 'ids': ids, 'pred': pred, 'weight': m.get('weight', 1.0), 'target_weight': m.get('target_weight'), 'holdout': m.get('holdout')})
            if public_pred is not None and len(starts) == len(starts_full):
                if float(np.std(public_pred)) < 1e-09:
                    raise WeightsError(f"{m['id']}: degenerate public-frontier prediction")
                public_frontier_members.append({'id': m['id'], 'fold': m.get('fold'), 'ids': ids, 'pred': public_pred, 'soft_pred': public_soft})
            elif public_pred is not None:
                log(f"  {m['id']}: public-frontier vote omitted because only {len(starts)} / {len(starts_full)} windows completed")
            all_ids, acc = _combine(per_member)
            write_submission(acc, all_ids, test_df, 'submission.csv')
            log(f"  banked {m['id']} fold {m.get('fold', '?')} ({len(starts)} window(s){(', jitter' if jitter else '')}); submission.csv = weighted rank mean of {len(per_member)} member(s)")
    for gi, (key, gm) in enumerate(groups.items(), 1):
        cfg = json.loads(key)
        adopt_config_globals(cfg)
        log(f"decode group {gi}/{len(groups)}: {cfg['img']}px x {cfg['slices']} slices, crop {cfg['crop_mm']} mm -> {len(gm)} member(s)")
        st_te, Cte, Mte = build_cache(pick_slots(hte, plane_map), plane_map, lat_of(hte, 'test '), f'test g{gi}')
        idx = np.arange(len(st_te))
        starts_full = window_starts(Cte.shape[2], GROUP)
        pending = sorted(gm, key=lambda m: -(m.get('holdout') or 0))
        left_after = sum((len(g) for j, (_, g) in enumerate(groups.items(), 1) if j > gi))

        def pop_next():
            with STATE_LOCK:
                if not pending:
                    return (None, None, False)
                left = TIME_BUDGET - (time.time() - T0)
                remaining = len(pending) + left_after
                slots_left = -(-remaining // len(DEVS))
                starts, jit = (starts_full, False)
                if est['fixed'] is not None and est['win'] is not None:
                    afford = max(left * 0.9, 0.0)
                    room = afford / max(slots_left, 1)
                    if est['fixed'] + est['win'] > room:
                        log(f'  {left / 60:.0f} min left: surrendering {len(pending)} member(s); not one more fits')
                        pending.clear()
                        return (None, None, False)
                    jit = est['fixed'] + 2 * len(starts_full) * est['win'] <= room * 0.6
                    per_win = est['win'] * (2 if jit else 1)
                    n_win = int((room - est['fixed']) / per_win) if per_win > 0 else len(starts_full)
                    n_win = max(1, min(len(starts_full), n_win))
                    if n_win < len(starts_full):
                        mid = (len(starts_full) - n_win) // 2
                        starts = starts_full[mid:mid + n_win]
                return (pending.pop(0), starts, jit)

        def worker(dev):
            others = [d for d in DEVS if d is not dev]
            while True:
                m, starts, jit = pop_next()
                if m is None:
                    return
                for attempt, d in enumerate([dev] + others[:1]):
                    try:
                        p, public_p, public_soft, (fs, ws) = _run_member(path, m, d, Cte, Mte, idx, starts, jit)
                        with STATE_LOCK:
                            est['fixed'], est['win'] = (fs, ws)
                        bank(m, st_te, p, starts, jit, public_p, public_soft)
                        break
                    except Exception as exc:
                        log(f"  MEMBER {m['id']} failed on {d} ({type(exc).__name__}: {exc}); " + ('retrying on peer device' if attempt == 0 and others else 'dropped -- costs one vote, not the run'))
                        if d.type == 'cuda':
                            with torch.cuda.device(d):
                                torch.cuda.empty_cache()
        threads = [threading.Thread(target=worker, args=(d,)) for d in DEVS]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        del Cte, Mte
        gc.collect()
    if not per_member:
        raise WeightsError('no member produced predictions; submission stays at 0.5')
    all_ids, acc = _combine(per_member)
    sub = write_submission(acc, all_ids, test_df, 'submission.csv')
    log(f'final submission.csv = weighted rank mean of {len(per_member)} member(s); {sub.shape}; nulls {int(sub[TARGETS].isna().sum().sum())}')
    if len(public_frontier_members) == len(members):
        frontier_ids, frontier_acc = _combine(public_frontier_members)
        frontier_sub = write_submission(frontier_acc, frontier_ids, test_df, 'submission_public_0899.csv')
        log(f'submission_public_0899.csv = exact no-jitter public-frontier rank mean of {len(public_frontier_members)} member(s); {frontier_sub.shape}; nulls {int(frontier_sub[TARGETS].isna().sum().sum())}')
        fold_ids, fold_frontier, fold_diagnostics = combine_public_members_by_fold(public_frontier_members, 'pred')
        soft_ids, fold_soft, _ = combine_public_members_by_fold(public_frontier_members, 'soft_pred')
        if fold_ids != soft_ids:
            raise WeightsError('legacy hard/soft study order mismatch')
        legacy_prediction = blend_legacy_frontier_and_soft(fold_frontier, fold_soft)
        legacy_sub = write_submission(legacy_prediction, fold_ids, test_df, 'submission_legacy_fold_blend.csv')
        fold_diagnostics.to_csv('legacy_fold_diagnostics.csv', index=False)
        log(f'legacy DINO aggregation written from five folds; {legacy_sub.shape}')
    else:
        log(f'public-frontier fallback not emitted: {len(public_frontier_members)} / {len(members)} required public members completed')
    return sub

def adopt_config_globals(cfg):
    global IMG, CACHE_IMG, GROUP, CACHE_SLICES, N_GROUP, CROP_MM, SLICE_BAND, RULES
    CACHE_IMG = IMG = int(cfg['img'])
    GROUP = int(cfg['group'])
    CACHE_SLICES = int(cfg['slices'])
    N_GROUP = max(CACHE_SLICES // GROUP, 1)
    CROP_MM = float(cfg['crop_mm'])
    SLICE_BAND = tuple((float(x) for x in cfg['band']))
    rules = cfg.get('rules') or RULES_NATIVE
    unknown = {k: v for k, v in rules.items() if k not in RULES_NATIVE or v not in (RULES_NATIVE[k], RULES_LEGACY[k])}
    if unknown:
        raise WeightsError(f'the members record pixel rules this pipeline cannot reproduce: {unknown}')
    RULES = {**RULES_NATIVE, **rules}
    if [s[0] for s in SLOTS] != list(cfg['slots']):
        raise WeightsError(f"the members were fitted on slots {cfg['slots']} and this pipeline defines {[s[0] for s in SLOTS]}; a weight would be read against the wrong slot")
```

In \[24\]:

linkcode

```
def take_group(cache_rows, g):
    return cache_rows[:, :, g * GROUP:(g + 1) * GROUP]

def augment(imgs, generator=None):
    lead = imgs.shape[:-3]
    x = imgs.reshape(-1, *imgs.shape[-3:]).float()
    n, dev = (x.shape[0], x.device)
    rot = (torch.rand(n, device=dev, generator=generator) - 0.5) * 2 * (AUG_ROT_DEG * np.pi / 180)
    sc = 1.0 + torch.rand(n, device=dev, generator=generator) * AUG_SCALE
    tx = (torch.rand(n, device=dev, generator=generator) - 0.5) * 2 * AUG_SHIFT
    ty = (torch.rand(n, device=dev, generator=generator) - 0.5) * 2 * AUG_SHIFT
    cos, sin = (torch.cos(rot) / sc, torch.sin(rot) / sc)
    theta = torch.zeros(n, 2, 3, device=dev, dtype=torch.float32)
    theta[:, 0, 0], theta[:, 0, 1], theta[:, 0, 2] = (cos, -sin, tx)
    theta[:, 1, 0], theta[:, 1, 1], theta[:, 1, 2] = (sin, cos, ty)
    grid = F.affine_grid(theta, x.shape, align_corners=False)
    x = F.grid_sample(x, grid, mode='bilinear', padding_mode='border', align_corners=False)
    scale = 1.0 + (torch.rand(n, 1, 1, 1, device=dev, generator=generator) - 0.5) * 2 * AUG_INTENSITY
    x = (x * scale).clamp(0, 255)
    return x.reshape(*lead, *x.shape[-3:]).to(imgs.dtype)

@torch.no_grad()
def predict(model, cache, mask, idx, dev, img_size=None):
    model.eval()
    out = []
    for b in range(0, len(idx), EVAL_BATCH):
        sel = idx[b:b + EVAL_BATCH]
        m = torch.from_numpy(mask[sel]).to(dev)
        acc = None
        for g in range(N_GROUP):
            rows = torch.from_numpy(np.ascontiguousarray(cache[sel, :, g * GROUP:(g + 1) * GROUP])).to(dev)
            with torch.autocast('cuda', enabled=dev.type == 'cuda'):
                z = model(rows, m, img_size).float()
            acc = z if acc is None else acc + z
        out.append(torch.sigmoid(acc / N_GROUP).cpu().numpy())
    return np.concatenate(out) if out else np.zeros((0, len(TARGETS)), np.float32)

def macro_auc(y, p):
    from sklearn.metrics import roc_auc_score
    return float(np.nanmean([roc_auc_score(y[:, j], p[:, j]) if len(set(y[:, j])) > 1 else np.nan for j in range(y.shape[1])]))
```

In \[25\]:

linkcode

```
import math
import cv2

'Runtime helpers embedded into the V26 Kaggle notebook.\n\nThe exact RTAHMIL class from the public report-teacher notebook is prepended by the\ncandidate builder. This file contains only hidden-test feature extraction, checkpoint\ninference, and the fail-safe Synovitis blend.\n'
```

Out\[25\]:

```
'Runtime helpers embedded into the V26 Kaggle notebook.\n\nThe exact RTAHMIL class from the public report-teacher notebook is prepended by the\ncandidate builder. This file contains only hidden-test feature extraction, checkpoint\ninference, and the fail-safe Synovitis blend.\n'
```

In \[26\]:

linkcode

```
import base64
import gc
import hashlib
import io
import json
import math
import os
import random
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path
import cv2
import joblib
import numpy as np
import pandas as pd
import pydicom
from scipy.stats import rankdata
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel
```

In \[27\]:

linkcode

```
def write_submission(pred, studies, test_df, path):
    sub = pd.DataFrame(pd.DataFrame(pred).rank(pct=True).values, columns=TARGETS)
    sub.insert(0, 'StudyInstanceUID', studies)
    sub = test_df[['StudyInstanceUID']].merge(sub, on='StudyInstanceUID', how='left')
    sub[TARGETS] = sub[TARGETS].fillna(0.5)
    sub.to_csv(path, index=False)
    return sub

def write_benchmark_submission():
    t = pd.read_csv(ROOT / 'test.csv')
    for c in TARGETS:
        t[c] = 0.5
    t.to_csv('submission.csv', index=False)

def _v37_validate_submission(path, test_df, tag):
    path = Path(path)
    frame = pd.read_csv(path)
    expected = ['StudyInstanceUID'] + TARGETS
    if list(frame.columns) != expected:
        raise ValueError(f'{tag}: columns differ from the competition contract')
    if len(frame) != len(test_df) or not frame['StudyInstanceUID'].is_unique:
        raise ValueError(f'{tag}: row count or StudyInstanceUID uniqueness failed')
    if set(frame['StudyInstanceUID'].astype(str)) != set(test_df['StudyInstanceUID'].astype(str)):
        raise ValueError(f'{tag}: StudyInstanceUID set differs from test.csv')
    values = frame[TARGETS].to_numpy(np.float64)
    if not np.isfinite(values).all():
        raise ValueError(f'{tag}: non-finite prediction')
    return test_df[['StudyInstanceUID']].merge(frame, on='StudyInstanceUID', how='left')

def main():
    write_benchmark_submission()
    pkg = find_weights()
    if pkg is not None:
        dev = DEVS[0]
        infer_from_package(pkg, dev)
        try:
            test_df = pd.read_csv(ROOT / 'test.csv')
            native_path = Path('submission.csv')
            public_path = Path('submission_public_0899.csv')
            native = _v37_validate_submission(native_path, test_df, 'native 24-member')
            public = _v37_validate_submission(public_path, test_df, 'public DINO frontier')
            native.to_csv('submission_native_v38.csv', index=False)
            public.to_csv(native_path, index=False)
            promoted = _v37_validate_submission(native_path, test_df, 'V40 primary')
            if not promoted.equals(public):
                raise AssertionError('V40 serialization differs from validated public frontier')
            log('V40 primary = exact no-jitter public-frontier target pooling; native 24-member output retained')
        except Exception as public_frontier_error:
            log(f'public-frontier promotion skipped safely: {public_frontier_error}')
            traceback.print_exc()
        log('done')
        return
    read_labels(pd.read_csv(ROOT / 'train.csv', usecols=['StudyInstanceUID', 'Report']))
    test_df = pd.read_csv(ROOT / 'test.csv')
    test_series = pd.read_csv(ROOT / 'test_series.csv')
    train_df = pd.read_csv(ROOT / 'train.csv')
    train_series = pd.read_csv(ROOT / 'train_series.csv')
    log(f'train {train_df.shape} test {test_df.shape}')
    both = pd.concat([train_series, test_series])
    plane_map = dict(zip(both['SeriesInstanceUID'], both['Anatomical_Plane']))
    log('header pass: test')
    hte = annotate(walk('test_series'))
    log(f'  {len(hte)} test series')
    log('header pass: train')
    htr = annotate(walk('train_series'))
    log(f'  {len(htr)} train series')
    slots_te, slots_tr = (pick_slots(hte, plane_map), pick_slots(htr, plane_map))
    cov = pd.Series([len(v) for v in slots_tr.values()]).describe()
    log(f"train slots per study: mean {cov['mean']:.2f} min {cov['min']:.0f} max {cov['max']:.0f}")
    st_tr, Ctr, Mtr = build_cache(slots_tr, plane_map, lat_of(htr, 'train '), 'train')
    st_te, Cte, Mte = build_cache(slots_te, plane_map, lat_of(hte, 'test '), 'test')
    t_lab = time.time()
    lab = read_labels(train_df)
    log(f'derived labels for {len(lab)} studies in {time.time() - t_lab:.1f}s')
    gold = train_df.set_index('StudyInstanceUID')[TARGETS]
    gold = gold[gold.notna().all(axis=1)]
    Y = np.zeros((len(st_tr), len(TARGETS)), np.float32)
    W = np.zeros_like(Y)
    for i, st in enumerate(st_tr):
        if st in gold.index:
            Y[i], W[i] = (gold.loc[st].values, 3.0)
        elif st in lab.index:
            r = lab.loc[st]
            Y[i] = r[TARGETS].values
            W[i] = 0.25 + 0.75 * r[[t + '__conf' for t in TARGETS]].values
    keep = np.where(W.sum(1) > 0)[0]
    log(f'supervised {len(keep)} of {len(st_tr)} studies (annotated {len(gold)})')
    import hashlib
    rep = train_df.set_index('StudyInstanceUID')['Report'].fillna('')
    grp = np.array([int(hashlib.md5(rep.get(s, s).encode()).hexdigest()[:8], 16) % 5 for s in st_tr])
    va = np.array([i for i in keep if grp[i] == 0])
    tr = np.array([i for i in keep if grp[i] != 0])
    if len(va) == 0 or len(tr) < BATCH_STUDIES:
        cut = max(1, len(keep) // 5)
        va, tr = (keep[:cut], keep[cut:])
    log(f'train {len(tr)} / holdout {len(va)} studies')
    gpos = {s: i for i, s in enumerate(st_tr)}
    va_set = set(va.tolist())
    gi = np.array([gpos[s] for s in gold.index if s in gpos and gpos[s] in va_set])
    gold_y = gold.loc[[st_tr[i] for i in gi]].values.astype(int) if len(gi) else None
    yv = (Y[va] > 0.5).astype(int)
    log(f'annotation check: {len(gi)} of {len(gold)} annotated studies are in the holdout')
    dev = DEVS[0]
    results, test_preds = ({}, {})
    for cfg in RUNS:
        pitch = CROP_MM / cfg['img']
        log(f"=== {cfg['name']}: {cfg['img']} px, {pitch:.3f} mm/pixel, {pitch * 14:.2f} mm per patch token ===")
        torch.manual_seed(SEED)
        model = build_model(UNFREEZE_LAST).to(dev)
        opt = torch.optim.AdamW([{'params': [p for p in model.backbone.parameters() if p.requires_grad], 'lr': LR_BACKBONE}, {'params': model.head.parameters(), 'lr': LR_HEAD}], weight_decay=WEIGHT_DECAY)
        steps = max(EPOCHS * (len(tr) // BATCH_STUDIES), 1)
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=[LR_BACKBONE, LR_HEAD], total_steps=steps, pct_start=0.15)
        scaler = torch.amp.GradScaler('cuda', enabled=dev.type == 'cuda')
        best, best_state, best_annot = (-1.0, None, float('nan'))
        for ep in range(EPOCHS):
            model.train()
            perm = np.random.permutation(tr)
            tot, nstep = (0.0, 0)
            for b in range(0, len(perm) - BATCH_STUDIES + 1, BATCH_STUDIES):
                sel = perm[b:b + BATCH_STUDIES]
                rows = torch.from_numpy(Ctr[sel]).to(dev)
                g = int(torch.randint(N_GROUP, (1,)).item())
                imgs = augment(take_group(rows, g))
                m = torch.from_numpy(Mtr[sel]).to(dev)
                y = torch.from_numpy(Y[sel]).to(dev)
                w = torch.from_numpy(W[sel]).to(dev)
                with torch.autocast('cuda', enabled=dev.type == 'cuda'):
                    loss = (F.binary_cross_entropy_with_logits(model(imgs, m, cfg['img']), y, reduction='none') * w).mean()
                opt.zero_grad(set_to_none=True)
                scaler.scale(loss).backward()
                scaler.step(opt)
                scaler.update()
                sched.step()
                tot += loss.item()
                nstep += 1
            pv = predict(model, Ctr, Mtr, va, dev, cfg['img'])
            d = macro_auc(yv, pv)
            g_auc = float('nan')
            if gold_y is not None and len(gi):
                g_auc = macro_auc(gold_y, predict(model, Ctr, Mtr, gi, dev, cfg['img']))
            log(f'  epoch {ep + 1}/{EPOCHS}  loss {tot / max(nstep, 1):.4f}  holdout {d:.4f}  annot(n={len(gi)}) {g_auc:.4f}')
            if d > best:
                best, best_annot = (d, g_auc)
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            if time.time() - T0 > TIME_BUDGET:
                log('  time budget reached')
                break
        if best_state is not None:
            model.load_state_dict(best_state)
        results[cfg['name']] = (best, best_annot)
        test_preds[cfg['name']] = predict(model, Cte, Mte, np.arange(len(st_te)), dev, cfg['img'])
        log(f"  {cfg['name']}: best holdout {best:.4f} (annot {best_annot:.4f})")
        del model, opt, sched, scaler, best_state
        gc.collect()
        if dev.type == 'cuda':
            torch.cuda.empty_cache()
    log('---- summary ----')
    for n, (d, g_auc) in results.items():
        log(f'  {n:12s} holdout {d:.4f}   annot {g_auc:.4f}')
    pick = max(results, key=lambda k: results[k][0])
    log(f'best on the holdout: {pick} ({results[pick][0]:.4f})')
    for name, pred in test_preds.items():
        sub = write_submission(pred, st_te, test_df, f'submission_{name}.csv')
        log(f'  submission_{name}.csv {sub.shape}; nulls {int(sub[TARGETS].isna().sum().sum())}')
    ens = np.mean([pd.DataFrame(p).rank(pct=True).values for p in test_preds.values()], axis=0)
    write_submission(ens, st_te, test_df, 'submission_rankmean.csv')
    log(f'  submission_rankmean.csv (rank mean of {len(test_preds)})')
    sub = write_submission(test_preds[pick], st_te, test_df, 'submission.csv')
    log(f'submission.csv = {pick}; {sub.shape}; nulls {int(sub[TARGETS].isna().sum().sum())}')
    print(sub.head().to_string())
```

In \[28\]:

linkcode

```
try:
    main()
except LabelSourceError:
    traceback.print_exc()
    raise
except Exception:
    traceback.print_exc()
    t = pd.read_csv(find_root() / 'test.csv')
    for c in TARGETS:
        t[c] = 0.5
    t.to_csv('submission.csv', index=False)
    print('wrote fallback submission.csv')
log('done')
```

```
[   20.4s] weights package: 20 member(s) from /kaggle/input/rsna-knee-weights; 2 device(s)
[   20.4s] test header pass: 15 series
[   20.4s] decode group 1/1: 336px x 12 slices, crop 130.0 mm -> 20 member(s)
[   20.5s] test laterality: 1 from the tag, 2 from geometry, 0 unresolved; tag and geometry disagree on 0 (0.0% of the tagged)
[   20.5s] test g1: cache (3, 6, 12, 336, 336) = 0.0 GB
[   20.5s] test g1: ordering 12 slot-series (469 slice headers)
[   22.5s] test g1: ordered 12/12 by geometry (0 kept arbitrary) in 2s
[   22.5s] test g1: decoding 12 slot-series
[   23.3s]   test g1 12/12
[   23.3s] test g1: 12/12 slots filled
```

```
[   26.1s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   27.1s] e5427d6c21: fingerprint matches within 2.8e-06
```

```
[   27.9s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   28.5s]   banked e5427d6c21 fold 2 (10 window(s)); submission.csv = weighted rank mean of 1 member(s)
[   28.8s] d47313baef: fingerprint matches within 2.1e-06
[   29.7s]   banked d47313baef fold 2 (10 window(s)); submission.csv = weighted rank mean of 2 member(s)
```

```
[   29.9s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   30.3s] ea3fbf6edf: fingerprint matches within 3.8e-06
```

```
[   31.2s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   31.7s] 5f8ba4c5ea: fingerprint matches within 3.3e-06
[   32.1s]   banked ea3fbf6edf fold 2 (10 window(s), jitter); submission.csv = weighted rank mean of 3 member(s)
```

```
[   33.2s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   33.5s]   banked 5f8ba4c5ea fold 2 (10 window(s), jitter); submission.csv = weighted rank mean of 4 member(s)
[   33.7s] 013dc75703: fingerprint matches within 3.3e-06
```

```
[   35.1s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   35.5s]   banked 013dc75703 fold 4 (10 window(s), jitter); submission.csv = weighted rank mean of 5 member(s)
[   35.8s] 2f7e785e82: fingerprint matches within 1.1e-06
```

```
[   37.1s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   37.5s]   banked 2f7e785e82 fold 4 (10 window(s), jitter); submission.csv = weighted rank mean of 6 member(s)
[   37.8s] 8baecb9d1b: fingerprint matches within 2.4e-06
```

```
[   39.1s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   39.6s]   banked 8baecb9d1b fold 4 (10 window(s), jitter); submission.csv = weighted rank mean of 7 member(s)
[   39.8s] 44bc3c6f14: fingerprint matches within 3.8e-06
```

```
[   40.7s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   41.1s] 44128e3ff3: fingerprint matches within 4.3e-06
[   41.5s]   banked 44bc3c6f14 fold 0 (10 window(s), jitter); submission.csv = weighted rank mean of 8 member(s)
```

```
[   42.5s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   43.1s] 84079fe8cb: fingerprint matches within 1.2e-06
[   43.1s]   banked 44128e3ff3 fold 0 (10 window(s), jitter); submission.csv = weighted rank mean of 9 member(s)
```

```
[   43.9s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   44.3s] ed427aa10a: fingerprint matches within 4.6e-06
[   44.7s]   banked 84079fe8cb fold 3 (10 window(s), jitter); submission.csv = weighted rank mean of 10 member(s)
```

```
[   45.5s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   45.9s] 2dce50ebd9: fingerprint matches within 3.8e-06
[   46.3s]   banked ed427aa10a fold 0 (10 window(s), jitter); submission.csv = weighted rank mean of 11 member(s)
[   47.6s]   banked 2dce50ebd9 fold 0 (10 window(s), jitter); submission.csv = weighted rank mean of 12 member(s)
```

```
[   48.0s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   48.4s] 3d1f4c48fc: fingerprint matches within 1.3e-06
[   50.0s]   banked 3d1f4c48fc fold 4 (10 window(s), jitter); submission.csv = weighted rank mean of 13 member(s)
```

```
[   50.2s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   50.6s] 91f171fe6f: fingerprint matches within 2.6e-06
[   52.1s]   banked 91f171fe6f fold 1 (10 window(s), jitter); submission.csv = weighted rank mean of 14 member(s)
```

```
[   52.3s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   52.7s] 8476b29285: fingerprint matches within 4.4e-06
```

```
[   54.0s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   54.4s]   banked 8476b29285 fold 1 (10 window(s), jitter); submission.csv = weighted rank mean of 15 member(s)
[   54.7s] 72081758ce: fingerprint matches within 2.9e-06
[   56.2s]   banked 72081758ce fold 3 (10 window(s), jitter); submission.csv = weighted rank mean of 16 member(s)
```

```
[   56.5s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   56.8s] 7f8321affc: fingerprint matches within 2.9e-06
```

```
[   57.9s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   58.6s] 1e553ba481: fingerprint matches within 1.7e-06
[   58.6s]   banked 7f8321affc fold 3 (10 window(s), jitter); submission.csv = weighted rank mean of 17 member(s)
```

```
[   59.6s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   59.9s] b7c37cc80e: fingerprint matches within 1.1e-06
[   60.3s]   banked 1e553ba481 fold 1 (10 window(s), jitter); submission.csv = weighted rank mean of 18 member(s)
```

```
[   61.1s] backbone: 12 blocks, last 6 trainable (10.7M params), feature dim 768
[   61.4s] f335c812fe: fingerprint matches within 2.9e-06
[   61.9s]   banked b7c37cc80e fold 3 (10 window(s), jitter); submission.csv = weighted rank mean of 19 member(s)
[   63.1s]   banked f335c812fe fold 1 (10 window(s), jitter); submission.csv = weighted rank mean of 20 member(s)
[   63.4s] final submission.csv = weighted rank mean of 20 member(s); (3, 13); nulls 0
[   63.4s] submission_public_0899.csv = exact no-jitter public-frontier rank mean of 20 member(s); (3, 13); nulls 0
[   63.4s] legacy DINO aggregation written from five folds; (3, 13)
[   63.4s] V40 primary = exact no-jitter public-frontier target pooling; native 24-member output retained
[   63.4s] done
[   63.4s] done
```

linkcode

## Stage 2 — A5: attention-pooling folds at 45% [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Stage-2-%E2%80%94-A5:-attention-pooling-folds-at-45%25)

In \[29\]:

linkcode

```
_A5_SAVED = dict(globals())
import gc, os, time, warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import pydicom
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
warnings.filterwarnings('ignore')
cv2.setNumThreads(1)
CROP_MM = 130.0
SIZE = 336
SLICE_BAND = (0.12, 0.88)
N_SLICE = 16
INTENSITY = 'slice'
SLOTS = [('Sagittal', 1), ('Sagittal', 0), ('Coronal', 1), ('Coronal', 0), ('Axial', 1), ('Axial', 0)]
N_SLOT = len(SLOTS)
LABELS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA', 'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']

def _find_dir(*names):
    root = Path('/kaggle/input')
    cand = []
    for n in names:
        cand += [root / n, root / 'competitions' / n, root / 'datasets' / n]
        for parent in (root / 'datasets', root / 'competitions', root):
            if parent.is_dir():
                try:
                    cand += [d / n for d in parent.iterdir() if d.is_dir()]
                except OSError:
                    pass
    for p in cand:
        if p.is_dir():
            return p
    return None
COMP = _find_dir('rsna-knee-abnormality-detection')
CKPT = _find_dir('knee-mri-fold-weights')
assert COMP is not None, 'competition data not attached'
assert CKPT is not None, 'fold weights not attached'
assert (COMP / 'sample_submission.csv').exists(), f'no competition data at {COMP}'
assert list(CKPT.glob('*_f*.pt')), f'no checkpoints at {CKPT}'
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'competition : {COMP}')
print(f'checkpoints : {CKPT}')
print(f'device      : {DEV}')
for i in range(torch.cuda.device_count() if DEV == 'cuda' else 0):
    cc = torch.cuda.get_device_capability(i)
    print(f'  gpu{i}       : {torch.cuda.get_device_name(i)} sm_{cc[0]}{cc[1]}, {torch.cuda.get_device_properties(i).total_memory / 2 ** 30:.0f} GiB, native bf16={cc >= (8, 0)}')
```

```
competition : /kaggle/input/rsna-knee-abnormality-detection
checkpoints : /kaggle/input/knee-mri-fold-weights
device      : cuda
  gpu0       : Tesla T4 sm_75, 15 GiB, native bf16=False
  gpu1       : Tesla T4 sm_75, 15 GiB, native bf16=False
```

In \[30\]:

linkcode

```
SERIES_ROOT = COMP / 'test_series'
if not SERIES_ROOT.exists():
    SERIES_ROOT = COMP / 'train_series'
print('series root:', SERIES_ROOT)

def ordered_files(sdir, cap=64):
    keyed = []
    for f in sdir.glob('*.dcm'):
        try:
            ds = pydicom.dcmread(str(f), stop_before_pixels=True)
            keyed.append((int(ds.InstanceNumber), str(f)))
        except Exception:
            continue
        if len(keyed) >= cap * 4:
            break
    return [f for _, f in sorted(keyed)]

def series_side(path):
    try:
        return float(pydicom.dcmread(path, stop_before_pixels=True).ImagePositionPatient[0])
    except Exception:
        return 0.0

def read_crop(path):
    try:
        ds = pydicom.dcmread(path)
        arr = ds.pixel_array.astype(np.float32)
    except Exception:
        return None
    try:
        ps = float(ds.PixelSpacing[0])
    except Exception:
        ps = CROP_MM / max(arr.shape)
    half = int(round(CROP_MM / ps / 2))
    cy, cx = (arr.shape[0] // 2, arr.shape[1] // 2)
    y0, y1 = (max(0, cy - half), min(arr.shape[0], cy + half))
    x0, x1 = (max(0, cx - half), min(arr.shape[1], cx + half))
    crop = arr[y0:y1, x0:x1]
    return None if crop.size == 0 else crop

def window(crop, lo, hi, flip):
    c = np.clip((crop - lo) / max(hi - lo, 1e-06), 0, 1)
    img = cv2.resize(c, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    return img[:, ::-1].copy() if flip else img

def render(path, flip):
    crop = read_crop(path)
    if crop is None:
        return None
    lo, hi = np.percentile(crop[::4, ::4], [1, 99])
    return window(crop, lo, hi, flip)

def build_study(args):
    idx, study, recs = args
    out = np.zeros((N_SLOT, N_SLICE, SIZE, SIZE), np.uint8)
    mask = np.zeros(N_SLOT, np.uint8)
    rows = pd.DataFrame(recs)
    if len(rows):
        for s_i, (plane, fs) in enumerate(SLOTS):
            sub = rows[(rows.Anatomical_Plane == plane) & (rows.Fat_Suppression == fs)]
            if sub.empty:
                continue
            files = ordered_files(SERIES_ROOT / study / sub.iloc[0].SeriesInstanceUID)
            if not files:
                continue
            flip = plane != 'Sagittal' and series_side(files[0]) < 0
            lo, hi = SLICE_BAND
            i0 = int(round(lo * (len(files) - 1)))
            i1 = int(round(hi * (len(files) - 1)))
            avail = list(range(i0, i1 + 1))
            if len(avail) >= N_SLICE:
                picks = [avail[int(round(t))] for t in np.linspace(0, len(avail) - 1, N_SLICE)]
                off = 0
            else:
                picks, off = (avail, (N_SLICE - len(avail)) // 2)
            if INTENSITY == 'series':
                crops = [read_crop(files[p]) for p in picks]
                got = [x for x in crops if x is not None]
                if got:
                    samp = np.concatenate([x[::4, ::4].ravel() for x in got])
                    lo_, hi_ = np.percentile(samp, [1, 99])
                    for c, x in enumerate(crops):
                        if x is None:
                            x = read_crop(files[min(len(files) - 1, picks[c] + 1)])
                        if x is not None:
                            out[s_i, off + c] = (window(x, lo_, hi_, flip) * 255).astype(np.uint8)
            else:
                for c, p in enumerate(picks):
                    img = render(files[p], flip)
                    if img is None:
                        img = render(files[min(len(files) - 1, p + 1)], flip)
                    if img is not None:
                        out[s_i, off + c] = (img * 255).astype(np.uint8)
            mask[s_i] = len(picks)
    return (idx, out, mask)
sub_df = pd.read_csv(COMP / 'sample_submission.csv')
ser_csv = pd.read_csv(COMP / 'test_series.csv')
if not (COMP / 'test_series').exists():
    ser_csv = pd.read_csv(COMP / 'train_series.csv')
ser_csv = ser_csv.loc[:, ~ser_csv.columns.duplicated()]
studies = sub_df.StudyInstanceUID.tolist()
by = {s: g.to_dict('records') for s, g in ser_csv[ser_csv.StudyInstanceUID.isin(set(studies))].groupby('StudyInstanceUID')}
print(f'{len(studies):,} test studies, {len(by):,} with series metadata')
```

```
series root: /kaggle/input/rsna-knee-abnormality-detection/test_series
3 test studies, 3 with series metadata
```

In \[31\]:

linkcode

```
N_SLOT_TYPES, MASK_IDX = (6, 0)

def segment_softmax(scores, sidx, B):
    T, K = scores.shape
    idx = sidx.unsqueeze(1).expand(-1, K)
    m = torch.full((B, K), float('-inf'), device=scores.device, dtype=scores.dtype)
    m = m.scatter_reduce(0, idx, scores, reduce='amax', include_self=True)
    e = (scores - m[sidx]).exp()
    s = torch.zeros(B, K, device=scores.device, dtype=scores.dtype).index_add_(0, sidx, e)
    return e / s[sidx].clamp(min=1e-06)

class MeanMaxPool(nn.Module):

    def forward(self, f, sidx, B, slot=None, return_attn=False):
        D = f.shape[1]
        cnt = torch.zeros(B, device=f.device, dtype=f.dtype).index_add_(0, sidx, torch.ones(f.shape[0], device=f.device, dtype=f.dtype))
        mean = torch.zeros(B, D, device=f.device, dtype=f.dtype).index_add_(0, sidx, f)
        mean = mean / cnt.clamp(min=1).unsqueeze(1)
        mx = torch.full((B, D), -10000.0, device=f.device, dtype=f.dtype)
        mx = mx.scatter_reduce(0, sidx.unsqueeze(1).expand(-1, D), f, reduce='amax', include_self=True)
        return (torch.cat([mean, mx], 1), None)

class LabelAttentionPool(nn.Module):

    def __init__(self, d, n_labels=12, n_heads=4, slot_bias=True):
        super().__init__()
        self.d, self.k, self.h = (d, n_labels, n_heads)
        self.q = nn.Parameter(torch.randn(n_labels, d) * 0.02)
        self.key, self.val = (nn.Linear(d, d), nn.Linear(d, d))
        self.slot_bias = nn.Parameter(torch.zeros(n_labels, N_SLOT_TYPES + 1)) if slot_bias else None

    def forward(self, f, sidx, B, slot=None, return_attn=False):
        scores = self.key(f) @ self.q.t() / self.d ** 0.5
        if self.slot_bias is not None and slot is not None:
            scores = scores + self.slot_bias.t()[slot]
        a = segment_softmax(scores, sidx, B)
        out = torch.zeros(B, self.k, self.d, device=f.device, dtype=f.dtype)
        out = out.index_add_(0, sidx, a.unsqueeze(-1) * self.val(f).unsqueeze(1))
        return (out, a)

class TokenXAttnPool(nn.Module):

    def __init__(self, d, n_labels=12, n_heads=6, dropout=0.2):
        super().__init__()
        self.d, self.k = (d, n_labels)
        self.q = nn.Parameter(torch.randn(n_labels, d) * 0.02)
        self.slot_emb = nn.Embedding(N_SLOT_TYPES + 1, d, padding_idx=0)
        self.kv_norm = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, n_heads, dropout=dropout, batch_first=True)

    def forward(self, tok, sidx, B, slot=None, return_attn=False):
        T, N, D = tok.shape
        cnt = torch.bincount(sidx, minlength=B)
        S = int(cnt.max().item())
        starts = torch.cumsum(cnt, 0) - cnt
        pos = torch.arange(T, device=tok.device) - starts[sidx]
        kv = tok + self.slot_emb(slot).unsqueeze(1)
        pad = tok.new_zeros(B, S, N, D)
        pad[sidx, pos] = kv
        keep = torch.zeros(B, S, dtype=torch.bool, device=tok.device)
        keep[sidx, pos] = True
        kpm = ~keep.repeat_interleave(N, dim=1)
        pad = self.kv_norm(pad.reshape(B, S * N, D))
        q = self.q.unsqueeze(0).expand(B, -1, -1)
        att, w = self.attn(q, pad, pad, key_padding_mask=kpm, need_weights=return_attn, average_attn_weights=True)
        cls = tok[:, 0]
        mean = torch.zeros(B, D, device=tok.device, dtype=tok.dtype).index_add_(0, sidx, cls) / cnt.clamp(min=1).unsqueeze(1)
        mx = torch.full((B, D), -10000.0, device=tok.device, dtype=tok.dtype)
        mx = mx.scatter_reduce(0, sidx.unsqueeze(1).expand(-1, D), cls, reduce='amax', include_self=True)
        base = torch.cat([mean, mx], 1).unsqueeze(1).expand(-1, self.k, -1)
        return (torch.cat([att, base], -1), w)

class ViTSlotToken(nn.Module):

    def __init__(self, vit, n_cat, dim=None):
        super().__init__()
        self.vit = vit
        d = dim or vit.embed_dim
        self.tok = nn.Embedding(n_cat + 1, d, padding_idx=MASK_IDX)
        self.num_features = vit.num_features
        self._orig_prefix = getattr(vit, 'num_prefix_tokens', 1)
        vit.num_prefix_tokens = self._orig_prefix + 1
        for blk in vit.blocks:
            a = getattr(blk, 'attn', None)
            if a is not None and hasattr(a, 'num_prefix_tokens'):
                a.num_prefix_tokens = a.num_prefix_tokens + 1

    @staticmethod
    def _maybe(mod, x):
        return x if mod is None else mod(x)

    def forward_features(self, x, cat):
        v = self.vit
        x = v.patch_embed(x)
        pos = v._pos_embed(x)
        rope = None
        if isinstance(pos, tuple):
            x, rope = pos
        else:
            x = pos
        x = self._maybe(getattr(v, 'patch_drop', None), x)
        x = self._maybe(getattr(v, 'norm_pre', None), x)
        npt = self._orig_prefix
        tok = self.tok(cat).unsqueeze(1)
        x = torch.cat([x[:, :npt], tok, x[:, npt:]], dim=1)
        if rope is not None:
            if getattr(v, 'rope_mixed', False):
                for i, blk in enumerate(v.blocks):
                    x = blk(x, rope=rope[i])
            else:
                for blk in v.blocks:
                    x = blk(x, rope=rope)
        else:
            x = v.blocks(x)
        return v.norm(x)

    def forward_head(self, x, pre_logits=True):
        return self.vit.forward_head(x, pre_logits=pre_logits)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

class _GatedDepthBlock(nn.Module):

    def __init__(self, n_slice, dropout=0.0, ls_init=0.1):
        super().__init__()
        self.norm = nn.GroupNorm(1, n_slice)
        self.v = nn.Conv2d(n_slice, n_slice, 1)
        self.g = nn.Conv2d(n_slice, n_slice, 1)
        self.out = nn.Conv2d(n_slice, n_slice, 1)
        self.gamma = nn.Parameter(torch.full((n_slice, 1, 1), ls_init))
        self.drop = nn.Dropout2d(dropout) if dropout else nn.Identity()

    def forward(self, x):
        z = self.norm(x)
        return x + self.gamma * self.drop(self.out(self.v(z) * F.silu(self.g(z))))

class DepthCompress(nn.Module):

    def __init__(self, n_slice=16, out_ch=3, depth=1, dropout=0.0, ls_init=0.1, imagenet=True, proj_noise=0.25):
        super().__init__()
        self.imagenet = imagenet
        self.blocks = nn.ModuleList([_GatedDepthBlock(n_slice, dropout, ls_init) for _ in range(depth)])
        self.proj = nn.Conv2d(n_slice, out_ch, 1, bias=True)
        if imagenet:
            self.register_buffer('mu', torch.tensor(IMAGENET_MEAN).view(1, -1, 1, 1))
            self.register_buffer('sd', torch.tensor(IMAGENET_STD).view(1, -1, 1, 1))

    def forward(self, x):
        keep = (x.amax(dim=1, keepdim=True) > 0).to(x.dtype)
        z = x
        for b in self.blocks:
            z = b(z)
        z = self.proj(z)
        if self.imagenet:
            z = (z - self.mu.to(z.dtype)) / self.sd.to(z.dtype)
        return z * keep
N_PLANE, N_CONTRAST = (3, 2)
_PLANE_OF = lambda s: torch.clamp(s - 1, 0, 5) // 2
_CONTRAST_OF = lambda s: torch.clamp(s - 1, 0, 5) % 2

class SlotDepthMixer(nn.Module):

    def __init__(self, n_slice=16, ksize=5, alpha_max=0.25):
        super().__init__()
        self.n_slice, self.ksize, self.r = (n_slice, ksize, ksize // 2)
        self.alpha_max = alpha_max
        b = torch.tensor([1.0, 4.0, 6.0, 4.0, 1.0])
        self.register_buffer('base', b.log()[self.r:])
        n_u = self.r + 1
        self.shared = nn.Parameter(torch.zeros(n_u))
        self.plane_k = nn.Parameter(torch.zeros(N_PLANE, n_u))
        self.contrast_k = nn.Parameter(torch.zeros(N_CONTRAST, n_u))
        self.g0 = nn.Parameter(torch.zeros(()))
        self.gate_p = nn.Parameter(torch.zeros(N_PLANE))
        self.gate_c = nn.Parameter(torch.zeros(N_CONTRAST))
        idx = torch.arange(n_slice)
        self.register_buffer('off', idx[None, :] - idx[:, None])

    def kernel(self, slot):
        p, c = (_PLANE_OF(slot), _CONTRAST_OF(slot))
        half = self.base + self.shared + self.plane_k[p] + self.contrast_k[c]
        full = torch.cat([half.flip(-1)[..., :self.r], half], dim=-1)
        return F.softmax(full, dim=-1)

    def alpha(self, slot):
        p, c = (_PLANE_OF(slot), _CONTRAST_OF(slot))
        return self.alpha_max * torch.tanh(self.g0 + self.gate_p[p] + self.gate_c[c])

    def forward(self, x, slot, vmask):
        T, S, H, W = x.shape
        if vmask is None:
            raise ValueError('stem=mixer requires the padding mask')
        k = self.kernel(slot)
        v = vmask.to(k.dtype)
        d = self.off + self.r
        inb = (d >= 0) & (d < self.ksize)
        kk = k[:, d.clamp(0, self.ksize - 1)] * inb
        M = kk * v[:, None, :]
        den = M.sum(-1, keepdim=True)
        eye = torch.eye(S, device=x.device, dtype=M.dtype).expand(T, S, S)
        ok = (den > 1e-06) & v[:, :, None].bool()
        M = torch.where(ok, M / den.clamp(min=1e-06), eye)
        a = self.alpha(slot)[:, None, None]
        Aop = ((1.0 - a) * eye + a * M).to(x.dtype)
        if x.is_contiguous(memory_format=torch.channels_last) and (not x.is_contiguous()):
            y = torch.bmm(x.permute(0, 2, 3, 1).reshape(T, H * W, S), Aop.transpose(1, 2))
            return y.reshape(T, H, W, S).permute(0, 3, 1, 2)
        return torch.bmm(Aop, x.reshape(T, S, H * W)).reshape(T, S, H, W)

def _seg_mean_max(v, sidx, B):
    D = v.shape[1]
    cnt = torch.zeros(B, device=v.device, dtype=v.dtype).index_add_(0, sidx, torch.ones(v.shape[0], device=v.device, dtype=v.dtype))
    mean = torch.zeros(B, D, device=v.device, dtype=v.dtype).index_add_(0, sidx, v)
    mean = mean / cnt.clamp(min=1).unsqueeze(1)
    mx = torch.full((B, D), -10000.0, device=v.device, dtype=v.dtype)
    mx = mx.scatter_reduce(0, sidx.unsqueeze(1).expand(-1, D), v, reduce='amax', include_self=True)
    return torch.cat([mean, mx], 1)

def _pad_kv(x, sidx, B, norm):
    T, P, D = x.shape
    cnt = torch.bincount(sidx, minlength=B)
    S = int(cnt.max().item())
    starts = torch.cumsum(cnt, 0) - cnt
    pos = torch.arange(T, device=x.device) - starts[sidx]
    pad = x.new_zeros(B, S, P, D)
    pad[sidx, pos] = x
    keep = torch.zeros(B, S, dtype=torch.bool, device=x.device)
    keep[sidx, pos] = True
    return (norm(pad.reshape(B, S * P, D)), ~keep.repeat_interleave(P, dim=1))

class _GatedDelta(nn.Module):

    def __init__(self, d, n_labels, n_heads, dropout):
        super().__init__()
        self.q = nn.Parameter(torch.randn(n_labels, d) * 0.02)
        self.kv_norm = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, n_heads, dropout=dropout, batch_first=True)
        self.d_norm = nn.LayerNorm(d)
        self.dw = nn.Parameter(torch.randn(n_labels, d) * (1.0 / d ** 0.5))
        self.db = nn.Parameter(torch.zeros(n_labels))
        self.gate = nn.Parameter(torch.zeros(n_labels))

    def delta(self, pat, sidx, B, return_attn):
        kv, kpm = _pad_kv(pat, sidx, B, self.kv_norm)
        q = self.q.unsqueeze(0).expand(B, -1, -1)
        att, w = self.attn(q, kv, kv, key_padding_mask=kpm, need_weights=return_attn, average_attn_weights=True)
        return ((self.d_norm(att) * self.dw).sum(-1) + self.db, w)

class TokenResidualPool(_GatedDelta):

    def __init__(self, d, n_labels=12, n_heads=6, pe=64, dropout=0.2):
        super().__init__(d, n_labels, n_heads, dropout)
        self.base = nn.Sequential(nn.LayerNorm(2 * d + pe), nn.Dropout(dropout), nn.Linear(2 * d + pe, n_labels))

    def forward(self, tok, slot, sidx, B, pres, return_attn=False):
        base = self.base(torch.cat([_seg_mean_max(tok[:, 1:].mean(1), sidx, B), pres], 1))
        d_, w = self.delta(tok[:, 1:], sidx, B, return_attn)
        return (base + self.gate * d_, w)

class CodexResidualPool(_GatedDelta):

    def __init__(self, d, n_labels=12, n_heads=6, pe=64, dropout=0.2):
        super().__init__(d, n_labels, n_heads, dropout)
        self.base = nn.Sequential(nn.LayerNorm(2 * d + pe), nn.Dropout(dropout), nn.Linear(2 * d + pe, n_labels))

    def forward(self, tok, slot, sidx, B, pres, return_attn=False):
        base = self.base(torch.cat([_seg_mean_max(tok[:, 0], sidx, B), pres], 1))
        d_, w = self.delta(tok[:, 1:], sidx, B, return_attn)
        return (base + self.gate * d_, w)

class ClsAddPool(nn.Module):

    def __init__(self, d, n_labels=12, pe=64, dropout=0.2):
        super().__init__()
        self.net = nn.Sequential(nn.LayerNorm(4 * d + pe), nn.Dropout(dropout), nn.Linear(4 * d + pe, n_labels))

    def forward(self, tok, slot, sidx, B, pres, return_attn=False):
        return (self.net(torch.cat([_seg_mean_max(tok[:, 1:].mean(1), sidx, B), _seg_mean_max(tok[:, 0], sidx, B), pres], 1)), None)

class Readout(nn.Module):

    def __init__(self, pool, d, n_labels=12, pe=64):
        super().__init__()
        self.pool_kind, self.k = (pool, n_labels)
        self.pres_emb = nn.Embedding(N_SLOT_TYPES + 1, pe, padding_idx=0)
        if pool in ('xres', 'clsadd', 'xcodex'):
            self.pool = {'xres': TokenResidualPool, 'clsadd': ClsAddPool, 'xcodex': CodexResidualPool}[pool](d, n_labels, pe=pe)
        elif pool in ('attn', 'xattn'):
            if pool == 'xattn':
                self.pool = TokenXAttnPool(d, n_labels)
                wd = 3 * d + pe
            else:
                self.pool = LabelAttentionPool(d, n_labels)
                wd = d + pe
            self.norm = nn.LayerNorm(wd)
            self.w = nn.Parameter(torch.randn(n_labels, wd) * (1.0 / wd ** 0.5))
            self.b = nn.Parameter(torch.zeros(n_labels))
        else:
            self.pool = MeanMaxPool()
            self.net = nn.Sequential(nn.LayerNorm(2 * d + pe), nn.Dropout(0.2), nn.Linear(2 * d + pe, n_labels))
        self.drop = nn.Dropout(0.2)

    def forward(self, f, slot, sidx, B, return_attn=False):
        pe = self.pres_emb(slot)
        pres = torch.zeros(B, pe.shape[1], device=f.device, dtype=f.dtype).index_add_(0, sidx, pe)
        if self.pool_kind in ('xres', 'clsadd', 'xcodex'):
            return self.pool(f, slot, sidx, B, pres)[0]
        pooled, attn = self.pool(f, sidx, B, slot=slot, return_attn=return_attn)
        if self.pool_kind in ('attn', 'xattn'):
            x = torch.cat([pooled, pres.unsqueeze(1).expand(-1, self.k, -1)], -1)
            x = self.drop(self.norm(x))
            return (x * self.w).sum(-1) + self.b
        return self.net(torch.cat([pooled, pres], 1))

class Net(nn.Module):

    def __init__(self, enc, cond, n_meta=0, pool='mean_max', stem='native', n_slice=16):
        super().__init__()
        self.enc, self.cond = (enc, cond)
        self.compress = DepthCompress(n_slice, 3) if stem == 'compress' else None
        self.mixer = SlotDepthMixer(n_slice) if stem == 'mixer' else None
        self.tokens = pool in ('xattn', 'xres', 'clsadd', 'xcodex')
        D = enc.num_features
        self.meta_mlp = nn.Sequential(nn.LayerNorm(n_meta), nn.Linear(n_meta, 128), nn.GELU(), nn.Linear(128, D)) if n_meta > 0 else None
        self.readout = Readout(pool, D)
        if cond == 'post':
            self.slot_emb = nn.Embedding(N_SLOT_TYPES + 1, D, padding_idx=MASK_IDX)

    def forward(self, im, slot, smeta, sidx, B, vm=None):
        if self.mixer is not None:
            im = self.mixer(im, slot, vm)
        if self.compress is not None:
            im = self.compress(im)
        f = self.enc.forward_features(im, slot) if self.cond == 'token' else self.enc.forward_features(im)
        if self.tokens:
            inner = getattr(self.enc, 'vit', self.enc)
            orig = getattr(self.enc, '_orig_prefix', getattr(inner, 'num_prefix_tokens', 1))
            f = torch.cat([f[:, :1], f[:, orig:]], 1)
        else:
            f = self.enc.forward_head(f, pre_logits=True)
            if f.dim() > 2:
                f = f.flatten(1)
        ex = (lambda v: v.unsqueeze(1)) if self.tokens else lambda v: v
        if self.cond == 'post':
            f = f + ex(self.slot_emb(slot))
        if self.meta_mlp is not None and smeta.shape[1] > 0:
            mt = self.meta_mlp(smeta)
            f = torch.cat([f, mt.unsqueeze(1)], 1) if self.tokens else f + mt
        return self.readout(f, slot, sidx, B)
models = []
for ckpt_path in sorted(CKPT.glob('*_f*.pt')):
    z = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    cfg = z['cfg']
    _stem = cfg.get('stem', 'native')
    _in = 3 if _stem == 'compress' else cfg.get('n_slice', 16)
    enc = timm.create_model(cfg['backbone'], pretrained=False, num_classes=0, in_chans=_in, **{'img_size': cfg['img']} if 'vit_' in cfg['backbone'] else {})
    if cfg['cond'] == 'token':
        enc = ViTSlotToken(enc, N_SLOT_TYPES)
    m = Net(enc, cfg['cond'], cfg.get('n_meta', 0), cfg['pool'], stem=_stem, n_slice=cfg.get('n_slice', 16))
    missing, unexpected = m.load_state_dict(z['state_dict'], strict=False)
    assert not [k for k in missing if not k.startswith('enc.')], f'missing {missing[:5]}'
    assert not unexpected, f'unexpected {unexpected[:5]}'
    models.append(m.eval())
    print(f"loaded {ckpt_path.name}  fold {z['fold']}  {cfg['backbone']} pool={cfg['pool']} meta={cfg['meta']}")
CFG = cfg
assert CFG.get('n_meta', 0) == 0, f"checkpoint expects {CFG['n_meta']} metadata features -- build slot_meta for the TEST studies and pass it to predict() before submitting"
print(f"\n{len(models)} fold models ready | input norm: {CFG.get('norm', 'none')}")
```

```
loaded m_f0.pt  fold 0  vit_small_patch16_dinov3.lvd1689m pool=xcodex meta=none
loaded m_f1.pt  fold 1  vit_small_patch16_dinov3.lvd1689m pool=xcodex meta=none
loaded m_f2.pt  fold 2  vit_small_patch16_dinov3.lvd1689m pool=xcodex meta=none
loaded m_f3.pt  fold 3  vit_small_patch16_dinov3.lvd1689m pool=xcodex meta=none
loaded m_f4.pt  fold 4  vit_small_patch16_dinov3.lvd1689m pool=xcodex meta=none

5 fold models ready | input norm: none
```

In \[32\]:

linkcode

```
AMP_PREF = 'bf16'

def amp_for(dev):
    if not str(dev).startswith('cuda'):
        return (torch.float32, False)
    cc = torch.cuda.get_device_capability(dev)
    if AMP_PREF == 'bf16':
        return (torch.bfloat16, True)
    if AMP_PREF == 'fp16':
        return (torch.float16, True)
    if AMP_PREF == 'fp32':
        return (torch.float32, False)
    return (torch.bfloat16 if cc >= (8, 0) else torch.float16, True)
AMP_DT, AMP_ON = amp_for(DEV)
WORKERS = max(1, min(4, os.cpu_count() or 4))
CHUNK = 48
MICRO = 8
models = [m.to(DEV).eval() for m in models]
print(f"device {DEV} | amp {str(AMP_DT).split('.')[-1]} (on={AMP_ON}) | workers {WORKERS} | chunk {CHUNK} | micro {MICRO}")

def _norm_(im):
    k = CFG.get('norm', 'none')
    if k == 'zscore':
        m = (im > 0).float()
        n = m.sum(dim=(1, 2, 3), keepdim=True).clamp(min=1.0)
        mu = (im * m).sum(dim=(1, 2, 3), keepdim=True) / n
        var = (((im - mu) * m) ** 2).sum(dim=(1, 2, 3), keepdim=True) / n
        return (im - mu) / (var.sqrt() + 1e-06) * m
    if k == 'imagenet':
        m = (im > 0).float()
        return (im - 0.485) / 0.229 * m
    return im

@torch.no_grad()
def _micro(images, masks):
    dev = DEV
    ims, slots, sidx, vms = ([], [], [], [])
    for b in range(len(masks)):
        present = np.nonzero(masks[b] > 0)[0]
        if len(present) == 0:
            continue
        blk = images[b][present]
        ims.append(torch.from_numpy(blk))
        vms.append(torch.from_numpy(blk.reshape(blk.shape[0], blk.shape[1], -1).max(2) > 0))
        slots.append(torch.from_numpy(present + 1).long())
        sidx.append(torch.full((len(present),), b, dtype=torch.long))
    out = np.full((len(models), len(masks), len(LABELS)), np.nan, np.float32)
    if not ims:
        return out
    im = _norm_(torch.cat(ims).to(dev, non_blocking=True).float().div_(255.0))
    sl = torch.cat(slots).to(dev)
    si = torch.cat(sidx).to(dev)
    vm = torch.cat(vms).to(dev)
    sm = torch.zeros(len(sl), CFG.get('n_meta', 0), device=dev)
    per = torch.zeros(len(models), len(masks), len(LABELS), device=dev, dtype=torch.float32)
    with torch.autocast('cuda' if str(dev).startswith('cuda') else 'cpu', dtype=AMP_DT, enabled=AMP_ON):
        for fold_index, model in enumerate(models):
            per[fold_index] = torch.sigmoid(
                model(im, sl, sm, si, len(masks), vm=vm).float()
            )
    got = per.cpu().numpy()
    keep = np.array([(masks[b] > 0).any() for b in range(len(masks))])
    out[:, keep] = got[:, keep]
    return out

def predict(images, masks):
    out = np.full((len(models), len(masks), len(LABELS)), np.nan, np.float32)
    for a in range(0, len(masks), MICRO):
        b = min(a + MICRO, len(masks))
        out[:, a:b] = _micro(images[a:b], masks[a:b])
    return out

# Macro ROC-AUC depends on ordering, so combine fold orderings rather
# than allowing a fold's probability scale to dominate the mean.
preds = np.full((len(models), len(studies), len(LABELS)), np.nan, np.float32)
t0, done = (time.time(), 0)
with ProcessPoolExecutor(max_workers=WORKERS) as ex:
    for c0 in range(0, len(studies), CHUNK):
        block = studies[c0:c0 + CHUNK]
        imgs = np.zeros((len(block), N_SLOT, N_SLICE, SIZE, SIZE), np.uint8)
        msks = np.zeros((len(block), N_SLOT), np.uint8)
        futs = [ex.submit(build_study, (i, s, by.get(s, []))) for i, s in enumerate(block)]
        for f in as_completed(futs):
            try:
                i, a, k = f.result()
                imgs[i], msks[i] = (a, k)
            except Exception as e:
                print(f'  study failed: {type(e).__name__}: {e}')
        preds[:, c0:c0 + len(block)] = predict(imgs, msks)
        done += len(block)
        el = time.time() - t0
        print(f'  {done:,}/{len(studies):,}  {el / 60:.1f}m  eta {el / done * (len(studies) - done) / 60:.1f}m', flush=True)
        del imgs, msks
        gc.collect()
print(f'\ninference done in {(time.time() - t0) / 60:.1f} min')
A5_W = RUN['a5_w']
A5_LABELS = list(LABELS)
_a5_ok = np.isfinite(preds).all(axis=(0, 2))
_a5_rank_mean = np.zeros((len(studies), len(LABELS)), np.float64)
for fold_index in range(preds.shape[0]):
    fold = preds[fold_index][_a5_ok]
    ordinal = fold.argsort(0).argsort(0).astype(np.float64)
    _a5_rank_mean[_a5_ok] += ordinal / max(len(fold) - 1, 1)
_a5_rank_mean /= preds.shape[0]
_a5_rank_mean[~_a5_ok] = np.nan
A5_PREDS = dict(zip(
    sub_df['StudyInstanceUID'].astype(str), _a5_rank_mean.astype(np.float32)
))
for _a5k, _a5v in _A5_SAVED.items():
    globals()[_a5k] = _a5v
del _A5_SAVED, _a5k, _a5v
```

```
device cuda | amp bfloat16 (on=True) | workers 4 | chunk 48 | micro 8
  3/3  0.1m  eta 0.0m

inference done in 0.1 min
```

In \[33\]:

linkcode

```
_a5_sub = pd.read_csv('/kaggle/working/submission.csv',
                      dtype={'StudyInstanceUID': str})
assert _a5_sub.columns.tolist()[1:] == A5_LABELS, 'submission schema drift'
if A5_W > 0:
    _a5_ours = np.stack([A5_PREDS[_u]\
                         for _u in _a5_sub['StudyInstanceUID'].astype(str)])
    _a5_base_rank = _a5_sub[A5_LABELS].rank(method='average', pct=True)
    _a5_ours_rank = pd.DataFrame(_a5_ours, columns=A5_LABELS,
                                 index=_a5_sub.index).rank(method='average', pct=True)
    _a5_sub[A5_LABELS] = (1.0 - A5_W) * _a5_base_rank + A5_W * _a5_ours_rank
    assert np.isfinite(_a5_sub[A5_LABELS].to_numpy()).all()
    _a5_sub.to_csv('/kaggle/working/submission.csv', index=False)
```

linkcode

## Stage 3 — RadImageNet: reference, twin E10 and E13 [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Stage-3-%E2%80%94-RadImageNet:-reference,-twin-E10-and-E13)

In \[34\]:

linkcode

```
from __future__ import annotations
import base64 as _rad_b64
import zlib as _rad_zlib
_RAD_CAL_PAYLOAD = 'eNrtmk1vI8cRhv9KsJdcKKE/q6tzc4z4ZCMBcjQWhrCRDSG2ZEjaIEGQ/57n7RlRQ3KG4jqLJAcDS4o709NdXR9vvVU9/3z30+3N/bvffRuuawgxlm7eq2ePeffrpV8v/V9euvLraD3k6ilW6zn126vYd+U6eKmx9RiaF7OSx+X1weE67K7SdSgpVSauuaecUxr3rtp1LK0HyyV7y9Gmy/E6pBhTL61Zt2gWx+WtSew6JmOoM5AHutXp+ro8+ZrlsnvJOfDdfRL+Kl4zd2bqllNmga7rvrva2OzGNFuynGxpmnxrS/069hCtpt6T1dLLOQVsTbJ1fWunG2qXAX8NiU+7VK8rdqvNU89uwQwjpWyeLdTCnVy84ua9pthSjznHXLjDpZxbLe4WPRAQCT+LrSVcGGdLzNX0XKhesC2eV5uZ67lQPDlmSzUhS2+61ELtoTOyWGjdPudc73fvnj7c/Hg7ElpyzYXjdwIZ32m7X3INZ0crtvtc833ua6fyoUYUGf4H13rJpX+GK5aa5VbeWO9ye/03bLi97i8SpaSCl49nc4gdxI2p1dZyVmQnfL56jBH/j70GqSq6dyMROLHQGvCpcSnkYsyeohNErnVjbamVjs47wOpBa7BAsa61SXulDfSIwAbAkQqDmSK38WwImKK1kFJ3d11CpFqR1mPHlj1pWVAHeDfyU2hk0vGogz0GqCBbKmFMx9xIWEAbQ8I4PUvmAplQCeuij7GNXGMk3yhBsFIfEnvVE6HFYMHDtFuLzKwpya9gisaZduAkcyAvmw1ROjmd7OnBYytpOBqJjTyK4KzT0Pi0tQJYslc0nGqcNZV7dEaRvfcSewg9h4p41iwO+4CWMkNG1326VBmHFUoB7VoakzE+JAtYN/NknS9lLJ+9S5qR56Q2kLA4qgTuplGNmUJAkbXiGbrU0HCIsgtYaGOUVXbayNeykLfpGv8lulBfgiFEmx61xm3LTlrOPoa51Ng7IyJiT4tWxrE0ZmnJRnhawZsyLgjXIC9MRu0tRAgImkJ7bUyHKk1eUgIewtRjXGDJqO1mNJrHfNUty1HRW2SSoV3FAVIA//hrUXKANxhbRbEkgqAFKiCC43qOEXsPTaKtKCdkqx3/koMYsuP+mh4HrHoQtqSIw/h4DM7EpRL5zRirAcHiUDj2SUlr9fFAsElHBX/zWgJCQlw+83Qksw8Pt9+Ty0hmOBQBh9XQAr7fxjRQ2IkGTT/w8cAiBKwRc1jwcMh+WKtMgFShNaDGJWRAechNSOMUldXTynNIUPAaEKKkCv1cLFzxaowBOmX8vU8Pj1voWa5JTPFcGN4QXm+PpZPjA8QQYYp9Qab9rZiIAuLX8AA8f/jX4kHgI+BXCtBEeOTFvNPapIyC92YAEOmHypJcCSiFOpQi712M73IL8KiBX8Hz62pDNsAH8MK/rMR+tNSRIRJwAkIIY8Rn/fD2kB2V9I7BMX+KSJ/XJtNAbwFglmQZbu/90CZcMhAeZKudKAvlSBLwNwP1aA88BYpPdJRkbADGeBzWN2IOvySVELxyU0Lx0JHQHsFpEQRsCB9iO1qT3IOHGUjMDqeczX4BiIbvCjkiLD6t6G239p+gAML1KQuAdaLLdidDV6Y6uPR+9+3LT8KrlYgzAsjg7ok+VJakimvgAjn5qUFmtTGJKXGxSadg2UuLkWok4EvGJ0Hdsr+DmpVlGsUMZkxtuTI8vDAVaIsnSIDbK0DhVSpAFlu4iRtgrLYWRaArADOcFDAfErEdwBS8dWpNqHupW3o7nIukTmxlmASq4L/51ESrznqJTSkgCzslVSMncekb8659ljeyYttxK0oX9k50n3h2kDqoapToWt8S9/yO3tTXyteLu+19rkPViKkIblLnzJhJUhYENUJCtdfWKkEFe9WTsWin6azpqJFIfEwNyLNes+PZXFV3h+tIOXjb5mzIRnCLaWKuhnPtjsCVPAOwdkhQhBSMfWLVruTgwEM/WXt1FYgv5AN4IsyBiHrOSscCBjIomksgZCPFn9grqDrE9UXDQCSPfs5RXyeuQl3gwcEIdn5JzADhpG34s4uF5NQ24eh1GWISkEmYA6iFiNezYAbkKNGJhIk+l9XNXK3r7AgLT4YnRUuHicJS0NRLLG0KDrF1IbkaMzj2MoeKzAH/kTo9KsnWJe8gDZUuxs1iPi0CayABMdLIT4qQCbfENfCiAsujIsj9KMUQ1kXwXUBFZspHZm9Zj/dB/SrVy1qOJg9ApKAlmSQNpr6SjibnNgVoqZQCr8gllgsTiFAOCFSeDcYWuKOChZQXi5dPxouF5Oo6ogVTaxDwnVE8KfQFI6Zomwgb/oI4VG2Ae1MdsTQCwQuZp5ZROZPcdudWHrZRfwe4cPE1cv9L/FDuwRwGNYOttGllMRItS1K3sFDQDAwQMvgpfIzyIeQj2yTFOhomGLsBVPtAASGLqiXKnChASW/4ILUTGlftQlUVl8FDjifbKYIzLKXmco4anNPK6ZVl8MhVBs+D5YgTo8HXuIEDQDJF4wHEYL5PvEExn4PIt7x0JumDeUgjxHeFIZDt+6xN5mALCc6pMjTZ7oy8EomCUA09MTRvvuCLxyFC+sEWCGiqjE+HIAJ4g39Bi5sadSN9MJZaFWLbpubBNBvlmwrPAONJWS1DpaIgbyKuZSbKg7qZzgNKsqnwIX8RAOvINdgfRg0jPNJBWE+5xAQ9qDaAPh4nKInagjAL9otj26U+sAnbUERTF0QYjHV8j8OEA+mohtH9SLLuoUIh6uAWHI6yAw54uEsqL6zufMAAt3yW+6xSFLmKwEmYgIPlXHYbPAo3AvKovCk/0KR5m3fmKkpFz2W3ng58h7KzqVVHqVYUpfGlAJHvQ2dN7QKmXoQITggHUz9HGZhSty5smYHeSL4pFdvbXlXZcSJV7GCHKPpsePEmVAOm41WxbuW3Y+qkrhYhisbrSBqbGiGdAkBwd5gzNehxGUVhzu5JCKa2VAyL2pfYgYgUtcTwu3RKZzO2JublhfCDbO1Qqypu8SdTWO0501Z6iAAH68g21mECvjX8bZZ7yvpViqq9BlHCnhj7DFuiXm8qEwgrAkK9hpfbuU/nN/i4l7I/qQEnpR4qVHUxgDjblWuM2UZFhOpzp+apb8i4ua8gnyHrqPMHs839gK7gaaYDDtILqNTWOF8kxVYdMxlVDwE68/F8DR2CgpCSkkzkEvKY3x9GoRqjpn8ZLj62TyEoRVV1dxrV2GtNOMosPAjqSC6pm6yRKRJFM5wnixbhh6uLl9FdjElsUvX7WxR61T1gGohOkQaej27MxiR+DQjAndQ5SgL4Yb+VMKT2UncGK4se5hfeR7Jr6nygbTJcPGK7QSpXOoBJkuMXlFTYQX0aRsObYEQn22BNrDQdKwmZ1DDaZNcANxumdkGs3pZIJcaCcxBuPSlGziTf+UNZIgqmLMTWS1/XYNBxFowH5FchZb7uT5EQqervUK+Rc15pP55mBpKra6Wju5MCbZwiKOSS/HFuZyVRBFeeIoVrc35oNnVt1ARpKDaHF2BO1z3DLILOrOVZdhIG52ojyFxsVa1k6Bq+sOS7AA0upIqpiCt9Om8+1SsIoI4/ZYFKZq9tdwnhCzrVRpoCxpqSo+0ua1DNLCOMc3X19vGSZZ9znfEAMTUpymSGqYW/kpXU6FWV6+pah9OGLveaTkopOV1d3U9oWfAhMiyK46fRgPeL9LTSDAtUjj5cFN4D8S5zmaCjmaTjJ/Kvxb3MaFrHVI27QS2vRfcMCmeqcUXY+NX6652okyj19OEC3SaFrdWyeyJMxo7gPrANn17GjQ5RgtqvregNjzr1hYOOxATeos4b/IItGRxEFZC4aNruVL1ZbGx8ojpE5moLiGNavazB+baxPoXr/gK56zjI1VGbjtG8nA3Xg3SpFl2gtqzqsM/oGgb5Axj4w+XD1g48MBFrMAnR+TRxMci1+8h+uCC1e1nmC7XEWhf2zEdIw5SsCe3Tcc18XibsU/PKhJhd7a380s67RLEvQQWUw9KKjmps7qefVeub/IZQoLbK0qxnHRFP7qlOy8BURC7Fy2LDPk7N1F1VEm1lrZbSmSWVSoNk63DQXgvIohAjYcjXU7b/zI8u7RVvPiRChSqVjkiU6YQjrT1ImVAAN/WoKEp62V2aQGAdAuQKhSW5qouyIdQ4jNe5NS6I8v10hLIeqIIMqplDn71o0dYl4fEFkRZ4LmhFJNUSQqZCNlBT2fIWnKzJ9XWwG48bOzGZWEIffcVx/q23xAziBV83gf1cE4/+mvI8/EFV3QVmPW0a6rB7ZD314ploTllOSlFYqX3X4u7TJg6jmxLRWxit1FaPtArKoHfHeb3jwPmNGDqfvS+Iv9Ns14Vv6p9rfyft+HGiFqmJIQSU++rlbegPBqDumli9zoOGSptec8O6GAWqtaAgkOgqZ3P1WhQQ08aj2KGONuEIqdZetzuLFB6qQniid8HkZTnlyGsPGnA4lY5Qu1456WnbokG9IupwU0NoPhHTwRRUqynZU0HObV8QUyZuo/lb6tFhsdxb7bCoU9qWe8vLxBwj2laVzgS+bIZGMfee1Qaldl87gBZ5jjr3Y4rq2Xaf3LatohHwxzbqBKtv4d8bHnh1eUqfVRx07jc4zfzySrj8IGV9NMFX4mBKrq6FXc4Jz154/3737u7++fbxw+3Pz9N7eg0X0mHCeHfHbHrNhrCIpdXRA/LRRC4WR9sU/ZqJB46XJsJouwU1rPT+il6uKHqNAdbJ2InUJp0wVWBV7w8NuldU7uMyajZqh2N6UfeoM6ym1zLGizF6T6AnNQZiHO/KZMijZMOV2/yKQFKv0TSXq0Hb5teE9F4HLp50QKJ3OX64edZ7ie+++PLrd7t339z+5e7mx9/88Qt+f82dx5f//Omr6e8fvv/+49Pdwz0/f3/z19vH3z7x68uH++fpKhP+/Pjw/PDh4cfv+Hz86f5Jk99/93T7eHersfff/fnmh/H3y4fH8feLv9/x96ub5+l7vq9f0wj9msf8+HH6fhnDr3kMvzRGG3p8+PizVt3vaXy/ysjox5sPzx8fbxn+7cuWv7m9v3v68PFpsfH9pcWwLc1oyEI3f/7H/cPf7p7vnhZ6ev/+X/8GYIe3xg=='
# Surgical reproduction of V48's deployed prediction branch.
#
# The pinned reference Rad family is fused with correct-contract E13, then
# the same E13 heads run on the E11 layout at 0.15. No twin/legacy wrapper
# follows it, matching the branch that produced V48's visible submission.

import contextlib as _rad_contextlib
import gc as _rad_gc
import hashlib as _rad_hashlib
import json as _rad_json
import os as _rad_os
import re as _rad_re
import time as _rad_time
from concurrent.futures import ThreadPoolExecutor as _RadThreadPool
from pathlib import Path as _RadPath

import numpy as _rad_np
import pandas as _rad_pd
import pydicom as _rad_pydicom
import torch as _rad_torch
import torch.nn as _rad_nn
import torch.nn.functional as _rad_F
from torchvision.models import resnet50 as _rad_resnet50

_RAD_LABELS = [\
    'ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA',\
    'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's",\
    'Contusion', 'Fracture',\
]
_RAD_ALPHA = RUN['rad_alpha']
_RAD_EXCLUDE = ("Baker's", 'Fracture')
_RAD_HEADS_SHA256 = '54f657826b3458a7ba3d462e198ba380732f2b136246182312704929874a9a2c'
_RAD_REFERENCE_HEADS_SHA256 = '0f465649799ecfbccaac1767844639e7ced44e1bc9babde6e4bac7c5d9b89eaa'
_RAD_ENCODER_SHA256 = '08629f7e7bd3e29b8ee9522ca3f65ce4d010a7ddf74f0ea3c7e3f3d0bbab0734'
_RAD_E13_HEADS_SHA256 = 'ad9f19af73bfdf4e49263c0e45060dc3cb239e1195039b26dc8c0a3a6bcd1a8a'
_RAD_E13_MEMBER_WEIGHT = RUN['rad_e13_member_w']
_RAD_V48_SECOND_ALPHA = RUN['rad_second_alpha']
_RAD_TWIN_ALT_WEIGHT = RUN['rad_twin_alt_w']
_RAD_TOKEN_DIM, _RAD_HEAD_DIM = 2048, 512

_RAD_E11_SLOTS = [\
    ('SAG_NOFS', 'Sagittal', None, False),\
    ('COR_NOFS', 'Coronal', None, False),\
    ('AX_NOFS', 'Axial', None, False),\
    ('SAG_FS', 'Sagittal', None, True),\
]
_RAD_E11_CROP_MM = 130.0
_RAD_E11_CACHE_SLICES = 8
_RAD_E11_IMG = 224

_RAD_E13_SLOTS = [\
    ('SAG_FS', 'Sagittal', None, True),\
    ('COR_FS', 'Coronal', None, True),\
    ('AX_FS', 'Axial', None, True),\
    ('SAG_NOFS', 'Sagittal', None, False),\
]
_RAD_E13_CROP_MM = 130.0
_RAD_E13_CACHE_SLICES = 8
_RAD_E13_IMG = 224

# Our independently trained five-fold family.  Its preprocessing and estimator
# are preserved from V35: native DICOM geometry/fat-sat handling and a mean of
# per-fold percentile ranks (rather than v15's rank of the probability mean).
_OUR_N_SLOT, _OUR_N_SLICE, _OUR_IMG = 3, 8, 224

# Exact V40/E10 test representation: three fat-suppressed planes, eight
# acquired slices per plane, full frame, legacy ordering/laterality/fill.
SLOTS = [\
    ('SAG_FS', 'Sagittal', None, True),\
    ('COR_FS', 'Coronal', None, True),\
    ('AX_FS', 'Axial', None, True),\
]
N_SLOT = len(SLOTS)
CACHE_SLICES = 8
IMG = CACHE_IMG = 224
CROP_MM = 10_000.0
SLICE_BAND = (0.2, 0.8)
RULES = dict(RULES_LEGACY)
TIME_BUDGET = 8.0 * 3600

def _rad_log(message):
    print(f'[Rad-dual5] {message}', flush=True)

def _rad_sha256(path, chunk=8 << 20):
    digest = _rad_hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(chunk), b''):
            digest.update(block)
    return digest.hexdigest()

def _rad_find_file(name, expected_sha=None, explicit_env=None):
    if explicit_env and _rad_os.environ.get(explicit_env):
        candidates = [_RadPath(_rad_os.environ[explicit_env])]
    else:
        candidates = []
        base = _RadPath('/kaggle/input')
        if base.is_dir():
            for root, dirs, files in _rad_os.walk(base):
                dirs[:] = [d for d in dirs if d not in ('train_series', 'test_series')]
                if name in files:
                    candidates.append(_RadPath(root) / name)
    if not candidates:
        raise FileNotFoundError(f'V36 missing input artifact {name}')
    for path in candidates:
        if expected_sha is None or _rad_sha256(path) == expected_sha:
            return path
    raise RuntimeError(f'V36 found {name}, but no copy has the required SHA-256')

class _RadEncoder(_rad_nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = _rad_nn.Sequential(
            *list(_rad_resnet50(weights=None).children())[:-2]
        )

    def forward(self, image):
        return self.backbone(image).mean(dim=(2, 3))

class _RadHead(_rad_nn.Module):
    def __init__(self):
        super().__init__()
        self.project = _rad_nn.Sequential(
            _rad_nn.LayerNorm(_RAD_TOKEN_DIM),
            _rad_nn.Linear(_RAD_TOKEN_DIM, _RAD_HEAD_DIM),
            _rad_nn.GELU(),
        )
        self.plane = _rad_nn.Parameter(_rad_torch.randn(N_SLOT, _RAD_HEAD_DIM) * .01)
        self.position = _rad_nn.Parameter(_rad_torch.randn(CACHE_SLICES, _RAD_HEAD_DIM) * .01)
        self.query = _rad_nn.Parameter(_rad_torch.randn(len(_RAD_LABELS), _RAD_HEAD_DIM) * .02)
        self.attn = _rad_nn.MultiheadAttention(
            _RAD_HEAD_DIM, 8, dropout=.10, batch_first=True
        )
        self.fuse = _rad_nn.Sequential(
            _rad_nn.LayerNorm(_RAD_HEAD_DIM * 4),
            _rad_nn.Linear(_RAD_HEAD_DIM * 4, _RAD_HEAD_DIM),
            _rad_nn.GELU(),
            _rad_nn.Dropout(.15),
        )
        self.weight = _rad_nn.Parameter(
            _rad_torch.randn(len(_RAD_LABELS), _RAD_HEAD_DIM) * .02
        )
        self.bias = _rad_nn.Parameter(_rad_torch.zeros(len(_RAD_LABELS)))

    def forward(self, feature, mask):
        token = self.project(feature.float())
        token = token.view(len(token), N_SLOT, CACHE_SLICES, _RAD_HEAD_DIM)
        token = token + self.plane[None, :, None] + self.position[None, None]
        token = token.flatten(1, 2)
        key_padding = mask <= 0
        all_empty = key_padding.all(1)
        if all_empty.any():
            key_padding = key_padding.clone()
            key_padding[all_empty, 0] = False
        query = self.query.unsqueeze(0).expand(len(token), -1, -1)
        attended = query + self.attn(
            query, token, token, key_padding_mask=key_padding, need_weights=False
        )[0]
        denominator = mask.sum(1, keepdim=True).clamp_min(1).unsqueeze(-1)
        mean = (token * mask.unsqueeze(-1)).sum(1, keepdim=True) / denominator
        mean = mean.expand(-1, len(_RAD_LABELS), -1)
        fused = self.fuse(_rad_torch.cat(
            [attended, mean, _rad_torch.abs(attended - mean), attended * mean], dim=-1
        ))
        return (fused * self.weight.unsqueeze(0)).sum(-1) + self.bias

def _rad_load_public_heads(device, expected_sha):
    heads_path = _rad_find_file('v52_radimagenet_heads.pt', expected_sha)
    payload = _rad_torch.load(heads_path, map_location='cpu', weights_only=True)
    expected = {
        'version': 'v52-radimagenet-resnet50-official-1',
        'targets': _RAD_LABELS,
        'encoder_sha256': _RAD_ENCODER_SHA256,
        'encoder_source_commit': '0ce16f7375db4236e646829d1eca61cdb4282133',
        'img': 224,
        'slices_per_plane': 8,
        'feature': 'global_average_pool',
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise RuntimeError(f'public-v15 head contract drift for {key}')
    folds = payload.get('folds')
    if not isinstance(folds, list) or len(folds) != 5:
        raise RuntimeError('public-v15 bundle requires exactly five heads')
    if sorted(int(record.get('fold', -1)) for record in folds) != list(range(5)):
        raise RuntimeError('public-v15 fold identity drift')
    heads = []
    for record in folds:
        head = _RadHead().to(device).eval()
        head.load_state_dict(record['state_dict'], strict=True)
        heads.append(head)
    return heads, str(heads_path)

def _rad_load_e13_heads(device):
    # V48 used an unqualified filename shared by E11 and E13. Resolve the
    # intended E13 bundle by content and validate its complete pixel contract.
    heads_path = _rad_find_file('v52_e11_heads.pt', _RAD_E13_HEADS_SHA256)
    payload = _rad_torch.load(heads_path, map_location='cpu', weights_only=False)
    expected = {
        'version': 'e11-radimagenet-resnet50-diverse-1',
        'targets': _RAD_LABELS,
        'encoder_sha256': _RAD_ENCODER_SHA256,
        'slots': [list(slot) for slot in _RAD_E13_SLOTS],
        'crop_mm': _RAD_E13_CROP_MM,
        'img': _RAD_E13_IMG,
        'slices_per_plane': _RAD_E13_CACHE_SLICES,
        'feature': 'global_average_pool',
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise RuntimeError(f'E13 head contract drift for {key}')
    folds = payload.get('folds')
    if not isinstance(folds, list) or len(folds) != 5:
        raise RuntimeError('E13 bundle requires exactly five heads')
    if sorted(int(record.get('fold', -1)) for record in folds) != list(range(5)):
        raise RuntimeError('E13 fold identity drift')
    heads = []
    for record in folds:
        head = _RadHead().to(device).eval()
        head.load_state_dict(record['state_dict'], strict=True)
        heads.append(head)
    return heads, str(heads_path)

def _rad_load_models(device):
    encoder_path = _rad_find_file(
        'ResNet50.pt', _RAD_ENCODER_SHA256, explicit_env='RSNA_RAD_WEIGHT_PATH'
    )
    encoder = _RadEncoder()
    encoder.load_state_dict(
        _rad_torch.load(encoder_path, map_location='cpu', weights_only=True), strict=True
    )
    if sum(parameter.numel() for parameter in encoder.parameters()) != 23_508_032:
        raise RuntimeError('V36 RadImageNet encoder parameter-count drift')
    encoder.eval().to(device)
    for parameter in encoder.parameters():
        parameter.requires_grad_(False)
    if device.type == 'cuda' and _rad_torch.cuda.device_count() > 1:
        encoder = _rad_nn.DataParallel(
            encoder, device_ids=list(range(_rad_torch.cuda.device_count()))
        )

    alt_heads, alt_path = _rad_load_public_heads(device, _RAD_HEADS_SHA256)
    reference_heads, reference_path = _rad_load_public_heads(
        device, _RAD_REFERENCE_HEADS_SHA256
    )
    if alt_path == reference_path:
        raise RuntimeError('twin E10 branches resolved to the same artifact')
    return encoder, alt_heads, reference_heads, str(encoder_path), alt_path, reference_path

@_rad_torch.inference_mode()
def _rad_encode(encoder, pixels, slot_mask, device):
    n, slots, slices, height, width = pixels.shape
    features = _rad_np.zeros(
        (n, slots * slices, _RAD_TOKEN_DIM), _rad_np.float16
    )
    token_mask = _rad_np.repeat(slot_mask[:, :, None], slices, axis=2).reshape(n, -1)
    valid = _rad_np.flatnonzero(token_mask.reshape(-1) > 0)
    flat = pixels.reshape(-1, height, width)
    batch = 192 if device.type == 'cuda' and _rad_torch.cuda.device_count() > 1 else (
        96 if device.type == 'cuda' else 8
    )
    for start in range(0, len(valid), batch):
        indices = valid[start:start + batch]
        image = _rad_torch.from_numpy(flat[indices]).to(device).float().div_(127.5).sub_(1.0)
        image = image.unsqueeze(1).expand(-1, 3, -1, -1).contiguous()
        amp = (_rad_torch.autocast('cuda')
               if device.type == 'cuda' else _rad_contextlib.nullcontext())
        with amp:
            feature = encoder(image)
        values = feature.float().cpu().numpy()
        if not _rad_np.isfinite(values).all():
            raise RuntimeError('V36 non-finite RadImageNet feature')
        features.reshape(-1, _RAD_TOKEN_DIM)[indices] = values.astype(_rad_np.float16)
    return features, token_mask.astype(_rad_np.float32)

@_rad_torch.inference_mode()
def _rad_predict_head(head, features, masks, device, batch=64):
    predictions = []
    for start in range(0, len(features), batch):
        image = _rad_torch.from_numpy(features[start:start + batch]).to(device)
        mask = _rad_torch.from_numpy(masks[start:start + batch]).to(device)
        amp = (_rad_torch.autocast('cuda')
               if device.type == 'cuda' else _rad_contextlib.nullcontext())
        with amp:
            predictions.append(_rad_torch.sigmoid(head(image, mask)).float().cpu())
    return _rad_torch.cat(predictions).numpy()

def _rad_rank_columns(values):
    return _rad_pd.DataFrame(
        _rad_np.asarray(values, dtype=_rad_np.float64)
    ).rank(method='average', pct=True).to_numpy(_rad_np.float64)

def _rad_validate(frame, expected_ids):
    if frame.columns.tolist() != ['StudyInstanceUID', *_RAD_LABELS]:
        raise RuntimeError('V36 submission schema drift')
    ids = frame['StudyInstanceUID'].astype(str).tolist()
    if ids != list(map(str, expected_ids)) or len(ids) != len(set(ids)):
        raise RuntimeError('V36 submission study identity/order drift')
    values = frame[_RAD_LABELS].to_numpy(_rad_np.float64)
    if not _rad_np.isfinite(values).all() or values.min() < 0 or values.max() > 1:
        raise RuntimeError('V36 invalid submission values')

def _rad_main():
    started = _rad_time.time()
    work = _RadPath(_rad_os.environ.get('RSNA_RAD_OUTPUT_DIR', '/kaggle/working'))
    primary = work / 'submission.csv'
    if not primary.is_file():
        raise FileNotFoundError('V37 requires the completed DINO parent submission.csv')
    test = _rad_pd.read_csv(ROOT / 'test.csv', dtype={'StudyInstanceUID': str})
    expected_ids = test['StudyInstanceUID'].astype(str).tolist()
    baseline = _rad_pd.read_csv(primary, dtype={'StudyInstanceUID': str})
    _rad_validate(baseline, expected_ids)

    device = _rad_torch.device('cuda:0' if _rad_torch.cuda.is_available() else 'cpu')
    print(f'[RadImageNet] Selected device: {device}')
    (encoder, public_heads, reference_heads, encoder_path,
     public_heads_path, reference_heads_path) = _rad_load_models(device)

    # Family 1: public v15/E10 legacy pixels.  Keep this path bit-for-bit as in
    # V36, including rank(mean(fold probability)).
    test_series = _rad_pd.read_csv(
        ROOT / 'test_series.csv',
        dtype={'StudyInstanceUID': str, 'SeriesInstanceUID': str},
    )
    plane = dict(zip(test_series.SeriesInstanceUID, test_series.Anatomical_Plane))
    headers = annotate(walk('test_series'))
    studies, pixels, slot_mask = build_cache(
        pick_slots(headers, plane), plane, lat_of(headers, 'test-e10 '), 'test-e10'
    )
    by_uid = {str(uid): index for index, uid in enumerate(studies)}
    missing = [uid for uid in expected_ids if uid not in by_uid]
    if missing:
        raise RuntimeError(f'{len(missing)} test studies absent from public-v15 cache')
    order = _rad_np.asarray([by_uid[uid] for uid in expected_ids], dtype=_rad_np.int64)
    pixels, slot_mask = pixels[order], slot_mask[order]
    token_count = int(
        _rad_np.repeat(slot_mask[:, :, None], CACHE_SLICES, axis=2).sum()
    )
    if token_count < int(0.85 * len(test) * N_SLOT * CACHE_SLICES):
        raise RuntimeError(f'insufficient acquired public-v15 test slices: {token_count}')

    features, token_mask = _rad_encode(encoder, pixels, slot_mask, device)
    del pixels, slot_mask, headers
    _rad_gc.collect()
    public_fold_predictions = [\
        _rad_predict_head(head, features, token_mask, device)\
        for head in public_heads\
    ]
    reference_fold_predictions = [\
        _rad_predict_head(head, features, token_mask, device)\
        for head in reference_heads\
    ]
    if len(public_fold_predictions) != 5 or len(reference_fold_predictions) != 5:
        raise RuntimeError('twin E10 inference did not use all ten heads')

    # Preserve each public recipe's rank(mean(fold probability)) estimator.
    public_probability = _rad_np.mean(_rad_np.stack(public_fold_predictions), axis=0)
    reference_probability = _rad_np.mean(
        _rad_np.stack(reference_fold_predictions), axis=0
    )
    public_rank = _rad_rank_columns(public_probability)
    reference_rank = _rad_rank_columns(reference_probability)
    del (public_heads, reference_heads, public_fold_predictions,
         reference_fold_predictions, public_probability, reference_probability,
         features, token_mask)
    _rad_gc.collect()
    _rad_torch.cuda.empty_cache()
    _rad_log(
        f'twin public-v15 families complete ({public_heads_path}; {reference_heads_path})'
    )

    # One new member from V48: three fat-sensitive planes plus a sagittal
    # structural anchor, all at a 130 mm crop. Average ranks inside the Rad block
    # and re-rank the result exactly as V48 does before the unchanged E10 vote.
    globals().update(
        SLOTS=list(_RAD_E13_SLOTS),
        N_SLOT=len(_RAD_E13_SLOTS),
        CACHE_SLICES=int(_RAD_E13_CACHE_SLICES),
        IMG=int(_RAD_E13_IMG),
        CACHE_IMG=int(_RAD_E13_IMG),
        CROP_MM=float(_RAD_E13_CROP_MM),
        RULES=dict(RULES_LEGACY),
    )
    e13_heads, e13_path = _rad_load_e13_heads(device)
    headers = annotate(walk('test_series'))
    studies, pixels, slot_mask = build_cache(
        pick_slots(headers, plane), plane, lat_of(headers, 'test-e13 '), 'test-e13'
    )
    by_uid = {str(uid): index for index, uid in enumerate(studies)}
    missing = [uid for uid in expected_ids if uid not in by_uid]
    if missing:
        raise RuntimeError(f'{len(missing)} test studies absent from E13 cache')
    order = _rad_np.asarray([by_uid[uid] for uid in expected_ids], dtype=_rad_np.int64)
    pixels, slot_mask = pixels[order], slot_mask[order]
    e13_token_count = int(
        _rad_np.repeat(slot_mask[:, :, None], CACHE_SLICES, axis=2).sum()
    )
    if e13_token_count < int(0.85 * len(test) * N_SLOT * CACHE_SLICES):
        raise RuntimeError(f'insufficient acquired E13 test slices: {e13_token_count}')
    e13_features, e13_token_mask = _rad_encode(
        encoder, pixels, slot_mask, device
    )
    del pixels, slot_mask, headers
    _rad_gc.collect()
    e13_predictions = [\
        _rad_predict_head(head, e13_features, e13_token_mask, device)\
        for head in e13_heads\
    ]
    if len(e13_predictions) != 5:
        raise RuntimeError('E13 inference did not use all five heads')
    e13_probability = _rad_np.mean(_rad_np.stack(e13_predictions), axis=0)
    if (
        e13_probability.shape != (len(test), len(_RAD_LABELS))
        or not _rad_np.isfinite(e13_probability).all()
    ):
        raise RuntimeError(f'invalid E13 prediction shape/value: {e13_probability.shape}')
    e13_rank = _rad_rank_columns(e13_probability)
    public_rank = _rad_rank_columns(
        (1.0 - _RAD_E13_MEMBER_WEIGHT) * public_rank
        + _RAD_E13_MEMBER_WEIGHT * e13_rank
    )
    reference_rank = _rad_rank_columns(
        (1.0 - _RAD_E13_MEMBER_WEIGHT) * reference_rank
        + _RAD_E13_MEMBER_WEIGHT * e13_rank
    )
    # V48 resolves this same bundle again after switching pixel layouts.
    del (e13_predictions, e13_probability, e13_rank,
         e13_features, e13_token_mask)
    _rad_gc.collect()
    _rad_torch.cuda.empty_cache()
    _rad_log(
        f'E13 FS-crop member complete at Rad-block weight '
        f'{_RAD_E13_MEMBER_WEIGHT:.2f} ({e13_path})'
    )

    # E10 keeps its audited 0.50 parent/Rad vote. The two excluded findings
    # remain the raw parent values, matching the audited deployment.
    baseline_rank = _rad_rank_columns(baseline[_RAD_LABELS].to_numpy())

    def _rad_e10_branch(head_rank):
        branch = baseline.copy()
        for index, target in enumerate(_RAD_LABELS):
            if target not in _RAD_EXCLUDE:
                branch[target] = (
                    (1.0 - _RAD_ALPHA) * baseline_rank[:, index]
                    + _RAD_ALPHA * head_rank[:, index]
                )
        return branch

    candidate_alt = _rad_e10_branch(public_rank)
    candidate_reference = _rad_e10_branch(reference_rank)
    for branch in (candidate_alt, candidate_reference):
        for target in _RAD_EXCLUDE:
            if not _rad_np.array_equal(
                branch[target].to_numpy(), baseline[target].to_numpy()
            ):
                raise RuntimeError(f'E10 failed to preserve raw parent values for {target}')
        _rad_validate(branch, expected_ids)
    # Diagnostic E10 output only; the final equal rank mean is formed after E11
    # and the legacy-DINO tie-break have completed independently in each branch.
    candidate = baseline.copy()
    alt_e10_rank = _rad_rank_columns(candidate_alt[_RAD_LABELS].to_numpy())
    reference_e10_rank = _rad_rank_columns(
        candidate_reference[_RAD_LABELS].to_numpy()
    )
    candidate[_RAD_LABELS] = (
        _RAD_TWIN_ALT_WEIGHT * alt_e10_rank
        + (1.0 - _RAD_TWIN_ALT_WEIGHT) * reference_e10_rank
    )
    _rad_validate(candidate, expected_ids)
    e10_path = work / 'submission_e10_v2.csv'
    candidate.to_csv(e10_path, index=False)
    _rad_log(
        f'twin E10 branches complete at alpha={_RAD_ALPHA:.2f}; '
        f'preserved raw={list(_RAD_EXCLUDE)}'
    )

    # V48's successful run selected the E13 bundle a second time after
    # installing the older E11 slot order. Express that observed behavior
    # directly, without relying on duplicate-filename directory order.
    globals().update(
        SLOTS=list(_RAD_E11_SLOTS),
        N_SLOT=len(_RAD_E11_SLOTS),
        CACHE_SLICES=int(_RAD_E11_CACHE_SLICES),
        IMG=int(_RAD_E11_IMG),
        CACHE_IMG=int(_RAD_E11_IMG),
        CROP_MM=float(_RAD_E11_CROP_MM),
        RULES=dict(RULES_LEGACY),
    )
    headers = annotate(walk('test_series'))
    studies, pixels, slot_mask = build_cache(
        pick_slots(headers, plane), plane,
        lat_of(headers, 'test-v48-pass2 '), 'test-v48-pass2'
    )
    by_uid = {str(uid): index for index, uid in enumerate(studies)}
    missing = [uid for uid in expected_ids if uid not in by_uid]
    if missing:
        raise RuntimeError(f'{len(missing)} test studies absent from V48 pass-2 cache')
    order = _rad_np.asarray([by_uid[uid] for uid in expected_ids], dtype=_rad_np.int64)
    pixels, slot_mask = pixels[order], slot_mask[order]
    v48_pass2_token_count = int(
        _rad_np.repeat(slot_mask[:, :, None], CACHE_SLICES, axis=2).sum()
    )
    if v48_pass2_token_count < int(0.55 * len(test) * N_SLOT * CACHE_SLICES):
        raise RuntimeError(
            f'insufficient acquired V48 pass-2 slices: {v48_pass2_token_count}'
        )
    v48_features, v48_token_mask = _rad_encode(
        encoder, pixels, slot_mask, device
    )

    # --- optional horizontal-flip TTA -------------------------------------
    # Only the slots named in the mode are mirrored; see the RUN config for
    # why flipping a coronal slot is not a neutral augmentation here.
    _flip_mode = str(RUN.get('rad_flip_tta', 'off')) if 'RUN' in globals() else 'off'
    v48_flip_rank = None
    if _flip_mode not in ('off', ''):
        _flip_slots = [\
            index for index, slot in enumerate(_RAD_E11_SLOTS)\
            if _flip_mode == 'all' or slot[1] == 'Sagittal'\
        ]
        if not _flip_slots:
            raise RuntimeError(f'flip mode {_flip_mode!r} selects no slots')
        pixels_flip = pixels.copy()
        pixels_flip[:, _flip_slots] = pixels[:, _flip_slots][..., ::-1]
        _rad_log(
            f'flip TTA: mode={_flip_mode}, mirroring slots '
            f'{[_RAD_E11_SLOTS[index][0] for index in _flip_slots]}'
        )
        v48_features_flip, v48_token_mask_flip = _rad_encode(
            encoder, pixels_flip, slot_mask, device
        )
        del pixels_flip
        _rad_gc.collect()
        v48_flip_predictions = [\
            _rad_predict_head(head, v48_features_flip, v48_token_mask_flip, device)\
            for head in e13_heads\
        ]
        v48_flip_rank = _rad_rank_columns(
            _rad_np.mean(_rad_np.stack(v48_flip_predictions), axis=0)
        )
        del v48_features_flip, v48_token_mask_flip, v48_flip_predictions
        _rad_gc.collect()

    del pixels, slot_mask, headers
    _rad_gc.collect()
    v48_pass2_predictions = [\
        _rad_predict_head(head, v48_features, v48_token_mask, device)\
        for head in e13_heads\
    ]
    if len(v48_pass2_predictions) != 5:
        raise RuntimeError('V48 second pass did not use all five E13 heads')
    v48_pass2_probability = _rad_np.mean(
        _rad_np.stack(v48_pass2_predictions), axis=0
    )
    if (
        v48_pass2_probability.shape != (len(test), len(_RAD_LABELS))
        or not _rad_np.isfinite(v48_pass2_probability).all()
    ):
        raise RuntimeError(
            f'invalid V48 pass-2 prediction: {v48_pass2_probability.shape}'
        )
    v48_pass2_rank = _rad_rank_columns(v48_pass2_probability)

    if v48_flip_rank is not None:
        _flip_ok = set(RUN.get('rad_flip_findings') or _RAD_LABELS)
        _merged = v48_pass2_rank.copy()
        _taken = []
        for _index, _label in enumerate(_RAD_LABELS):
            if _label in _flip_ok:
                _merged[:, _index] = (
                    v48_pass2_rank[:, _index] + v48_flip_rank[:, _index]
                ) / 2.0
                _taken.append(_label)
        v48_pass2_rank = _rad_rank_columns(_merged)
        _rad_log(
            f'flip TTA averaged into {len(_taken)} of {len(_RAD_LABELS)} findings: '
            f'{_taken}'
        )
        del _merged

    reference_branch = candidate_reference.copy()
    reference_branch[_RAD_LABELS] = _rad_rank_columns(
        (1.0 - _RAD_V48_SECOND_ALPHA)
        * _rad_rank_columns(candidate_reference[_RAD_LABELS].to_numpy())
        + _RAD_V48_SECOND_ALPHA * v48_pass2_rank
    )
    _rad_validate(reference_branch, expected_ids)
    _rad_log(
        f'V48 second E13 pass complete at alpha '
        f'{_RAD_V48_SECOND_ALPHA:.2f} on the E11 slot layout'
    )

    # V48 deploys the pinned reference branch directly after the second pass.
    # The alternative-head twin and legacy-DINO tie-break are not part of .917.
    _RAD_CAL = _rad_json.loads(_rad_zlib.decompress(
        _rad_b64.b64decode(_RAD_CAL_PAYLOAD)).decode())
    _RAD_CAL_GATE = set(_RAD_CAL['gate'])
    _RAD_CAL_W = RUN['rad_cal_w']

    def _rad_cal_protocol(uids):
        frame = _rad_pd.read_csv(
            ROOT / 'test_series.csv',
            dtype={'StudyInstanceUID': str, 'SeriesInstanceUID': str},
        )
        frame['StudyInstanceUID'] = frame['StudyInstanceUID'].astype(str)
        index = _rad_pd.Index([str(u) for u in uids], name='StudyInstanceUID')
        table = _rad_pd.DataFrame(index=index)
        table['n_series'] = frame.groupby(
            'StudyInstanceUID').size().reindex(index).fillna(0)
        for plane in ('Sagittal', 'Coronal', 'Axial'):
            part = frame[frame['Anatomical_Plane'].astype(str) == plane]
            table[f'n_{plane[:3]}'] = part.groupby(
                'StudyInstanceUID').size().reindex(index).fillna(0)
        for flag in ('Fat_Suppression', 'Fluid_Sensitive'):
            marked = frame[_rad_pd.to_numeric(\
                frame[flag], errors='coerce').fillna(0) > 0]
            table[flag[:3]] = marked.groupby(
                'StudyInstanceUID').size().reindex(index).fillna(0)
            for plane in ('Sagittal', 'Coronal', 'Axial'):
                part = marked[marked['Anatomical_Plane'].astype(str) == plane]
                table[f'{flag[:3]}_{plane[:3]}'] = part.groupby(
                    'StudyInstanceUID').size().reindex(index).fillna(0)
        if list(table.columns) != list(_RAD_CAL['protocol_columns']):
            raise RuntimeError('calibration protocol layout mismatch')
        return table.to_numpy(_rad_np.float64)

    def _rad_calibrate(branch):
        base = baseline_rank
        public = reference_rank
        pass2 = v48_pass2_rank
        mean = (base + public + pass2) / 3.0
        blocks = [base, public, pass2, public - base, pass2 - base, mean]
        for _grp in _RAD_CAL['groups']:
            cols = [_RAD_LABELS.index(t) for t in _grp]
            blocks.append(mean[:, cols].mean(axis=1, keepdims=True))
        blocks.append(_rad_cal_protocol(expected_ids))
        x = _rad_np.concatenate(blocks, axis=1)
        centre = _rad_np.asarray(_RAD_CAL['mean'], _rad_np.float64)
        spread = _rad_np.asarray(_RAD_CAL['scale'], _rad_np.float64)
        coef = _rad_np.asarray(_RAD_CAL['coef'], _rad_np.float64)
        bias = _rad_np.asarray(_RAD_CAL['intercept'], _rad_np.float64)
        if x.shape[1] != coef.shape[1]:
            raise RuntimeError(
                f'calibration expects {coef.shape[1]} columns, built {x.shape[1]}')
        adjusted = _rad_rank_columns(((x - centre) / spread) @ coef.T + bias)
        out = branch.copy()
        values = out[_RAD_LABELS].to_numpy(_rad_np.float64).copy()
        for index, target in enumerate(_RAD_LABELS):
            if target in _RAD_CAL_GATE:
                values[:, index] = (
                    (1.0 - _RAD_CAL_W) * values[:, index]
                    + _RAD_CAL_W * adjusted[:, index]
                )
        out[_RAD_LABELS] = _rad_rank_columns(values)
        _rad_validate(out, expected_ids)
        return out

    final = _rad_calibrate(reference_branch)
    globals()['V18_CALIBRATOR_APPLIED'] = True
    globals()['V18_CAL_GATE'] = tuple(sorted(_RAD_CAL_GATE))
    _rad_validate(final, expected_ids)
    temporary = primary.with_suffix('.csv.tmp')
    final.to_csv(temporary, index=False)
    _rad_os.replace(temporary, primary)

    receipt = {
        'recipe': 'V48 deployed reference branch: correct E13@0.50-inside-Rad -> E10@0.50 -> same E13 on E11 layout@0.15',
        'e13_member_weight_inside_rad': _RAD_E13_MEMBER_WEIGHT,
        'e10_alpha': _RAD_ALPHA,
        'e10_preserved_targets': list(_RAD_EXCLUDE),
        'v48_second_alpha': _RAD_V48_SECOND_ALPHA,
        'reference_heads_sha256': _RAD_REFERENCE_HEADS_SHA256,
        'e13_heads_sha256': _RAD_E13_HEADS_SHA256,
        'v48_second_heads_sha256': _RAD_E13_HEADS_SHA256,
        'v48_second_slots': [list(slot) for slot in _RAD_E11_SLOTS],
        'encoder_sha256': _RAD_ENCODER_SHA256,
        'test_studies': len(expected_ids),
        'e10_tokens': token_count,
        'v48_second_tokens': v48_pass2_token_count,
        'e13_tokens': e13_token_count,
        'submission_sha256': _rad_sha256(primary),
    }
    (work / 'v50_v2_repro_receipt.json').write_text(
        _rad_json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    )
    del (encoder, e13_heads, v48_pass2_predictions,
         v48_pass2_probability, v48_pass2_rank, v48_features, v48_token_mask)
    _rad_gc.collect()
    _rad_torch.cuda.empty_cache()
    _rad_log(
        f'V48 reference branch complete; reference-v15={reference_heads_path}; '
        f'e13-two-pass={e13_path}; second_alpha='
        f'{_RAD_V48_SECOND_ALPHA:.2f}; encoder={encoder_path}; '
        f'elapsed={(_rad_time.time()-started)/60:.1f}m'
    )

try:
    _rad_main()
except Exception as _rad_exc:
    print(f'[RadImageNet] Warning: {_rad_exc}. Preserving master 20-fold SOTA submission.csv.')
```

```
[RadImageNet] Selected device: cuda:0
[   79.3s] test-e10 laterality: 1 from the tag, 2 from geometry, 0 unresolved; tag and geometry disagree on 0 (0.0% of the tagged)
[   79.3s] test-e10: cache (3, 3, 8, 224, 224) = 0.0 GB
[   79.3s] test-e10: ordering 8 slot-series (366 slice headers)
[   80.0s] test-e10: ordered 8/8 by geometry (0 kept arbitrary) in 1s
[   80.0s] test-e10: decoding 8 slot-series
[   80.5s]   test-e10 8/8
[   80.5s] test-e10: 8/8 slots filled
[Rad-dual5] twin public-v15 families complete (/kaggle/input/rsna-knee-v52-radimagenet-heads-20260812/v52_radimagenet_heads.pt; /kaggle/input/rsna-knee-e9-radimagenet-heads-v15/v52_radimagenet_heads.pt)
[   82.9s] test-e13 laterality: 1 from the tag, 2 from geometry, 0 unresolved; tag and geometry disagree on 0 (0.0% of the tagged)
[   82.9s] test-e13: cache (3, 4, 8, 224, 224) = 0.0 GB
[   82.9s] test-e13: ordering 11 slot-series (444 slice headers)
[   83.9s] test-e13: ordered 11/11 by geometry (0 kept arbitrary) in 1s
[   83.9s] test-e13: decoding 11 slot-series
[   84.3s]   test-e13 11/11
[   84.3s] test-e13: 11/11 slots filled
[Rad-dual5] E13 FS-crop member complete at Rad-block weight 0.50 (/kaggle/input/rsna-knee-e13-train/rsna_rad_e11/v52_e11_heads.pt)
[Rad-dual5] twin E10 branches complete at alpha=0.50; preserved raw=["Baker's", 'Fracture']
[   85.4s] test-v48-pass2 laterality: 1 from the tag, 2 from geometry, 0 unresolved; tag and geometry disagree on 0 (0.0% of the tagged)
[   85.4s] test-v48-pass2: cache (3, 4, 8, 224, 224) = 0.0 GB
[   85.4s] test-v48-pass2: ordering 7 slot-series (185 slice headers)
[   85.9s] test-v48-pass2: ordered 7/7 by geometry (0 kept arbitrary) in 0s
[   85.9s] test-v48-pass2: decoding 7 slot-series
[   86.2s]   test-v48-pass2 7/7
[   86.2s] test-v48-pass2: 7/7 slots filled
[Rad-dual5] V48 second E13 pass complete at alpha 0.15 on the E11 slot layout
[Rad-dual5] V48 reference branch complete; reference-v15=/kaggle/input/rsna-knee-e9-radimagenet-heads-v15/v52_radimagenet_heads.pt; e13-two-pass=/kaggle/input/rsna-knee-e13-train/rsna_rad_e11/v52_e11_heads.pt; second_alpha=0.15; encoder=/kaggle/input/resnet-50-radimagenet-marwan/ResNet50.pt; elapsed=0.2m
```

linkcode

## Stage 4 — CoAtNet: Raptor views, residual checkpoints, final routing [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Stage-4-%E2%80%94-CoAtNet:-Raptor-views,-residual-checkpoints,-final-routing)

linkcode

### The Raptor module [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#The-Raptor-module)

Same source the release `exec`'d, unescaped so it can be read. View weights come from `RUN`, and arms sharing a volume recipe now decode each study once between them.

In \[35\]:

linkcode

```
# The Raptor arm. In the release this was a 36 KB backslash-escaped string
# handed to exec(); same source, same exec below, now readable. Two changes:
# view weights come from RUN, and arms sharing a volume recipe are grouped
# so each study is decoded once per recipe rather than once per arm.
_KE_SRC = r"""
import os, glob, time, gc, hashlib
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY', '1')
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
import timm
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
IMG = 336
CROP_MM = 140.0
SPAN_LO, SPAN_HI = 0.02, 0.98
SLOTS = [("Sagittal", 1, 18), ("Sagittal", 0, 14),\
         ("Coronal", 1, 12), ("Coronal", 0, 8), ("Axial", -1, 12)]
MAXS = sum(slot[2] for slot in SLOTS)
K_EVAL = 62
NORM = "imagenet"
LAB = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",\
       "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",\
       "Contusion", "Fracture"]
_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
_STD = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
_SLOTS64 = [("Sagittal", 1, 18), ("Sagittal", 0, 14),\
            ("Coronal", 1, 12), ("Coronal", 0, 8), ("Axial", -1, 12)]
_SLOTS44 = [("Sagittal", 1, 12), ("Sagittal", 0, 10),\
            ("Coronal", 1, 8), ("Coronal", 0, 6), ("Axial", -1, 8)]
ARMS = [\
    {"name": "maxspan-v5", "file": "raptor_ft_coatnet_v5_full_swa.pt",\
     "arch": "coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k", "res": 384,\
     "img": 336, "slots": _SLOTS64, "span": (0.02, 0.98), "k_eval": 62,\
     "reverse": False, "w": 0.55},\
    {"name": "native384dense-v10", "file": "raptor_ft_coatnet_v10_full.pt",\
     "arch": "coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k", "res": 384,\
     "img": 384, "slots": _SLOTS64, "span": (0.02, 0.98), "k_eval": 62,\
     "reverse": False, "w": 0.10},\
    {"name": "maxspan-v5-reverse", "file": "raptor_ft_coatnet_v5_full_swa.pt",\
     "arch": "coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k", "res": 384,\
     "img": 336, "slots": _SLOTS64, "span": (0.02, 0.98), "k_eval": 62,\
     "reverse": True, "w": 0.15},\
    {"name": "native384-v8", "file": "raptor_ft_coatnet_v8_full_swa.pt",\
     "arch": "coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k", "res": 384,\
     "img": 384, "slots": _SLOTS44, "span": (0.06, 0.94), "k_eval": 42,\
     "reverse": False, "w": 0.20},\
]

# View weights and the optional fifth view come from the RUN config.
_VIEW_W = (RUN.get("raptor_view_w") or {}) if "RUN" in globals() else {}
for _arm in ARMS:
    if _arm["name"] in _VIEW_W:
        _arm["w"] = float(_VIEW_W[_arm["name"]])
_EXTRA_W = RUN.get("raptor_extra_arm_w") if "RUN" in globals() else None
if _EXTRA_W:
    _v8 = next(a for a in ARMS if a["name"] == "native384-v8")
    ARMS.append({**_v8, "name": "native384-v8-reverse", "reverse": True,
                 "w": float(_EXTRA_W)})
    print(f"[arms] fifth view enabled at w={float(_EXTRA_W):.2f}; it shares a volume "
          f"recipe with native384-v8, so it adds GPU passes only", flush=True)

def build_backbone(arch, pretrained=False):
    hybrid = arch.startswith(('maxvit', 'maxxvit', 'coatnet', 'coat_', 'convnext'))
    is_vit = not hybrid and any((k in arch for k in ('vit', 'deit', 'dinov2', 'eva', 'beit')))
    kw = dict(pretrained=pretrained, num_classes=0, in_chans=3)
    if is_vit:
        kw.update(global_pool='token', dynamic_img_size=True)
    else:
        kw.update(global_pool='avg')
    return timm.create_model(arch, **kw)

class RaptorClassifier(nn.Module):

    def __init__(self, backbone, F_dim=768, n=12, drop=0.2):
        super().__init__()
        self.backbone = backbone
        self.norm = nn.LayerNorm(F_dim)
        self.att = nn.Sequential(nn.Linear(F_dim, 256), nn.Tanh(), nn.Dropout(drop), nn.Linear(256, n))
        self.clsW = nn.Parameter(torch.zeros(n, F_dim))
        self.clsb = nn.Parameter(torch.zeros(n))
        nn.init.trunc_normal_(self.clsW, std=0.02)
        self.n = n

    def encode(self, x):
        B, K = x.shape[:2]
        f = self.backbone(x.flatten(0, 1))
        return f.view(B, K, -1)

    def head(self, feats):
        h = self.norm(feats)
        a = self.att(h)
        a = torch.softmax(a, dim=1)
        pooled = torch.einsum('bkn,bkf->bnf', a, h)
        logits = (pooled * self.clsW).sum(-1) + self.clsb
        return logits

    def forward(self, x):
        return self.head(self.encode(x))

def load_model(pt_path, arch_default, res_default, device, ngpu=1):
    ck = torch.load(pt_path, map_location='cpu', weights_only=False)
    arch = ck.get('arch', arch_default)
    ck_res = int(ck.get('res', res_default))
    bb = build_backbone(arch, pretrained=False)
    model = RaptorClassifier(bb, F_dim=bb.num_features)
    model.load_state_dict(ck['model'], strict=True)
    model.eval().to(device)
    del ck
    gc.collect()
    return (model, ck_res)

def load_refit_head(pt_path, feature_dim, device):
    ck = torch.load(pt_path, map_location='cpu', weights_only=False)
    state = ck.get('model', ck)
    head = RaptorClassifier(nn.Identity(), F_dim=int(feature_dim))
    head_state = {name: tensor for name, tensor in state.items()
                  if not name.startswith('backbone.')}
    head.load_state_dict(head_state, strict=True)
    head.eval().to(device)
    del ck, state, head_state
    gc.collect()
    return head

def _eval_centers(mask, D, k):
    valid = np.where(mask > 0)[0]
    if len(valid) < 3:
        valid = np.arange(min(3, D))
    lo, hi = (int(valid.min()), int(valid.max()))
    cs = [c for c in range(lo + 1, hi) if c - 1 >= lo and c + 1 <= hi]
    if not cs:
        cs = [max(1, min((lo + hi) // 2, D - 2))]
    idx = np.linspace(0, len(cs) - 1, k).round().astype(int)
    return [cs[i] for i in idx]

def eval_windows(vol, mask, k, res, norm=NORM):
    D = vol.shape[0]
    cs = _eval_centers(mask, D, k)
    wins = np.empty((len(cs), 3, res, res), np.float32)
    for j, c in enumerate(cs):
        c = max(1, min(c, D - 2))
        tri = np.stack([vol[c - 1], vol[c], vol[c + 1]], 0).astype(np.float32) / 255.0
        t = torch.from_numpy(tri)
        if t.shape[-1] != res:
            t = F.interpolate(t[None], size=(res, res), mode='bilinear', align_corners=False)[0]
        wins[j] = t.numpy()
    x = torch.from_numpy(wins)
    if norm == 'imagenet':
        x = (x - _MEAN) / _STD
    return x

@torch.no_grad()
def infer_probs(model, xwins, device):
    x = xwins.unsqueeze(0).to(device)
    use_cuda = device != 'cpu' and str(device).startswith('cuda')
    if use_cuda:
        try:
            with torch.autocast('cuda', dtype=torch.float16):
                o = torch.sigmoid(model(x).float())
            return o[0].cpu().numpy()
        except RuntimeError:
            torch.cuda.empty_cache()
            o = torch.sigmoid(model(x).float())
            return o[0].cpu().numpy()
    o = torch.sigmoid(model(x).float())
    return o[0].cpu().numpy()

@torch.no_grad()
def infer_probs_two_heads(model, refit_head, xwins, device):
    x = xwins.unsqueeze(0).to(device)
    use_cuda = device != 'cpu' and str(device).startswith('cuda')
    def forward_heads():
        features = model.encode(x)
        original = torch.sigmoid(model.head(features).float())
        refitted = torch.sigmoid(refit_head.head(features).float())
        return (original[0].cpu().numpy(), refitted[0].cpu().numpy())
    if use_cuda:
        try:
            with torch.autocast('cuda', dtype=torch.float16):
                return forward_heads()
        except RuntimeError:
            torch.cuda.empty_cache()
            return forward_heads()
    return forward_heads()

def rankpct(x):
    order = x.argsort(0).argsort(0).astype(np.float64)
    return order / max(1, x.shape[0] - 1)

def _make_reader():
    import pydicom, cv2
    from pydicom.pixel_data_handlers.util import apply_modality_lut

    def order_and_meta(sdir):
        fs = glob.glob(sdir + '/*.dcm')
        recs = []
        ps_list = []
        for f in fs:
            try:
                h = pydicom.dcmread(f, stop_before_pixels=True)
                iop = getattr(h, 'ImageOrientationPatient', None)
                ipp = getattr(h, 'ImagePositionPatient', None)
                if iop is not None and ipp is not None and (len(iop) == 6):
                    r = np.array(iop[:3], float)
                    c = np.array(iop[3:], float)
                    n = np.cross(r, c)
                    pos = float(np.dot(np.array(ipp, float), n))
                else:
                    pos = float(getattr(h, 'InstanceNumber', 0) or 0)
                ps = getattr(h, 'PixelSpacing', None)
                ps = float(ps[0]) if ps is not None else 0.5
                ps_list.append(ps)
                recs.append((pos, f, ps))
            except Exception:
                recs.append((0.0, f, 0.5))
        recs.sort(key=lambda x: x[0])
        med_ps = float(np.median(ps_list)) if ps_list else 0.5
        return ([(f, ps) for _, f, ps in recs], med_ps)

    def read_px(f):
        d = pydicom.dcmread(f)
        a = apply_modality_lut(d.pixel_array, d).astype(np.float32)
        if str(getattr(d, 'PhotometricInterpretation', '')) == 'MONOCHROME1':
            a = a.max() - a
        return a

    def mm_crop_resize(a, ps):
        h, w = a.shape
        cpx = int(round(CROP_MM / max(ps, 0.001)))
        cpx = min(cpx, min(h, w))
        y0 = (h - cpx) // 2
        x0 = (w - cpx) // 2
        a = a[y0:y0 + cpx, x0:x0 + cpx]
        return cv2.resize(a, (IMG, IMG), interpolation=cv2.INTER_AREA)
    return (order_and_meta, read_px, mm_crop_resize)

def _pick_series_for_slot(rows, plane, fluid, used):
    cands = [r for r in rows if r['Anatomical_Plane'] == plane and r['SeriesInstanceUID'] not in used]
    if fluid in (0, 1):
        pref = [r for r in cands if int(r.get('Fluid_Sensitive', 0) or 0) == fluid]
        if pref:
            return pref[0]
    return cands[0] if cands else None

def build_study(sid, ser_records, tsdir, reader):
    order_and_meta, read_px, mm_crop_resize = reader
    rows = ser_records.get(sid, [])
    vol = np.zeros((MAXS, IMG, IMG), np.uint8)
    idx = 0
    used = set()
    for plane, fluid, k in SLOTS:
        r = _pick_series_for_slot(rows, plane, fluid, used)
        if r is None:
            idx += k
            continue
        used.add(r['SeriesInstanceUID'])
        files, med_ps = order_and_meta(f"{tsdir}/{sid}/{r['SeriesInstanceUID']}")
        if not files:
            idx += k
            continue
        n = len(files)
        lo, hi = (int(n * SPAN_LO), int(n * SPAN_HI) - 1)
        hi = max(hi, lo)
        picks = np.linspace(lo, hi, k).round().astype(int) if n > 1 else [0] * k
        arrs = []
        pss = []
        for p in picks:
            fp, ps = files[min(p, n - 1)]
            try:
                arrs.append(read_px(fp))
                pss.append(ps)
            except Exception:
                arrs.append(None)
                pss.append(med_ps)
        valid = [a for a in arrs if a is not None]
        if valid:
            allpx = np.concatenate([a.ravel() for a in valid])
            loq, hiq = np.percentile(allpx, [2.0, 98.0])
        else:
            loq, hiq = (0.0, 1.0)
        for a, ps in zip(arrs, pss):
            if idx >= MAXS:
                break
            if a is None:
                idx += 1
                continue
            aw = np.clip((a - loq) / (hiq - loq + 1e-06), 0, 1)
            aw = mm_crop_resize(aw, ps if ps > 0 else med_ps)
            vol[idx] = (aw * 255).astype(np.uint8)
            idx += 1
        if idx >= MAXS:
            break
    mask = (vol.reshape(MAXS, -1).sum(1) > 0).astype(np.uint8)
    return (vol, mask)

def find_test_root():
    cands = ['/kaggle/input/competitions/rsna-knee-abnormality-detection', '/kaggle/input/rsna-knee-abnormality-detection']
    for b in cands:
        if os.path.exists(b + '/test.csv'):
            return b
    for d, _, f in os.walk('/kaggle/input'):
        if 'test.csv' in f and (os.path.isdir(d + '/test_series') or os.path.isdir(d + '/test_images')):
            return d
    for d, _, f in os.walk('/kaggle/input'):
        if 'test.csv' in f:
            return d
    raise RuntimeError('no test root under /kaggle/input')

def find_weight_file(fname):
    direct = [f'/kaggle/input/raptor-knee-maxspan/{fname}', f'/kaggle/input/raptor-knee-native384dense/{fname}', f'/kaggle/input/raptor-knee-native384/{fname}', f'/kaggle/input/raptor-knee-arms/{fname}', f'/kaggle/input/raptor-knee-arms/1/{fname}', f'/kaggle/input/raptor-cnn336/{fname}']
    for p in direct:
        if os.path.exists(p):
            return p
    for d in sorted(glob.glob('/kaggle/input/*/')):
        if 'competition' in d.lower():
            continue
        hits = glob.glob(os.path.join(d, '**', fname), recursive=True)
        if hits:
            return hits[0]
    raise RuntimeError(f'{fname} not found under /kaggle/input')

def find_optional_verified_weight(fname, expected_sha256, root='/kaggle/input'):
    hits = []
    for directory in sorted(glob.glob(os.path.join(root, '*/'))):
        if 'competition' in directory.lower():
            continue
        hits.extend(glob.glob(os.path.join(directory, '**', fname), recursive=True))
    for path in sorted(set(hits)):
        digest = hashlib.sha256()
        with open(path, 'rb') as stream:
            for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() == expected_sha256:
            return path
        print(f'[head-refit] ignored hash-mismatched optional checkpoint: {path}', flush=True)
    return None

def main():
    import pandas as pd
    t0 = time.time()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device {dev} | gpus {torch.cuda.device_count()} | torch {torch.__version__}", flush=True)
    root = find_test_root()
    tsdir = root + "/test_series"
    if not os.path.isdir(tsdir):
        tsdir = root + "/test_images"
    print("test root:", root, "| series dir:", tsdir, flush=True)
    test = pd.read_csv(root + "/test.csv")
    test["StudyInstanceUID"] = test["StudyInstanceUID"].astype(str)
    test_ids = test["StudyInstanceUID"].tolist()
    tser = pd.read_csv(root + "/test_series.csv")
    tser["StudyInstanceUID"] = tser["StudyInstanceUID"].astype(str)
    tser["SeriesInstanceUID"] = tser["SeriesInstanceUID"].astype(str)
    series = {key: frame.to_dict("records") for key, frame in tser.groupby("StudyInstanceUID")}
    print(f"test studies {len(test_ids)} | test series {len(tser)}", flush=True)
    sub_cols = ["StudyInstanceUID"] + LAB
    sample = os.path.join(root, "sample_submission.csv")
    if os.path.exists(sample):
        sub_cols = list(pd.read_csv(sample, nrows=1).columns)
    reader = _make_reader()
    n_study, n_arm = len(test_ids), len(ARMS)
    arm_probs = [np.full((n_study, len(LAB)), 0.5, np.float32) for _ in range(n_arm)]
    # Arms that agree on image size, slot layout, span and window count see
    # exactly the same volume. The released loop rebuilt that volume once per
    # arm, so every study was decoded from DICOM as many times as there are
    # arms. Grouping by recipe decodes it once per recipe instead. Same
    # volumes, same windows, same models, same numbers.
    recipes = {}
    for arm_index, arm in enumerate(ARMS):
        key = (int(arm["img"]), tuple(tuple(slot) for slot in arm["slots"]),
               tuple(float(v) for v in arm["span"]), int(arm["k_eval"]))
        recipes.setdefault(key, []).append((arm_index, arm))
    print(f"[plan] {len(ARMS)} arms over {len(recipes)} volume recipe(s); "
          f"saves {len(ARMS) - len(recipes)} full pass(es) over the test set",
          flush=True)

    for recipe_index, (key, group) in enumerate(recipes.items()):
        img, slots, span, k_eval = key
        globals()["IMG"] = img
        globals()["SLOTS"] = [list(slot) for slot in slots]
        globals()["MAXS"] = sum(slot[2] for slot in SLOTS)
        globals()["SPAN_LO"], globals()["SPAN_HI"] = span
        globals()["K_EVAL"] = k_eval
        loaded = []
        for arm_index, arm in group:
            weight_path = find_weight_file(arm["file"])
            model, resolution = load_model(weight_path, arm["arch"], arm["res"], dev)
            loaded.append((arm_index, arm, model, resolution))
            print(f"[recipe {recipe_index}] arm {arm_index} {arm['name']} | img {IMG} | "
                  f"slices {MAXS} | span {SPAN_LO:.2f}-{SPAN_HI:.2f} | windows {K_EVAL} | "
                  f"res {resolution} | {time.time() - t0:.0f}s", flush=True)
        for study_index, study_uid in enumerate(test_ids):
            try:
                volume, mask = build_study(study_uid, series, tsdir, reader)
            except Exception as error:
                print(f"  [recipe {recipe_index}] study {study_index} {study_uid[:16]} "
                      f"BUILD FALLBACK ({type(error).__name__}: {error})", flush=True)
                continue
            for arm_index, arm, model, resolution in loaded:
                try:
                    windows = eval_windows(volume, mask, k=K_EVAL, res=resolution, norm=NORM)
                    if bool(arm.get("reverse", False)):
                        windows = windows.flip(1).contiguous()
                    arm_probs[arm_index][study_index] = infer_probs(model, windows, dev)
                    del windows
                except Exception as error:
                    print(f"  [arm {arm_index}] study {study_index} {study_uid[:16]} "
                          f"FALLBACK ({type(error).__name__}: {error})", flush=True)
            del volume, mask
            if (study_index + 1) % 100 == 0 or study_index + 1 == n_study:
                print(f"  [recipe {recipe_index}] {study_index + 1}/{n_study} | "
                      f"{time.time() - t0:.0f}s", flush=True)
        for _, _, model, _ in loaded:
            del model
        loaded.clear()
        gc.collect()
        if str(dev).startswith("cuda"):
            torch.cuda.empty_cache()
        print(f"[recipe {recipe_index}] done + freed | {time.time() - t0:.0f}s", flush=True)

    weights = np.array([float(arm.get("w", 1.0)) for arm in ARMS], dtype=np.float64)
    weights /= weights.sum()
    print(f"[blend] global probability mean w="
          f"{dict(zip([arm['name'] for arm in ARMS], weights.round(4)))}", flush=True)
    probability_blend = np.tensordot(
        weights, np.stack([np.clip(values, 0, 1) for values in arm_probs]), axes=(0, 0))
    ranks = rankpct(probability_blend)
    if not np.isfinite(ranks).all():
        ranks[~np.isfinite(ranks)] = 0.5
    submission = pd.DataFrame(ranks.astype(np.float32), columns=LAB)
    submission.insert(0, "StudyInstanceUID", test_ids)
    submission = submission[sub_cols]
    assert submission["StudyInstanceUID"].tolist() == test_ids
    assert np.isfinite(submission[LAB].values).all()
    out = "/kaggle/working/_raptor.csv"
    submission.to_csv(out, index=False)
    print("wrote", out, "|", len(submission), "rows x", len(submission.columns), "cols", flush=True)
    print(submission.head().to_string(index=False), flush=True)
    print(f"DONE {time.time() - t0:.0f}s", flush=True)

"""
```

In \[36\]:

linkcode

```
import numpy as _ke_np
import pandas as _ke_pd
from pathlib import Path as _KePath

_ke_primary = _KePath('/kaggle/working/submission.csv')
_ke_ours = _ke_pd.read_csv(_ke_primary, dtype={'StudyInstanceUID': str})
_KE_LAB = [c for c in _ke_ours.columns if c != 'StudyInstanceUID']

_KE_SRC
_KE_NS = {'__name__': '_ke_raptor', 'RUN': RUN}
exec(compile(_KE_SRC, '<raptor>', 'exec'), _KE_NS)
_KE_NS['main']()

# ---------------------------------------------------------------------
# 0.939 addition:
# blend residual-gated CoAt top3 into the public Raptor arm.
#
# IMPORTANT:
# This inner blend remains EXACTLY the reproduced 0.939 recipe:
#   60% old/public Raptor + 40% new residual-gated CoAt.
# Probe #22 does NOT modify this stage.
# ---------------------------------------------------------------------

def _coat_substitute():
    import hashlib as _h, os as _o, subprocess as _sp, sys as _sy
    from pathlib import Path as _P
    import pandas as _pd

    MAN_SHA = '98511a8fdeb9da0e6e70c78d013ff636e1476f31c80b5dc134d294b18c3f284e'
    WHL_SHA = '236c8df54a90f4d02076e6f9c1cc763d794542e886c576a6fee46ec8ff75a7a9'
    raptor = _P('/kaggle/working/_raptor.csv')

    def sha(p):
        d = _h.sha256()
        with _P(p).open('rb') as f:
            for b in iter(lambda: f.read(8 << 20), b''):
                d.update(b)
        return d.hexdigest()

    def find(name, want):
        root = _P('/kaggle/input')
        if not root.is_dir():
            return None
        for base in sorted(root.iterdir()):
            if base.name in ('competitions', 'train_series', 'test_series'):
                continue
            for p in sorted(base.rglob(name)):
                if p.is_file() and sha(p) == want:
                    return p
        return None

    man = find('coat_resgated_ep10_top3_manifest.json', MAN_SHA)
    if man is None:
        raise RuntimeError('coat manifest absent or hash mismatch')

    art = man.parent

    whl = find('opencv_python_headless-4.12.0.88-*.whl', WHL_SHA)
    if whl is None:
        for c in sorted(
            _P('/kaggle/input').rglob(
                'opencv_python_headless-4.12.0.88-*.whl'
            )
        ):
            if sha(c) == WHL_SHA:
                whl = c
                break

    if whl is None:
        raise RuntimeError('pinned opencv wheel absent or hash mismatch')

    envd = _P('/kaggle/working/_coat_env')
    _sp.run(
        [\
            _sy.executable,\
            '-m',\
            'pip',\
            'install',\
            '--no-deps',\
            '--quiet',\
            '--target',\
            str(envd),\
            str(whl),\
        ],
        check=True,
    )

    out = _P('/kaggle/working/_coat_arm.csv')

    child = (
        "import sys, json\n"
        f"sys.path.insert(0, {str(envd)!r})\n"
        f"sys.path.insert(0, {str(art)!r})\n"
        "import cv2; assert cv2.__version__ == '4.12.0', cv2.__version__\n"
        "import torch; assert torch.cuda.device_count() == 2\n"
        "import coatnet_resgated_ep10_top3_inference as rt\n"
        "assert rt.base.cv2.__version__ == '4.12.0'\n"
        "from pathlib import Path\n"
        "r = rt.run_submission("
        "competition_root=rt.base.find_competition_root(),\n"
        f"    artifact_root=Path({str(art)!r}), "
        f"output_path=Path({str(out)!r}),\n"
        "    gpu_batch_studies=2, backbone_micro_images=8)\n"
        "assert r['status'] == rt.SUBMISSION_STATUS\n"
        "assert r['models'] == 3\n"
        "assert [i['epoch'] for i in r['checkpoints']] == [4, 6, 8]\n"
        "assert r['fallback_studies'] == 0, r['failures']\n"
        "Path('/kaggle/working/_coat_arm_receipt.json').write_text("
        "json.dumps(r, indent=2))\n"
    )

    env = dict(_o.environ)
    env['PYTHONPATH'] = f"{envd}:{art}:" + env.get('PYTHONPATH', '')

    proc = _sp.run(
        [_sy.executable, '-c', child],
        env=env,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f'coat child failed: {proc.stderr[-700:]}'
        )

    pub = _pd.read_csv(
        raptor,
        dtype={'StudyInstanceUID': str},
    )

    ours = _pd.read_csv(
        out,
        dtype={'StudyInstanceUID': str},
    )

    if list(ours.columns) != list(pub.columns):
        raise RuntimeError('coat arm column drift')

    ours = (
        ours
        .set_index('StudyInstanceUID')
        .reindex(pub.StudyInstanceUID.astype(str).tolist())
        .reset_index()
    )

    lab = [\
        c for c in pub.columns\
        if c != 'StudyInstanceUID'\
    ]

    if ours[lab].isna().any().any():
        raise RuntimeError(
            'coat arm does not cover every study'
        )

    import json as _j
    import numpy as _np

    # Exact reproduced 0.939 inner blend.
    private_alpha = float(RUN['coat_private_alpha'])

    public_rank = pub[lab].rank(
        method='average',
        pct=True,
    )

    private_rank = ours[lab].rank(
        method='average',
        pct=True,
    )

    hybrid = pub.copy()

    hybrid[lab] = (
        (1.0 - private_alpha) * public_rank
        + private_alpha * private_rank
    ).rank(
        method='average',
        pct=True,
    )

    if not _np.isfinite(
        hybrid[lab].to_numpy(_np.float64)
    ).all():
        raise RuntimeError(
            'CoAt/Raptor hybrid contains non-finite values'
        )

    tmp = raptor.with_name(
        '.raptor_coat_hybrid.csv'
    )

    hybrid.to_csv(
        tmp,
        index=False,
    )

    _o.replace(
        tmp,
        raptor,
    )

    raptor.with_name(
        '_coat_raptor_blend_receipt.json'
    ).write_text(
        _j.dumps(
            {
                'contract':
                    'public_raptor_private_residual_coat_'
                    'global_rank_blend_v1',
                'private_alpha':
                    private_alpha,
                'public_raptor_alpha':
                    1.0 - private_alpha,
                'study_count':
                    len(ours),
                'finding_specific_weights':
                    False,
            },
            indent=2,
            sort_keys=True,
        )
        + '\n'
    )

    return len(ours)

_coat_public_path = _KePath(
    '/kaggle/working/_raptor.csv'
)

_coat_public_bytes = (
    _coat_public_path.read_bytes()
)

try:
    _coat_n = _coat_substitute()

    print(
        '[coat-arm] blended OUR resgated e4/e6/e8 '
        'into the public Raptor arm '
        f'(private alpha 0.400; {_coat_n} studies)',
        flush=True,
    )

except Exception as _coat_err:
    _coat_public_path.write_bytes(
        _coat_public_bytes
    )

    print(
        '[coat-arm] unavailable; restored PUBLIC '
        'raptor arm '
        f'({type(_coat_err).__name__}: {_coat_err})',
        flush=True,
    )

# ---------------------------------------------------------------------
# Align the strengthened Raptor arm with the Transformer/Rad branch.
# ---------------------------------------------------------------------

_ke_theirs = _ke_pd.read_csv(
    '/kaggle/working/_raptor.csv',
    dtype={'StudyInstanceUID': str},
)

assert (
    list(_ke_theirs.columns)
    == list(_ke_ours.columns)
), 'column drift'

_ke_theirs = (
    _ke_theirs
    .set_index('StudyInstanceUID')
    .reindex(_ke_ours['StudyInstanceUID'])
    .reset_index()
)

assert (
    _ke_theirs[_KE_LAB]
    .notna()
    .all()
    .all()
), 'study identity drift'

_ke_tr = _ke_ours[_KE_LAB].rank(
    method='average',
    pct=True,
)

_ke_cr = _ke_theirs[_KE_LAB].rank(
    method='average',
    pct=True,
)

_blend_transformer = _ke_ours.copy()
_blend_coatnet = _ke_theirs.copy()
_blend_labels = list(_KE_LAB)

_blend_tr = _ke_tr.copy()
_blend_cr = _ke_cr.copy()

# =====================================================================
# Preserve the exact reproduced 0.939 parent BEFORE probe #22.
#
# Original 0.939 outer routing:
#   Transformer/Rad = 40%
#   strengthened Raptor = 60%
# for all 12 targets.
#
# This file is diagnostic only. submission.csv below becomes #22.
# =====================================================================

_probe22_parent0939 = (
    _blend_transformer.copy()
)

for _probe22_label in _blend_labels:
    _probe22_parent0939[\
        _probe22_label\
    ] = (
        (1.0 - RUN['coatnet_w']['__default__'])
        * _blend_tr[_probe22_label]
        + RUN['coatnet_w']['__default__']
        * _blend_cr[_probe22_label]
    )

_probe22_parent0939[\
    _blend_labels\
] = (
    _probe22_parent0939[\
        _blend_labels\
    ]
    .rank(
        method='average',
        pct=True,
    )
)

assert _ke_np.isfinite(
    _probe22_parent0939[\
        _blend_labels\
    ].to_numpy(_ke_np.float64)
).all()

_probe22_parent0939_path = _KePath(
    '/kaggle/working/'
    'submission_0939_parent_exact.csv'
)

_probe22_parent0939.to_csv(
    _probe22_parent0939_path,
    index=False,
)

# Compatibility name retained, but now correctly means
# the unmodified 0.939 parent before probe #22.
_probe22_parent_compat_path = _KePath(
    '/kaggle/working/'
    'submission_parent_exact.csv'
)

_probe22_parent0939.to_csv(
    _probe22_parent_compat_path,
    index=False,
)

# =====================================================================
# PROBE #22
#
# 0.939 parent
#   +
# #15 target-specific outer routing
#
# IMPORTANT:
# _blend_cr already contains the exact 0.939 hybrid Raptor:
#   60% old/public Raptor
#   40% residual-gated CoAt e4/e6/e8
#
# Probe #22 changes ONLY the OUTER Raptor weight.
# =====================================================================

_coatnet_weight = {label: coat_w(label) for label in _blend_labels}

# The guard still fires if the code and the config disagree; it just no
# longer hard-codes probe #22's numbers in a second place.
_expected_22 = {label: coat_w(label) for label in _blend_labels}

assert (
    set(_coatnet_weight)
    == set(_expected_22)
)

for _label, _expected in (
    _expected_22.items()
):
    assert abs(
        float(
            _coatnet_weight[_label]
        )
        - _expected
    ) < 1e-12

print(
    '[probe #22] '
    '0.939 parent + #15 target-specific '
    'outer routing',
    flush=True,
)

print(
    '[probe #22] '
    'inner Raptor blend remains '
    'public=0.60 / residual-CoAt=0.40',
    flush=True,
)

print(
    '[probe #22] '
    'target-specific outer weights:',
    flush=True,
)

for _label in _blend_labels:
    print(
        f'  {_label:18s} '
        f'T='
        f'{1.0 - _coatnet_weight[_label]:.2f} '
        f'R='
        f'{_coatnet_weight[_label]:.2f}',
        flush=True,
    )

# ---------------------------------------------------------------------
# Apply #22 outer routing using the SAME final rerank as the 0.939 parent.
# ---------------------------------------------------------------------

_blend_output = (
    _blend_transformer.copy()
)

for _blend_label in _blend_labels:

    _blend_w = float(
        _coatnet_weight[\
            _blend_label\
        ]
    )

    _blend_output[\
        _blend_label\
    ] = (
        (1.0 - _blend_w)
        * _blend_tr[\
            _blend_label\
        ]
        + _blend_w
        * _blend_cr[\
            _blend_label\
        ]
    )

_blend_output[\
    _blend_labels\
] = (
    _blend_output[\
        _blend_labels\
    ].rank(
        method='average',
        pct=True,
    )
)

assert _ke_np.isfinite(
    _blend_output[\
        _blend_labels\
    ].to_numpy(
        _ke_np.float64
    )
).all()

# ---------------------------------------------------------------------
# Hard gate:
# targets whose outer weight remains 0.60 must be exactly identical
# to the reproduced 0.939 parent.
# ---------------------------------------------------------------------

_probe22_changed_targets = [\
    label for label in _blend_labels\
    if abs(coat_w(label) - RUN['coatnet_w']['__default__']) > 1e-12\
]

_probe22_unchanged_targets = [\
    label\
    for label in _blend_labels\
    if label\
    not in _probe22_changed_targets\
]

for _label in (
    _probe22_unchanged_targets
):
    _probe22_parent_values = (
        _probe22_parent0939[\
            _label\
        ].to_numpy(
            _ke_np.float64
        )
    )

    _probe22_candidate_values = (
        _blend_output[\
            _label\
        ].to_numpy(
            _ke_np.float64
        )
    )

    if not _ke_np.array_equal(
        _probe22_parent_values,
        _probe22_candidate_values,
    ):
        raise RuntimeError(
            '[probe #22] unchanged target '
            f'drifted: {_label}'
        )

# ---------------------------------------------------------------------
# Write final submission.csv.
#
# No public0033/fullfit0033 overlay is allowed in probe #22.
# This deliberately removes the optional legacy branch which could
# overwrite Medial Meniscus after the #22 routing.
# ---------------------------------------------------------------------

_blend_output.to_csv(
    _ke_primary,
    index=False,
)

print(
    '[probe #22] '
    '0033 overlay DISABLED; '
    'pure target-routed 0.939 candidate retained',
    flush=True,
)

# ---------------------------------------------------------------------
# Receipt / audit.
# ---------------------------------------------------------------------

import hashlib as _ke_hashlib
import json as _ke_json

def _ke_sha256(_ke_path):
    _ke_digest = (
        _ke_hashlib.sha256()
    )

    with _KePath(
        _ke_path
    ).open(
        'rb'
    ) as _ke_handle:

        for _ke_block in iter(
            lambda:
                _ke_handle.read(
                    8 << 20
                ),
            b'',
        ):
            _ke_digest.update(
                _ke_block
            )

    return (
        _ke_digest.hexdigest()
    )

_probe22_parent_sha = (
    _ke_sha256(
        _probe22_parent0939_path
    )
)

_probe22_output_sha = (
    _ke_sha256(
        _ke_primary
    )
)

_probe22_changed_numeric_counts = {}

for _label in (
    _probe22_changed_targets
):
    _parent_values = (
        _probe22_parent0939[\
            _label\
        ].to_numpy(
            _ke_np.float64
        )
    )

    _candidate_values = (
        _blend_output[\
            _label\
        ].to_numpy(
            _ke_np.float64
        )
    )

    _probe22_changed_numeric_counts[\
        _label\
    ] = int(
        _ke_np.count_nonzero(
            _parent_values
            != _candidate_values
        )
    )

_probe22_receipt = {
    'contract':
        'public0939_target_specific_'
        'outer_routing_probe22_v1',

    'status':
        'passed',

    'candidate_id':
        22,

    'candidate_name':
        'public0939_plus_probe15_outer_map',

    'parent':
        'reproduced_public_0.939',

    'parent0939_path':
        str(
            _probe22_parent0939_path
        ),

    'parent0939_sha256':
        _probe22_parent_sha,

    'output_path':
        str(
            _ke_primary
        ),

    'output_sha256':
        _probe22_output_sha,

    'study_count':
        int(
            len(
                _blend_output
            )
        ),

    'bag_present':
        False,

    'overlay_applied':
        False,

    'inner_public_raptor_alpha':
        0.60,

    'inner_private_coat_alpha':
        0.40,

    'inner_finding_specific_weights':
        False,

    'outer_raptor_weight_by_target':
        {
            label:
                float(
                    _coatnet_weight[\
                        label\
                    ]
                )
            for label
            in _blend_labels
        },

    'changed_targets':
        list(
            _probe22_changed_targets
        ),

    'unchanged_targets':
        list(
            _probe22_unchanged_targets
        ),

    'changed_numeric_count_by_target':
        _probe22_changed_numeric_counts,

    'unchanged_targets_exact_parent_match':
        True,

    'final_rank_after_outer_blend':
        True,

    'raptor_arms':
        [\
            {\
                'name':\
                    arm['name'],\
\
                'weight':\
                    float(\
                        arm['w']\
                    ),\
\
                'windows':\
                    int(\
                        arm[\
                            'k_eval'\
                        ]\
                    ),\
            }\
            for arm\
            in _KE_NS[\
                'ARMS'\
            ]\
        ],
}

_probe22_receipt_path = _KePath(
    '/kaggle/working/'
    'probe22_outer_routing_receipt.json'
)

_probe22_receipt_path.write_text(
    _ke_json.dumps(
        _probe22_receipt,
        indent=2,
        sort_keys=True,
    )
    + '\n',
    encoding='utf-8',
)

# Keep the historical receipt filename as a compatibility alias,
# but with truthful #22 contents rather than the old global-0.60 claim.
_KePath(
    '/kaggle/working/'
    'repro937_fallback_receipt.json'
).write_text(
    _ke_json.dumps(
        _probe22_receipt,
        indent=2,
        sort_keys=True,
    )
    + '\n',
    encoding='utf-8',
)

_ke_ours = _ke_pd.read_csv(
    _ke_primary,
    dtype={
        'StudyInstanceUID':
            str
    },
)

assert (
    _ke_ours[\
        'StudyInstanceUID'\
    ].astype(str).tolist()
    ==
    _blend_output[\
        'StudyInstanceUID'\
    ].astype(str).tolist()
)

assert _ke_np.isfinite(
    _ke_ours[\
        _blend_labels\
    ].to_numpy(
        _ke_np.float64
    )
).all()

print(
    '[probe #22] PASS',
    flush=True,
)

print(
    '[probe #22] parent 0.939 sha256:',
    _probe22_parent_sha,
    flush=True,
)

print(
    '[probe #22] candidate sha256:',
    _probe22_output_sha,
    flush=True,
)

print(
    '[probe #22] changed row counts:',
    _probe22_changed_numeric_counts,
    flush=True,
)

print(
    '[probe #22] submission:',
    _ke_primary,
    flush=True,
)

print(
    '[probe #22] receipt:',
    _probe22_receipt_path,
    flush=True,
)
```

```
device cuda | gpus 2 | torch 2.10.0+cu128
test root: /kaggle/input/rsna-knee-abnormality-detection | series dir: /kaggle/input/rsna-knee-abnormality-detection/test_series
test studies 3 | test series 15
[plan] 4 arms over 3 volume recipe(s); saves 1 full pass(es) over the test set
[recipe 0] arm 0 maxspan-v5 | img 336 | slices 64 | span 0.02-0.98 | windows 62 | res 384 | 3s
[recipe 0] arm 2 maxspan-v5-reverse | img 336 | slices 64 | span 0.02-0.98 | windows 62 | res 384 | 5s
  [recipe 0] 3/3 | 31s
[recipe 0] done + freed | 31s
[recipe 1] arm 1 native384dense-v10 | img 384 | slices 64 | span 0.02-0.98 | windows 62 | res 384 | 34s
  [recipe 1] 3/3 | 41s
[recipe 1] done + freed | 41s
[recipe 2] arm 3 native384-v8 | img 384 | slices 44 | span 0.06-0.94 | windows 42 | res 384 | 45s
  [recipe 2] 3/3 | 60s
[recipe 2] done + freed | 61s
[blend] global probability mean w={'maxspan-v5': np.float64(0.55), 'native384dense-v10': np.float64(0.1), 'maxspan-v5-reverse': np.float64(0.15), 'native384-v8': np.float64(0.2)}
wrote /kaggle/working/_raptor.csv | 3 rows x 13 cols
                                                StudyInstanceUID  ACL  MCL  Medial Meniscus  Lateral Meniscus  Medial OA  Lateral OA  PF OA  Effusion  Synovitis  Baker's  Contusion  Fracture
1.2.826.0.1.3680043.8.498.10047035057544427318018579121635276191  0.0  0.0              1.0               0.0        1.0         0.0    0.0       0.5        0.0      1.0        0.0       0.0
1.2.826.0.1.3680043.8.498.10062861783145312629332250977456991776  0.5  1.0              0.5               1.0        0.5         0.5    0.5       1.0        1.0      0.5        1.0       1.0
1.2.826.0.1.3680043.8.498.10067514707072572280263481548497591402  1.0  0.5              0.0               0.5        0.0         1.0    1.0       0.0        0.5      0.0        0.5       0.5
DONE 61s
[coat-arm] blended OUR resgated e4/e6/e8 into the public Raptor arm (private alpha 0.400; 3 studies)
[probe #22] 0.939 parent + #15 target-specific outer routing
[probe #22] inner Raptor blend remains public=0.60 / residual-CoAt=0.40
[probe #22] target-specific outer weights:
  ACL                T=0.25 R=0.75
  MCL                T=0.40 R=0.60
  Medial Meniscus    T=0.20 R=0.80
  Lateral Meniscus   T=0.00 R=1.00
  Medial OA          T=0.40 R=0.60
  Lateral OA         T=0.25 R=0.75
  PF OA              T=0.40 R=0.60
  Effusion           T=0.40 R=0.60
  Synovitis          T=0.40 R=0.60
  Baker's            T=0.40 R=0.60
  Contusion          T=0.40 R=0.60
  Fracture           T=0.25 R=0.75
[probe #22] 0033 overlay DISABLED; pure target-routed 0.939 candidate retained
[probe #22] PASS
[probe #22] parent 0.939 sha256: 7d3b8bd4e76b309171e2c44a58301e71da26104d1049cc9f8c445c17eee3c770
[probe #22] candidate sha256: ff848c73ba6f31e487d175161304d26df307e6e777189c01dfb508a76532ddfc
[probe #22] changed row counts: {'ACL': 0, 'Medial Meniscus': 2, 'Lateral Meniscus': 0, 'Lateral OA': 0, 'Fracture': 0}
[probe #22] submission: /kaggle/working/submission.csv
[probe #22] receipt: /kaggle/working/probe22_outer_routing_receipt.json
```

linkcode

## Diagnostics — is the routing doing anything? [¶](https://www.kaggleusercontent.com/kf/352801590/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..kxuKLrIkX6V91p4XXudVrg.5v1LYPi90iJhMl6cLPNgZpEE4R05Q7oUvBvz-wd_FHJ9P7IqoUleO_407NiddmJBDYAJuL3cnkUHHzpFoMMpViCVtot7kFamhuoObMKahk735Ioh433mGpQj_rEAJJZst2pEf5049KoUGcWRVtD-eJiGj6dq_wvmdKgQrcIR1GS-9hD9cxeUuK2mbnDhMfImKA04UTbEQ3nrSrnKjb7Nn6nvvPKdS4Vz1j3Wbxhc7Ym_xdoAcSaEccbnpnpQk8dJhfoL9Hjfym8AX1047msDaVf9D3NsWWb8Vb9v-KsMeIKlo8NM7xj3BhvP6WQsIMEpxBHVj05bfIyTUrU2PVczUDDmCmJtoVhiEDVbfovTHjPSJgDtQ21zKKiaG86nTxmjvqrP3UDhj49uYPiLxaQFE0wAYIYo1aVE-nNDPa_s_U2u7SMPLiSPbQ5mTxCr-qyaCBjg4A6gusUOtv49oWQ2Q-y29dqxRurwZ04UAlYJSmhqSVOcqFRLoZDKQxFfVeYsbNDIc7m0Qw0reV5eWCV6U_bvEMIhxG4_RxpmitZ-3TGeN_wLULR7P2wc2_c-enLLEM2KYWkKNvcu2pzXhpSooeaZDQItD7hmDiFhQQetymSvjUa2cz886XXE02_YnqMBAcvha6mRL4dg-MnJ3j11FA.mSdL4COEmG3VbI6xJAOtEQ/__results__.html?sharingControls=true\#Diagnostics-%E2%80%94-is-the-routing-doing-anything?)

In \[37\]:

linkcode

```
# ========================= DIAGNOSTICS =====================================
# Two questions the leaderboard cannot answer, both cheap here because the two
# arms are still in memory:
#
#   agreement - if the transformer stack and the CoAtNet arm rank studies
#               almost identically for a finding, then the outer weight for
#               that finding cannot matter, whatever the probes suggested;
#   ties      - a block of identical scores earns half credit against every
#               study it ties with.
import numpy as _dg_np
import pandas as _dg_pd

try:
    _dg_labels = list(_blend_labels)
    _dg_rows = []
    for _dg_label in _dg_labels:
        left = _blend_tr[_dg_label].to_numpy(_dg_np.float64)
        right = _blend_cr[_dg_label].to_numpy(_dg_np.float64)
        final = _blend_output[_dg_label].to_numpy(_dg_np.float64)
        _dg_rows.append({
            "finding": _dg_label,
            "outer CoAtNet w": coat_w(_dg_label),
            "arm agreement": float(_dg_np.corrcoef(left, right)[0, 1]),
            "largest tie block": int(_dg_np.unique(final, return_counts=True)[1].max()),
        })
    _DG = _dg_pd.DataFrame(_dg_rows).set_index("finding")
    print(_DG.to_string(float_format=lambda v: f"{v:.3f}"))

    _dg_flat = _DG[_DG["arm agreement"] > 0.99]
    if len(_dg_flat):
        print("\nThese findings have two arms that already agree above 0.99, so "
              "their outer weight is close to a no-op no matter what it is set to:",
              ", ".join(_dg_flat.index), flush=True)
    _dg_loud = _DG[_DG["arm agreement"] < 0.85]
    if len(_dg_loud):
        print("\nThese findings have genuinely different arms, which is where an "
              "outer weight actually decides the ordering — and therefore where a "
              "weight fitted to the public split can do real damage privately:",
              ", ".join(_dg_loud.index), flush=True)
except NameError:
    print("[diag] fusion variables not in memory; run the final stage first", flush=True)
```

```
                  outer CoAtNet w  arm agreement  largest tie block
finding
ACL                         0.750          0.500                  1
MCL                         0.600          0.500                  1
Medial Meniscus             0.800         -0.500                  1
Lateral Meniscus            1.000          1.000                  1
Medial OA                   0.600         -1.000                  1
Lateral OA                  0.750          0.500                  1
PF OA                       0.600          1.000                  1
Effusion                    0.600          0.500                  1
Synovitis                   0.600          1.000                  1
Baker's                     0.600          1.000                  1
Contusion                   0.600          0.500                  1
Fracture                    0.750          1.000                  1

These findings have two arms that already agree above 0.99, so their outer weight is close to a no-op no matter what it is set to: Lateral Meniscus, PF OA, Synovitis, Baker's, Fracture

These findings have genuinely different arms, which is where an outer weight actually decides the ordering — and therefore where a weight fitted to the public split can do real damage privately: ACL, MCL, Medial Meniscus, Medial OA, Lateral OA, Effusion, Contusion
```

## License

This Notebook has been released under the [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0) open source license.

## Continue exploring

- ![](https://www.kaggle.com/static/images/kernel/viewer/input_light.svg)







Input

16 files




arrow\_right\_alt

- ![](https://www.kaggle.com/static/images/kernel/viewer/output_light.svg)







Output

134 files




arrow\_right\_alt

- ![](https://www.kaggle.com/static/images/kernel/viewer/logs_light.svg)







Logs

590.2 second run - successful




arrow\_right\_alt

- ![](https://www.kaggle.com/static/images/kernel/viewer/comments_light.svg)







Comments

1 comment




arrow\_right\_alt