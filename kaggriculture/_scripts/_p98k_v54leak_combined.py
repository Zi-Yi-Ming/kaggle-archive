from pathlib import Path
import json
import re
import base64
import gzip
import zlib
import lzma
import hashlib

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")
OUT = ROOT / "extracted"

# v54leak cell6: main = v54 + LAYER_SEED_FLOAT + LAYER_FERT_DAY29
nb = ROOT / "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb"
data = json.loads(nb.read_text(encoding="utf-8"))
cells = []
for c in data.get("cells", []):
    src = c.get("source", "")
    if isinstance(src, list):
        src = "".join(src)
    cells.append(src)

# cell 5 gives v54 bytes via write; we already have v54leak_main.py as V54
# cell 6 defines LAYER_* and main = v54 + ...
layer_cell = cells[6]
print("layer cell head:", layer_cell[:300].replace("\n", " | "))

# extract LAYER_SEED_FLOAT and LAYER_FERT_DAY29 string literals
ns = {}
# isolate just the layer string assignments
# Find triple-quoted or long quoted strings assigned to LAYER_*
layers = {}
for name in ("LAYER_SEED_FLOAT", "LAYER_FERT_DAY29"):
    m = re.search(rf"{name}\s*=\s*[r]?[\"']{{3}}([\s\S]+?)[\"']{{3}}", layer_cell)
    if m:
        layers[name] = m.group(1)
        print(name, "len", len(m.group(1)))
    else:
        m = re.search(rf"{name}\s*=\s*[\"']([^\"']+)[\"']", layer_cell)
        if m:
            layers[name] = m.group(1)
            print(name, "len single", len(m.group(1)))

v54 = (OUT / "v54leak_main.py").read_bytes()
# actual combined from notebook: main = v54 + b"\n\n" + LAYER_SEED_FLOAT.encode() + b"\n\n" + LAYER_FERT_DAY29.encode()
if "LAYER_SEED_FLOAT" in layers and "LAYER_FERT_DAY29" in layers:
    main = (
        v54
        + b"\n\n"
        + layers["LAYER_SEED_FLOAT"].encode()
        + b"\n\n"
        + layers["LAYER_FERT_DAY29"].encode()
    )
    print("combined", len(main), hashlib.sha256(main).hexdigest()[:16])
    # claimed sha 562f34ad0ba7824b35a4ca12d63c4f869add4dd7f71dc30869fd77c431aee16d
    print("expected 562f34ad0ba7824b...")
    p = OUT / "v54leak_combined_main.py"
    p.write_bytes(main)
    print("WROTE", p)
else:
    print("layers missing", layers.keys())
    print(layer_cell[-800:])
