# -*- coding: utf-8 -*-
"""P94b targeted extract high-value notebooks."""
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
SCAN = PROJ / "_external/scan_p94_violent"
OUTDIR = SCAN / "extracted"
OUTJSON = PROJ / "_research/p94_violent_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)


def write_try(src, out: Path):
    if src is None:
        return False
    if isinstance(src, str):
        src = src.encode("utf-8")
    if b"def agent" not in src or len(src) < 8000:
        return False
    out.write_bytes(src)
    print("WROTE", out.name, len(src), hashlib.sha256(src).hexdigest()[:16], flush=True)
    try:
        p79.load_quiet(out, f"ok_{out.stem[:20]}")
        return True
    except Exception as e:
        print("LOAD FAIL", e)
        return False


def decode_any(raw):
    if isinstance(raw, str):
        raw = raw.encode("latin1", "replace")
    if not raw:
        return None
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


def extract_from_tar_b64(cell: str, out: Path):
    # ARCHIVE_BYTES / archive_bytes = base64.b64decode('...')
    for key in ("ARCHIVE_BYTES", "archive_bytes", "TAR_B64", "submission_bytes"):
        if key not in cell:
            continue
        m = re.search(rf"{key}\s*=\s*base64\.b64decode\(\s*['\"]([A-Za-z0-9+/=\s]+)['\"]", cell)
        if not m:
            m = re.search(rf"{key}\s*=\s*['\"]([A-Za-z0-9+/=]{{100,}})['\"]", cell)
        if not m:
            continue
        packed = re.sub(r"\s+", "", m.group(1))
        raw = base64.b64decode(packed)
        if raw[:2] == b"\x1f\x8b":
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
                for mem in tf.getmembers():
                    if mem.name.endswith("main.py") or mem.name == "main.py":
                        src = tf.extractfile(mem).read()
                        if write_try(src, out):
                            return True
        src = decode_any(raw)
        if src and write_try(src, out):
            return True
    # generic b64decode long strings that are gzip tars
    for m in re.finditer(r"b64decode\(\s*['\"]([A-Za-z0-9+/=]{200,})['\"]", cell):
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
                            src = tf.extractfile(mem).read()
                            if write_try(src, out):
                                return True
            except Exception:
                continue
        src = decode_any(raw)
        if src and write_try(src, out):
            return True
    # source=gzip.decompress(base64.b85decode('...'))
    m = re.search(r"(?:source|SOURCE)\s*=\s*gzip\.decompress\(\s*base64\.b85decode\(\s*['\"]([^'\"]+)['\"]", cell)
    if m:
        try:
            src = gzip.decompress(base64.b85decode(m.group(1)))
            if write_try(src, out):
                return True
        except Exception as e:
            print("wonderful-life decode", e)
            # try zlib b85
            try:
                src = zlib.decompress(base64.b85decode(m.group(1)))
                if write_try(src, out):
                    return True
            except Exception as e2:
                print("b85z", e2)
    return False


def concat_agent_cells(nb_path: Path, out: Path):
    """Assemble tutorial-style agent from multiple cells defining agent helpers + agent."""
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if "def agent" in s or "def " in s and any(k in s for k in ("ROI", "Tile", "Worker", "scan", "assign")):
            # skip pip/env install cells
            if "pip install" in s[:200] or "kaggle_environments" in s[:300]:
                continue
            parts.append(s)
    if not parts:
        return False
    code = "\n\n".join(parts)
    if "def agent" not in code:
        return False
    return write_try(code.encode("utf-8"), out)


def extract_one(nb_path: Path) -> Path | None:
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", nb_path.stem)[:48]
    out = OUTDIR / f"{name}.py"
    if out.exists() and out.stat().st_size > 20000:
        try:
            p79.load_quiet(out, f"c_{name}")
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
    cells.sort(key=len, reverse=True)
    for s in cells[:6]:
        if extract_from_tar_b64(s, out):
            return out
        # FILES
        if "FILES" in s and "main.py" in s and len(s) > 20000:
            try:
                ns = {}
                exec("import base64,zlib,gzip,hashlib,io,tarfile\n" + s, ns)
                files = ns.get("FILES") or {}
                payload = files.get("main.py")
                if isinstance(payload, str):
                    payload = payload.encode("latin1", "replace")
                src = decode_any(payload)
                if src and write_try(src, out):
                    return out
            except Exception as e:
                print("FILES", e)
    if concat_agent_cells(nb_path, out):
        return out
    print("NO EXTRACT", nb_path.name)
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
    payload = {"results": {}, "note": "P94b"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    targets = [
        "kaggriculture-top-2-master-engine-v4",
        "25-27-strict-future-v27-midgame-meta-reset",
        "84-84-base-public-holdout-v14-clone-preemption",
        "kaggriculture-rank-your-agent",
        "cropsense-the-adaptive-farm-ai",
        "farmpilot-ai",
        "a-wonderful-life",
        "flyfarmer-connectome-plays-kaggriculture",
        "every-community-agent-one-arena",
    ]
    extracted = []
    for t in targets:
        nbs = list((SCAN / t).rglob("*.ipynb")) if (SCAN / t).exists() else []
        if not nbs:
            print("missing nb", t)
            continue
        print("extract", t, flush=True)
        p = extract_one(nbs[0])
        if p:
            extracted.append((p.stem[:40], p))

    print("EXTRACTED", extracted, flush=True)
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

    print("\n==== P94b TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "dual", v.get("dual"), "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
