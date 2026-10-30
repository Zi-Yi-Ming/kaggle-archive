# -*- coding: utf-8 -*-
"""P150 FINAL: extract 2965/2950 and dual-gate vs Metav4+shop. No submit without pass."""
from __future__ import annotations

import base64
import gzip
import importlib.util
import json
import re
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
SCAN = PROJ / "_external" / "scan_final"
OUT = SCAN / "extracted"
OUT.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research" / "p150_final_gate.json"


def extract(nb_path: Path, tag: str):
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    for c in data.get("cells", []):
        src = c.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        # b85 or b64 gzip
        for name in ("SOURCE_BLOB", "PAYLOAD", "AGENT_B64", "V59", "SOURCE"):
            m = re.search(rf"{name}\s*=\s*['\"]['\"]\.join\(\(", src)
            if m:
                region = src[m.end(): m.end() + 2000000]
                packed = "".join(re.findall(r"['\"]([^'\"]*)['\"]", region.split(")")[0] if False else region[: len(region)]))
                # better: until decompress line
                end = re.search(rf"{name}\)", src[m.start():])
                reg = src[m.end(): m.start() + (end.start() if end else 500000)]
                packed = "".join(re.findall(r"['\"]([^'\"]*)['\"]", reg))
                for dec in (
                    lambda s: gzip.decompress(base64.b85decode(s)),
                    lambda s: gzip.decompress(base64.b64decode(s)),
                    lambda s: base64.b85decode(s),
                ):
                    try:
                        out = dec(packed)
                        if b"def " in out and len(out) > 5000:
                            p = OUT / f"{tag}_main.py"
                            p.write_bytes(out)
                            print("WROTE", p, len(out), flush=True)
                            return p
                    except Exception:
                        continue
        # inline main
        if "def agent" in src and len(src) > 20000 and "import base64" not in src[:200]:
            p = OUT / f"{tag}_main.py"
            p.write_text(src, encoding="utf-8")
            print("INLINE", p, len(src), flush=True)
            return p
        # writefile
        if "%%writefile" in src and "def agent" in src:
            text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", src)
            p = OUT / f"{tag}_main.py"
            p.write_text(text, encoding="utf-8")
            print("WRITEFILE", p, len(text), flush=True)
            return p
    print("FAIL extract", tag, flush=True)
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
            print(f"{label} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
        except Exception as e:
            print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    cands = {}
    for tag, folder, pat in (
        ("hy2965", SCAN / "hy2965", "*.ipynb"),
        ("peak2950", SCAN / "peak2950", "*.ipynb"),
    ):
        nbs = list(folder.glob(pat))
        if nbs:
            p = extract(nbs[0], tag)
            if p:
                cands[tag] = p

    payload = {}
    for tag, path in cands.items():
        print(f"\n==== {tag} ====", flush=True)
        mv = series(path, METAV4, (1, 2, 3), f"{tag}_mv")
        sh = series(path, SHOPV7, (1, 2), f"{tag}_sh")
        print("MV", mv, "SH", sh, flush=True)
        ok = mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5
        payload[tag] = {"mv": mv, "sh": sh, "dual": "PASS" if ok else "FAIL"}
        print("DUAL", payload[tag]["dual"], flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("DONE", payload, flush=True)


if __name__ == "__main__":
    main()
