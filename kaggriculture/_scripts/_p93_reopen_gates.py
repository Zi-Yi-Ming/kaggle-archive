# -*- coding: utf-8 -*-
"""P93 Reopen: extract + dual-gate newest public notebooks after freeze scan."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import re
import time
import zlib
import tarfile
import io
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
PIPE16 = PROJ / "_push_pipe16" / "main.py"
SCAN = PROJ / "_external/scan_p93_reopen"
OUTDIR = SCAN / "extracted"
OUTJSON = PROJ / "_research/p93_reopen_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)

PRIORITY = [
    "v54",
    "v53",
    "idle-workers",
    "farmer-john",
    "god-s-mode",
    "farmcraft",
]


def try_write(src: bytes, out: Path) -> bool:
    if isinstance(src, str):
        src = src.encode("utf-8")
    if b"def agent" not in src or len(src) < 5000:
        return False
    text = src.decode("utf-8", errors="ignore")
    if text.lstrip().startswith("%%writefile"):
        text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", text, count=1)
        src = text.encode("utf-8")
    out.write_bytes(src)
    print("WROTE", out.name, len(src), flush=True)
    return True


def extract_nb(nb_path: Path) -> Path | None:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", nb_path.stem)[:48]
    out = OUTDIR / f"{name}.py"
    if out.exists() and out.stat().st_size > 8000:
        try:
            p79.load_quiet(out, f"cache_{name}")
            return out
        except Exception:
            pass
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    cells = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        cells.append(s)
    # A writefile with def agent
    for s in cells:
        if "%%writefile" in s and "main.py" in s and "def agent" in s:
            if try_write(s, out):
                return out
    # B SOURCE_BYTES
    for s in cells:
        if "SOURCE_BYTES" in s:
            m = re.search(r"(SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\))", s)
            if m:
                try:
                    ns = {}
                    exec(m.group(1), ns)
                    if try_write(ns.get("SOURCE_BYTES") or b"", out):
                        return out
                except Exception as e:
                    print("SOURCE_BYTES fail", e)
    # C FILES dict
    for s in cells:
        if "FILES" in s and "main.py" in s and len(s) > 5000:
            try:
                ns = {}
                exec("import base64,zlib,gzip,hashlib\n" + s, ns)
                files = ns.get("FILES") or {}
                payload = files.get("main.py")
                if isinstance(payload, str):
                    payload = payload.encode("latin1", "replace")
                if payload:
                    for dec in (
                        lambda p: zlib.decompress(base64.b85decode(p)),
                        lambda p: zlib.decompress(base64.a85decode(p)),
                        lambda p: gzip.decompress(base64.b64decode(p)),
                    ):
                        try:
                            if try_write(dec(payload), out):
                                return out
                        except Exception:
                            continue
            except Exception as e:
                print("FILES fail", e)
    # D PAYLOAD zlib b85 / gzip b64
    for s in cells:
        if "PAYLOAD" not in s and "b85decode" not in s and "b64decode" not in s:
            continue
        m = re.search(r"PAYLOAD\s*=\s*[\"']([^\"']+)[\"']", s)
        if m:
            packed = m.group(1)
            for dec in (
                lambda p: zlib.decompress(base64.b85decode(p)),
                lambda p: zlib.decompress(base64.a85decode(p)),
                lambda p: gzip.decompress(base64.b64decode(p)),
            ):
                try:
                    if try_write(dec(packed), out):
                        return out
                except Exception:
                    continue
        m = re.search(r"b64decode\(\s*[\"']([A-Za-z0-9+/=\s]{80,})[\"']", s)
        if m:
            packed = re.sub(r"\s+", "", m.group(1))
            for dec in (
                lambda p: gzip.decompress(base64.b64decode(p)),
                lambda p: zlib.decompress(base64.b64decode(p)),
                lambda p: base64.b64decode(p),
            ):
                try:
                    raw = dec(packed)
                    if raw[:2] == b"\x1f\x8b":
                        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
                            for mem in tf.getmembers():
                                if mem.name.endswith("main.py"):
                                    if try_write(tf.extractfile(mem).read(), out):
                                        return out
                    if try_write(raw, out):
                        return out
                except Exception:
                    continue
    # E source_bytes=b'...' literal
    for s in cells:
        if "source_bytes" in s and "def agent" in s:
            m = re.search(r"source_bytes\s*=\s*b(['\"])([\s\S]*?)\1", s)
            if m:
                try:
                    src = eval("b" + m.group(1) + m.group(2) + m.group(1))
                    if try_write(src, out):
                        return out
                except Exception:
                    pass
            try:
                ns = {}
                exec(s, ns)
                if try_write(ns.get("source_bytes") or ns.get("SOURCE_BYTES") or b"", out):
                    return out
            except Exception:
                pass
    print("NO EXTRACT", nb_path.name, flush=True)
    return None


def series(path, name, opp_path, opp_name, seeds):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = p79.load_quiet(path, f"c_{tag}")
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
                print(f"{name} vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {name} {opp_name} s={seed} seat0={int(seat0)}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": f"{type(e).__name__}:{e}"[:200]})
    sm = {
        "cand": name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    payload = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": "P93 reopen scan; dual-gate only; no submit without auth",
        "cli_metav4": 2630.2,
        "results": {},
    }
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    nbs = [p for p in SCAN.rglob("*.ipynb") if "extracted" not in str(p)]
    nbs.sort(key=lambda p: next((i for i, k in enumerate(PRIORITY) if k in p.name.lower() or k in p.as_posix().lower()), 50))
    extracted = []
    for nb in nbs:
        print("extract", nb.name, flush=True)
        p = extract_nb(nb)
        if p:
            extracted.append((p.stem, p))
            print(" sha", hashlib.sha256(p.read_bytes()).hexdigest()[:16], flush=True)

    print("\nEXTRACTED", [(n, p.stat().st_size) for n, p in extracted], flush=True)

    for name, path in extracted:
        prev = payload["results"].get(name) or {}
        if (prev.get("vs_metav4") or {}).get("n", 0) >= 4:
            print("SKIP done", name, flush=True)
            continue
        print(f"\n===== {name} =====", flush=True)
        try:
            p79.load_quiet(path, f"probe_{name}")
        except Exception as e:
            print("LOAD FAIL", e, flush=True)
            payload["results"][name] = {"path": str(path), "load_error": str(e)[:200]}
            continue
        r_mv, s_mv = series(path, name, METAV4, "metav4", (1, 2))
        r_sp, s_sp = series(path, name, SHOPV7, "shop_v7", (1, 2))
        r_th, s_th = series(path, name, THOMAS, "thomas", (1,))
        payload["results"][name] = {
            "path": str(path), "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL {name}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) th={s_th.get('win_rate')} dual={dual}", flush=True)
        if dual:
            print("ESCALATE", name, flush=True)
            r2, s2 = series(path, name, METAV4, "metav4_h", (3, 4, 5))
            r3, s3 = series(path, name, SHOPV7, "shop_h", (3, 4, 5))
            payload["results"][name]["hold_mv"] = s2
            payload["results"][name]["hold_sp"] = s3
            payload["results"][name]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P93 TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
