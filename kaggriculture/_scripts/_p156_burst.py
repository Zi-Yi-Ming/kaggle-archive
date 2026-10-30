# -*- coding: utf-8 -*-
"""P156 BURST: extract+gate all scan_burst kernels. Find anything > H3x +508."""
from __future__ import annotations

import base64
import gzip
import importlib.util
import json
import re
import zlib
import lzma
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
SCAN = PROJ / "_external/scan_burst"
OUT = SCAN / "extracted"
OUT.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research" / "p156_burst.json"


def extract_one(nb_path: Path, tag: str):
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    src = ""
    for c in data.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if len(s) > len(src):
            src = s
    # AGENT_B64 triple quote gzip
    m = re.search(r"AGENT_B64\s*=\s*[\"']{3}([A-Za-z0-9+/=]+)[\"']{3}", src)
    if m:
        try:
            out = gzip.decompress(base64.b64decode(re.sub(r"\s+", "", m.group(1))))
            if b"def " in out and len(out) > 5000:
                p = OUT / f"{tag}.py"
                p.write_bytes(out)
                print("b64gz", tag, len(out), flush=True)
                return p
        except Exception:
            pass
    # join concat b85
    m = re.search(r"(\w+)\s*=\s*[\"'][\"']\.join\(\(", src)
    if m:
        rest = src[m.end():]
        end = rest.find("))")
        reg = rest[: end if end > 0 else 900000]
        packed = "".join(re.findall(r"[\"']([^\"']*)[\"']", reg))
        for fn in (
            lambda s: gzip.decompress(base64.b85decode(s)),
            lambda s: zlib.decompress(base64.b85decode(s)),
            lambda s: lzma.decompress(base64.b85decode(s)),
            lambda s: gzip.decompress(base64.b64decode(s)),
        ):
            try:
                out = fn(packed)
                if b"def " in out and len(out) > 5000:
                    p = OUT / f"{tag}.py"
                    p.write_bytes(out)
                    print("join", tag, len(out), flush=True)
                    return p
            except Exception:
                continue
    # writefile / big inline
    for c in data.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if "def agent" in s and len(s) > 30000 and "import base64" not in s[:300]:
            p = OUT / f"{tag}.py"
            p.write_text(s, encoding="utf-8")
            print("inline", tag, len(s), flush=True)
            return p
        if "%%writefile" in s and "def agent" in s:
            text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
            p = OUT / f"{tag}.py"
            p.write_text(text, encoding="utf-8")
            print("writefile", tag, len(text), flush=True)
            return p
    print("FAIL", tag, "src", len(src), flush=True)
    return None


def series(cand: Path, opp: Path, seeds, label):
    wins = 0
    margins = []
    for seed in seeds:
        try:
            c = p79.load_quiet(cand, f"c_{label}_{seed}")
            o = p79.load_quiet(opp, f"o_{label}_{seed}")
            b0, b1, stt, sec = p79.run(c, o, seed)
            margin = b0 - b1
            win = b0 > b1
            wins += int(win)
            margins.append(margin)
            print(f"  {label} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
        except Exception as e:
            print(f"  FAIL {label} s={seed}: {str(e)[:120]}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    cands = {}
    for folder in sorted(SCAN.iterdir()):
        if not folder.is_dir() or folder.name == "extracted":
            continue
        nbs = list(folder.glob("*.ipynb"))
        if not nbs:
            continue
        p = extract_one(nbs[0], folder.name)
        if p:
            cands[folder.name] = p

    payload = {}
    for tag, path in cands.items():
        print(f"\n==== {tag} ====", flush=True)
        mv = series(path, METAV4, (1, 2, 3), f"{tag}_mv")
        sh = series(path, SHOPV7, (1, 2), f"{tag}_sh")
        dual = mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5
        better = (mv.get("mean_margin") or -1e9) > 508
        payload[tag] = {"mv": mv, "sh": sh, "dual": "PASS" if dual else "FAIL",
                        "beats_h3x": better}
        print(f"DUAL={payload[tag]['dual']} beats_h3x={better} mv={mv} sh={sh}", flush=True)
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nWINNERS", {k: v for k, v in payload.items() if v.get("beats_h3x")}, flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
