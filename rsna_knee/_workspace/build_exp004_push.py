from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
PUSH = ROOT / "_push_exp004"
PUSH.mkdir(parents=True, exist_ok=True)

# Use EXP-003 embedded sources for single-variable code parity
v3 = Path(r"D:/桌面/Kaggle/_workspace/rsna_exp004_prep/embedded_rsna_v3.py").read_bytes()
lab = Path(r"D:/桌面/Kaggle/_workspace/rsna_exp004_prep/embedded_rsna_report_labels.py").read_bytes()
v3_h = hashlib.sha256(v3).hexdigest()
lab_h = hashlib.sha256(lab).hexdigest()
assert v3_h == "1612f21b81b0abb56735a5675504043aced36a468c25328004d7bf35f5f02630", v3_h
assert lab_h == "bc356e71999ca16bcf07293c8cccf50f786f79177cb1b3c32f476b4442775a1a", lab_h
b64_v3 = base64.b64encode(v3).decode("ascii")
b64_lab = base64.b64encode(lab).decode("ascii")

md = [
    "# RSNA EXP-004 Axial fold0\n",
    "\n",
    "唯一变量: planes `sagittal,coronal` → `axial`（相对 EXP-003 fold0）\n",
    "对照: EXP-003 S+C fold0 LB=**0.685**（当前 BEST）/ EXP-001 fold0 Sagittal LB=0.663\n",
    "\n",
    "- 超参与 EXP-003 fold0 完全一致: epochs=3 batch=8 n_clips=2 seed=42 ResNet34 report-labels\n",
    "- 代码与 EXP-003 同源（sha256 锁定，含 per-plane artifact 布局 `fold{k}/{plane}/`）\n",
    f"- rsna_v3 sha256: `{v3_h}`\n",
    f"- labels sha256: `{lab_h}`\n",
    "- 依据: test_series 3/3 study 含 Axial；fold 间相关 ~0.85，平面相关仅 ~0.47 → 加平面 > 堆 fold\n",
    "- 跑完本地再与已有 S+C fold0 pred 做 mean，不在此 notebook 自动提交\n",
    "- TIMING: 以本 run meta.json 为准，不预填估算\n",
]

cell_torch = """# 提交模式:禁网(enable_internet:false),torch 2.2.0+cu118 + nvidia-cu11 依赖全部离线安装
# 坑1:Kaggle 挂载把文件名中 '+' 去掉(2.2.0cu118=非法 PEP440)→ 复制为合法名
# 坑2:torch 2.2.0+cu118 的 CUDA 库在 nvidia-*-cu11 依赖包中(不在 torch wheel 内),
#     只装 torch 会缺 libcudart(v8/v9 实证)→ 必须显式安装全部 13 个 wheel
# 坑3:/kaggle/working 会被收集为 kernel 输出 → 装完立即删除
import subprocess, sys, os, glob, shutil
wh = sorted(glob.glob('/kaggle/input/**/*.whl', recursive=True))
print('挂载 wheel 共', len(wh), '个')
for w in wh: print('  ', os.path.basename(w))
assert len(wh) >= 13, 'FAIL: 离线 wheel 不足(应 13: torch+torchvision+11 nvidia-cu11)'
fixed = []
for w in wh:
    base = os.path.basename(w)
    dst = os.path.join('/kaggle/working', base.replace('cu118', '+cu118', 1) if 'cu118' in base else base)
    shutil.copy(w, dst)
    fixed.append(dst)
print('安装 wheel:', [os.path.basename(f) for f in fixed])
subprocess.check_call([sys.executable,"-m","pip","uninstall","-y","-q","torch","torchvision","torchaudio"])
# 显式安装全部 wheel(--no-deps --no-index: 无版本解析/无联网)
subprocess.check_call([sys.executable,"-m","pip","install","-q","--no-deps","--no-index"] + fixed)
for f in fixed: os.remove(f)
import numpy, torch, torchvision, sklearn, pandas
print("torch", torch.__version__, "cuda", torch.version.cuda, "| numpy", numpy.__version__)
assert torch.cuda.is_available()
print("GPU:", torch.cuda.get_device_name(0))
"""

