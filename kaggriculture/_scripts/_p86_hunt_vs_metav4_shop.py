# -*- coding: utf-8 -*-
"""P86: extract newest public agents; dual-gate vs Metav4 AND shop_v7.

PASS bar for submit discussion:
- WR vs Metav4 >= 0.6 on smoke (escalate)
- WR vs shop_v7 >= 0.5 (must NOT collapse like pipe16 0/24)
NO SUBMIT.
"""
from __future__ import annotations

import base64
import gzip
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

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p86_hunt")
OUTDIR = ROOT / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
OUTJSON = PROJ / "_research/p86_hunt_vs_metav4_shop.json"


def extract(nb_path: Path) -> bytes | None:
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    srcs = []
    for c in nb.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        srcs.append(s)
    blob = "\n".join(srcs)

    # AGENT_B64 / _PAYLOAD gzip
    for key in ("AGENT_B64", "_PAYLOAD", "PAYLOAD", "SOURCE_BYTES"):
        if key not in blob:
            continue
        # quoted chunks after key
        idx = blob.find(key)
        region = blob[idx : idx + min(len(blob) - idx, 1_200_000)]
        # b''.join((b'...', b'...'))
        m = re.search(rf"{key}\s*=\s*b?['\"](.+?)['\"]", blob[idx:idx + 200000], re.S)
        parts = re.findall(r"b?'([^']{30,})'", region)
        parts += re.findall(r'b"([^"]{30,})"', region)
        packed = "".join(parts)
        if len(packed) < 200:
            # single string assignment
            m = re.search(rf"{key}\s*=\s*'([^']+)'", blob)
            if m:
                packed = m.group(1)
        if len(packed) < 200:
            continue
        for name, fn in [
            ("gzip+b64", lambda p: gzip.decompress(base64.b64decode(p))),
            ("zlib+b85", lambda p: zlib.decompress(base64.b85decode(p))),
            ("zlib+a85", lambda p: zlib.decompress(base64.a85decode(p))),
            ("raw+b64", lambda p: base64.b64decode(p)),
            ("bytes_escape", None),
        ]:
            if fn is None:
                try:
                    src = packed.encode("utf-8").decode("unicode_escape").encode("latin1")
                    if b"def agent" in src:
                        return src
                except Exception:
                    continue
                continue
            try:
                src = fn(packed)
                if b"def agent" in src or b"_e350_agent" in src:
                    print("  payload", key, name, len(src))
                    return src
            except Exception:
                continue
        # SOURCE_BYTES = b''.join((b'...',))
        mjoin = re.search(rf"{key}\s*=\s*b''\.join\(\(([\s\S]*?)\)\)", blob)
        if mjoin:
            try:
                ns = {}
                exec(f"{key} = b''.join(({mjoin.group(1)}))", ns)
                src = ns[key]
                if b"def agent" in src:
                    return src
            except Exception as e:
                print("  join fail", key, e)

    # %%writefile main.py
    m = re.search(r"(?ms)^%%writefile\s+main\.py\s*\n(.+?)(?=^%%writefile|\Z)", blob)
    if m and "def agent" in m.group(1):
        return m.group(1).encode("utf-8")

    # largest cell with def agent — may need WORKDIR stub + skip packaging
    best = None
    for s in srcs:
        if "def agent" in s and len(s) > 4000:
            if best is None or len(s) > len(best):
                best = s
    if best:
        return best.encode("utf-8")
    return None


def prep(code: bytes) -> str:
    text = code.decode("utf-8", errors="ignore")
    # if already full main.py keep agent part
    if "def agent" not in text and b"def agent" in code:
        # binary-ish; try decode after finding def agent
        i = code.find(b"def agent")
        if i > 0:
            text = code[max(0, i - 5000) :].decode("utf-8", errors="ignore")
    text = re.sub(r"(?m)^%%writefile.*\n", "", text)
    stub = (
        "import sys, types, json, copy, math, hashlib, zlib, base64, io, os, gzip, tarfile, ast\n"
        "from pathlib import Path\n"
        "WORKDIR=Path('.')\n"
        "OUTPUT_ROOT=Path('.')\n"
        "class _P:\n"
        "    def __init__(self,*a,**k): self.name=str(a[0]) if a else ''\n"
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
        "Path=lambda *a,**k: _P(a[0] if a else '.')\n"
        "if 'IPython' not in sys.modules:\n"
        "    ip=types.ModuleType('IPython'); ip.__path__=[]; ip.display=lambda *a,**k:None\n"
        "    ip.get_ipython=lambda: type('X',(),{'run_line_magic':lambda *a,**k:None,'magic':lambda *a,**k:None,'events':type('E',(),{'register':lambda *a,**k:None})()})()\n"
        "    sys.modules['IPython']=ip\n"
        "    d=types.ModuleType('IPython.display'); d.display=lambda *a,**k:None; d.HTML=object; d.FileLink=object\n"
        "    sys.modules['IPython.display']=d\n"
        "matplotlib=types.ModuleType('matplotlib'); matplotlib.use=lambda *a,**k:None; sys.modules['matplotlib']=matplotlib\n"
        "plt=types.ModuleType('matplotlib.pyplot'); plt.show=plt.close=lambda *a,**k:None; plt.rcParams={}\n"
        "plt.subplots=lambda *a,**k: (types.SimpleNamespace(), types.SimpleNamespace())\n"
        "plt.figure=lambda *a,**k: types.SimpleNamespace()\n"
        "sys.modules['matplotlib.pyplot']=plt\n"
        "patches=types.ModuleType('matplotlib.patches'); patches.FancyBboxPatch=object; patches.FancyArrowPatch=object\n"
        "sys.modules['matplotlib.patches']=patches\n"
        "HTML=object\n"
        "import hashlib\n"
    )
    # truncate packaging after agent
    agent_i = text.find("\ndef agent")
    if agent_i < 0:
        agent_i = text.find("def agent")
    if agent_i > 0:
        for mark in (
            "from kaggle_environments",
            "Wrote verified",
            "Path(\"main.py\")",
            "%%writefile",
            "def load_agent",
            "SOURCE_BYTES",
            "EXPECTED_MAIN",
        ):
            i = text.find(mark, agent_i)
            if i > agent_i + 50:
                text = text[:i]
                break
        keys = ["_ACTIONS =", "def agent", "def _get", "PRODUCTS =", "def build_agent"]
        idxs = [text.find(k) for k in keys if text.find(k) >= 0]
        if idxs and min(idxs) > 3000:
            text = stub + text[min(idxs) :]
        else:
            text = stub + text
    else:
        text = stub + text
    return text


