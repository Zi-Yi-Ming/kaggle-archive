# -*- coding: utf-8 -*-
"""P151: extract 2965 V59.2 from join-concat b85."""
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

SCAN = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_final")
OUT = SCAN / "extracted"
OUT.mkdir(parents=True, exist_ok=True)

nb = next((SCAN / "hy2965").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > len(src):
        src = s

print("biggest cell", len(src), flush=True)
print("head:", src[:300], flush=True)
idx = src.find("decompress")
print("decompress ctx:", src[max(0, idx - 150): idx + 150], flush=True)

m = re.search(r"(\w+)\s*=\s*['\"]['\"]\.join\(\(", src)
print("join match", bool(m), m.group(1) if m else None, flush=True)
if m:
    rest = src[m.end():]
    end = rest.find("))")
    reg = rest[: end if end > 0 else 900000]
    packed = "".join(re.findall(r"['\"]([^'\"]*)['\"]", reg))
    print("packed", len(packed), flush=True)
    for label, fn in (
        ("b85gz", lambda s: gzip.decompress(base64.b85decode(s))),
        ("b85", lambda s: base64.b85decode(s)),
        ("b64gz", lambda s: gzip.decompress(base64.b64decode(s + "=" * (-len(s) % 4)))),
    ):
        try:
            out = fn(packed)
            print(label, "OK", len(out), flush=True)
            if len(out) > 5000:
                (OUT / "hy2965_main.py").write_bytes(out)
                print("WROTE hy2965_main.py", flush=True)
                break
        except Exception as e:
            print(label, type(e).__name__, e, flush=True)
