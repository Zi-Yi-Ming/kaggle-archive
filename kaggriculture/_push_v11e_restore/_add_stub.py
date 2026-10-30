# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"D:\桌面\Kaggle\kaggriculture\_push_v11e_restore\main.py")
src = p.read_text(encoding="utf-8")
stub = '''
import os as _os, shutil as _shutil
if _os.path.isdir("/kaggle/working"):
    try:
        _s = _os.path.abspath(__file__)
        _d = "/kaggle/working/main.py"
        if _os.path.isfile(_s) and _os.path.realpath(_s) != _os.path.realpath(_d):
            _shutil.copyfile(_s, _d)
        elif not _os.path.isfile(_d):
            open(_d, "w", encoding="utf-8").write("# v11e\\n")
    except Exception:
        pass
'''
if "/kaggle/working" not in src:
    idx = src.find("\nimport ")
    if idx == -1:
        src = stub + src
    else:
        src = src[: idx + 1] + stub + src[idx + 1 :]
    p.write_text(src, encoding="utf-8")
    print("stub inserted")
else:
    print("stub already present")
print("bytes", p.stat().st_size)
