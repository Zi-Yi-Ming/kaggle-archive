# -*- coding: utf-8 -*-
"""P155: package hy2965 as submission (BT option in last-2). No code change."""
from __future__ import annotations

import tarfile
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
SRC = PROJ / "_external/scan_final/extracted/hy2965_main.py"
PUSH = PROJ / "_push_2965_v592"
PUSH.mkdir(parents=True, exist_ok=True)

code = SRC.read_bytes()
main_py = PUSH / "main.py"
main_py.write_bytes(code)
print("main.py", len(code), flush=True)

# smoke compile
compile(code.decode("utf-8", errors="replace"), "main.py", "exec")
print("compile OK", flush=True)

tar = PUSH / "submission.tar.gz"
with tarfile.open(tar, "w:gz") as tf:
    tf.add(main_py, arcname="main.py")
print("PACKAGED", tar, tar.stat().st_size, flush=True)
