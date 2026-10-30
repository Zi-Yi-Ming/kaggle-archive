import json, pathlib, re

nb_path = pathlib.Path(r'D:\桌面\Kaggle\kaggriculture\_kaggle_notebooks\tetsu2131\adaptive-farming-strategy-for-kaggriculture.ipynb')
nb = json.loads(nb_path.read_text(encoding='utf-8'))
src = ''.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code')

m = re.search(r'TOP_AGENT_FILES\s*=\s*\{', src)
if not m:
    raise SystemExit('TOP_AGENT_FILES not found')
start = m.start()
i = start
while i < len(src) and src[i] != '{':
    i += 1
depth = 0
in_str = False
str_char = ''
j = i
while j < len(src):
    ch = src[j]
    if in_str:
        if ch == '\\':
            j += 2
            continue
        if ch == str_char:
            in_str = False
    else:
        if ch in ("'", '"'):
            in_str = True
            str_char = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                break
    j += 1
dict_str = src[i:j+1]
print('dict_len', len(dict_str))
print('dict_head', repr(dict_str[:120]))
print('dict_tail', repr(dict_str[-120:]))

ns = {}
exec('TOP_AGENT_FILES = ' + dict_str, {'__builtins__': {}}, ns)
d = ns['TOP_AGENT_FILES']
print('keys', list(d.keys()))
agent_src = d['main.py']
print('agent_len', len(agent_src))
print('agent_head', repr(agent_src[:200]))
print('agent_tail', repr(agent_src[-200:]))
idx = agent_src.find('def agent(')
print('def agent at', idx)
if idx != -1:
    print(agent_src[idx:idx+400])
else:
    print('no def agent found')
