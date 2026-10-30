# -*- coding: utf-8 -*-
"""P86b targeted extractors + dual gate vs Metav4 and shop_v7."""
from __future__ import annotations

import base64
import gzip
import importlib.util
import json
import lzma
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
OUTJSON = PROJ / "_research/p86b_gate.json"


def cells(nb_path):
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    out = []
    for c in nb.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        out.append(s)
    return out


def strip_agent(src: bytes | str) -> str:
    if isinstance(src, bytes):
        # find last def agent entry often at end
        text = src.decode("utf-8", errors="ignore")
    else:
        text = src
    return text


def extract_source_bytes(cell: str) -> bytes | None:
    """Exec SOURCE_BYTES = b''.join((...)) from notebook cell."""
    m = re.search(r"(SOURCE_BYTES\s*=\s*b''\.join\(\([\s\S]*?\)\))", cell)
    if not m:
        return None
    ns = {}
    try:
        exec(m.group(1), ns)
        return ns.get("SOURCE_BYTES")
    except Exception as e:
        print("  SOURCE_BYTES exec fail", e)
        return None


def extract_source_blob(cell: str) -> bytes | None:
    """SOURCE_BLOB = ''.join(( 'b85...', ...)); zlib decompress."""
    idx = cell.find("SOURCE_BLOB")
    if idx < 0:
        return None
    region = cell[idx:]
    # stop at EXPECTED or next major assign
    for stop in ("EXPECTED_MAIN", "source_bytes", "MAIN ="):
        j = region.find(stop)
        if j > 20:
            region = region[:j]
    parts = re.findall(r"'([A-Za-z0-9+/=]{20,})'", region)
    if not parts:
        parts = re.findall(r'"([A-Za-z0-9+/=]{20,})"', region)
    packed = "".join(parts)
    print("  SOURCE_BLOB parts", len(parts), "len", len(packed))
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.a85decode(p)),
        lambda p: zlib.decompress(base64.b85decode(p), -zlib.MAX_WBITS),
        lambda p: gzip.decompress(base64.b64decode(p)),
    ):
        try:
            src = fn(packed)
            print("  blob decoded", len(src), b"def agent" in src)
            return src
        except Exception:
            continue
    return None


def extract_agent_b64(cell: str) -> bytes | None:
    m = re.search(r"AGENT_B64\s*=\s*\(([\s\S]*?)\)", cell)
    if m:
        parts = re.findall(r'"([^"]+)"', m.group(1))
        packed = "".join(parts)
    else:
        m = re.search(r"AGENT_B64\s*=\s*'([^']+)'", cell)
        if not m:
            return None
        packed = m.group(1)
    try:
        src = gzip.decompress(base64.b64decode(packed))
        print("  AGENT_B64", len(src), b"def agent" in src)
        return src
    except Exception as e:
        print("  AGENT_B64 fail", e)
        return None


def extract_lzma_b85(cell: str) -> bytes | None:
    m = re.search(r"AGENT_SOURCE\s*=\s*lzma\.decompress\(base64\.b85decode\('([^']+)'\)\)", cell)
    if not m:
        # may be split
        m = re.search(r"b85decode\('([^']+)'\)", cell)
        if not m or "lzma" not in cell:
            return None
    packed = m.group(1)
    try:
        src = lzma.decompress(base64.b85decode(packed))
        print("  lzma", len(src), b"def agent" in src)
        return src
    except Exception as e:
        print("  lzma fail", e)
        return None


def extract_zlib_b85_pathlib(cell: str) -> bytes | None:
    # reyhanksatria reconstruct
    parts = re.findall(r"b85decode\('([^']+)'\)", cell)
    if not parts:
        return None
    packed = parts[0]
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: gzip.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.b85decode(p), -zlib.MAX_WBITS),
    ):
        try:
            src = fn(packed)
            print("  zlib85", len(src), b"def agent" in src)
            return src
        except Exception:
            continue
    return None


def prep_full_main(src: bytes) -> str:
    """Production main.py — load as module agent without stubbing the whole file."""
    return src.decode("utf-8", errors="ignore")


STUB = (
    "import sys, types, json, copy, math, hashlib, zlib, base64, io, os, gzip, tarfile, ast\n"
    "from pathlib import Path\n"
    "WORKDIR=Path('.')\n"
    "class _P:\n"
    "    def __init__(self,*a,**k): self.name=str(a[0]) if a else ''\n"
    "    def write_text(self,*a,**k): return len(a[0]) if a else 0\n"
    "    def write_bytes(self,*a,**k): return len(a[0]) if a else 0\n"
    "    def read_bytes(self): return b''\n"
    "    def read_text(self,*a,**k): return ''\n"
    "    def mkdir(self,*a,**k): return self\n"
    "    def exists(self): return True\n"
    "    def is_dir(self): return True\n"
    "    def open(self,*a,**k):\n"
    "        import io as _io; return _io.StringIO('')\n"
    "    def __truediv__(self,o): return _P(self.name+'/'+str(o))\n"
    "Path=lambda *a,**k: _P(a[0] if a else '.')\n"
    "HTML=object\n"
    "if 'IPython' not in sys.modules:\n"
    "    ip=types.ModuleType('IPython'); ip.__path__=[]; ip.display=lambda *a,**k:None\n"
    "    sys.modules['IPython']=ip\n"
    "    d=types.ModuleType('IPython.display'); d.display=lambda *a,**k:None; d.HTML=object\n"
    "    sys.modules['IPython.display']=d\n"
)


