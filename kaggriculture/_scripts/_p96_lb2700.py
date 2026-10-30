# -*- coding: utf-8 -*-
"""Gate dmitrii herd-safe-sale-window-lb-2700 (candidate '2700 package')."""
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
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
NBS = [
    PROJ / "_external/scan_p84_vs_metav4/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700/kaggriculture-herd-safe-sale-window-lb-2700.ipynb",
    PROJ / "_external/scan_p79_kernels/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700/kaggriculture-herd-safe-sale-window-lb-2700.ipynb",
    PROJ / "_external/scan_p77/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700/kaggriculture-herd-safe-sale-window-lb-2700.ipynb",
]
EXISTING = [
    PROJ / "_external/scan_p84_vs_metav4/extracted/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700.py",
    PROJ / "_external/scan_p79_kernels/extracted/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700.py",
    PROJ / "_external/scan_p77/extracted/dmitriigluzdov__kaggriculture-herd-safe-sale-win.py",
]
OUT = PROJ / "_external/scan_p96_dig/extracted/lb2700_herd_safe.py"
OUT.parent.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research/p96_lb2700.json"


def try_load(path: Path, tag: str):
    return p79.load_quiet(path, tag)


def decode(raw):
    if isinstance(raw, str):
        raw = raw.encode("latin1", "replace")
    if not raw:
        return None
    if b"def agent" in raw and len(raw) > 5000:
        return raw
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.a85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: gzip.decompress(base64.b85decode(p)),
        lambda p: base64.b64decode(p),
    ):
        try:
            src = fn(raw)
            if b"def agent" in src:
                return src
        except Exception:
            continue
    return None


def extract():
    for p in EXISTING:
        if p.exists() and p.stat().st_size > 5000:
            try:
                try_load(p, f"ex_{p.stem[:20]}")
                print("LOAD existing", p, p.stat().st_size)
                OUT.write_bytes(p.read_bytes())
                return OUT
            except Exception as e:
                print("existing fail", p.name, e)
    for nb_path in NBS:
        if not nb_path.exists():
            continue
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
        for c in nb.get("cells", []):
            if c.get("cell_type") != "code":
                continue
            s = c.get("source", "")
            if isinstance(s, list):
                s = "".join(s)
            if len(s) < 3000:
                continue
            # SOURCE / PAYLOAD assigns
            for name in ("SOURCE_BLOB", "SOURCE_B85", "AGENT_B64", "PAYLOAD", "SOURCE", "source"):
                if name not in s:
                    continue
                parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{40,})['\"]", s[:400000])
                packed = "".join(parts)
                src = decode(packed.encode("ascii", "ignore")) if packed else None
                if src:
                    OUT.write_bytes(src)
                    print("decoded via", name, len(src))
                    try_load(OUT, "dec")
                    return OUT
                m = re.search(r"b85decode\(\s*['\"]([^'\"]{50,})['\"]", s)
                if m:
                    src = decode(m.group(1).encode())
                    if src:
                        OUT.write_bytes(src)
                        print("decoded b85", len(src))
                        try_load(OUT, "dec2")
                        return OUT
            if "def agent" in s and "%%writefile" in s:
                text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
                OUT.write_text(text, encoding="utf-8")
                try_load(OUT, "wf")
                return OUT
            if "def agent" in s and len(s) > 20000:
                OUT.write_text(s, encoding="utf-8")
                try:
                    try_load(OUT, "inline")
                    return OUT
                except Exception as e:
                    print("inline fail", e)
    print("NO EXTRACT")
    return None


def series(path, name, opp_path, opp_name, seeds):
    wins = n = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = try_load(path, f"c_{tag}")
                o = try_load(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                m = cb - ob
                win = cb > ob
                n += 1
                wins += int(win)
                margins.append(m)
                print(f"{name} vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {name} {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
    sm = {"n": n, "wins": wins, "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm


def main():
    path = extract()
    if not path:
        return
    print("sha", hashlib.sha256(path.read_bytes()).hexdigest()[:16], "size", path.stat().st_size)
    s_mv = series(path, "lb2700", METAV4, "metav4", (1, 2, 3))
    s_sp = series(path, "lb2700", SHOPV7, "shop_v7", (1, 2, 3))
    s_th = series(path, "lb2700", THOMAS, "thomas", (1, 2))
    dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
    payload = {
        "path": str(path),
        "vs_metav4": s_mv,
        "vs_shop_v7": s_sp,
        "vs_thomas": s_th,
        "dual": dual,
        "note": "dmitrii herd-safe-sale-window-lb-2700; prior extracts failed",
    }
    print("DUAL", dual, payload)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
