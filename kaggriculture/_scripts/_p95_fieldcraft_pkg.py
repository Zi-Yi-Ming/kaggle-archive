# -*- coding: utf-8 -*-
"""Extract Fieldcraft main.py + mirror_plan.py then dual-gate."""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import sys
import zlib
import gzip
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
pkg = PROJ / "_external/scan_p95_again/extracted/fieldcraft_pkg"
pkg.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research/p95_again_gates.json"

nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
s = nb["cells"][4]["source"]
if isinstance(s, list):
    s = "".join(s)
ns = {"base64": base64, "zlib": zlib, "gzip": gzip, "hashlib": hashlib}
exec(s, ns)
payloads = ns["PAYLOADS"]


def dec(raw):
    if isinstance(raw, str):
        raw = raw.encode("latin1", "replace")
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.a85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: gzip.decompress(base64.b85decode(p)),
    ):
        try:
            return fn(raw)
        except Exception:
            continue
    return None


files = {}
for name, raw in payloads.items():
    src = dec(raw)
    print(name, "decoded", len(src) if src else None, b"def agent" in (src or b""))
    if src:
        path = pkg / name
        path.write_bytes(src)
        files[name] = path
        print(" wrote", path, hashlib.sha256(src).hexdigest()[:16])

main_py = files.get("main.py")
if not main_py:
    raise SystemExit("no main.py")

# ensure mirror_plan importable
sys.path.insert(0, str(pkg))

# p79.load_quiet execs file with ns __file__ but imports of mirror_plan need path
# monkeypatch: prepend sys.path in load by writing a loader

def load_fc(tag):
    code = main_py.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(main_py), "__builtins__": __builtins__}
    import io
    from contextlib import redirect_stdout
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(main_py), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


load_fc("probe")
print("LOAD OK fieldcraft+mirror_plan")


def series(opp_path, opp_name, seeds=(1, 2)):
    wins = n = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"fc2887_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = load_fc(f"c_{tag}")
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
                print(f"FAIL {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
    sm = {"n": n, "wins": wins, "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", opp_name, sm, flush=True)
    return sm


s_mv = series(METAV4, "metav4")
s_sp = series(SHOPV7, "shop_v7")
s_th = series(THOMAS, "thomas", (1,))
dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
print("DUAL fieldcraft2887", "mv", s_mv, "shop", s_sp, "dual", dual)
payload = {"results": {}}
if OUTJSON.exists():
    try:
        payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
    except Exception:
        pass
payload.setdefault("results", {})
res = payload["results"].get("fieldcraft_2887") or {}
res.update({
    "path": str(main_py),
    "pkg": str(pkg),
    "vs_metav4": s_mv,
    "vs_shop_v7": s_sp,
    "vs_thomas": s_th,
    "dual": dual,
    "note": "Hak public 2887.4 sub 56258004; main+mirror_plan exact extract",
})
if dual:
    s2 = series(METAV4, "metav4_h", (3, 4, 5, 6))
    s3 = series(SHOPV7, "shop_h", (3, 4, 5, 6))
    res["hold_mv"] = s2
    res["hold_sp"] = s3
    res["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
    print("HOLDOUT", res["hold_mv"], res["hold_sp"], res["holdout_dual"])
payload["results"]["fieldcraft_2887"] = res
OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