cell_preflight = """# preflight: competition mount + Axial coverage (train/test) — 防训完才发现没 Axial
import os, csv
base='/kaggle/input'
def _find(b, depth=0, max_depth=3):
    if not os.path.isdir(b): return None
    try: entries = sorted(os.listdir(b))
    except OSError: return None
    for e in entries:
        p = os.path.join(b, e)
        if not os.path.isdir(p): continue
        if e in ('train_series', 'test_series'): continue
        if os.path.isfile(os.path.join(p, 'test.csv')) and os.path.isdir(os.path.join(p, 'test_series')):
            return p
        if depth < max_depth - 1:
            r = _find(p, depth + 1)
            if r: return r
    return None
root = _find(base)
if root is None:
    raise SystemExit('FAIL: 未找到含 test_series+test.csv 的比赛挂载')
print('root =', root)

def plane_stats(series_csv, series_dir, label):
    if not os.path.isfile(series_csv):
        print(label, 'series csv missing', series_csv)
        return
    with open(series_csv, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    plane_key = None
    for k in rows[0].keys() if rows else []:
        if 'plane' in k.lower() or 'anatom' in k.lower():
            plane_key = k
            break
    uid_key = 'StudyInstanceUID'
    from collections import Counter, defaultdict
    c = Counter()
    studies = defaultdict(set)
    for r in rows:
        pl = r.get(plane_key, '?') if plane_key else '?'
        c[pl] += 1
        if uid_key in r:
            studies[pl].add(r[uid_key])
    print(label, 'plane series counts', dict(c))
    print(label, 'plane study counts', {k: len(v) for k, v in studies.items()})
    axial_studies = studies.get('Axial', set())
    print(label, 'Axial studies', len(axial_studies))
    assert len(axial_studies) > 0, f'FAIL: {label} 无 Axial study'
    # sample dicom counts for axial series in test
    if label == 'test':
        n_dcm = 0
        axial_series = [r['SeriesInstanceUID'] for r in rows if r.get(plane_key)=='Axial']
        for se in axial_series[:4]:
            sdir = os.path.join(series_dir, se)
            if not os.path.isdir(sdir):
                print(' missing axial series dir', se)
                continue
            k = len([f for f in os.listdir(sdir) if f.lower().endswith('.dcm')])
            print(' axial series', se[:16], 'dcm', k)
            n_dcm += k
        print('test axial dcm sample total', n_dcm)
        assert n_dcm > 0, 'FAIL: test Axial DICOM 为空'
    return studies

plane_stats(os.path.join(root,'test_series.csv'), os.path.join(root,'test_series'), 'test')
# train_series may be large but csv is small
plane_stats(os.path.join(root,'train_series.csv'), os.path.join(root,'train_series'), 'train')
print('preflight axial: OK')
"""

cell_v3 = f'''import base64, os, hashlib
parts = []
parts.append("{b64_v3}")
path = "/kaggle/working/rsna_v3.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(base64.b64decode(parts[0]).decode("utf-8"))
expect = "{v3_h}"
h = hashlib.sha256(open(path, "rb").read()).hexdigest()
print(f"wrote rsna_v3.py ({{os.path.getsize(path)}} bytes)")
print("sha256", h)
assert h == expect, f"V3 HASH MISMATCH {{h}} != {{expect}}"
src = open(path, encoding="utf-8").read()
assert "_fold_dir" in src, "missing per-plane artifact layout (need EXP-003 code)"
print("rsna_v3 EXP-003-parity OK")
'''

cell_lab = f'''import base64, os, hashlib
parts = []
parts.append("{b64_lab}")
path = "/kaggle/working/rsna_report_labels.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(base64.b64decode(parts[0]).decode("utf-8"))
expect = "{lab_h}"
h = hashlib.sha256(open(path, "rb").read()).hexdigest()
print(f"wrote rsna_report_labels.py ({{os.path.getsize(path)}} bytes)")
print("sha256", h)
assert h == expect, f"LABEL HASH MISMATCH {{h}} != {{expect}}"
print("baseline labels OK")
'''

