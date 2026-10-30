from pathlib import Path
import base64
import gzip
import json
import re
import zlib
import lzma

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\extracted")
OUT.mkdir(exist_ok=True)


def biggest(path):
    nbs = list(path.glob("*.ipynb"))
    data = json.loads(nbs[0].read_text(encoding="utf-8"))
    src = ""
    for c in data["cells"]:
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if len(s) > len(src):
            src = s
    return src


def try_dec(packed, tag):
    packed = re.sub(r"\s+", "", packed)
    for label, fn in (
        ("b85zlib", lambda s: zlib.decompress(base64.b85decode(s))),
        ("b85gz", lambda s: gzip.decompress(base64.b85decode(s))),
        ("b85lzma", lambda s: lzma.decompress(base64.b85decode(s))),
        ("b85", lambda s: base64.b85decode(s)),
        ("b64gz", lambda s: gzip.decompress(base64.b64decode(s + "=" * (-len(s) % 4)))),
        ("b64zlib", lambda s: zlib.decompress(base64.b64decode(s + "=" * (-len(s) % 4)))),
        ("b64", lambda s: base64.b64decode(s + "=" * (-len(s) % 4))),
    ):
        try:
            out = fn(packed)
            if b"def " in out and len(out) > 5000:
                p = OUT / f"{tag}.py"
                p.write_bytes(out)
                print("OK", tag, label, len(out), flush=True)
                return p
        except Exception:
            continue
    print("dec fail", tag, "packed", len(packed), flush=True)
    return None


# harvest: join or long b85 near decompress
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\harvest_ledger"))
print("harvest decompress ctx:", src[src.find("decompress") - 100: src.find("decompress") + 80], flush=True)
# find longest quoted b85 run
chunks = re.findall(r"['\"]([A-Za-z0-9+/=_~!@#$%^&*()<>{}|;:,.\-]{500,})['\"]", src)
print("harvest long quotes", len(chunks), [len(c) for c in chunks[:5]], flush=True)
if chunks:
    packed = "".join(chunks)
    try_dec(packed, "harvest_ledger")

# ice_fire: gzip b64 near start + b85 later
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\ice_fire"))
print("ice decompress ctx:", src[src.find("decompress") - 80: src.find("decompress") + 60], flush=True)
m = re.search(r"[\"']{3}([A-Za-z0-9+/=]{500,})[\"']{3}", src)
if m:
    try_dec(m.group(1), "ice_fire")
chunks = re.findall(r"['\"]([A-Za-z0-9+/=_~!@#$%^&*()<>{}|;:,\-]{500,})['\"]", src)
print("ice long quotes", len(chunks), [len(c) for c in chunks[:5]], flush=True)
if chunks and not (OUT / "ice_fire.py").exists():
    try_dec("".join(chunks), "ice_fire")

# pop_robust: MAIN_BLOB join
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\pop_robust"))
m = re.search(r"MAIN_BLOB\s*=\s*['\"]['\"]\.join\(\(([\s\S]*?)\)\)", src)
if m:
    packed = "".join(re.findall(r"['\"]([^'\"]*)['\"]", m.group(1)))
    print("pop packed", len(packed), flush=True)
    try_dec(packed, "pop_robust")
