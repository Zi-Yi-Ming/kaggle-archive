# -*- coding: utf-8 -*-
from pathlib import Path
import ast

dst = Path(r"D:\桌面\Kaggle\kaggriculture\_push_tetsu_r3")
dst.mkdir(parents=True, exist_ok=True)
src_path = Path(r"D:\桌面\Kaggle\kaggriculture\_external\top5_notebooks\tetsu2131\tetsu2131_main.py")
p = dst / "main.py"
text = src_path.read_text(encoding="utf-8")
stub = (
    "\nimport os as _os, shutil as _shutil\n"
    "if _os.path.isdir('/kaggle/working'):\n"
    "    try:\n"
    "        _s = _os.path.abspath(__file__)\n"
    "        _d = '/kaggle/working/main.py'\n"
    "        if _os.path.isfile(_s) and _os.path.realpath(_s) != _os.path.realpath(_d):\n"
    "            _shutil.copyfile(_s, _d)\n"
    "        elif not _os.path.isfile(_d):\n"
    "            open(_d, 'w', encoding='utf-8').write('# tetsu\\n')\n"
    "    except Exception:\n"
    "        pass\n"
)
if "/kaggle/working" not in text:
    idx = text.find("\nimport ")
    text = stub + text if idx < 0 else text[: idx + 1] + stub + text[idx + 1 :]
p.write_text(text, encoding="utf-8")
ast.parse(p.read_text(encoding="utf-8"))
print("ok", p.stat().st_size)

meta = {
    "competition_sources": ["kaggriculture"],
    "language": "python",
    "enable_internet": False,
    "is_private": True,
    "id": "ziyiming/kaggriculture-tetsu-r3",
    "title": "Kaggriculture tetsu R3",
    "code_file": "main.py",
    "enable_gpu": False,
    "kernel_type": "script",
}
import json
(dst / "kernel-metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
print("meta ok")