cell_run = '''import subprocess, sys, os, json
os.chdir("/kaggle/working")
cmd = [sys.executable, "-u", "rsna_v3.py",
       "--planes", "axial",
       "--epochs", "3", "--folds", "5", "--only-fold", "0",
       "--batch", "8", "--n-clips", "2",
       "--experiment-id", "exp_004_axial_fold0",
       "--verbose"]
print("=== EXP-004 Axial fold0 ===", flush=True)
print(" ".join(cmd), flush=True)
r = subprocess.run(cmd)
print("returncode", r.returncode, flush=True)

import numpy as np, pandas as pd
artifact_root = "/kaggle/working/artifacts/exp_004_axial_fold0"
# EXP-003-parity code stores per-plane dirs
candidates = [
    os.path.join(artifact_root, "fold0", "Axial"),
    os.path.join(artifact_root, "fold0"),
]
canon = None
for uid_path in [
    os.path.join(artifact_root, "test_uid.csv"),
    os.path.join(artifact_root, "fold0", "Axial", "test_uid.csv"),
    os.path.join(artifact_root, "fold0", "test_uid.csv"),
]:
    if os.path.isfile(uid_path):
        canon = pd.read_csv(uid_path)["StudyInstanceUID"].tolist()
        print("canonical uids", len(canon), "from", uid_path)
        break

found = None
for d in candidates:
    ok = all(os.path.isfile(os.path.join(d, n)) for n in ["test_pred.npy", "test_uid.csv", "meta.json"])
    print(f"[artifact] {d}: {'PASS' if ok else 'MISSING'}")
    if ok:
        found = d
        meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
        pred = np.load(os.path.join(d, "test_pred.npy"))
        uids = pd.read_csv(os.path.join(d, "test_uid.csv"))["StudyInstanceUID"].tolist()
        print("  meta", {k: meta.get(k) for k in ["fold","plane","completion_status","fold_train_time_sec","fold_inference_time_sec","prediction_shape","experiment_id"]})
        print("  pred shape", pred.shape, "uid_match", uids==canon, "finite", bool(np.isfinite(pred).all()),
              "range", float(pred.min()), float(pred.max()), "mean", float(pred.mean()))
        assert meta.get("completion_status") == "done"
        assert pred.shape[1] == 12
        assert np.isfinite(pred).all()

sub_path = "/kaggle/working/submission.csv"
if os.path.isfile(sub_path):
    sub = pd.read_csv(sub_path)
    print("[sub] shape", sub.shape, "NaN", int(sub.isna().sum().sum()),
          "uid_match", sub["StudyInstanceUID"].tolist()==canon if canon else "n/a")
    print("[sub] head\\n", sub.head(3).to_string())
else:
    print("[sub] missing")

print("[exp004] done. TIMING above is authoritative. Do not invent hours.")
'''

nb = {
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "kaggle": {
            "accelerator": "nvidiaTeslaT4",
            "isGpuEnabled": True,
            "isInternetEnabled": False,
            "language": "python",
            "sourceType": "notebook",
            "title": "RSNA EXP-004 Axial fold0 GPU",
            "slug": "rsna-exp004-axial-fold0-gpu",
        },
    },
    "nbformat_minor": 4,
    "nbformat": 4,
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": md},
        {
            "id": "exp004-torch",
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": cell_torch,
        },
        {
            "id": "exp004-preflight",
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": cell_preflight,
        },
        {
            "id": "exp004-v3",
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": cell_v3,
        },
        {
            "id": "exp004-lab",
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": cell_lab,
        },
        {
            "id": "exp004-run",
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": cell_run,
        },
    ],
}

nb_path = PUSH / "rsna_exp004_axial_fold0_run.ipynb"
nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

meta = {
    "id": "ziyiming/rsna-exp004-axial-fold0-gpu",
    "title": "RSNA EXP-004 Axial fold0 GPU",
    "code_file": "rsna_exp004_axial_fold0_run.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": False,
    "enable_gpu": True,
    "enable_internet": False,
    "competition_sources": ["rsna-knee-abnormality-detection"],
    "dataset_sources": [
        "matteonaccarato/resnet34-imagenet-pth",
        "ziyiming/torch-cu118-offline",
    ],
    "model_sources": [],
}
(PUSH / "kernel-metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

# local plan note
plan = f"""# EXP-004 Axial fold0 — 运行计划

- Kernel: `ziyiming/rsna-exp004-axial-fold0-gpu`
- Push dir: `rsna_knee/_push_exp004/`
- 唯一训练变量: `--planes axial`（相对 EXP-003 fold0 S+C / EXP-001 fold0 Sagittal）
- 超参: epochs=3 batch=8 n-clips=2 folds=5 only-fold=0 seed=42 fuse 默认
- 代码: EXP-003 同源 rsna_v3 `{v3_h}` + labels `{lab_h}`
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

1. `kaggle kernels output -k ziyiming/rsna-exp004-axial-fold0-gpu -p rsna_knee/_out/exp004_axial_pull`
2. 校验 meta status=done / shape / uid_match
3. 本地 fuse: mean(Axial, Sagittal, Coronal) fold0
4. 对照 LB: Axial-only vs 0.685 S+C fold0
"""
(PUSH / "PLAN.md").write_text(plan, encoding="utf-8")
print("wrote", nb_path)
print("wrote", PUSH / "kernel-metadata.json")
print("v3", v3_h)
print("lab", lab_h)
# validate notebook json + embedded hashes by re-decode
import re
text = nb_path.read_text(encoding="utf-8")
assert "exp004-axial-fold0" in text
assert "--planes\", \"axial\"" in text or '"--planes", "axial"' in text
print("notebook bytes", nb_path.stat().st_size)
