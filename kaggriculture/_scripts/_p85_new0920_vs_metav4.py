# -*- coding: utf-8 -*-
"""P85: extract & gate today's new public agents vs Metav4. NO SUBMIT."""
from __future__ import annotations

import base64
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

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p85_new_0920")
OUTDIR = ROOT / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
METAV4 = Path(r"D:\桌面\Kaggle\kaggriculture\_push_metav4_v13\main.py")
OUTJSON = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p85_new0920_vs_metav4.json")


def extract(nb_path: Path) -> str | None:
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        print("nb fail", e)
        return None
    srcs = []
    for c in nb.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        srcs.append(s)
    blob = "\n".join(srcs)
    # compressed payload
    for pat in [
        r"_PAYLOAD\s*=\s*'([A-Za-z0-9+/=]+)'",
        r"_AGENT_B64\s*=\s*'([A-Za-z0-9+/=]+)'",
        r"PAYLOAD\s*=\s*'([A-Za-z0-9+/=]{500,})'",
    ]:
        m = re.search(pat, blob)
        if m:
            for decoder in (
                lambda x: zlib.decompress(base64.b64decode(x)),
                lambda x: zlib.decompress(base64.b64decode(x), -zlib.MAX_WBITS),
                lambda x: base64.b64decode(x),
            ):
                try:
                    raw = decoder(m.group(1))
                    if b"def agent" in raw:
                        print("payload hit", nb_path.parent.name, len(raw))
                        return raw.decode("utf-8", errors="ignore")
                except Exception:
                    continue
    # writefile
    m = re.search(r"(?ms)^%%writefile\s+main\.py\s*\n(.+?)(?=^%%writefile|\Z)", blob)
    if m and "def agent" in m.group(1):
        return m.group(1)
    # largest def agent cell
    best = None
    for s in srcs:
        if "def agent" in s and len(s) > 3000:
            if best is None or len(s) > len(best):
                best = s
    return best


def prep(code: str) -> str:
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    agent_i = code.find("\ndef agent")
    # stubs for builder notebooks
    stub = (
        "import sys, types, json, copy, math, hashlib, zlib, base64, io, os\n"
        "from pathlib import Path\n"
        "WORKDIR=Path('.')\n"
        "class _P:\n"
        "    def __init__(self,*a,**k):\n"
        "        self.name=str(a[0]) if a else ''\n"
        "    def write_text(self,*a,**k): return len(a[0]) if a else 0\n"
        "    def write_bytes(self,*a,**k): return len(a[0]) if a else 0\n"
        "    def read_bytes(self): return b''\n"
        "    def read_text(self,*a,**k): return ''\n"
        "    def mkdir(self,*a,**k): return self\n"
        "    def exists(self): return True\n"
        "    def is_dir(self): return True\n"
        "    def rglob(self,*a,**k): return []\n"
        "    def open(self,*a,**k):\n"
        "        import io as _io; return _io.StringIO('')\n"
        "    def __truediv__(self,o): return _P(self.name+'/'+str(o))\n"
        "    def resolve(self): return self\n"
        "def _path(*a,**k): return _P(a[0] if a else '.')\n"
        "Path=_path\n"
        "if 'IPython' not in sys.modules:\n"
        "    ip=types.ModuleType('IPython'); ip.__path__=[]; ip.display=lambda *a,**k:None\n"
        "    ip.get_ipython=lambda: type('X',(),{'run_line_magic':lambda *a,**k:None,'magic':lambda *a,**k:None,'events':type('E',(),{'register':lambda *a,**k:None})()})()\n"
        "    sys.modules['IPython']=ip\n"
        "    d=types.ModuleType('IPython.display'); d.display=lambda *a,**k:None; d.HTML=object; d.FileLink=object\n"
        "    sys.modules['IPython.display']=d; ip.display_mod=d\n"
        "matplotlib=types.ModuleType('matplotlib'); matplotlib.use=lambda *a,**k:None; sys.modules['matplotlib']=matplotlib\n"
        "plt=types.ModuleType('matplotlib.pyplot'); plt.show=plt.close=lambda *a,**k:None; plt.rcParams={}\n"
        "plt.subplots=lambda *a,**k: (types.SimpleNamespace(), types.SimpleNamespace())\n"
        "plt.figure=lambda *a,**k: types.SimpleNamespace()\n"
        "sys.modules['matplotlib.pyplot']=plt\n"
        "patches=types.ModuleType('matplotlib.patches'); patches.FancyBboxPatch=object; patches.FancyArrowPatch=object\n"
        "sys.modules['matplotlib.patches']=patches\n"
        "try:\n"
        "    import pandas as pd\n"
        "except Exception:\n"
        "    pd=types.ModuleType('pandas'); pd.DataFrame=lambda *a,**k: None; sys.modules['pandas']=pd\n"
        "import hashlib\n"
        "HTML=object\n"
    )
    if agent_i > 0:
        for mark in (
            "from kaggle_environments",
            'Path("main.py")',
            "Wrote verified",
            "%%writefile",
            "def load_agent",
            "submission.tar.gz",
        ):
            i = code.find(mark, max(agent_i, 0))
            if i > agent_i:
                code = code[:i]
                break
        # if builder: take from first _ACTIONS / def helper near agent
        keys = ["_ACTIONS =", "def agent", "def build_agent", "PRODUCTS =", "def _get"]
        idxs = [code.find(k) for k in keys if code.find(k) >= 0]
        if idxs:
            start = min(idxs)
            if start > 2000:
                code = code[start:]
    return stub + code