def load_full_agent(path: Path, tag: str):
    """exec full main.py; take last callable agent / _eXXX_agent"""
    code = path.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
    import io as _io
    from contextlib import redirect_stdout

    with redirect_stdout(_io.StringIO()):
        exec(compile(code, str(path), "exec"), ns)
    fn = ns.get("agent")
    if fn is None:
        # last def starting with _e that is callable and named agent-like
        for k, v in ns.items():
            if callable(v) and k.endswith("agent") and k != "agent":
                fn = v
    if fn is None and callable(ns.get("build_agent")):
        fn = ns["build_agent"]({})
    if fn is None:
        raise RuntimeError("no_agent in full main")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def series(key, cand_path, opp_path, opp_name, seeds, full=False):
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{key}_{opp_name}_{seed}_{int(seat0)}"
            try:
                if full:
                    c = load_full_agent(cand_path, f"c_{tag}")
                else:
                    c = p79.load_quiet(cand_path, f"c_{tag}")
                o = load_full_agent(opp_path, f"o_{tag}") if opp_path.name == "main.py" and "metav4" in str(opp_path).lower() else p79.load_quiet(opp_path, f"o_{tag}")
                # Metav4 is full main.py
                if opp_path == METAV4 or opp_path.name == "main.py":
                    try:
                        o = load_full_agent(opp_path, f"o_{tag}")
                    except Exception:
                        o = p79.load_quiet(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                row = {"opp": opp_name, "seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": cb - ob, "win": cb > ob}
                print(f"{key} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={row['margin']:.0f} win={row['win']}", flush=True)
            except Exception as e:
                row = {"opp": opp_name, "seed": seed, "seat0": seat0, "error": str(e)[:200]}
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
    extracted = []
    for nb in sorted(ROOT.rglob("*.ipynb")):
        if "extracted" in str(nb):
            continue
        name = nb.parent.name
        cs = cells(nb)
        blob = "\n".join(cs)
        src = None
        print("extract", name)
        for cell in cs:
            if "SOURCE_BYTES" in cell:
                src = extract_source_bytes(cell)
                if src:
                    print("  via SOURCE_BYTES", len(src))
                    break
            if "SOURCE_BLOB" in cell:
                src = extract_source_blob(cell)
                if src:
                    print("  via SOURCE_BLOB", len(src))
                    break
            if "AGENT_B64" in cell:
                src = extract_agent_b64(cell)
                if src:
                    print("  via AGENT_B64", len(src))
                    break
            if "lzma.decompress" in cell and "AGENT_SOURCE" in cell:
                src = extract_lzma_b85(cell)
                if src:
                    print("  via lzma", len(src))
                    break
            if "b85decode" in cell and "zlib" in cell and "def agent" not in cell[:200]:
                src = extract_zlib_b85_pathlib(cell)
                if src:
                    print("  via zlib85", len(src))
                    break
        if not src:
            # guru payload is metav4 clone
            if "_PAYLOAD" in blob and "9d63494603f8" in blob:
                print("  SKIP guru payload = Metav4 clone")
            continue
        out = OUTDIR / (name[:48] + ".py")
        out.write_bytes(src)
        print("  wrote", out.name, out.stat().st_size)
        extracted.append((name[:40], out, "def agent" in src.decode("utf-8", errors="ignore")))

    payload = {"results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {"results": {}}
    payload.setdefault("results", {})

    for key, path, has_agent in extracted:
        print(f"===== {key} =====", flush=True)
        try:
            rows_mv, sm_mv = series(key, path, METAV4, "metav4", (1, 2), full=True)
            rows_sp, sm_sp = series(key, path, SHOPV7, "shop_v7", (1, 2), full=False)
            payload["results"][key] = {"path": str(path), "vs_metav4": sm_mv, "vs_shop_v7": sm_sp}
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            if (sm_mv.get("wins") or 0) >= 2 and (sm_sp.get("win_rate") or 0) >= 0.5:
                print("DUAL_PASS escalate", key, flush=True)
                _, s2 = series(key, path, METAV4, "metav4_h", (3, 4, 5), full=True)
                _, s3 = series(key, path, SHOPV7, "shop_h", (3, 4, 5), full=False)
                payload["results"][key]["vs_metav4_hold"] = s2
                payload["results"][key]["vs_shop_hold"] = s3
                OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            elif (sm_mv.get("wins") or 0) >= 2:
                print("METAV4_OK_SHOP_WEAK", key, sm_sp, flush=True)
        except Exception as e:
            payload["results"][key] = {"path": str(path), "error": str(e)[:250]}
            print("GATE FAIL", key, e, flush=True)
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P86B ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv=", v.get("vs_metav4"), "shop=", v.get("vs_shop_v7"), flush=True)


if __name__ == "__main__":
    main()
