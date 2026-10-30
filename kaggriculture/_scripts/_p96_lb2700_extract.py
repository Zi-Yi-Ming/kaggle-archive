# -*- coding: utf-8 -*-
"""Extract dmitrii lb-2700 full package including settings.json if present."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import re
import sys
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
nb = PROJ / "_external/scan_p79_kernels/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700/kaggriculture-herd-safe-sale-window-lb-2700.ipynb"
if not nb.exists():
    nb = PROJ / "_external/scan_p84_vs_metav4/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700/kaggriculture-herd-safe-sale-window-lb-2700.ipynb"
pkg = PROJ / "_external/scan_p96_local/extracted/dmitrii_lb2700"
pkg.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research/p96_local_gates.json"


def dec(raw):
    if isinstance(raw, str):
        raw = raw.encode("latin1", "replace")
    if not raw:
        return None
    if isinstance(raw, (bytes, bytearray)) and (b"def agent" in raw or b"settings" in raw[:200] or raw[:1] in (b"{", b"[")):
        return bytes(raw)
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: zlib.decompress(base64.b64decode(p)),
        lambda p: gzip.decompress(base64.b85decode(p)),
        lambda p: base64.b85decode(p),
    ):
        try:
            return fn(raw)
        except Exception:
            continue
    return None


data = json.loads(nb.read_text(encoding="utf-8", errors="ignore"))
print("nb", nb.name, "cells", len(data.get("cells", [])))
for i, c in enumerate(data.get("cells", [])):
    if c.get("cell_type") != "code":
        continue
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    print(" cell", i, "len", len(s), s[:120].replace("\n", " "))
    # FILES / dict of name -> payload
    if "FILES" in s or "settings.json" in s or "main.py" in s:
        try:
            ns = {"base64": base64, "zlib": zlib, "gzip": gzip, "hashlib": hashlib}
            exec(s, ns)
            for key in ("FILES", "PAYLOADS", "ARCHIVE"):
                files = ns.get(key)
                if isinstance(files, dict):
                    print(" ", key, "keys", list(files))
                    for name, raw in files.items():
                        src = dec(raw)
                        if src:
                            path = pkg / Path(name).name
                            path.write_bytes(src)
                            print("  wrote", path.name, len(src), hashlib.sha256(src).hexdigest()[:12])
        except Exception as e:
            print(" exec fail", e)
            # regex FILENAME = b85
            for m in re.finditer(r"['\"]([^'\"]+\.(?:py|json))['\"]\s*:\s*['\"]([A-Za-z0-9+/=_-]{20,})['\"]", s):
                name, packed = m.group(1), m.group(2)
                src = dec(packed.encode())
                if src:
                    path = pkg / Path(name).name
                    path.write_bytes(src)
                    print("  wrote-regex", path.name, len(src))

print("pkg contents", list(pkg.iterdir()))
sys.path.insert(0, str(pkg))
# try load
code = (pkg / "main.py").read_text(encoding="utf-8", errors="ignore") if (pkg / "main.py").exists() else ""
ns = {"__name__": "lb2700", "__file__": str(pkg / "main.py"), "__builtins__": __builtins__}
import io
from contextlib import redirect_stdout
try:
    with redirect_stdout(io.StringIO()):
        exec(compile(code, "main.py", "exec"), ns)
    fn = ns.get("agent")
    print("agent", fn)
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    def series(opp_path, opp_name, seeds=(1, 2)):
        wins = n = 0
        margins = []
        for seed in seeds:
            for seat0 in (True, False):
                tag = f"lb2700_{opp_name}_{seed}_{int(seat0)}"
                try:
                    # reload each time for clean state
                    ns2 = {"__name__": tag, "__file__": str(pkg / "main.py"), "__builtins__": __builtins__}
                    with redirect_stdout(io.StringIO()):
                        exec(compile(code, "main.py", "exec"), ns2)
                    fn2 = ns2.get("agent")
                    n2 = getattr(getattr(fn2, "__code__", None), "co_argcount", 2)

                    def a2(obs, configuration=None):
                        return fn2(obs) if n2 <= 1 else fn2(obs, configuration)

                    o = p79.load_quiet(opp_path, f"o_{tag}")
                    if seat0:
                        b0, b1, st, sec = p79.run(a2, o, seed)
                        cb, ob = b0, b1
                    else:
                        b0, b1, st, sec = p79.run(o, a2, seed)
                        cb, ob = b1, b0
                    m = cb - ob
                    win = cb > ob
                    n += 1
                    wins += int(win)
                    margins.append(m)
                    print(f"lb2700 vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                except Exception as e:
                    print(f"FAIL {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
        sm = {"cand": "dmitrii_herd_lb2700_pkg", "opp": opp_name, "n": n, "wins": wins,
              "win_rate": round(wins / n, 3) if n else None,
              "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
        print("SUM", sm, flush=True)
        return sm

    s_mv = series(METAV4, "metav4")
    s_sp = series(SHOPV7, "shop_v7")
    s_th = series(THOMAS, "thomas", (1,))
    dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
    print("DUAL lb2700", s_mv, s_sp, dual)
    payload = {"results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})
    payload["results"]["dmitrii_herd_lb2700_pkg"] = {
        "path": str(pkg),
        "vs_metav4": s_mv,
        "vs_shop_v7": s_sp,
        "vs_thomas": s_th,
        "dual": dual,
    }
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
except Exception as e:
    print("LOAD/GATE FAIL", type(e).__name__, e)
    import traceback
    traceback.print_exc()
