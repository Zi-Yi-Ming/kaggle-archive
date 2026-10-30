# -*- coding: utf-8 -*-
"""P93d: exec packaging assignments then dual-gate reopen candidates."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import lzma
import re
import time
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
SCAN = PROJ / "_external/scan_p93_reopen"
OUTDIR = SCAN / "extracted3"
OUTJSON = PROJ / "_research/p93_reopen_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)


def decode_blob(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = raw.encode("latin1", "replace")
    if not isinstance(raw, (bytes, bytearray)):
        return None
    raw = bytes(raw)
    if b"def agent" in raw and len(raw) > 8000:
        return raw
    for fn in (
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.a85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: zlib.decompress(base64.b64decode(p)),
        lambda p: lzma.decompress(base64.b85decode(p)),
        lambda p: lzma.decompress(base64.b64decode(p)),
        lambda p: base64.b85decode(p),
        lambda p: base64.b64decode(p),
    ):
        try:
            src = fn(raw)
            if b"def agent" in src and len(src) > 8000:
                return src
        except Exception:
            continue
    # maybe raw is already ascii compressed payload as str
    if isinstance(raw, (bytes, bytearray)):
        try:
            packed = raw.decode("ascii", "ignore")
            for fn in (
                lambda p: zlib.decompress(base64.b85decode(p)),
                lambda p: gzip.decompress(base64.b64decode(p)),
            ):
                try:
                    src = fn(packed)
                    if b"def agent" in src:
                        return src
                except Exception:
                    continue
        except Exception:
            pass
    return None


def exec_assign(cell: str, names):
    """Exec only assignment-like prefixes for requested names."""
    ns = {"base64": base64, "zlib": zlib, "gzip": gzip, "hashlib": hashlib, "lzma": lzma}
    for name in names:
        if name not in cell:
            continue
        # find assignment start
        m = re.search(rf"(?m)^{re.escape(name)}\s*=", cell)
        if not m:
            m = re.search(rf"{re.escape(name)}\s*=", cell)
        if not m:
            continue
        chunk = cell[m.start() :]
        # cut at next top-level name assignment or assert/def/import after reasonable length
        for stop in re.finditer(r"(?m)^(EXPECTED|assert|def |import |from |MAIN|source_bytes|Path\()", chunk[20:]):
            cut = 20 + stop.start()
            if cut > 80:
                chunk = chunk[:cut]
                break
        try:
            exec(chunk, ns)
        except Exception as e:
            print(f"  exec {name} fail {type(e).__name__}: {e}", flush=True)
            # try smaller: just the join/paren expression
            m2 = re.search(rf"{re.escape(name)}\s*=\s*(.+)", cell[m.start(): m.start() + 300000], re.S)
            if m2:
                expr = m2.group(1)
                for stop in ("EXPECTED", "\nassert", "\ndef ", "\nimport "):
                    j = expr.find(stop)
                    if j > 20:
                        expr = expr[:j]
                try:
                    ns[name] = eval(expr, {"__builtins__": {}}, {"base64": base64, "zlib": zlib, "gzip": gzip, "lzma": lzma})
                except Exception as e2:
                    print(f"  eval {name} fail {e2}", flush=True)
        val = ns.get(name)
        if val is not None:
            src = decode_blob(val)
            if src:
                return name, src
    return None, None


def farmcraft_source(cell: str):
    if "SUBMISSION_SOURCE" not in cell:
        return None
    m = re.search(r"SUBMISSION_SOURCE\s*=\s*r?'''([\s\S]+?)'''", cell)
    if m and "def agent" in m.group(1):
        return m.group(1).encode("utf-8")
    m = re.search(r'SUBMISSION_SOURCE\s*=\s*r?"""([\s\S]+?)"""', cell)
    if m and "def agent" in m.group(1):
        return m.group(1).encode("utf-8")
    return None


def extract_nb(nb_path: Path) -> Path | None:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", nb_path.stem)[:48]
    out = OUTDIR / f"{name}.py"
    if out.exists() and out.stat().st_size > 20000:
        try:
            p79.load_quiet(out, f"cache_{name}")
            return out
        except Exception:
            pass
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if len(s) < 3000:
            continue
        src = farmcraft_source(s)
        if src:
            out.write_bytes(src)
            print("FARMCRAFT", out, len(src), flush=True)
            try:
                p79.load_quiet(out, f"t_{name}")
                return out
            except Exception as e:
                print(" load fail", e)
        for names in (
            ("SOURCE_BLOB",),
            ("SOURCE_B85", "SOURCE"),
            ("AGENT_B64", "AGENT_GZ_B64"),
            ("PAYLOAD_B85", "PAYLOAD"),
            ("SOURCE_BYTES",),
        ):
            key, src = exec_assign(s, names)
            if src:
                out.write_bytes(src)
                print(f"OK {name} via {key} len={len(src)} sha={hashlib.sha256(src).hexdigest()[:16]}", flush=True)
                try:
                    p79.load_quiet(out, f"t_{name}")
                    return out
                except Exception as e:
                    print(" load fail", e, flush=True)
    print("NO EXTRACT", nb_path.name, flush=True)
    return None


def series(path, name, opp_path, opp_name, seeds):
    wins = n = 0
    margins = []
    rows = []
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
                print(f"FAIL {name} {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {
        "cand": name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
        "rows": rows,
    }
    print("SUM", sm["cand"], sm["opp"], {k: sm[k] for k in ("n", "wins", "win_rate", "mean_margin")}, flush=True)
    return sm


def main():
    payload = {"results": {}, "note": "P93d reopen dual-gate", "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    nbs = list(SCAN.rglob("*.ipynb"))
    nbs = [p for p in nbs if "extracted" not in str(p)]
    nbs.sort(key=lambda p: 0 if "v54" in p.name.lower() else (1 if "idle" in p.name.lower() else 2))
    extracted = []
    for nb in nbs:
        print("extract", nb.name, flush=True)
        p = extract_nb(nb)
        if p:
            extracted.append((p.stem[:40], p))

    print("EXTRACTED", extracted, flush=True)
    for name, path in extracted:
        if (payload["results"].get(name) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            print("skip cached", name)
            continue
        print(f"\n===== {name} =====", flush=True)
        s_mv = series(path, name, METAV4, "metav4", (1, 2))
        s_sp = series(path, name, SHOPV7, "shop_v7", (1, 2))
        s_th = series(path, name, THOMAS, "thomas", (1,))
        dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
        payload["results"][name] = {
            "path": str(path), "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th, "dual": dual,
        }
        print(f"DUAL {name}: mv={s_mv.get('win_rate')}({s_mv.get('mean_margin')}) shop={s_sp.get('win_rate')}({s_sp.get('mean_margin')}) dual={dual}", flush=True)
        if dual:
            s2 = series(path, name, METAV4, "metav4_h", (3, 4, 5))
            s3 = series(path, name, SHOPV7, "shop_h", (3, 4, 5))
            payload["results"][name]["hold_mv"] = s2
            payload["results"][name]["hold_sp"] = s3
            payload["results"][name]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P93d TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "dual", v.get("dual"), "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
