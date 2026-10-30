from pathlib import Path
import base64
import gzip
import json
import re

nb = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\hamburger").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if "CANDIDATE_SOURCES" in s or len(s) > len(src):
        if "CANDIDATE_SOURCES" in s:
            src = s
            break
        src = s
print("src", len(src), flush=True)
print(src[:500], flush=True)
print("--- keys ---", flush=True)
for m in re.finditer(r"CANDIDATE_SOURCES\s*=\s*\{([\s\S]{0,500})", src):
    print(m.group(0)[:400], flush=True)
# names of candidates
names = re.findall(r"[\"']([^\"']+)[\"']\s*:\s*[\"']{3}", src)
print("names", names[:20], flush=True)
names2 = re.findall(r"[\"'](Anchor Exact|[^\"']{0,40}Exact[^\"']{0,20})[\"']", src)
print("exact names", set(names2), flush=True)

# extract each triple-quote source blob that has def agent
blobs = re.findall(r"[\"']{3}([\s\S]{5000,}?)[\"']{3}", src)
print("blobs", len(blobs), [len(b) for b in blobs[:10]], flush=True)
out = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\extracted")
for i, b in enumerate(blobs):
    if "def agent" in b or "def bid" in b:
        p = out / f"burger_{i}.py"
        p.write_text(b, encoding="utf-8")
        print("WROTE", p.name, len(b), flush=True)
# also try gzip b64 in src
for m in re.finditer(r"b64decode\(\s*[\"']([A-Za-z0-9+/=]{200,})[\"']", src):
    packed = re.sub(r"\s+", "", m.group(1))
    try:
        outb = gzip.decompress(base64.b64decode(packed))
        print("gz blob", len(outb), flush=True)
        (out / "burger_gz.py").write_bytes(outb)
    except Exception:
        try:
            outb = base64.b64decode(packed)
            if b"def " in outb and len(outb) > 5000:
                (out / "burger_b64.py").write_bytes(outb)
                print("b64 blob", len(outb), flush=True)
        except Exception:
            continue
