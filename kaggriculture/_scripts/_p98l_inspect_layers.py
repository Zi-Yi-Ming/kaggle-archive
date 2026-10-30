from pathlib import Path
import json
import re
import hashlib

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")
OUT = ROOT / "extracted"

nb = ROOT / "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb"
data = json.loads(nb.read_text(encoding="utf-8"))
cells = []
for c in data.get("cells", []):
    src = c.get("source", "")
    if isinstance(src, list):
        src = "".join(src)
    cells.append(src)

layer_cell = cells[6]
print("=== layer cell length", len(layer_cell))
print("--- first 800 ---")
print(layer_cell[:800])
print("--- around LAYER_FERT ---")
i = layer_cell.find("LAYER_FERT")
print(layer_cell[max(0, i - 100): i + 400])
print("--- last 600 ---")
print(layer_cell[-600:])
print("--- repr of quotes near LAYER_SEED ---")
i = layer_cell.find("LAYER_SEED_FLOAT")
print(repr(layer_cell[i:i+80]))
