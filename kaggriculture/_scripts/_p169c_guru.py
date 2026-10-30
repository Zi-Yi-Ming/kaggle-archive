from pathlib import Path
import json

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_last\extracted")
nbs = list(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_last\guru_v3").glob("*.ipynb"))
data = json.loads(nbs[0].read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if "SOURCE_BYTES" in s and len(s) > 10000:
        src = s
        break

# statement ends at the line after the closing )) that is followed by assert or similar
# find last occurrence of \n)  or \n)) before assert hashlib
i = src.find("SOURCE_BYTES")
# look for pattern:  ))\nassert  or ))\n\nassert
for pat in ("\n)\n", "\n))\n", ")\nassert", "))\nassert", ")\n\nassert", "))\n\nassert"):
    j = src.find(pat, i + 1000)
    if j > 0:
        print("pat", repr(pat), "at", j, "ctx", src[j : j + 40].replace("\n", "|"), flush=True)

# take from SOURCE_BYTES to first \nassert hashlib after it
k = src.find("\nassert hashlib", i)
print("assert at", k, flush=True)
stmt = src[i:k]
print("stmt len", len(stmt), "head", stmt[:80], "tail", stmt[-80:], flush=True)

# exec in a way that tolerates - use compile
ns = {}
try:
    exec(stmt, ns)
    raw = ns["SOURCE_BYTES"]
    print("OK", len(raw), raw[:50], flush=True)
    (OUT / "guru_v3.py").write_bytes(raw)
    print("WROTE", raw.count(b"def "), flush=True)
except Exception as e:
    print("exec fail", e, flush=True)
    # fallback: regex extract all b'...' or b"..." pieces
    import re
    parts = re.findall(r"b(?:'([^']*)'|\"([^\"]*)\")", stmt)
    print("parts", len(parts), flush=True)
    raw = b"".join((a.encode() if a else b.encode()) for a, b in parts)
    print("joined", len(raw), raw[:50], flush=True)
    if len(raw) > 5000:
        (OUT / "guru_v3.py").write_bytes(raw)
        print("WROTE fallback", flush=True)
