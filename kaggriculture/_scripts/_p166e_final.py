from pathlib import Path
import base64
import json
import re
import zlib
import lzma

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\extracted")


def cell_srcs(path):
    nbs = list(path.glob("*.ipynb"))
    data = json.loads(nbs[0].read_text(encoding="utf-8"))
    out = []
    for c in data["cells"]:
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        out.append(s)
    return out


def save(tag, raw):
    if isinstance(raw, str):
        raw = raw.encode()
    if b"def " in raw and len(raw) > 5000:
        (OUT / f"{tag}.py").write_bytes(raw)
        print("WROTE", tag, len(raw), flush=True)
        return True
    return False


# HARVEST: find FILES = { ... } by brace matching
for s in cell_srcs(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\harvest_ledger")):
    if "FILES = {" not in s:
        continue
    i = s.find("FILES = {")
    j = i + len("FILES = {")
    depth = 1
    while j < len(s) and depth:
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
        j += 1
    body = s[i + len("FILES = ") : j]
    ns = {}
    try:
        exec("FILES = " + body, ns)
        print("harvest keys", list(ns["FILES"].keys()), [len(v) for v in ns["FILES"].values()], flush=True)
        for fn, enc in ns["FILES"].items():
            content = zlib.decompress(base64.b85decode(enc))
            print(" ", fn, len(content), flush=True)
            if "main" in fn:
                save("harvest_main", content)
    except Exception as e:
        print("harvest fail", e, flush=True)
    break

# POP: find MAIN_BLOB = ''.join((  ...  ))  by paren matching
for s in cell_srcs(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\pop_robust")):
    if "MAIN_BLOB = ''.join((" not in s and 'MAIN_BLOB = "".join((' not in s:
        continue
    i = s.find("MAIN_BLOB")
    j = s.find(".join((", i) + len(".join((")
    depth = 2  # already inside join((
    # actually we need to consume until the closing )) of join
    depth = 1
    k = j
    while k < len(s) and depth:
        if s[k] == "(":
            depth += 1
        elif s[k] == ")":
            depth -= 1
        k += 1
    # k is just after the closing ( of join's arg... need one more )
    # simpler: take s[j:k] where k found matching close of join((
    arg = s[j : k - 1] if k > j else ""
    # arg is the tuple source
    ns = {}
    try:
        exec("MAIN_BLOB = " + s[i + len("MAIN_BLOB = ") : k], ns)
        packed = ns["MAIN_BLOB"]
        print("pop packed", len(packed), flush=True)
        for fn in (
            lambda x: zlib.decompress(base64.b85decode(x)),
            lambda x: base64.b85decode(x),
        ):
            try:
                save("pop_robust", fn(packed))
                break
            except Exception as e:
                print("pop dec", e, flush=True)
    except Exception as e:
        print("pop fail", e, "arglen", len(arg), flush=True)
    break

# ICE: PAYLOAD_B85 = ''.join(( ... ))
for s in cell_srcs(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_today\ice_fire")):
    if "PAYLOAD_B85" not in s:
        continue
    i = s.find("PAYLOAD_B85")
    print("ice PAYLOAD line", s[i : i + 80], flush=True)
    # could be triple quote or join
    ns = {}
    # find statement end roughly at next \nEXPECTED or \nassert or \nmain
    m = re.search(r"PAYLOAD_B85\s*=\s*[\s\S]{0,5}join\(\(", s)
    if m:
        j = s.find(".join((", i) + len(".join((")
        depth = 1
        k = j
        while k < len(s) and depth:
            if s[k] == "(":
                depth += 1
            elif s[k] == ")":
                depth -= 1
            k += 1
        try:
            exec("PAYLOAD_B85 = " + s[i + len("PAYLOAD_B85 = ") : k], ns)
            packed = ns["PAYLOAD_B85"]
            print("ice packed", len(packed), flush=True)
            out = lzma.decompress(base64.b85decode(packed))
            save("ice_fire", out)
        except Exception as e:
            print("ice fail", e, flush=True)
    else:
        m = re.search(r"PAYLOAD_B85\s*=\s*[\"']{3}([\s\S]+?)[\"']{3}", s)
        if m:
            try:
                out = lzma.decompress(base64.b85decode(m.group(1)))
                save("ice_fire", out)
            except Exception as e:
                print("ice tq fail", e, flush=True)
    break
