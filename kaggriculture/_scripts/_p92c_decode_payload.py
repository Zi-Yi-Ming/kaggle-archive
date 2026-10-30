# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import json
import re
import zlib
from pathlib import Path

p = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p92b_versions\andrey_latest\kaggriculture-breaking-the-tie.ipynb")
nb = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
s = nb["cells"][0]["source"]
if isinstance(s, list):
    s = "".join(s)
m = re.search(r'PAYLOAD\s*=\s*"([^"]+)"', s)
print("payload len", len(m.group(1)) if m else None)
packed = m.group(1)
out = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p92b_versions\extracted\andrey_breaking_tie.py")
out.parent.mkdir(parents=True, exist_ok=True)
for name, fn in [
    ("gzip_b64", lambda x: gzip.decompress(base64.b64decode(x))),
    ("zlib_b64", lambda x: zlib.decompress(base64.b64decode(x))),
    ("raw_b64", lambda x: base64.b64decode(x)),
]:
    try:
        src = fn(packed)
        print(name, "ok", len(src), "def agent", b"def agent" in src)
        print("sha", hashlib.sha256(src).hexdigest())
        if b"def agent" in src:
            out.write_bytes(src)
            print("WROTE", out, len(src))
            break
    except Exception as e:
        print(name, "fail", type(e).__name__, e)

print("---cell0 tail---")
print(s[-600:])
# how does notebook write main.py?
idx = s.find("main.py")
print("---around main.py---")
print(s[idx - 200 : idx + 400] if idx > 0 else "none")
