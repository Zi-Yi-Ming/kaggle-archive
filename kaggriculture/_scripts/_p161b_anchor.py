from pathlib import Path
import base64
import gzip
import re

src = ""
import json
nb = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\hamburger").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if "ANCHOR_BLOB" in s:
        src = s
        break

m = re.search(r"ANCHOR_BLOB\s*=\s*[\"']([A-Za-z0-9+/=]+)[\"']", src)
if not m:
    m = re.search(r"ANCHOR_BLOB\s*=\s*[\"']{3}([A-Za-z0-9+/=]+)[\"']{3}", src)
print("m", bool(m), len(m.group(1)) if m else 0, flush=True)
packed = re.sub(r"\s+", "", m.group(1))
out = gzip.decompress(base64.b64decode(packed))
p = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\extracted\burger_anchor.py")
p.write_bytes(out)
print("WROTE", len(out), out[:60], flush=True)
print("def agent", out.count(b"def agent"), flush=True)
