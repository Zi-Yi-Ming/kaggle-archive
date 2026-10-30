import json, pathlib, hashlib

nb = json.loads(pathlib.Path(r'D:\桌面\Kaggle\kaggriculture\_kaggle_notebooks\prvsiyan\kaggriculture-frontier-the-soil-remembers-rain.ipynb').read_text(encoding='utf-8'))
c = nb['cells'][3]['source']
ns = {}
try:
    exec(c, {'__builtins__': {'print': print, 'hashlib': hashlib}, 'hashlib': hashlib}, ns)
    print('exec ok')
    print('keys:', [k for k in ns.keys() if not k.startswith('_')])
    print('AGENT_SOURCE len:', len(ns.get('AGENT_SOURCE', '')))
    print('AGENT_SOURCE head:', repr(ns.get('AGENT_SOURCE', '')[:200]))
    print('def agent at:', ns.get('AGENT_SOURCE', '').find('def agent('))
except Exception as e:
    print('ERROR:', type(e).__name__, e)
