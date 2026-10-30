from pathlib import Path
import json

for tag in ["pilk_econ", "hamburger", "rayk_meta"]:
    nbs = list(Path(rf"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\{tag}").glob("*.ipynb"))
    if not nbs:
        print(tag, "no nb")
        continue
    data = json.loads(nbs[0].read_text(encoding="utf-8"))
    print("====", tag, "cells", len(data["cells"]))
    for i, c in enumerate(data["cells"][:8]):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        print(f"  [{i}] {c.get('cell_type')} len={len(s)} {s[:80]!r}")
