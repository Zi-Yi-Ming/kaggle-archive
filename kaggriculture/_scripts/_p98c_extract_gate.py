# -*- coding: utf-8 -*-
"""P98c: extract+gate new public notebooks vs Metav4 + shop_v7."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import re
import tarfile
import io
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
SCAN = PROJ / "_external/scan_p98_new"
OUTDIR = SCAN / "extracted"
OUTJSON = PROJ / "_research/p98_new_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)
RESEARCH = PROJ / "_research"
RESEARCH.mkdir(exist_ok=True)


def decode_any(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, (bytes, bytearray)):
        return None
    raw = bytes(raw)
    if b"def agent" in raw and len(raw) > 8000:
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
    if b"def agent" not in src or len(src) < 8000:
        return False
    out.write_bytes(src)
    print("WROTE", out.name, len(src), hashlib.sha256(src).hexdigest()[:16], flush=True)
    try:
        p79.load_quiet(out, f"ok_{out.stem[:24]}")
        return True
    except Exception as e:
        print("LOAD FAIL", e, flush=True)
        return False


def extract_from_cell(s: str, out: Path):
    if "%%writefile" in s and "main.py" in s and "def agent" in s:
        text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
        if write_try(text, out):
            return True
    # AGENT_B64 style
    for name in ("AGENT_B64", "SOURCE_B64", "PAYLOAD", "SOURCE_BLOB", "ARCHIVE_BYTES", "SOURCE_BYTES"):
        m = re.search(rf"{re.escape(name)}\s*=\s*[\"']{{3}}([\s\S]+?)[\"']{{3}}", s)
        if not m:
            m = re.search(rf"{re.escape(name)}\s*=\s*[\"']([A-Za-z0-9+/=\s]{{200,}})[\"']", s)
        if not m:
            continue
        packed = re.sub(r"\s+", "", m.group(1))
        src = decode_any(packed)
        if src and write_try(src, out):
            return True
        # maybe the name holds plain source
        if "def agent" in m.group(1) and len(m.group(1)) > 8000:
            if write_try(m.group(1), out):
                return True
    # any long b64
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
    # triple-quoted source assigned to source/main/agent
    for name in ("source", "source_bytes", "main", "main_py", "data", "agent_src", "code"):
        m = re.search(
            rf"(?m){re.escape(name)}\s*=\s*[r]?[\"']{{3}}([\s\S]{{5000,}}?)[\"']{{3}}",
            s,
        )
        if m and "def agent" in m.group(1):
            if write_try(m.group(1), out):
                return True
    # source = Path(...).read_text / open
    return False


def extract_nb(nb_path: Path, tag: str) -> Path | None:
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    out = OUTDIR / f"{tag}_main.py"
    for i, cell in enumerate(data.get("cells", [])):
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        if extract_from_cell(src, out):
            return out
    # full-text fallback
    full = "\n".join(
        "".join(c.get("source", [])) if isinstance(c.get("source"), list) else c.get("source", "")
        for c in data.get("cells", [])
    )
    if extract_from_cell(full, out):
        return out
    print("NO EXTRACT", tag)
    return None


def gate_one(name: str, path: Path) -> dict:
    row = {"name": name, "path": str(path), "bytes": path.stat().st_size}
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        row["has_agent"] = "def agent" in src
        row["sha"] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        # crude family
        row["pipe16_hint"] = any(
            k in src for k in ("PIPE16", "Pipe-16", "mirror_plan", "step0", "BUY_SEED")
        ) and "shop" in src.lower()
    except Exception as e:
        row["err"] = str(e)
        return row

    results = {}
    for opp_name, opp_path in (("metav4", METAV4), ("shopv7", SHOPV7), ("thomas", THOMAS)):
        if not opp_path.exists():
            results[opp_name] = {"error": "missing opp"}
            continue
        wins = 0
        margins = []
        n = 0
        for seed in (1, 2, 3, 4):
            try:
                r = p79.play_pair(path, opp_path, seed=seed)
                # play_pair API may differ — adapt below
                n += 1
            except Exception as e:
                results[opp_name] = {"error": str(e)}
                break
        else:
            results[opp_name] = {"n": n}
    row["raw"] = results
    return row


# Prefer p79's own gate if present
def gate_via_p79(name: str, path: Path) -> dict:
    if hasattr(p79, "gate_one"):
        try:
            return p79.gate_one(name, path)
        except Exception as e:
            return {"name": name, "error": f"p79.gate_one: {e}"}
    if hasattr(p79, "play_game"):
        return {"name": name, "note": "use play_game manually"}
    return {"name": name, "note": "no gate helper", "dir": [x for x in dir(p79) if not x.startswith("_")]}


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
    print("EXTRACTED", found, flush=True)

    # discover gate API
    api = [x for x in dir(p79) if not x.startswith("_")]
    print("p79 API", api, flush=True)
    (OUTJSON).write_text(json.dumps({"extracted": found, "p79_api": api}, indent=2), encoding="utf-8")

    # run gates if helper exists
    gated = {}
    for tag, path in found.items():
        print("GATE", tag, flush=True)
        if hasattr(p79, "gate_one"):
            try:
                gated[tag] = p79.gate_one(tag, Path(path))
            except Exception as e:
                gated[tag] = {"error": str(e)}
        else:
            gated[tag] = {"error": "no gate_one"}
        print(" ->", json.dumps(gated[tag], ensure_ascii=False)[:300], flush=True)

    OUTJSON.write_text(
        json.dumps({"extracted": found, "gated": gated}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
