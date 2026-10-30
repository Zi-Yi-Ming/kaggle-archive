# -*- coding: utf-8 -*-
"""Extract rayk C92/C94/C95 main.py from notebook base64+zlib embeds."""
from __future__ import annotations

import base64
import json
import re
import zlib
from pathlib import Path

NB = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p41_candidates\kaggriculture-findings-from-zero-to-top-meta.ipynb")
OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p41_extracted")
OUT.mkdir(exist_ok=True)


def extract_parts(src: str, varname: str) -> list[str]:
    # find varname = [ "....", "....", ... ]
    m = re.search(rf"{varname}\s*=\s*\[(.*?)\]", src, flags=re.S)
    if not m:
        raise RuntimeError(f"no {varname}")
    body = m.group(1)
    parts = re.findall(r'"([^"]*)"', body)
    if not parts:
        parts = re.findall(r"'([^']*)'", body)
    return parts


def decode_main(parts: list[str]) -> str:
    raw = base64.b64decode("".join(parts))
    try:
        text = zlib.decompress(raw).decode("utf-8")
    except Exception:
        text = raw.decode("utf-8", errors="replace")
    return text


def main():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    jobs = [
        (46, "_AGENT_B64_PARTS", "rayk_c92_main.py"),
        (51, "_AGENT_B64_PARTS", "rayk_c94_main.py"),
        (54, "_C95_AGENT_B64_PARTS", "rayk_c95_main.py"),
    ]
    for idx, var, name in jobs:
        src = "".join(nb["cells"][idx].get("source") or [])
        try:
            parts = extract_parts(src, var)
            text = decode_main(parts)
        except Exception as e:
            print(f"FAIL {name}: {e}")
            continue
        out = OUT / name
        out.write_text(text, encoding="utf-8")
        print(f"wrote {name} bytes={len(text)} agent={'def agent' in text}")


if __name__ == "__main__":
    main()
