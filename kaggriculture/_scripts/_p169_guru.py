from pathlib import Path
import ast
import base64
import gzip
import json
import re
import zlib
import lzma

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_last\extracted")
OUT.mkdir(exist_ok=True)

nbs = list(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_last\guru_v3").glob("*.ipynb"))
data = json.loads(nbs[0].read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > len(src):
        src = s
print("guru big", len(src), flush=True)
print(src[:400], flush=True)

# find decode line
for key in ["decompress", "b85decode", "b64decode", "MAIN", "SOURCE", "join((", "PAYLOAD", "BLOB"]:
    i = src.find(key)
    print(key, i, flush=True)
    if i > 0 and i < 2000:
        print(" ctx", src[max(0, i - 60): i + 100].replace("\n", " | "), flush=True)

# extract via exec of assignment + decode
for name in ("SOURCE_BYTES", "MAIN_BYTES", "SOURCE", "MAIN", "PAYLOAD_B85", "MAIN_BLOB", "AGENT_B64"):
    m = re.search(rf"{name}\s*=", src)
    if not m:
        continue
    # find decode for this name nearby
    j = src.find(name)
    print("FOUND", name, src[j: j + 120].replace("\n", " | "), flush=True)
    # look for name = zlib.decompress(...) or similar
    m2 = re.search(rf"{name}\s*=\s*(zlib|gzip|lzma)?\.?decompress\(([\s\S]*?)\)\s*\n", src)
    if m2:
        print(" decode expr", m2.group(0)[:100], flush=True)

# brute: find any long base64/b85 triple or concat
chunks = re.findall(r"[\"']([A-Za-z0-9+/=_~!@#$%^&*()<>{{}}|;:,\-]{{1000,}})[\"']", src)
print("long chunks", len(chunks), [len(c) for c in chunks[:5]], flush=True)
if chunks:
    packed = "".join(chunks)
    for label, fn in (
        ("b85zlib", lambda s: zlib.decompress(base64.b85decode(s))),
        ("b85gz", lambda s: gzip.decompress(base64.b85decode(s))),
        ("b85lzma", lambda s: lzma.decompress(base64.b85decode(s))),
        ("b85", lambda s: base64.b85decode(s)),
        ("b64gz", lambda s: gzip.decompress(base64.b64decode(s))),
    ):
        try:
            out = fn(packed)
            print(label, "OK", len(out), flush=True)
            if len(out) > 5000:
                (OUT / "guru_v3.py").write_bytes(out)
                print("WROTE guru_v3.py", flush=True)
                break
        except Exception as e:
            print(label, type(e).__name__, flush=True)

# also try join assignment exec
m = re.search(r"(\w+)\s*=\s*['\"]['\"]\.join\(\(", src)
if m:
    name = m.group(1)
    print("join name", name, flush=True)
    j = src.find(".join((", m.start()) + len(".join((")
    depth = 1
    k = j
    while k < len(src) and depth:
        if src[k] == "(":
            depth += 1
        elif src[k] == ")":
            depth -= 1
        k += 1
    stmt = src[m.start(1) - len(name): k]
    ns = {}
    try:
        exec(stmt, ns)
        packed = ns.get(name)
        print("joined", len(packed) if packed else None, flush=True)
        if packed:
            for label, fn in (
                ("b85zlib", lambda s: zlib.decompress(base64.b85decode(s))),
                ("b85lzma", lambda s: lzma.decompress(base64.b85decode(s))),
                ("b85gz", lambda s: gzip.decompress(base64.b85decode(s))),
            ):
                try:
                    out = fn(packed)
                    print(label, len(out), flush=True)
                    if len(out) > 5000:
                        (OUT / "guru_v3.py").write_bytes(out)
                        print("WROTE", flush=True)
                        break
                except Exception as e:
                    print(label, e, flush=True)
    except Exception as e:
        print("join exec", e, flush=True)
