import json

SRC = '_push_exp016_gpu/rsna_exp016_physical_axial_run.ipynb'
DST = '_push_exp018_density/rsna_exp018_physical_density_run.ipynb'

nb = json.load(open(SRC, encoding='utf-8'))

nb['cells'][0]['source'] = [
    "# EXP-018 GPU A/B - physical + density (12 -> 18 slices)\n",
    "\n",
    "Only variable: `n_clips` 4 -> 6 (used_slices 12 -> 18). `sampling_mode` stays **physical**.\n",
    "\n",
    "Control: EXP-016 physical Axial fold0 (n_clips=4).\n",
    "\n",
    "Frozen: EXP-013 multi-source labels + conf-weight loss + ResNet34/224 + Axial fold0 + 3ep + batch8 + seed42.\n",
    "\n",
    "**No auto-submit.** EXP-017 delta +0.0245 was not significant (perm p~0.73); physical remains NOT PROVEN.\n",
]

SMOKE = r'''# EXP-018 SMOKE GATE - must pass before training (experiment card section 8)
import os, sys, json
os.chdir('/kaggle/working')
sys.path.insert(0, '/kaggle/working')

def _blocked(reason):
    payload = {"STATUS": "BLOCKED", "experiment": "exp_018_physical_density", "reason": reason}
    os.makedirs('/kaggle/working/_out/exp018', exist_ok=True)
    json.dump(payload, open('/kaggle/working/_out/exp018/STATUS_BLOCKED.json', 'w'), indent=2)
    print('STATUS_BLOCKED', reason, flush=True)
    raise SystemExit(1)

import importlib
import rsna_v3 as R3
importlib.reload(R3)

if not getattr(R3, 'HAS_SG', False):
    _blocked('HAS_SG is False - physical would silently fall back to legacy sampling')
if not getattr(R3, 'HAS_PYDICOM', False):
    _blocked('HAS_PYDICOM is False')
print('[gate] HAS_SG=True HAS_PYDICOM=True HAS_TORCH=%s' % R3.HAS_TORCH, flush=True)

# runtime record (experiment card section 4)
import sys as _sys
import torch as _torch
try:
    import numpy as _np
    _npv = _np.__version__
except Exception:
    _npv = 'unavailable'
print('[gate] python = %s' % _sys.version.split()[0], flush=True)
print('[gate] torch = %s' % _torch.__version__, flush=True)
print('[gate] numpy = %s' % _npv, flush=True)
print('[gate] cuda_available = %s' % _torch.cuda.is_available(), flush=True)
if _torch.cuda.is_available():
    print('[gate] gpu = %s' % _torch.cuda.get_device_name(0), flush=True)
    print('[gate] vram_gb = %.2f' % (_torch.cuda.get_device_properties(0).total_memory / 1024**3), flush=True)

def _find_root(b='/kaggle/input', depth=0, maxd=4):
    if depth > maxd or not os.path.isdir(b):
        return None
    try:
        ents = sorted(os.listdir(b))
    except OSError:
        return None
    if 'train.csv' in ents and os.path.isdir(os.path.join(b, 'train_series')):
        return b
    for e in ents:
        r = _find_root(os.path.join(b, e), depth + 1, maxd)
        if r:
            return r
    return None

root = _find_root()
if root is None:
    _blocked('competition root with train.csv + train_series/ not found')
print('[gate] data root =', root, flush=True)

import pandas as pd
import numpy as np
import torch

series_df = pd.read_csv(os.path.join(root, 'train_series.csv'))
ax = series_df[series_df['Anatomical_Plane'].astype(str).str.lower() == 'axial']
uids = list(dict.fromkeys(ax['StudyInstanceUID'].tolist()))[:2]
if len(uids) < 2:
    _blocked('fewer than 2 Axial studies available for smoke test')

N_CLIPS = 6
ds = R3.KneeDataset(uids, None, os.path.join(root, 'train_series'), series_df, 'Axial',
                    has_targets=False, n_clips=N_CLIPS, sampling_mode='physical')

report = []
for i, uid in enumerate(uids):
    clips = ds._load_study(uid)
    x, _y, _v = ds[i]
    # torch-only stats: never call .numpy() here. torch 2.2.0+cu118 is built
    # against numpy 1.x and this image ships numpy 2.0.2, so the torch->numpy
    # bridge raises "Numpy is not available". rsna_v3.predict() avoids it with
    # .cpu().tolist(); this gate stays in torch instead.
    x_shape = list(x.shape)
    nonzero_frac = float((x != 0).float().mean())
    pixel_max = float(x.max())
    report.append({'uid_tail': uid[-12:], 'n_clips': len(clips), 'x_shape': x_shape,
                   'nonzero_frac': nonzero_frac, 'pixel_max': pixel_max})
    print('[gate] %s clips=%d x=%s nonzero=%.3f max=%.3f' % (
        uid[-12:], len(clips), x_shape, nonzero_frac, pixel_max), flush=True)

for r in report:
    if r['x_shape'][0] != N_CLIPS * 3:
        _blocked('channel dim %d != n_clips*3=%d (density not in effect)' % (r['x_shape'][0], N_CLIPS * 3))
    if r['n_clips'] < 1:
        _blocked('no clips read for %s' % r['uid_tail'])
    if r['nonzero_frac'] == 0.0:
        _blocked('all-zero tensor for %s (decode failure)' % r['uid_tail'])

net = R3.KneeModel(channels=N_CLIPS * 3, num_labels=len(R3.LABELS), pretrained=False, offline_paths=None)
net.eval()
with torch.no_grad():
    out = net(torch.randn(2, N_CLIPS * 3, 224, 224))
if tuple(out.shape) != (2, 12):
    _blocked('model output shape %s != (2,12)' % (tuple(out.shape),))
print('[gate] model forward OK, output', tuple(out.shape), flush=True)

try:
    import sampling_geometry as SG
    st = getattr(SG, 'STATS', None)
    print('[gate] SG.STATS =', json.dumps(st, default=str)[:600], flush=True)
except Exception as e:
    print('[gate] SG.STATS unavailable:', e, flush=True)

os.makedirs('/kaggle/working/_out/exp018', exist_ok=True)
json.dump({'smoke': report, 'data_root': root, 'n_clips': N_CLIPS,
           'sampling_mode': 'physical', 'HAS_SG': bool(R3.HAS_SG)},
          open('/kaggle/working/_out/exp018/smoke.json', 'w'), indent=2)
print('[gate] SMOKE GATE PASS', flush=True)
'''

