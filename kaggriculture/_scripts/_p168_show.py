from pathlib import Path
import json
import re

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_last")


def show(tag, n=8):
    d = OUT / tag
    nbs = list(d.glob("*.ipynb"))
    if not nbs:
        print(tag, "files", [f.name for f in d.iterdir()] if d.exists() else "missing")
        return
    data = json.loads(nbs[0].read_text(encoding="utf-8"))
    print("====", tag, "cells", len(data["cells"]))
    for i, c in enumerate(data["cells"][:n]):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        print(f"  [{i}] {c.get('cell_type')} len={len(s)} {s[:90]!r}")


show("guru_v3", 10)
show("farms2600", 8)
show("top10_replays", 6)
