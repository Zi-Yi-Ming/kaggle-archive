from pathlib import Path
import base64
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


def grab_dict_b85(src, name):
    # name = { 'file': 'b85...' , ...}
    m = re.search(rf"{name}\s*=\s*\{{([\s\S]*?)\n\}}", src)
    if not m:
        return {}
    out = {}
    for fn, enc in re.findall(r"[\"']([^\"']+)[\"']\s*:\s*[\"']([^\"']+)[\"']", m.group(1)):
        out[fn] = enc
    return out


def grab_var(src, name):
    m = re.search(rf"{name}\s*=\s*[\"']{{3}}([\s\S]+?)[\"']{{3}}", src)
    if m:
        return m.group(1)
    m = re.search(rf"{name}\s*=\s*[\"']([A-Za-z0-9+/=_~!@#$%^&*()<>{{}}|;:,\-]+)[\"']", src)
    return m.group(1) if m else None


def save(tag, raw: bytes):
    if b"def " in raw and len(raw) > 5000:
        p = OUT / f"{tag}.py"
        p.write_bytes(raw)
        print("WROTE", tag, len(raw), flush=True)
        return p
    print("skip", tag, len(raw), raw[:30], flush=True)
    return None


# harvest FILES dict
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\harvest_ledger"))
files = grab_dict_b85(src, "FILES")
print("harvest files", {k: len(v) for k, v in files.items()}, flush=True)
for fn, enc in files.items():
    try:
        content = zlib.decompress(base64.b85decode(enc))
        print("harvest member", fn, len(content), flush=True)
        if fn.endswith("main.py") or b"def " in content[:5000]:
            save("harvest_" + Path(fn).name, content)
    except Exception as e:
        print("harvest fail", fn, e, flush=True)

# ice PAYLOAD_B85
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\ice_fire"))
payload = grab_var(src, "PAYLOAD_B85")
print("ice payload", len(payload) if payload else None, flush=True)
if payload:
    try:
        main_bytes = lzma.decompress(base64.b85decode(payload))
        save("ice_fire", main_bytes)
    except Exception as e:
        print("ice fail", e, flush=True)

# pop MAIN_BLOB - maybe concat of short strings without name join match
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\pop_robust"))
print("pop MAIN_BLOB at", src.find("MAIN_BLOB"), flush=True)
print(src[src.find("MAIN_BLOB"): src.find("MAIN_BLOB") + 200], flush=True)
print(src[-400:], flush=True)