nb['cells'].insert(5, {"cell_type": "code", "execution_count": None, "metadata": {},
                       "outputs": [], "source": SMOKE.splitlines(keepends=True)})

tr = ''.join(nb['cells'][6]['source'])
pairs = [
    ("'experiment_id': 'exp_016_physical_axial'", "'experiment_id': 'exp_018_physical_density'"),
    ("'n_clips': 4,", "'n_clips': 6,"),
    ("'control': 'EXP-013 exp_013_multisource_axial_fold0 public 0.716 (legacy)'",
     "'control': 'EXP-016 exp_016_physical_axial fold0 (physical, n_clips=4); only density changes'"),
    ("'--n-clips', '4',", "'--n-clips', '6',"),
    ("'--experiment-id', 'exp_016_physical_axial'", "'--experiment-id', 'exp_018_physical_density'"),
    ("exp016_config.json", "exp018_config.json"),
    ("artifacts/exp_016_physical_axial", "artifacts/exp_018_physical_density"),
    ("=== EXP-016 physical Axial fold0 ===", "=== EXP-018 physical Axial fold0 n_clips=6 (density A/B) ==="),
    ("[exp016] train done", "[exp018] train done"),
]
for a, b in pairs:
    if a not in tr:
        raise SystemExit('MISSING PATTERN: ' + a)
    tr = tr.replace(a, b)
nb['cells'][6]['source'] = tr.splitlines(keepends=True)

json.dump(nb, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('notebook written, cells =', len(nb['cells']))
print('cell types =', [c['cell_type'] for c in nb['cells']])
