import json
import difflib

a = json.load(open('_push_exp016_gpu/rsna_exp016_physical_axial_run.ipynb', encoding='utf-8'))
b = json.load(open('_push_exp018_density/rsna_exp018_physical_density_run.ipynb', encoding='utf-8'))

print('EXP-016 cells:', len(a['cells']), ' EXP-018 cells:', len(b['cells']))
print()

# cells 1..4 must be byte-identical
for i in range(1, 5):
    sa = ''.join(a['cells'][i]['source'])
    sb = ''.join(b['cells'][i]['source'])
    print('cell %d identical: %s  (len %d vs %d)' % (i, sa == sb, len(sa), len(sb)))

print()
print('cell 5 (EXP-018 only): smoke gate, len =', len(''.join(b['cells'][5]['source'])))
print('cell 6 (was EXP-016 cell 5) diff:')
print('=' * 70)
sa = ''.join(a['cells'][5]['source']).splitlines()
sb = ''.join(b['cells'][6]['source']).splitlines()
n = 0
for line in difflib.unified_diff(sa, sb, 'exp016_cell5', 'exp018_cell6', lineterm='', n=1):
    print(line)
    n += 1
print('=' * 70)
print('total diff lines:', n)
