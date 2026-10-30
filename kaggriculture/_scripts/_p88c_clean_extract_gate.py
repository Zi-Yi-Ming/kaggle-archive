# -*- coding: utf-8 -*-
"""P88c robust extract from notebook packaging patterns + dual-gate."""
from __future__ import annotations

import base64
import gzip
import importlib.util
import io
import json
import re
import tarfile
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
NEW = PROJ / "_external/scan_p88_new"
OUTDIR = NEW / "extracted_clean"
OUTJSON = PROJ / "_research/p88c_clean_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)


def code_cells(nb_path: Path):
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    out = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        out.append(s)
    return out


def try_write_agent(src: bytes | str, out: Path) -> bool:
    if isinstance(src, str):
        src = src.encode("utf-8")
    if b"def agent" not in src and b"def kaggle_submission_agent" not in src:
        return False
    if len(src) < 8000:
        return False
    # strip %%writefile header
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
    if out.exists() and out.stat().st_size > 20000:
        print("cached", out.name, out.stat().st_size, flush=True)
        return out
    cells = code_cells(nb_path)
    # A) %%writefile main.py cell
    for s in cells:
        if "%%writefile" in s and "main.py" in s and "def agent" in s:
            if try_write_agent(s, out):
                return out
    # B) FILES = {...} base85/zlib payload (guru style)
    for s in cells:
        if "FILES" in s and ("b85decode" in s or "base64" in s) and len(s) > 5000:
            try:
                ns = {"__name__": "extract_files"}
                # only exec assignment-heavy prefix
                exec(s.split("Path(")[0] + "\nFILES=FILES\n", ns) if False else None
            except Exception:
                pass
            try:
                ns = {}
                # safer: eval FILES dict via regex of main.py entry
                m = re.search(r"FILES\s*=\s*\{([\s\S]*?)\n\}", s)
                if not m:
                    continue
                # find main.py payload string parts
                mm = re.search(r"[\"']main\.py[\"']\s*:\s*([\"']|b[\"'])", s)
                if not mm:
                    # try to decode whole FILES via exec of just the dict
                    # isolate FILES = {...} until next top-level non-string
                    body = s
                    # cut after FILES assignment roughly
                    idx = body.find("FILES")
                    chunk = body[idx:]
                    # stop at next def/import at col0 after large blob
                    ns2 = {}
                    # use zlib/base64 available
                    exec(
                        "import base64,zlib,gzip\n"
                        + chunk[: chunk.find("\nassert") if "\nassert" in chunk else len(chunk)],
                        ns2,
                    )
                    files = ns2.get("FILES") or {}
                    payload = files.get("main.py")
                    if isinstance(payload, str):
                        payload = payload.encode("latin1", errors="ignore")
                    if payload:
                        for dec in (
                            lambda p: zlib.decompress(base64.b85decode(p)),
                            lambda p: zlib.decompress(base64.a85decode(p)),
                            lambda p: gzip.decompress(base64.b64decode(p)),
                            lambda p: base64.b85decode(p),
                        ):
                            try:
                                src = dec(payload)
                                if try_write_agent(src, out):
                                    return out
                            except Exception:
                                continue
            except Exception as e:
                print("FILES extract fail", nb_path.name, e, flush=True)
    # C) ARCHIVE_BYTES / tar.gz base64
    for s in cells:
        if "ARCHIVE_BYTES" in s or ("base64.b64decode" in s and "tarfile" in s) or (
            "submission.tar.gz" in s and "b64decode" in s
        ):
            try:
                # find long base64 after b64decode
                m = re.search(r"b64decode\(\s*['\"]([A-Za-z0-9+/=\s]{200,})['\"]", s)
                if not m:
                    continue
                packed = re.sub(r"\s+", "", m.group(1))
                raw = base64.b64decode(packed)
                # tar.gz?
                if raw[:2] == b"\x1f\x8b":
                    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
                        for mem in tf.getmembers():
                            if mem.name.endswith("main.py") or mem.name == "main.py":
                                src = tf.extractfile(mem).read()
                                if try_write_agent(src, out):
                                    return out
                else:
                    if try_write_agent(raw, out):
                        return out
            except Exception as e:
                print("archive extract fail", nb_path.name, e, flush=True)
    # D) source_bytes=b'...'  (a1-t31)
    for s in cells:
        if "source_bytes" in s and "def agent" in s:
            try:
                ns = {}
                exec(s, ns)
                src = ns.get("source_bytes") or ns.get("SOURCE_BYTES")
                if src:
                    if try_write_agent(src, out):
                        return out
            except Exception as e:
                # regex literal
                m = re.search(r"source_bytes\s*=\s*b(['\"])([\s\S]*?)\1", s)
                if m:
                    try:
                        lit = "b" + m.group(1) + m.group(2) + m.group(1)
                        src = eval(lit)
                        if try_write_agent(src, out):
                            return out
                    except Exception as e2:
                        print("source_bytes fail", e, e2, flush=True)
                else:
                    print("source_bytes exec fail", nb_path.name, e, flush=True)
    # E) PAYLOAD zlib b85 (beat-v48)
    for s in cells:
        if "PAYLOAD" in s and ("b85decode" in s or "zlib" in s):
            try:
                m = re.search(r"PAYLOAD\s*=\s*['\"]([A-Za-z0-9+/=_-]{100,})['\"]", s)
                if not m:
                    continue
                packed = m.group(1)
                for dec in (
                    lambda p: zlib.decompress(base64.b85decode(p)),
                    lambda p: zlib.decompress(base64.a85decode(p)),
                    lambda p: gzip.decompress(base64.b64decode(p)),
                ):
                    try:
                        src = dec(packed)
                        if try_write_agent(src, out):
                            return out
                    except Exception:
                        continue
            except Exception as e:
                print("PAYLOAD fail", e, flush=True)
    # F) ENGINE_SOURCE / AGENT b64
    for s in cells:
        for key in ("ENGINE_SOURCE", "AGENT_B64", "AGENT_GZ_B64", "SOURCE_BLOB"):
            if key not in s:
                continue
            try:
                m = re.search(rf"{key}\s*=\s*(?:base64\.)?b64decode\(\s*['\"]([A-Za-z0-9+/=]{{80,}})['\"]", s)
                if m:
                    raw = base64.b64decode(m.group(1))
                    if raw[:2] == b"\x1f\x8b":
                        raw = gzip.decompress(raw)
                    if try_write_agent(raw, out):
                        return out
                m = re.search(rf"{key}\s*=\s*['\"]([A-Za-z0-9+/=_-]{{80,}})['\"]", s)
                if m:
                    packed = m.group(1)
                    for dec in (
                        lambda p: zlib.decompress(base64.b85decode(p)),
                        lambda p: gzip.decompress(base64.b64decode(p)),
                        lambda p: base64.b64decode(p),
                    ):
                        try:
                            src = dec(packed)
                            if try_write_agent(src, out):
                                return out
                        except Exception:
                            continue
            except Exception:
                continue
    print("NO EXTRACT", nb_path.name, flush=True)
    return None


