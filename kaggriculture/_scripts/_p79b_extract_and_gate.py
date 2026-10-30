# -*- coding: utf-8 -*-
"""Extract agent source from P79 notebooks / builder scripts, then smoke vs thomas."""
from __future__ import annotations

import ast
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\桌面\Kaggle\kaggriculture\_scripts")
# reuse loader from p79
import importlib.util

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external")
OUTDIR = ROOT / "scan_p79_kernels" / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
RESULTS = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p79b_extracted_gate.json")

NB_ROOT = ROOT / "scan_p79_kernels"
# plus builder extracts that write main.py internally
BUILDERS = [
    ROOT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v45-first-.py",
    ROOT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v47-reacti.py",
    ROOT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v48-clear-.py",
    ROOT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v49-funded.py",
    ROOT / "scan_20260919/extracted/ahmed_v50_clean.py",
    ROOT / "scan_p77/extracted/lynnsakurai__farming-score-v5-timing-optimized.py",
    ROOT / "scan_p77/extracted/crystalbaby__kaggriculture-v38-public-submission.py",
    ROOT / "scan_p77/extracted/arsgorynich__kaggriculture-v40-challenger.py",
]


def extract_from_notebook(nb_path: Path, out_name: str) -> Path | None:
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        print("nb parse fail", nb_path, e)
        return None
    sources = []
    for cell in nb.get("cells", []):
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        sources.append(src)
    blob = "\n".join(sources)
    # 1) %%writefile main.py blocks
    parts = re.split(r"(?m)^%%writefile\s+main\.py\s*$", blob)
    candidates = []
    for part in parts[1:]:
        # take until next %%writefile or cell marker
        chunk = re.split(r"(?m)^%%writefile\s+", part)[0]
        candidates.append(chunk)
    # 2) SOURCE_BYTES / agent literal with def agent
    if "def agent" in blob:
        # prefer largest chunk containing def agent
        pass
    # 3) %%writefile main.py inside with assignment SOURCE =
    m = re.search(r"(?ms)^%%writefile\s+main\.py\s*\n(.+?)(?=^%%writefile|\Z)", blob)
    if m:
        candidates.insert(0, m.group(1))
    # 4) reconstruct from base64 SOURCE if present
    m2 = re.search(r"(?ms)SOURCE_BYTES\s*=\s*b?(.+?)\n(?:SOURCE|main_bytes|agent_bytes|write)", blob)
    # pick best candidate: has def agent and largest
    best = None
    for c in candidates:
        if "def agent" in c and (best is None or len(c) > len(best)):
            best = c
    if best is None:
        for c in sources:
            if "def agent" in c and len(c) > 8000:
                if best is None or len(c) > len(best):
                    best = c
    if best is None:
        print("no agent source", nb_path.name)
        return None
    out = OUTDIR / out_name
    out.write_text(best, encoding="utf-8")
    print(f"extracted {out.name} bytes={out.stat().st_size} from {nb_path.name}")
    return out


