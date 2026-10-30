import json, pathlib, re, os

BASE = pathlib.Path(r'D:\桌面\Kaggle\kaggriculture')
OUT = BASE / '_external' / 'top5_notebooks'
OUT.mkdir(parents=True, exist_ok=True)

def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def read_nb_cells(name):
    mapping = {
        'tetsu2131': 'adaptive-farming-strategy-for-kaggriculture.ipynb',
        'prvsiyan': 'kaggriculture-frontier-the-soil-remembers-rain.ipynb',
        'flexonafft': 'kaggriculture-smart-farm-strategy-lab.ipynb',
        'salemali7': 'kaggriculture-2900.ipynb',
        'boatlee': 'v29-r1-adaptive-market-hysteresis.ipynb',
    }
    nb_name = mapping[name]
    nb_path = BASE / '_kaggle_notebooks' / name / nb_name
    if not nb_path.exists():
        raise FileNotFoundError(nb_path)
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    return nb['cells']

def extract_assignment_string(src, var):
    """Extract the string value of var= from src, respecting escape sequences."""
    m = re.search(rf'{var}\s*=\s*("""|\'\'\'|\'|")', src)
    if not m:
        raise SystemExit(f'{var} not found')
    q = m.group(1)
    start = m.end()
    i = start
    while i < len(src):
        if src[i] == '\\':
            i += 2
            continue
        if src[i] == q[0]:
            return src[start:i]
        i += 1
    raise SystemExit(f'{var} closing quote not found')

def decode_escapes(text):
    """Decode Python-style escape sequences embedded in notebook-extracted strings."""
    return text.encode('utf-8').decode('unicode_escape')

# tetsu2131
print('=== tetsu2131 ===')
tetsu_cells = read_nb_cells('tetsu2131')
tetsu_src = ''.join(''.join(c['source']) for c in tetsu_cells if c['cell_type']=='code')
m = re.search(r'TOP_AGENT_FILES\s*=\s*\{', tetsu_src)
if not m:
    raise SystemExit('TOP_AGENT_FILES not found')
start = m.start()
i = start
while i < len(tetsu_src) and tetsu_src[i] != '{':
    i += 1
depth = 0
in_str = False
str_char = ''
j = i
while j < len(tetsu_src):
    ch = tetsu_src[j]
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
dict_str = tetsu_src[i:j+1]
ns = {}
exec('TOP_AGENT_FILES = ' + dict_str, {'__builtins__': {}}, ns)
agent_src = ns['TOP_AGENT_FILES']['main.py']
write_text(OUT / 'tetsu2131_main.py', agent_src)
print('tetsu2131_main.py:', len(agent_src), 'def agent at', agent_src.find('def agent('))

# prvsiyan
print('=== prvsiyan ===')
prv_cells = read_nb_cells('prvsiyan')
prv_src = ''.join(''.join(c['source']) for c in prv_cells if c['cell_type']=='code')
agent_src = decode_escapes(extract_assignment_string(prv_src, 'AGENT_SOURCE'))
write_text(OUT / 'prvsiyan_main.py', agent_src)
print('prvsiyan_main.py:', len(agent_src), 'def agent at', agent_src.find('def agent('))

# flexonafft
print('=== flexonafft ===')
flex_cells = read_nb_cells('flexonafft')
flex_src = ''.join(''.join(c['source']) for c in flex_cells if c['cell_type']=='code')
agent_src = decode_escapes(extract_assignment_string(flex_src, 'AGENT_SOURCE'))
write_text(OUT / 'flexonafft_main.py', agent_src)
print('flexonafft_main.py:', len(agent_src), 'def agent at', agent_src.find('def agent('))

# Salem Ali
print('=== Salem Ali ===')
sal_cells = read_nb_cells('salemali7')
for idx, c in enumerate(sal_cells):
    if c['cell_type'] != 'code':
        continue
    src = ''.join(c['source']) if isinstance(c['source'], list) else c['source']
    if src.lstrip().startswith('%%writefile main.py'):
        agent_src = '\n'.join(src.splitlines()[1:])
        write_text(OUT / 'salemali7_main.py', agent_src)
        print('salemali7_main.py from cell', idx, 'len', len(agent_src), 'def agent at', agent_src.find('def agent('))
        break
else:
    raise SystemExit('Salem Ali %%writefile main.py cell not found')

# boatlee
print('=== boatlee ===')
boat_cells = read_nb_cells('boatlee')
boat_src = ''.join(''.join(c['source']) for c in boat_cells if c['cell_type']=='code')
has_agent = 'def agent(' in boat_src
print('boatlee has def agent:', has_agent)
if not has_agent:
    print('boatlee BLOCKED: no agent entry point found')

print('Done')
