# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import importlib.util
import io
import json
import re
import sys
from contextlib import redirect_stdout
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
nb = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p79_kernels\dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700\kaggriculture-herd-safe-sale-window-lb-2700.ipynb")
pkg = PROJ / "_external/scan_p96_local/extracted/dmitrii_lb2700_pkg"
pkg.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research/p96_local_gates.json"

data = json.loads(nb.read_text(encoding="utf-8", errors="ignore"))
src = None
for c in data.get("cells", []):
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    if "EMBEDDED_ASSETS" in s:
        src = s
        break

assert src
# exec only up to end of EMBEDDED_ASSETS dict
m = re.search(r"EMBEDDED_ASSETS\s*=\s*\{", src)
chunk = src[m.start() :]
# find matching close - use ast or exec whole imports+assign
# strip after dict by finding '\n\n' after closing - simpler: exec first N lines
head = chunk[: chunk.find("for name") if "for name" in chunk else 250000]
ns = {"base64": base64, "gzip": gzip, "hashlib": hashlib, "io": io, "Path": Path, "WORK": pkg}
try:
    exec("import base64,gzip,hashlib,io\nfrom pathlib import Path\nWORK=Path(r'%s')\n" % pkg + head, ns)
except Exception as e:
    print("exec fail", e)
    # try truncate at last )
    head2 = head[: head.rfind(")") + 1]
    exec("import base64,gzip,hashlib,io\nEMBEDDED_ASSETS=" + head2[head2.find("{") :], ns)

assets = ns.get("EMBEDDED_ASSETS") or {}
print("assets keys", list(assets))
for name, val in assets.items():
    # val is (size, sha, b64gzip) or similar
    print(name, type(val), len(val) if hasattr(val, "__len__") else val)
    if isinstance(val, (tuple, list)):
        for item in val:
            if isinstance(item, (bytes, str)) and len(str(item)) > 100:
                packed = item if isinstance(item, str) else item.decode("ascii", "ignore")
                try:
                    raw = gzip.decompress(base64.b64decode(packed))
                except Exception as e:
                    print(" dec fail", e)
                    continue
                path = pkg / name
                path.write_bytes(raw)
                print("WROTE", name, len(raw), hashlib.sha256(raw).hexdigest())
                break

print("pkg", {p.name: p.stat().st_size for p in pkg.iterdir()})
sys.path.insert(0, str(pkg))


def load_lb(tag):
    code = (pkg / "main.py").read_text(encoding="utf-8")
    ns = {"__name__": tag, "__file__": str(pkg / "main.py"), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(pkg / "main.py"), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def series(opp_path, opp_name, seeds=(1, 2)):
    wins = n = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"lb2700_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = load_lb(f"c_{tag}")
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
                print(f"lb2700 vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
    sm = {"cand": "dmitrii_lb2700_full", "opp": opp_name, "n": n, "wins": wins,
          "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm


load_lb("probe")
print("LOAD OK")
s_mv = series(METAV4, "metav4")
s_sp = series(SHOPV7, "shop_v7")
s_th = series(THOMAS, "thomas", (1,))
dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
print("DUAL", s_mv, s_sp, dual)
payload = {"results": {}}
if OUTJSON.exists():
    try:
        payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
    except Exception:
        pass
payload.setdefault("results", {})
payload["results"]["dmitrii_lb2700_full"] = {
    "path": str(pkg),
    "files": {p.name: p.stat().st_size for p in pkg.iterdir()},
    "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th, "dual": dual,
}
OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print("saved")
