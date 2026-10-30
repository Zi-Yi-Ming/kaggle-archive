# -*- coding: utf-8 -*-
"""Extract Andrey Breaking the Tie main.py from notebook cell 0 packaging."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import re
import zlib
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
NB = PROJ / "_external/scan_p92b_versions/andrey_latest/kaggriculture-breaking-the-tie.ipynb"
NB_OLD = PROJ / "_external/scan_p77/andrewsokolovsky__kaggriculture-breaking-the-tie/kaggriculture-breaking-the-tie.ipynb"
OUT = PROJ / "_external/scan_p92b_versions/extracted/andrey_breaking_tie.py"
OUT.parent.mkdir(parents=True, exist_ok=True)

METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUTJSON = PROJ / "_research/p92c_andrey.json"


def decode_payloads(text: str):
    out = []
    # SOURCE_BYTES join
    m = re.search(r"(SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\))", text)
    if m:
        try:
            ns = {}
            exec(m.group(1), ns)
            src = ns.get("SOURCE_BYTES")
            if src:
                out.append(("SOURCE_BYTES", src))
        except Exception as e:
            print("SOURCE_BYTES fail", e)
    # EXPECTED_SOURCE / gzip b64 patterns
    for key in ("SOURCE", "source_bytes", "MAIN_SOURCE", "AGENT_SOURCE", "payload", "PACKED"):
        if key not in text:
            continue
        idx = text.find(key)
        region = text[idx: idx + 300000]
        # b64 after b64decode
        for m in re.finditer(r"b64decode\(\s*['\"]([A-Za-z0-9+/=\s]{80,})['\"]", region):
            packed = re.sub(r"\s+", "", m.group(1))
            for dec in (
                lambda p: gzip.decompress(base64.b64decode(p)),
                lambda p: zlib.decompress(base64.b64decode(p)),
                lambda p: base64.b64decode(p),
            ):
                try:
                    src = dec(packed)
                    out.append((f"{key}_b64", src))
                    break
                except Exception:
                    continue
        # b85 zlib string chunks
        parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{40,})['\"]", region[:50000])
        packed = "".join(parts)
        if len(packed) > 200:
            for dec in (
                lambda p: zlib.decompress(base64.b85decode(p)),
                lambda p: zlib.decompress(base64.a85decode(p)),
            ):
                try:
                    src = dec(packed)
                    out.append((f"{key}_b85", src))
                    break
                except Exception:
                    continue
    return out


def main():
    candidates = []
    for nb_path in (NB, NB_OLD):
        if not nb_path.exists():
            continue
        print("NB", nb_path, nb_path.stat().st_size)
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
        for i, c in enumerate(nb.get("cells", [])):
            s = c.get("source", "")
            if isinstance(s, list):
                s = "".join(s)
            if len(s) < 1000:
                continue
            hits = decode_payloads(s)
            print(f"  cell{i} len={len(s)} hits={[(n,len(b)) for n,b in hits]}")
            for name, src in hits:
                if isinstance(src, str):
                    src = src.encode("utf-8")
                if b"def agent" in src and len(src) > 8000:
                    candidates.append((nb_path.name, i, name, src))
            if "def agent" in s and "%%writefile" in s:
                text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
                candidates.append((nb_path.name, i, "writefile", text.encode("utf-8")))

    for nbname, i, name, src in candidates:
        print("try", nbname, i, name, len(src), hashlib.sha256(src).hexdigest()[:16])
        OUT.write_bytes(src)
        try:
            p79.load_quiet(OUT, "andrey_try")
            print("LOAD OK ->", OUT, len(src))
            print("sha256", hashlib.sha256(src).hexdigest())
            return
        except Exception as e:
            print("LOAD FAIL", e)

    # last resort: cell5 overlay is not full agent; try combining engine stubs - skip
    print("NO CANDIDATE LOADED")


if __name__ == "__main__":
    main()