def extract_from_builder(path: Path) -> Path | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    out_name = path.stem + "__built.py"
    out = OUTDIR / out_name
    # look for long triple-quoted / bytes that contain def agent
    # 1) explicit write of agent source
    patterns = [
        r"(?ms)AGENT_SRC\s*=\s*'''(.+?)'''",
        r'(?ms)AGENT_SRC\s*=\s*"""(.+?)"""',
        r"(?ms)main_src\s*=\s*'''(.+?)'''",
        r'(?ms)main_src\s*=\s*"""(.+?)"""',
        r"(?ms)SOURCE\s*=\s*'''(.+?)'''",
        r'(?ms)SOURCE\s*=\s*"""(.+?)"""',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m and "def agent" in m.group(1):
            out.write_text(m.group(1).encode().decode("unicode_escape", errors="ignore") if "\\n" in m.group(1)[:200] else m.group(1), encoding="utf-8")
            print(f"extracted builder {out.name} bytes={out.stat().st_size}")
            return out
    # 2) embedded write via exec of big string assigned then write_text
    # find Path("main.py").write_text(X) and X is a name defined as long string
    m = re.search(r"write_text\((\w+)", text)
    if m:
        var = m.group(1)
        # find var = '''...'''
        for pat in [rf"(?ms){var}\s*=\s*'''(.+?)'''", rf'(?ms){var}\s*=\s*"""(.+?)"""']:
            mm = re.search(pat, text)
            if mm and "def agent" in mm.group(1):
                src = mm.group(1)
                if "\\n" in src[:500]:
                    src = src.encode("utf-8").decode("unicode_escape")
                out.write_text(src, encoding="utf-8")
                print(f"extracted builder {out.name} bytes={out.stat().st_size}")
                return out
    # 3) if file itself is nearly a full agent already
    if "def agent" in text and "def load_agent" not in text and len(text) < 200000:
        # strip packaging tail
        code = text
        agent_i = code.find("\ndef agent")
        if agent_i > 0:
            for marker in ("from kaggle_environments", "Path(\"main.py\")", "Wrote verified"):
                i = code.find(marker, agent_i)
                if i > agent_i:
                    code = code[:i]
                    break
        out.write_text(code, encoding="utf-8")
        print(f"extracted builder trimmed {out.name} bytes={out.stat().st_size}")
        return out
    # 4) ahmed-style: find embedded module dump as zlib/base64 that expands to agent
    # look for write_text with multi-line assignment near end named like v45_src
    assigns = re.findall(r"(?ms)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:f?'''|f?\"\"\")(.+?)(?:'''|\"\"\")", text)
    for name, body in assigns:
        if "def agent" in body and len(body) > 20000:
            src = body
            if "\\n" in src[:300]:
                try:
                    src = src.encode("utf-8").decode("unicode_escape")
                except Exception:
                    pass
            out.write_text(src, encoding="utf-8")
            print(f"extracted assign {name} -> {out.name} bytes={out.stat().st_size}")
            return out
    print("builder extract fail", path.name)
    return None


def smoke_gate(key: str, path: Path) -> dict:
    rows = p79.gate_one(key, path, (1, 2))
    sm = p79.summarize(rows)
    return {"path": str(path), "rows": rows, "summary": sm}


def main():
    extracted = []
    for nb in sorted(NB_ROOT.rglob("*.ipynb")):
        name = nb.parent.name + ".py"
        p = extract_from_notebook(nb, name)
        if p:
            extracted.append((nb.parent.name, p))
    for b in BUILDERS:
        if b.exists():
            p = extract_from_builder(b)
            if p:
                extracted.append((b.stem, p))
    # also any already extracted py with def agent under scan_p79
    for py in OUTDIR.glob("*.py"):
        if "def agent" in py.read_text(encoding="utf-8", errors="ignore"):
            if not any(py == p for _, p in extracted):
                extracted.append((py.stem, py))

    payload = {"results": {}}
    if RESULTS.exists():
        try:
            payload = json.loads(RESULTS.read_text(encoding="utf-8"))
        except Exception:
            payload = {"results": {}}
    payload.setdefault("results", {})

    for key, path in extracted:
        print(f"=== GATE79B {key} {path} ===", flush=True)
        try:
            res = smoke_gate(key, path)
        except Exception as e:
            res = {"path": str(path), "error": str(e)[:200]}
            print("gate fail", key, e, flush=True)
        payload["results"][key] = res
        RESULTS.parent.mkdir(parents=True, exist_ok=True)
        RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(key, res.get("summary") or res.get("error"), flush=True)

    print("\n==== P79B SUMMARY ====", flush=True)
    for k, v in payload["results"].items():
        print(f"{k:40s} {v.get('summary') or v.get('error')}", flush=True)


if __name__ == "__main__":
    main()
