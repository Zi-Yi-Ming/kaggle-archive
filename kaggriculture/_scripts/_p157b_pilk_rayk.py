from pathlib import Path
import base64
import gzip
import json
import re

# 1) extract pilk
nb = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\pilk_econ").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > 10000:
        src = s
print("pilk big", len(src), flush=True)
print(src[:400], flush=True)
# find b64
for pat in [r'B64\s*=\s*["\']{3}([A-Za-z0-9+/=]+)["\']{3}',
            r'b64decode\(\s*["\']([A-Za-z0-9+/=]{200,})["\']',
            r"['\']{3}([A-Za-z0-9+/=]{500,})['\']{3}"]:
    m = re.search(pat, src)
    if m:
        print("pat", pat[:30], "len", len(m.group(1)), flush=True)
        packed = re.sub(r"\s+", "", m.group(1))
        for fn in (
            lambda s: gzip.decompress(base64.b64decode(s)),
            lambda s: gzip.decompress(base64.b85decode(s)),
            lambda s: base64.b64decode(s),
        ):
            try:
                out = fn(packed)
                print("decoded", len(out), out[:40], flush=True)
                if len(out) > 5000:
                    Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\extracted\pilk_econ.py").write_bytes(out)
                    print("WROTE pilk", flush=True)
                    break
            except Exception as e:
                print("dec fail", type(e).__name__, flush=True)
        break

# 2) dump rayk strategy notes
nb = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\rayk_meta").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
texts = []
for c in data["cells"]:
    if c.get("cell_type") == "markdown":
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        texts.append(s)
Path(r"D:\桌面\Kaggle\kaggriculture\_research\rayk_meta_notes.md").write_text(
    "\n\n---\n\n".join(texts), encoding="utf-8"
)
print("rayk notes", len(texts), "md cells", flush=True)
# print strategy cluster section
full = "\n".join(texts)
i = full.find("Strategy clusters")
print(full[i:i+1500] if i >= 0 else full[:1500], flush=True)
