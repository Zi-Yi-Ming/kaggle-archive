# EXP-004 Axial fold0 — 运行计划

- Kernel actual slug: `ziyiming/rsna-exp-004-axial-fold0-gpu`
- Status: v1 ERROR（preflight 误用扁平路径）；**v2 已推送**，preflight 改为 `test_series/<Study>/<Series>/*.dcm`
- 对照: EXP-003 S+C fold0 LB=**0.685**
- Push dir: `rsna_knee/_push_exp004/`
- 唯一训练变量: `--planes axial`（相对 EXP-003 fold0 S+C / EXP-001 fold0 Sagittal）
- 超参: epochs=3 batch=8 n-clips=2 folds=5 only-fold=0 seed=42 fuse 默认
- 代码: EXP-003 同源 rsna_v3 `1612f21b81b0abb56735a5675504043aced36a468c25328004d7bf35f5f02630` + labels `bc356e71999ca16bcf07293c8cccf50f786f79177cb1b3c32f476b4442775a1a`
- Inputs: competition + resnet34-imagenet-pth + torch-cu118-offline
- Artifact 预期路径: `artifacts/exp_004_axial_fold0/fold0/Axial/`（若代码走 per-plane）或 `.../fold0/`
- 提交策略: notebook 不自动提交；拉回 pred 后与 exp003 fold0 S+C 本地 mean 成 S+C+A 再决定提交
- TIMING: 只认本 run meta.json
- GPU 预算: 30h 可用；Axial fold0 量级参照 S/C fold0（2–3.5h 为历史参考，非本次承诺）

## 提交命令（确认后执行）

```powershell
kaggle kernels push -p rsna_knee/_push_exp004
```

## 跑完后

1. `kaggle kernels output -k ziyiming/rsna-exp-004-axial-fold0-gpu -p rsna_knee/_out/exp004_axial_pull`
2. 校验 meta status=done / shape / uid_match
3. 本地 fuse: mean(Axial, Sagittal, Coronal) fold0
4. 对照 LB: Axial-only vs 0.685 S+C fold0
