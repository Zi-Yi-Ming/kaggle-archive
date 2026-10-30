# -*- coding: utf-8 -*-
"""P98 extract-only: pull source main.py out of scan_p98_new notebooks."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
import tarfile
import io
from pathlib import Path

SCAN = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")
OUT = SCAN / "extracted"
OUT.mkdir(parents=True, exist_ok=True)


def decode_any(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, (bytes, bytearray)):
        return None
    raw = bytes(raw)
    if b"def agent" in raw and len(raw) > 5000:
        return raw
    for fn in (
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: gzip.decompress(p),
        lambda p: base64.b64decode(p),
    ):
        try:
            src = fn(raw)
            if b"def agent" in src:
                return src
        except Exception:
            continue
    return None


def write_try(src, out: Path):
    if not src:
        return False
    if isinstance(src, str):
        src = src.encode("utf-8")
    if b"def agent" not in src or len(src) < 5000:
        return False
    if out.exists() and out.stat().st_size >= len(src):
        return False
    out.write_bytes(src)
    print("WROTE", out.name, len(src), hashlib.sha256(src).hexdigest()[:16], flush=True)
    return True


def extract_from_text(s: str, out: Path):
    if "%%writefile" in s and "main.py" in s and "def agent" in s:
        text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
        if write_try(text, out):
            return True
    for name in (
        "AGENT_B64",
        "SOURCE_B64",
        "PAYLOAD",
        "SOURCE_BLOB",
        "ARCHIVE_BYTES",
        "SOURCE_BYTES",
        "source",
        "source_bytes",
        "main",
        "data",
        "code",
        "agent_src",
    ):
        m = re.search(rf"{re.escape(name)}\s*=\s*[\"']{{3}}([\s\S]+?)[\"']{{3}}", s)
        if m and "def agent" in m.group(1) and len(m.group(1)) > 5000:
            if write_try(m.group(1), out):
                return True
        m = re.search(rf"{re.escape(name)}\s*=\s*[\"']([A-Za-z0-9+/=\s]{{300,}})[\"']", s)
        if m:
            packed = re.sub(r"\s+", "", m.group(1))
            src = decode_any(packed)
            if src and write_try(src, out):
                return True
    for m in re.finditer(r"b64decode\(\s*[\"']([A-Za-z0-9+/=]{200,})[\"']", s):
        packed = re.sub(r"\s+", "", m.group(1))
        try:
            raw = base64.b64decode(packed)
        except Exception:
            continue
        if raw[:2] == b"\x1f\x8b":
            try:
                with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
                    for mem in tf.getmembers():
                        if "main.py" in mem.name:
                            if write_try(tf.extractfile(mem).read(), out):
                                return True
            except Exception:
                pass
        src = decode_any(raw)
        if src and write_try(src, out):
            return True
    # long triple-quoted with def agent anywhere
    for m in re.finditer(r"[r]?[\"']{3}([\s\S]{8000,}?)[\"']{3}", s):
        body = m.group(1)
        if "def agent" in body:
            if write_try(body, out):
                return True
    return False


def extract_nb(nb_path: Path, tag: str) -> Path | None:
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    out = OUT / f"{tag}_main.py"
    chunks = []
    for cell in data.get("cells", []):
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        chunks.append(src)
        if extract_from_text(src, out):
            return out
    if extract_from_text("\n\n".join(chunks), out):
        return out
    print("NO EXTRACT", tag, flush=True)
    (OUT / f"{tag}_all_cells.txt").write_text("\n\n".join(chunks), encoding="utf-8")
    return None


def main():
    found = {}
    for nb in sorted(SCAN.rglob("*.ipynb")):
        tag = nb.parent.name
        if tag == "extracted":
            continue
        print("====", tag, nb.name, flush=True)
        try:
            p = extract_nb(nb, tag)
        except Exception as e:
            print("ERR", tag, e, flush=True)
            p = None
        if p and p.exists():
            found[tag] = str(p)
    (OUT / "extract_index.json").write_text(json.dumps(found, indent=2), encoding="utf-8")
    print("FOUND", found, flush=True)


if __name__ == "__main__":
    main()