def series(key, cand_path, opp_path, opp_name, seeds):
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{key}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = p79.load_quiet(cand_path, f"c_{tag}")
                o = p79.load_quiet(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                row = {
                    "opp": opp_name,
                    "seed": seed,
                    "seat0": seat0,
                    "cand": cb,
                    "opp": ob,
                    "margin": cb - ob,
                    "win": cb > ob,
                }
                print(
                    f"{key} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} "
                    f"m={row['margin']:.0f} win={row['win']}",
                    flush=True,
                )
            except Exception as e:
                row = {"opp": opp_name, "seed": seed, "seat0": seat0, "error": str(e)[:180]}
                print(f"FAIL {key} {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
            rows.append(row)
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    sm = {
        "opp": opp_name,
        "n": len(ok),
        "wins": wins,
        "win_rate": round(wins / len(ok), 3) if ok else None,
        "mean_margin": round(sum(r["margin"] for r in ok) / len(ok), 1) if ok else None,
        "errors": len(rows) - len(ok),
    }
    print("SUM", key, sm, flush=True)
    return rows, sm


def main():
    jobs = []
    for nb in sorted(ROOT.rglob("*.ipynb")):
        if "extracted" in str(nb):
            continue
        print("extract", nb.parent.name)
        raw = extract(nb)
        if not raw:
            print("  no raw")
            continue
        text = prep(raw)
        if "def agent" not in text:
            print("  no agent after prep, raw", len(raw))
            continue
        out = OUTDIR / (nb.parent.name + ".py")
        out.write_text(text, encoding="utf-8")
        print("  wrote", out.name, out.stat().st_size)
        jobs.append((nb.parent.name[:40], out))

    # also legacy pipe16 for comparison? skip - already decided NO
    payload = {"metav4": str(METAV4), "shopv7": str(SHOPV7), "results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    print("jobs", len(jobs), flush=True)
    for key, path in jobs:
        print(f"===== P86 {key} vs Metav4 =====", flush=True)
        rows_mv, sm_mv = series(key, path, METAV4, "metav4", (1, 2))
        print(f"===== P86 {key} vs shop_v7 =====", flush=True)
        rows_sp, sm_sp = series(key, path, SHOPV7, "shop_v7", (1, 2))
        payload["results"][key] = {
            "path": str(path),
            "vs_metav4": sm_mv,
            "vs_shop_v7": sm_sp,
            "rows": rows_mv + rows_sp,
        }
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        # escalate only if beats Metav4 AND does not collapse vs shop
        if (sm_mv.get("wins") or 0) >= 2 and (sm_sp.get("win_rate") or 0) >= 0.5:
            print("PROMISING dual-pass", key, flush=True)
            r2, s2 = series(key, path, METAV4, "metav4_h", (3, 4, 5))
            r3, s3 = series(key, path, SHOPV7, "shop_h", (3, 4, 5))
            payload["results"][key]["vs_metav4_hold"] = s2
            payload["results"][key]["vs_shop_hold"] = s3
            payload["results"][key]["rows"] += r2 + r3
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        elif (sm_mv.get("wins") or 0) >= 2:
            print("BEATS_METAV4_BUT_SHOP_RISK", key, sm_sp, flush=True)

    print("\n==== P86 TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(
            f"{k[:36]:36s} mv={v.get('vs_metav4')} shop={v.get('vs_shop_v7')}",
            flush=True,
        )


if __name__ == "__main__":
    main()
