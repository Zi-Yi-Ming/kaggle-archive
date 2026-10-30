from pathlib import Path
import base64
import json
import re
import zlib

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\extracted")
nbs = list(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\pop_robust").glob("*.ipynb"))
data = json.loads(nbs[0].read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > len(src):
        src = s

i = src.find("MAIN_BLOB")
print("MAIN_BLOB", i, flush=True)
# from join(( to matching ))
start = src.find(".join((", i)
print("join at", start, src[start:start+30], flush=True)
rest = src[start + len(".join(("):]
# find ))
end = rest.find("))")
print("end", end, flush=True)
reg = rest[:end]
packed = "".join(re.findall(r"['\"]([^'\"]*)['\"]", reg))
print("packed", len(packed), flush=True)
for label, fn in (
    ("b85zlib", lambda s: zlib.decompress(base64.b85decode(s))),
    ("b85", lambda s: base64.b85decode(s)),
):
    try:
        out = fn(packed)
        print(label, "OK", len(out), out[:40], flush=True)
        if len(out) > 5000:
            (OUT / "pop_robust.py").write_bytes(out)
            print("WROTE", flush=True)
            break
    except Exception as e:
        print(label, type(e).__name__, e, flush=True)

# also harvest FILES - maybe format is different
src2 = ""
nbs = list(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\harvest_ledger").glob("*.ipynb"))
data = json.loads(nbs[0].read_text(encoding="utf-8"))
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > len(src2):
        src2 = s
j = src2.find("FILES")
print("\nharvest FILES ctx:", src2[j: j + 250], flush=True)
# find zlib.decompress(base64.b85decode
k = src2.find("b85decode")
print("b85decode ctx:", src2[k - 80: k + 80], flush=True)
