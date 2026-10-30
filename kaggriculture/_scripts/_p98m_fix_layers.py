from pathlib import Path
import ast
import hashlib

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")
OUT = ROOT / "extracted"

import json
nb = ROOT / "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb"
data = json.loads(nb.read_text(encoding="utf-8"))
cells = []
for c in data.get("cells", []):
    src = c.get("source", "")
    if isinstance(src, list):
        src = "".join(src)
    cells.append(src)

layer_cell = cells[6]
tree = ast.parse(layer_cell)
layers = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name.startswith("LAYER_"):
            layers[name] = ast.literal_eval(node.value)
            print(name, "len", len(layers[name]))

v54 = (OUT / "v54leak_main.py").read_bytes()
main = (
    v54
    + b"\n\n"
    + layers["LAYER_SEED_FLOAT"].encode()
    + b"\n\n"
    + layers["LAYER_FERT_DAY29"].encode()
)
h = hashlib.sha256(main).hexdigest()
print("combined", len(main), h)
print("match expected", h == "562f34ad0ba7824b35a4ca12d63c4f869add4dd7f71dc30869fd77c431aee16d")
p = OUT / "v54leak_combined_main.py"
p.write_bytes(main)
print("WROTE", p)
