# -*- coding: utf-8 -*-
"""P95: extract+gate scan_p95_again high-priority kernels."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import re
import tarfile
import io
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
SCAN = PROJ / "_external/scan_p95_again"
OUTDIR = SCAN / "extracted"
OUTJSON = PROJ / "_research/p95_again_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)

PRIORITY = [
    "2887",
    "fieldcraft",
    "more-wheat-smarter",
    "multi-route",
    "reverse-engineering",
    "demand-preserving",
    "market-rhythm",
    "first-in-line",
    "game-theoretic",
    "auto-top1",
    "autonomous",
    "shop-router-0913",
    "shape-the-shop",
    "hamburger",
    "2600",
]


def decode_any(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        try:
            raw_b = raw.encode("latin1", "replace")
            if b"def agent" in raw_b and len(raw_b) > 8000:
                return raw_b
        except Exception:
            pass
        raw = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not isinstance(raw, (bytes, bytearray)):
        return None
    raw = bytes(raw)
    if b"def agent" in raw and len(raw) > 8000:
        return raw
    for fn in (
        lambda p: gzip.decompress(base64.b64decode(p)),
        lambda p: zlib.decompress(base64.b64decode(p)),
        lambda p: zlib.decompress(base64.b85decode(p)),
        lambda p: gzip.decompress(base64.b85decode(p)),
        lambda p: base64.b85decode(p),
        lambda p: base64.b64decode(p),
    ):
        try:
            src = fn(raw)
            if b"def agent" in src:
                return src
        except Exception:
            continue
    return None


def write_try(src, out: Path):
    if not src:
        return False
    if isinstance(src, str):
        src = src.encode("utf-8")
    if b"def agent" not in src or len(src) < 8000:
        return False
    out.write_bytes(src)
    print("WROTE", out.name, len(src), hashlib.sha256(src).hexdigest()[:16], flush=True)
    try:
        p79.load_quiet(out, f"ok_{out.stem[:24]}")
        return True
    except Exception as e:
        print("LOAD FAIL", e, flush=True)
        return False


def extract_from_cell(s: str, out: Path):
    # %%writefile main.py
    if "%%writefile" in s and "main.py" in s and "def agent" in s:
        text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
        if write_try(text, out):
            return True
    # tar.gz b64
    for m in re.finditer(r"b64decode\(\s*['\"]([A-Za-z0-9+/=]{200,})['\"]", s):
        packed = re.sub(r"\s+", "", m.group(1))
        try:
            raw = base64.b64decode(packed)
        except Exception:
            continue
        if raw[:2] == b"\x1f\x8b":
            try:
                with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
                    for mem in tf.getmembers():
                        if "main.py" in mem.name:
                            if write_try(tf.extractfile(mem).read(), out):
                                return True
            except Exception:
                continue
        src = decode_any(raw)
        if src and write_try(src, out):
            return True
    # named assigns
    for name in ("SOURCE_BLOB", "SOURCE_B85", "AGENT_B64", "PAYLOAD", "SOURCE_BYTES", "ARCHIVE_BYTES", "source"):
        if name not in s:
            continue
        m = re.search(rf"(?m)^{re.escape(name)}\s*=", s) or re.search(rf"{re.escape(name)}\s*=", s)
        if not m:
            continue
        chunk = s[m.start() : m.start() + 500000]
        parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{40,})['\"]", chunk[:300000])
        if not parts:
            continue
        packed = "".join(parts)
        src = decode_any(packed.encode("ascii", "ignore"))
        if src and write_try(src, out):
            return True
        # gzip.decompress(base64.b85decode('...'))
        m2 = re.search(r"b85decode\(\s*['\"]([^'\"]{50,})['\"]", chunk[:200000])
        if m2:
            try:
                src = gzip.decompress(base64.b85decode(m2.group(1)))
                if write_try(src, out):
                    return True
            except Exception:
                try:
                    src = zlib.decompress(base64.b85decode(m2.group(1)))
                    if write_try(src, out):
                        return True
                except Exception:
                    pass
    # SUBMISSION_SOURCE triple quote
    for pat in (
        r"SUBMISSION_SOURCE\s*=\s*r?'''([\s\S]+?)'''",
        r'SUBMISSION_SOURCE\s*=\s*r?"""([\s\S]+?)"""',
        r"main_py\s*=\s*r?'''([\s\S]+?)'''",
        r"AGENT_SOURCE\s*=\s*r?'''([\s\S]+?)'''",
    ):
        m = re.search(pat, s)
        if m and "def agent" in m.group(1):
            if write_try(m.group(1), out):
                return True
    # FILES dict
    if "FILES" in s and "main.py" in s and len(s) > 20000:
        try:
            ns = {}
            exec("import base64,zlib,gzip,hashlib\n" + s, ns)
            files = ns.get("FILES") or {}
            payload = files.get("main.py")
            if isinstance(payload, str):
                payload = payload.encode("latin1", "replace")
            src = decode_any(payload)
            if src and write_try(src, out):
                return True
        except Exception as e:
            print("FILES fail", e, flush=True)
    return False


def concat_agent(nb_path: Path, out: Path):
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if "pip install" in s[:250] or "subprocess" in s[:200]:
            continue
        if "def agent" in s or (len(s) > 1500 and "def " in s and any(k in s for k in ("sell", "hire", "plant", "route", "market", "farm"))):
            parts.append(s)
    if not parts:
        return False
    code = "\n\n".join(parts)
    if "def agent" not in code:
        return False
    return write_try(code, out)


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
        if len(s) > 800:
            cells.append(s)
    cells.sort(key=len, reverse=True)
    for s in cells[:8]:
        if extract_from_cell(s, out):
            return out
    if concat_agent(nb_path, out):
        return out
    print("NO EXTRACT", nb_path.name, flush=True)
    return None


def series(path, name, opp_path, opp_name, seeds):
    wins = n = 0
    margins = []
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
            except Exception as e:
                print(f"FAIL {name} {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
    sm = {"cand": name, "opp": opp_name, "n": n, "wins": wins,
          "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm


def main():
    payload = {"results": {}, "note": "P95 again dual-gate"}
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
            extracted.append((p.stem[:40], p))

    print("EXTRACTED", [(n, p.stat().st_size) for n, p in extracted], flush=True)
    for name, path in extracted:
        if (payload["results"].get(name) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
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
            s2 = series(path, name, METAV4, "metav4_h", (3, 4, 5, 6))
            s3 = series(path, name, SHOPV7, "shop_h", (3, 4, 5, 6))
            payload["results"][name]["hold_mv"] = s2
            payload["results"][name]["hold_sp"] = s3
            payload["results"][name]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P95 TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "dual", v.get("dual"), "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
