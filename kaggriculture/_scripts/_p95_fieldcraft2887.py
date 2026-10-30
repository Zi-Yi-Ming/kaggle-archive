# -*- coding: utf-8 -*-
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
nb_path = PROJ / "_external/scan_p95_again/kaggriculture-2887-score-fieldcraft-agent/kaggriculture-2887-score-fieldcraft-agent.ipynb"
out = PROJ / "_external/scan_p95_again/extracted/fieldcraft_2887.py"
out.parent.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research/p95_again_gates.json"

nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
s = nb["cells"][4]["source"]
if isinstance(s, list):
    s = "".join(s)
print("cell4 len", len(s))
print(s[:300])
# exec PAYLOADS
ns = {"base64": base64, "zlib": zlib, "gzip": gzip, "hashlib": hashlib}
try:
    exec(s, ns)
    payloads = ns.get("PAYLOADS") or {}
    print("PAYLOADS keys", list(payloads))
    raw = payloads.get("main.py")
    if isinstance(raw, str):
        raw = raw.encode("latin1", "replace")
    print("raw len", len(raw) if raw else None)
    src = None
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.a85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: gzip.decompress(base64.b85decode(p)),
    ):
        try:
            src = fn(raw)
            print("decoded", len(src), b"def agent" in src)
            break
        except Exception as e:
            print("dec fail", e)
    if src and b"def agent" in src:
        out.write_bytes(src)
        print("WROTE", out, len(src), hashlib.sha256(src).hexdigest())
        p79.load_quiet(out, "fieldcraft_probe")
        print("LOAD OK")
except Exception as e:
    print("exec fail", e)
    # regex join
    parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{30,})['\"]", s)
    packed = "".join(parts)
    print("parts", len(parts), "len", len(packed))
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
    ):
        try:
            src = fn(packed.encode())
            print("fn ok", len(src), b"def agent" in src)
            if b"def agent" in src:
                out.write_bytes(src)
                print("WROTE", out)
                break
        except Exception as e2:
            print(e2)

# gate if loaded
if out.exists() and out.stat().st_size > 8000:
    def series(opp_path, opp_name, seeds=(1, 2)):
        wins = n = 0
        margins = []
        for seed in seeds:
            for seat0 in (True, False):
                tag = f"fieldcraft2887_{opp_name}_{seed}_{int(seat0)}"
                try:
                    c = p79.load_quiet(out, f"c_{tag}")
                    o = p79.load_quiet(opp_path, f"o_{tag}")
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
                    print(f"fieldcraft vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                except Exception as e:
                    print(f"FAIL {opp_name} s={seed}: {e}", flush=True)
        sm = {"n": n, "wins": wins, "win_rate": round(wins / n, 3) if n else None,
              "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
        print("SUM", opp_name, sm, flush=True)
        return sm

    s_mv = series(METAV4, "metav4")
    s_sp = series(SHOPV7, "shop_v7")
    s_th = series(THOMAS, "thomas", (1,))
    dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
    print("DUAL fieldcraft2887", s_mv, s_sp, "dual", dual)
    payload = {"results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})
    payload["results"]["fieldcraft_2887"] = {
        "path": str(out), "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th, "dual": dual,
        "note": "Hak claimed public 2887.4 on submission 56258004",
    }
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
