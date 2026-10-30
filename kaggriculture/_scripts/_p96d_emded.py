# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import json
import re
import zlib
from pathlib import Path

nb = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p79_kernels\dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700\kaggriculture-herd-safe-sale-window-lb-2700.ipynb")
data = json.loads(nb.read_text(encoding="utf-8", errors="ignore"))
for c in data.get("cells", []):
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if "EMBEDDED_ASSETS" not in s:
        continue
    print("len", len(s))
    print(s[:1500])
    print("--- mid ---")
    # find EMBEDDED_ASSETS structure
    idx = s.find("EMBEDDED_ASSETS")
    print(s[idx:idx+800])
    print("--- around actions ---")
    j = s.find("actions.json")
    print(s[j-100:j+400])
    # try eval EMBEDDED_ASSETS
    m = re.search(r"EMBEDDED_ASSETS\s*=\s*(\{[\s\S]+?\n\})", s)
    if not m:
        m = re.search(r"EMBEDDED_ASSETS\s*=\s*(\{[\s\S]{0,200000})", s)
    if m:
        body = m.group(1)
        # cut at next top-level after dict
        print("body start", body[:300])
        try:
            ns = {}
            exec("EMBEDDED_ASSETS=" + body[: body.find("\n# ") if "\n# " in body[:50] else 150000], ns) if False else None
        except Exception as e:
            print(e)
        # manual: name -> (len, sha, b85 or b64)
        for name in ("actions.json", "NOTICE.txt", "LICENSE.txt", "main.py"):
            mm = re.search(rf"['\"]{re.escape(name)}['\"]\s*:\s*\(([\s\S]+?)\)\s*[,}}]", s)
            if not mm:
                print("no", name)
                continue
            chunk = mm.group(1)[:200000]
            print(name, "chunk head", chunk[:120])
            parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{20,})['\"]", chunk)
            print(" parts", len(parts), sum(map(len, parts)))
            packed = "".join(parts)
            for dec in (
                lambda p: gzip.decompress(base64.b64decode(p)),
                lambda p: zlib.decompress(base64.b64decode(p)),
                lambda p: zlib.decompress(base64.b85decode(p)),
                lambda p: base64.b64decode(p),
                lambda p: gzip.decompress(base64.b85decode(p)),
            ):
                try:
                    raw = dec(packed)
                    print("  decoded", name, len(raw), raw[:40])
                    out = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p96_local\extracted\dmitrii_lb2700_pkg") / name
                    out.write_bytes(raw)
                    break
                except Exception as e:
                    print("  fail", e)
