from pathlib import Path
import base64
import gzip
import json
import re
import tarfile
import io

nb = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\c05").glob("*.ipynb"))
data = json.loads(nb.read_text(encoding="utf-8"))
src = ""
for c in data["cells"]:
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if len(s) > len(src):
        src = s
print("biggest", len(src), flush=True)
print(src[:350], flush=True)

out_dir = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\extracted")
# AGENT_B64 gzip
m = re.search(r"AGENT_B64\s*=\s*[\"']{3}([A-Za-z0-9+/=]+)[\"']{3}", src)
if m:
    packed = re.sub(r"\s+", "", m.group(1))
    out = gzip.decompress(base64.b64decode(packed))
    (out_dir / "c05.py").write_bytes(out)
    print("WROTE c05.py", len(out), flush=True)
else:
    # join
    m = re.search(r"[\"'][\"']\.join\(\(", src)
    if m:
        rest = src[m.end():]
        end = rest.find("))")
        packed = "".join(re.findall(r"[\"']([^\"']*)[\"']", rest[: end if end > 0 else 900000]))
        for fn in (
            lambda s: gzip.decompress(base64.b85decode(s)),
            lambda s: gzip.decompress(base64.b64decode(s)),
            lambda s: base64.b85decode(s),
        ):
            try:
                out = fn(packed)
                print("join dec", len(out), flush=True)
                if len(out) > 5000:
                    (out_dir / "c05.py").write_bytes(out)
                    print("WROTE", flush=True)
                    break
            except Exception:
                continue
    else:
        # b64decode single
        m = re.search(r"b64decode\(\s*[\"']([A-Za-z0-9+/=]{200,})[\"']", src)
        if m:
            packed = re.sub(r"\s+", "", m.group(1))
            for fn in (
                lambda s: gzip.decompress(base64.b64decode(s)),
                lambda s: base64.b64decode(s),
            ):
                try:
                    out = fn(packed)
                    print("b64 dec", len(out), flush=True)
                    if len(out) > 5000:
                        (out_dir / "c05.py").write_bytes(out)
                        print("WROTE", flush=True)
                        break
                except Exception:
                    continue
        # writefile
        for c in data["cells"]:
            s = c.get("source", "")
            if isinstance(s, list):
                s = "".join(s)
            if "%%writefile" in s and "def agent" in s:
                text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
                (out_dir / "c05.py").write_text(text, encoding="utf-8")
                print("WROTE writefile", len(text), flush=True)
                break
