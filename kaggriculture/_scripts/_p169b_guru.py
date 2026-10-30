from pathlib import Path
import json
import re

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_last\extracted")
OUT.mkdir(exist_ok=True)

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

print("src", len(src), flush=True)
# find SOURCE_BYTES = b''.join((
i = src.find("SOURCE_BYTES")
print(src[i : i + 80], flush=True)
# extract statement by paren matching from b''.join((
j = src.find("b''.join((", i)
if j < 0:
    j = src.find('b"".join((', i)
print("join at", j, flush=True)
start = src.find("=", i) + 1
# from start to matching close of join((
k = src.find(".join((", i) + len(".join((")
depth = 1
p = k
while p < len(src) and depth:
    if src[p] == "(":
        depth += 1
    elif src[p] == ")":
        depth -= 1
    p += 1
stmt = src[i : p]
print("stmt head", stmt[:100], "tail", stmt[-40:], "len", len(stmt), flush=True)
ns = {}
exec(stmt, ns)
raw = ns["SOURCE_BYTES"]
print("SOURCE_BYTES", len(raw), raw[:60], flush=True)
(OUT / "guru_v3.py").write_bytes(raw)
print("WROTE guru_v3.py", raw.count(b"def agent"), flush=True)
