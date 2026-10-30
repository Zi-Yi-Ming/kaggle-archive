# -*- coding: utf-8 -*-
"""P96b: extract dmitrii lb-2700 multi-file %%writefile package then dual-gate."""
from __future__ import annotations

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
nb = PROJ / "_external/scan_p79_kernels/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700/kaggriculture-herd-safe-sale-window-lb-2700.ipynb"
pkg = PROJ / "_external/scan_p96_local/extracted/dmitrii_lb2700_pkg"
pkg.mkdir(parents=True, exist_ok=True)
OUTJSON = PROJ / "_research/p96_local_gates.json"

data = json.loads(nb.read_text(encoding="utf-8", errors="ignore"))
for c in data.get("cells", []):
    if c.get("cell_type") != "code":
        continue
    s = c.get("source", "")
    if isinstance(s, list):
        s = "".join(s)
    # %%writefile name
    m = re.match(r"%%writefile\s+(\S+)\s*\n([\s\S]+)", s)
    if m:
        name = Path(m.group(1)).name
        body = m.group(2)
        path = pkg / name
        path.write_text(body, encoding="utf-8")
        print("WROTE", name, len(body), flush=True)
        continue
    if "SETTINGS" in s and "sale_horizon" in s:
        (pkg / "settings.json").write_text(json.dumps({"sale_horizon": 3}, indent=2, sort_keys=True), encoding="utf-8")
        print("WROTE settings.json", flush=True)

print("pkg", sorted(p.name for p in pkg.iterdir()), flush=True)
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
    sm = {"cand": "dmitrii_lb2700_pkg", "opp": opp_name, "n": n, "wins": wins,
          "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm


load_lb("probe")
print("LOAD OK", flush=True)
s_mv = series(METAV4, "metav4")
s_sp = series(SHOPV7, "shop_v7")
s_th = series(THOMAS, "thomas", (1,))
dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
print("DUAL", s_mv, s_sp, dual, flush=True)
payload = {"results": {}}
if OUTJSON.exists():
    try:
        payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
    except Exception:
        pass
payload.setdefault("results", {})
payload["results"]["dmitrii_lb2700_pkg"] = {
    "path": str(pkg),
    "files": sorted(p.name for p in pkg.iterdir()),
    "vs_metav4": s_mv,
    "vs_shop_v7": s_sp,
    "vs_thomas": s_th,
    "dual": dual,
}
OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print("saved", flush=True)
