from pathlib import Path
import ast
import base64
import json
import re
import zlib

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\extracted")


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


def save(tag, raw):
    if isinstance(raw, str):
        raw = raw.encode()
    if b"def " in raw and len(raw) > 5000:
        p = OUT / f"{tag}.py"
        p.write_bytes(raw)
        print("WROTE", tag, len(raw), flush=True)
        return True
    print("skip", tag, len(raw), flush=True)
    return False


# harvest: exec the FILES assignment
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\harvest_ledger"))
m = re.search(r"FILES\s*=\s*\{[\s\S]*?\n\}", src)
if m:
    ns = {}
    try:
        exec(m.group(0), ns)
        print("harvest FILES", {k: len(v) for k, v in ns["FILES"].items()}, flush=True)
        for fn, enc in ns["FILES"].items():
            content = zlib.decompress(base64.b85decode(enc))
            print(" member", fn, len(content), flush=True)
            save("harvest_" + Path(fn).name.replace(".txt", ".py"), content)
    except Exception as e:
        print("harvest exec fail", e, flush=True)
        # fallback: ast the dict if it's pure
        try:
            d = ast.literal_eval(m.group(0).split("=", 1)[1].strip())
            print("ast FILES", {k: len(v) for k, v in d.items()}, flush=True)
            for fn, enc in d.items():
                content = zlib.decompress(base64.b85decode(enc))
                save("harvest_" + Path(fn).name.replace(".txt", ".py"), content)
        except Exception as e2:
            print("ast fail", e2, flush=True)

# pop: exec MAIN_BLOB assignment
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\pop_robust"))
m = re.search(r"MAIN_BLOB\s*=\s*['\"]['\"]\.join\(\([\s\S]*?\)\)", src)
if m:
    ns = {}
    try:
        exec(m.group(0), ns)
        packed = ns.get("MAIN_BLOB")
        print("pop MAIN_BLOB", len(packed) if packed else None, flush=True)
        if packed:
            # try zlib b85
            for fn in (
                lambda s: zlib.decompress(base64.b85decode(s)),
                lambda s: base64.b85decode(s),
            ):
                try:
                    out = fn(packed)
                    save("pop_robust", out)
                    break
                except Exception as e:
                    print("pop dec", e, flush=True)
    except Exception as e:
        print("pop exec fail", e, flush=True)
else:
    print("pop join regex fail", flush=True)

# ice PAYLOAD_B85
import lzma
src = biggest(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\ice_fire"))
m = re.search(r"PAYLOAD_B85\s*=\s*[\"']{3}([\s\S]+?)[\"']{3}", src)
if not m:
    m = re.search(r"PAYLOAD_B85\s*=\s*['\'][\"']?join\(\(([\s\S]*?)\)\)", src)
    if m:
        ns = {}
        exec("PAYLOAD_B85 = ''.join((" + m.group(1) + "))", ns)
        packed = ns["PAYLOAD_B85"]
    else:
        packed = None
else:
    packed = m.group(1)
print("ice packed", len(packed) if packed else None, flush=True)
if packed:
    try:
        out = lzma.decompress(base64.b85decode(packed))
        save("ice_fire", out)
    except Exception as e:
        print("ice fail", e, flush=True)
