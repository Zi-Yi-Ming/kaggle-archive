# -*- coding: utf-8 -*-
"""P164: package Shepherd's Ledger (DUAL PASS +1797) and confirm load."""
from __future__ import annotations

import tarfile
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
SRC = PROJ / "_external/scan_today/extracted/shepherd.py"
PUSH = PROJ / "_push_shepherd"
PUSH.mkdir(parents=True, exist_ok=True)

code = SRC.read_bytes()
main_py = PUSH / "main.py"
main_py.write_bytes(code)
print("main.py", len(code), flush=True)
compile(code.decode("utf-8", errors="replace"), "main.py", "exec")
print("compile OK", flush=True)
# smoke import agent
ns = {"__name__": "pkg", "__file__": str(main_py), "__builtins__": __builtins__}
exec(compile(code.decode("utf-8", errors="replace"), "main.py", "exec"), ns)
print("agent", ns.get("agent"), flush=True)

tar = PUSH / "submission.tar.gz"
with tarfile.open(tar, "w:gz") as tf:
    tf.add(main_py, arcname="main.py")
print("PACKAGED", tar, tar.stat().st_size, flush=True)
