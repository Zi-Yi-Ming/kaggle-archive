from __future__ import annotations

import json
from pathlib import Path

nb_path = Path(r"D:/桌面/Kaggle/rsna_knee/_push_exp004/rsna_exp004_axial_fold0_run.ipynb")
nb = json.loads(nb_path.read_text(encoding="utf-8"))

new_preflight = r'''# preflight: competition mount + Axial coverage
# Correct layout: test_series/<StudyInstanceUID>/<SeriesInstanceUID>/*.dcm
import os, csv
from collections import defaultdict

base = '/kaggle/input'

def _find(b, depth=0, max_depth=3):
    if not os.path.isdir(b):
        return None
    try:
        entries = sorted(os.listdir(b))
    except OSError:
        return None
    for e in entries:
        p = os.path.join(b, e)
        if not os.path.isdir(p):
            continue
        if e in ('train_series', 'test_series'):
            continue
        if os.path.isfile(os.path.join(p, 'test.csv')) and os.path.isdir(os.path.join(p, 'test_series')):
            return p
        if depth < max_depth - 1:
            r = _find(p, depth + 1)
            if r:
                return r
    return None

root = _find(base)
if root is None:
    raise SystemExit('FAIL: 未找到含 test_series+test.csv 的比赛挂载')
print('root =', root)

def count_dcm(dirpath):
    if not os.path.isdir(dirpath):
        return -1
    return sum(1 for f in os.listdir(dirpath) if f.lower().endswith('.dcm'))

def plane_stats(series_csv, series_dir, label):
    if not os.path.isfile(series_csv):
        print(label, 'series csv missing', series_csv)
        return
    with open(series_csv, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f'FAIL: {label} series csv empty')
    plane_key = None
    for k in rows[0].keys():
        if 'plane' in k.lower() or 'anatom' in k.lower():
            plane_key = k
            break
    uid_key = 'StudyInstanceUID'
    ser_key = 'SeriesInstanceUID'
    series_counts = defaultdict(int)
    study_sets = defaultdict(set)
    axial_series_rows = []
    for r in rows:
        pl = r.get(plane_key, '?') if plane_key else '?'
        series_counts[pl] += 1
        if uid_key in r:
            study_sets[pl].add(r[uid_key])
        if pl == 'Axial' and ser_key in r:
            axial_series_rows.append(r)
    print(label, 'plane series counts', dict(series_counts))
    print(label, 'plane study counts', {k: len(v) for k, v in study_sets.items()})
    print(label, 'Axial studies', len(study_sets.get('Axial', set())))
    assert len(study_sets.get('Axial', set())) > 0, f'FAIL: {label} 无 Axial study'

    # Walk both possible layouts
    n_dcm = 0
    hits = 0
    misses = []
    for r in axial_series_rows:
        suid = r[uid_key]
        seid = r[ser_key]
        candidates = [
            os.path.join(series_dir, suid, seid),
            os.path.join(series_dir, seid),
            os.path.join(series_dir, suid, 'series', seid),
        ]
        found = None
        for c in candidates:
            k = count_dcm(c)
            if k and k > 0:
                found = c
                n_dcm += k
                hits += 1
                print(f'  axial OK study={suid[:14]} series={seid[:16]} dcm={k} path={c}')
                break
        if found is None:
            # fallback: list study dir
            sdir = os.path.join(series_dir, suid)
            if os.path.isdir(sdir):
                children = sorted(os.listdir(sdir))[:8]
                print(f'  axial miss study={suid[:14]} series={seid[:16]} study_children={children}')
            else:
                print(f'  axial miss study={suid[:14]} series={seid[:16]} NO_STUDY_DIR {sdir}')
            misses.append(seid)
    print(label, f'axial series hits={hits}/{len(axial_series_rows)} dcm_total={n_dcm}')
    assert hits > 0 and n_dcm > 0, f'FAIL: {label} Axial DICOM 为空 (hits={hits}, dcm={n_dcm})'

    # also sample sagittal for sanity
    sag = [r for r in rows if (r.get(plane_key) if plane_key else '') == 'Sagittal']
    if sag:
        r0 = sag[0]
        for c in [os.path.join(series_dir, r0[uid_key], r0[ser_key]), os.path.join(series_dir, r0[ser_key])]:
            k = count_dcm(c)
            if k and k > 0:
                print(label, 'sagittal sanity', r0[ser_key][:16], 'dcm', k)
                break

plane_stats(os.path.join(root, 'test_series.csv'), os.path.join(root, 'test_series'), 'test')
plane_stats(os.path.join(root, 'train_series.csv'), os.path.join(root, 'train_series'), 'train')
print('preflight axial: OK')
'''

for cell in nb['cells']:
    if cell.get('id') == 'exp004-preflight' or (
        isinstance(cell.get('source'), (str, list))
        and 'Axial coverage' in (''.join(cell['source']) if isinstance(cell['source'], list) else cell['source'])
    ):
        cell['source'] = new_preflight
        cell['outputs'] = []
        cell['execution_count'] = None
        print('replaced preflight cell id=', cell.get('id'))
        break
else:
    raise SystemExit('preflight cell not found')

nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding='utf-8')
print('wrote', nb_path)

# verify
text = nb_path.read_text(encoding='utf-8')
assert 'StudyInstanceUID' in text and 'SeriesInstanceUID' in text
assert 'test_series' in text
print('ok')
