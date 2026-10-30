import json, pathlib, hashlib

nb = json.loads(pathlib.Path(r'D:\桌面\Kaggle\kaggriculture\_kaggle_notebooks\flexonafft\kaggriculture-smart-farm-strategy-lab.ipynb').read_text(encoding='utf-8'))
src = ''.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
ns = {}
try:
    exec(src, {'__builtins__': {'print': print, 'hashlib': hashlib}, 'hashlib': hashlib}, ns)
    print('exec ok')
    print('keys:', [k for k in ns.keys() if not k.startswith('_')])
    agent_src = ns['AGENT_SOURCE']
    print('AGENT_SOURCE len:', len(agent_src))
    print('def agent at:', agent_src.find('def agent('))
    path = pathlib.Path(r'D:\桌面\Kaggle\kaggriculture\_external\top5_notebooks\flexonafft\flexonafft_main_fixed.py')
    path.write_text(agent_src, encoding='utf-8')
    print('written to', path)
except Exception as e:
    print('ERROR:', type(e).__name__, e)
