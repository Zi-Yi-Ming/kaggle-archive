# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p95_again\kaggriculture-2887-score-fieldcraft-agent\kaggriculture-2887-score-fieldcraft-agent.ipynb")
nb = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
print("cells", len(nb.get("cells", [])))
for i, c in enumerate(nb.get("cells", [])):
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    print(i, c.get("cell_type"), len(s), repr(s[:200]))
