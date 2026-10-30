# -*- coding: utf-8 -*-
"""P93b robust extract from SOURCE_BLOB / large gzip-b85 cells."""
from __future__ import annotations

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
SCAN = PROJ / "_external/scan_p93_reopen"
OUTDIR = SCAN / "extracted2"
OUTJSON = PROJ / "_research/p93_reopen_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)


def try_write(src, out: Path) -> bool:
    if src is None:
        return False
    if isinstance(src, str):
        src = src.encode("utf-8")
    if not isinstance(src, (bytes, bytearray)):
        return False
    src = bytes(src)
    if b"def agent" not in src or len(src) < 8000:
        return False
    out.write_bytes(src)
    print("WROTE", out.name, len(src), hashlib.sha256(src).hexdigest()[:16], flush=True)
    return True


def decoders(packed: str):
    fns = [
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: zlib.decompress(base64.a85decode(p)),
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: zlib.decompress(base64.b64decode(p)),
        lambda p: base64.b85decode(p),
        lambda p: base64.b64decode(p),
    ]
    for fn in fns:
        try:
            yield fn(packed)
        except Exception:
            continue


def extract_from_cell(s: str, out: Path):
    # SOURCE_BLOB = ''.join(('...','...'))
    if "SOURCE_BLOB" in s:
        idx = s.find("SOURCE_BLOB")
        region = s[idx:]
        for stop in ("EXPECTED", "assert", "MAIN =", "source_bytes"):
            j = region.find(stop)
            if j > 30:
                region = region[:j]
        parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{20,})['\"]", region)
        packed = "".join(parts)
        print("  SOURCE_BLOB parts", len(parts), "len", len(packed), flush=True)
        for src in decoders(packed):
            if try_write(src, out):
                return True
    # SOURCE / SOURCE_BYTES / PAYLOAD single string
    for key in ("SOURCE", "PAYLOAD", "AGENT_SOURCE", "source_bytes"):
        if key not in s:
            continue
        m = re.search(rf"{key}\s*=\s*[\"']([A-Za-z0-9+/=_-]{{50,}})[\"']", s)
        if m:
            for src in decoders(m.group(1)):
                if try_write(src, out):
                    return True
        m = re.search(rf"{key}\s*=\s*[\"']([A-Za-z0-9+/=_-]{{50,}})[\"']", s)
        # also concatenated quotes after key
        idx = s.find(key)
        region = s[idx : idx + 400000]
        parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{40,})['\"]", region)
        if parts:
            packed = "".join(parts)
            for src in decoders(packed):
                if try_write(src, out):
                    return True
    # SUBMISSION_SOURCE = r'''...''' or assignment
    m = re.search(r"SUBMISSION_SOURCE\s*=\s*(?:r)?[\"']{3}([\s\S]*?)[\"']{3}", s)
    if m and "def agent" in m.group(1):
        if try_write(m.group(1), out):
            return True
    m = re.search(r"SUBMISSION_SOURCE\s*=\s*(?:r)?[\"']([\s\S]+?)[\"']\s*(?:\n|$)", s)
    if m and "def agent" in m.group(1) and len(m.group(1)) > 8000:
        text = m.group(1).encode("utf-8").decode("unicode_escape")
        if try_write(text, out):
            return True
    # large cell: collect b85/b64 chunks
    if len(s) > 100000:
        parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{60,})['\"]", s)
        packed = "".join(parts)
        if len(packed) > 200:
            for src in decoders(packed):
                if try_write(src, out):
                    return True
    return False


def extract_nb(nb_path: Path) -> Path | None:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", nb_path.stem)[:48]
    out = OUTDIR / f"{name}.py"
    if out.exists() and out.stat().st_size > 20000:
        try:
            p79.load_quiet(out, f"c_{name}")
            return out
        except Exception:
            pass
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    # prefer largest code cells
    cells = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        cells.append(s)
    cells.sort(key=len, reverse=True)
    for s in cells:
        if extract_from_cell(s, out):
            try:
                p79.load_quiet(out, f"t_{name}")
                return out
            except Exception as e:
                print("wrote but load fail", e, flush=True)
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
                print(f"FAIL {name} vs {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": f"{type(e).__name__}:{e}"[:200]})
    sm = {
        "cand": name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    payload = {"updated": "", "results": {}, "note": "P93b reopen dual-gate"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    nbs = [p for p in SCAN.rglob("*.ipynb") if "extracted" not in str(p)]
    # priority V54 first
    nbs.sort(key=lambda p: 0 if "v54" in p.name.lower() else 1)
    extracted = []
    for nb in nbs:
        print("extract", nb.name, flush=True)
        p = extract_nb(nb)
        if p:
            extracted.append((p.stem[:40], p))

    print("EXTRACTED", extracted, flush=True)
    for name, path in extracted:
        if (payload["results"].get(name) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            continue
        print(f"\n===== {name} =====", flush=True)
        r_mv, s_mv = series(path, name, METAV4, "metav4", (1, 2))
        r_sp, s_sp = series(path, name, SHOPV7, "shop_v7", (1, 2))
        r_th, s_th = series(path, name, THOMAS, "thomas", (1,))
        payload["results"][name] = {
            "path": str(path), "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        payload["updated"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL {name}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) dual={dual}", flush=True)
        if dual:
            r2, s2 = series(path, name, METAV4, "metav4_h", (3, 4, 5))
            r3, s3 = series(path, name, SHOPV7, "shop_h", (3, 4, 5))
            payload["results"][name]["hold_mv"] = s2
            payload["results"][name]["hold_sp"] = s3
            payload["results"][name]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P93b TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