def load_agent(path: Path, tag: str):
    return p79.load_quiet(path, tag)


def series(cand_path, cand_name, opp_path, opp_name, seeds):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{cand_name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = load_agent(cand_path, f"c_{tag}")
                o = load_agent(opp_path, f"o_{tag}")
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
                print(f"{cand_name} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {cand_name} {opp_name} s={seed} seat0={seat0}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": f"{type(e).__name__}:{e}"[:220]})
    sm = {
        "cand": cand_name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    nbs = list(NEW.rglob("*.ipynb"))
    extracted = []
    for nb in nbs:
        if "extracted" in str(nb):
            continue
        p = extract_nb(nb)
        if p:
            extracted.append((p.stem, p))
    print("\nCLEAN EXTRACTED", flush=True)
    for n, p in extracted:
        print(f"  {n} {p.stat().st_size}", flush=True)

    order_keys = ["2965", "2950", "master-engine-v4", "one-more-wheat", "a1-t31", "beat-v48", "countering", "demystifying"]

    def rank(item):
        n = item[0].lower()
        for i, k in enumerate(order_keys):
            if k in n:
                return i
        return 50

    extracted = sorted(extracted, key=rank)
    payload = {"results": {}, "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    for name, path in extracted:
        if (payload["results"].get(name) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            print("SKIP done", name, flush=True)
            continue
        print(f"\n===== {name} =====", flush=True)
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
            print(f"HOLD {name}: mv={s2.get('win_rate')} shop={s3.get('win_rate')} dual={payload['results'][name]['holdout_dual']}", flush=True)

    print("\n==== P88c TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "th", (v.get("vs_thomas") or {}).get("win_rate"), "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
