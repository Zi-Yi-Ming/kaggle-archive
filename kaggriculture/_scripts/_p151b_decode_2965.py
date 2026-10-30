import base64
import gzip
import json
import re
from pathlib import Path

nb = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_final\hy2965").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > len(src):
        src = s

m = re.search(r'AGENT_B64\s*=\s*["\']{3}([A-Za-z0-9+/=\s]+)["\']{3}', src)
print("match", bool(m), "len", len(m.group(1)) if m else 0)
packed = re.sub(r"\s+", "", m.group(1))
out = gzip.decompress(base64.b64decode(packed))
p = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_final\extracted\hy2965_main.py")
p.write_bytes(out)
print("WROTE", len(out), out[:50])
