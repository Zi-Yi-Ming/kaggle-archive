# -*- coding: utf-8 -*-
import base64
import gzip
import json
import re
import zlib
from pathlib import Path

p = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p88_new\kaggriculture-master-engine-v4\kaggriculture-master-engine-v4.ipynb")
nb = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
out = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p88_new\extracted_clean\guru_master_v4.py")
out.parent.mkdir(parents=True, exist_ok=True)

for i, c in enumerate(nb["cells"]):
    if c.get("cell_type") != "code":
        continue
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if "FILES" not in s or "main.py" not in s or len(s) < 5000:
        continue
    print("cell", i, "len", len(s))
    print(s[:180].replace("\n", " | "))
    ns = {}
    try:
        exec("import base64,zlib,gzip,hashlib\n" + s, ns)
        files = ns.get("FILES") or {}
        print("FILES keys", list(files)[:12])
        payload = files.get("main.py")
        if payload is None:
            # maybe different key
            for k, v in files.items():
                if "main" in str(k).lower():
                    payload = v
                    print("use key", k)
                    break
        if isinstance(payload, str):
            payload = payload.encode("latin1", "replace")
        if not payload:
            print("no payload")
            continue
        print("payload len", len(payload), "head", payload[:20])
        for name, fn in [
            ("b85z", lambda x: zlib.decompress(base64.b85decode(x))),
            ("a85z", lambda x: zlib.decompress(base64.a85decode(x))),
            ("b64g", lambda x: gzip.decompress(base64.b64decode(x))),
            ("b64z", lambda x: zlib.decompress(base64.b64decode(x))),
            ("b85", lambda x: base64.b85decode(x)),
        ]:
            try:
                src = fn(payload)
                print(name, "ok", len(src), b"def agent" in src)
                if b"def agent" in src:
                    out.write_bytes(src)
                    print("WROTE", out, len(src))
                    break
            except Exception as e:
                print(name, "fail", type(e).__name__, e)
    except Exception as e:
        print("exec fail", type(e).__name__, e)

# also try beat-v48 PAYLOAD
p2 = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p88_new\beat-v48-100-0-your-herd-is-decided-on-day-6\beat-v48-100-0-your-herd-is-decided-on-day-6.ipynb")
if p2.exists():
    nb2 = json.loads(p2.read_text(encoding="utf-8", errors="ignore"))
    out2 = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p88_new\extracted_clean\beat_v48.py")
    for c in nb2["cells"]:
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if "PAYLOAD" not in s:
            continue
        print("beat cell len", len(s))
        m = re.search(r"PAYLOAD\s*=\s*[\"']([A-Za-z0-9+/=_-]{80,})[\"']", s)
        if not m:
            print("no PAYLOAD string")
            print(s[:300])
            continue
        packed = m.group(1)
        print("packed", len(packed))
        for name, fn in [
            ("b85z", lambda x: zlib.decompress(base64.b85decode(x))),
            ("a85z", lambda x: zlib.decompress(base64.a85decode(x))),
            ("b64g", lambda x: gzip.decompress(base64.b64decode(x))),
        ]:
            try:
                src = fn(packed)
                print(name, "ok", len(src), b"def agent" in src)
                if b"def agent" in src:
                    out2.write_bytes(src)
                    print("WROTE", out2, len(src))
                    break
            except Exception as e:
                print(name, "fail", e)