def series(key, path, seeds=(1, 2, 3)):
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{key}_{seed}_{int(seat0)}"
            try:
                c = p79.load_quiet(path, f"c_{tag}")
                o = p79.load_quiet(METAV4, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                row = {
                    "cand": key,
                    "seed": seed,
                    "seat0": seat0,
                    "cand": cb,
                    "metav4": ob,
                    "margin": cb - ob,
                    "win": cb > ob,
                    "status": st,
                }
                print(
                    f"{key} vs Metav4 s={seed} seat0={seat0} c={cb:.0f} mv={ob:.0f} "
                    f"Δ={row['margin']:.0f} win={row['win']}",
                    flush=True,
                )
            except Exception as e:
                row = {"cand": key, "seed": seed, "seat0": seat0, "error": str(e)[:200]}
                print(f"FAIL {key} s={seed} seat0={seat0}: {e}", flush=True)
            rows.append(row)
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    sm = {
        "cand": key,
        "opp": "metav4",
        "n": len(ok),
        "wins": wins,
        "win_rate": round(wins / len(ok), 3) if ok else None,
        "mean_margin": round(sum(r["margin"] for r in ok) / len(ok), 1) if ok else None,
        "errors": len(rows) - len(ok),
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    jobs = []
    for nb in sorted(ROOT.rglob("*.ipynb")):
        if "extracted" in str(nb):
            continue
        print("extract", nb.parent.name)
        code = extract(nb)
        if not code:
            print("  no code")
            continue
        code = prep(code)
        if "def agent" not in code:
            print("  no agent after prep")
            continue
        out = OUTDIR / (nb.parent.name + ".py")
        out.write_text(code, encoding="utf-8")
        print("  wrote", out.name, out.stat().st_size)
        jobs.append((nb.parent.name, out))

    payload = {"baseline": str(METAV4), "results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    for key, path in jobs:
        print(f"===== P85 {key} =====", flush=True)
        rows, sm = series(key, path)
        payload["results"][key] = {"path": str(path), "summary": sm, "rows": rows}
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        if (sm.get("wins") or 0) >= 2:
            print("PROMISING", key, sm, flush=True)
            rows2, sm2 = series(key, path, seeds=(4, 5, 6))
            wins = sm["wins"] + sm2["wins"]
            n = sm["n"] + sm2["n"]
            payload["results"][key]["rows"] = rows + rows2
            payload["results"][key]["summary"] = {
                **sm2,
                "wins": wins,
                "n": n,
                "win_rate": round(wins / max(1, n), 3),
            }
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print("ESC", payload["results"][key]["summary"], flush=True)

    print("\n==== P85 TABLE vs Metav4 ====", flush=True)
    for k, v in payload["results"].items():
        print(k, v.get("summary") or v.get("error"), flush=True)


if __name__ == "__main__":
    main()
