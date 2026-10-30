# -*- coding: utf-8 -*-
"""P92b: exact dual-gate for Kaito v48 + Breaking the Tie.

Counsel priority:
1) Kaito v48 Fast Routes (local public_nb artifact; version pull 403)
2) Andrey Breaking the Tie V12 (extract repair)
Smoke 3 seeds x 2 seats; escalate only if pass.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
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
ALPEREN = PROJ / "_push_alperen" / "main.py"
KAITO43 = PROJ / "_external/public_nb/kaito_v43/main.py"
KAITO48 = PROJ / "_external/public_nb/kaito_v48/main.py"
GURU4 = PROJ / "_external/scan_p88_new/extracted_clean/guru_master_v4.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
ANDREY_RAW = PROJ / "_external/scan_p77/extracted/andrewsokolovsky__kaggriculture-breaking-the-tie.py"
ANDREY_NB = PROJ / "_external/scan_p77/andrewsokolovsky__kaggriculture-breaking-the-tie/kaggriculture-breaking-the-tie.ipynb"
OUTDIR = PROJ / "_external/scan_p92b_versions/extracted"
OUTJSON = PROJ / "_research/p92b_v48_tie.json"
OUTDIR.mkdir(parents=True, exist_ok=True)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def try_load(path: Path, tag: str):
    return p79.load_quiet(path, tag)


def extract_andrey() -> Path | None:
    out = OUTDIR / "andrey_breaking_tie.py"
    if out.exists() and out.stat().st_size > 15000:
        try:
            try_load(out, "andrey_cache")
            return out
        except Exception:
            pass
    # pull latest nb if needed
    if not ANDREY_NB.exists():
        print("andrey nb missing", flush=True)
    sources = []
    if ANDREY_NB.exists():
        nb = json.loads(ANDREY_NB.read_text(encoding="utf-8", errors="ignore"))
        for c in nb.get("cells", []):
            if c.get("cell_type") != "code":
                continue
            s = c.get("source", "")
            if isinstance(s, list):
                s = "".join(s)
            sources.append(s)
    if ANDREY_RAW.exists():
        sources.append(ANDREY_RAW.read_text(encoding="utf-8", errors="ignore"))
    for s in sources:
        # %%writefile main.py
        if "def agent" in s and ("%%writefile" in s or len(s) > 20000):
            text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", s)
            # strip packaging tails
            for marker in ("from kaggle_environments", "env.run(", "Path(\"main.py\")"):
                i = text.find(marker)
                if i > 5000:
                    text = text[:i]
            if "def agent" in text:
                out.write_text(text, encoding="utf-8")
                try:
                    try_load(out, "andrey_inline")
                    print("andrey OK inline", out.stat().st_size, flush=True)
                    return out
                except Exception as e:
                    print("andrey inline fail", e, flush=True)
        # payload blobs
        for pat, name in [
            (r"SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\)", "sb"),
            (r"payload\s*=\s*\(([\s\S]*?)\)\s*\n", "payload"),
            (r"b64decode\(\s*['\"]([A-Za-z0-9+/=]{100,})['\"]", "b64"),
        ]:
            if name == "sb" and "SOURCE_BYTES" in s:
                m = re.search(r"(SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\))", s)
                if m:
                    try:
                        ns = {}
                        exec(m.group(1), ns)
                        src = ns.get("SOURCE_BYTES")
                        if src and b"def agent" in src:
                            out.write_bytes(src)
                            try_load(out, "andrey_sb")
                            print("andrey OK SOURCE_BYTES", len(src), flush=True)
                            return out
                    except Exception as e:
                        print("andrey sb fail", e, flush=True)
            if "b85decode" in s or "zlib" in s:
                # collect quoted chunks after payload-ish assign
                parts = re.findall(r"['\"]([A-Za-z0-9+/=_-]{20,})['\"]", s[:80000])
                packed = "".join(parts)
                if len(packed) > 200:
                    for dec in (
                        lambda p: zlib.decompress(base64.b85decode(p)),
                        lambda p: zlib.decompress(base64.a85decode(p)),
                        lambda p: gzip.decompress(base64.b64decode(p)),
                    ):
                        try:
                            src = dec(packed)
                            if b"def agent" in src:
                                out.write_bytes(src)
                                try_load(out, "andrey_blob")
                                print("andrey OK blob", len(src), flush=True)
                                return out
                        except Exception:
                            continue
    # repair raw syntax: truncate at error and hope agent already defined
    if ANDREY_RAW.exists():
        raw = ANDREY_RAW.read_text(encoding="utf-8", errors="ignore")
        # decode unicode_escape if single-line mess
        if raw.count("\n") < 5 and "\\n" in raw:
            try:
                raw = raw.encode("utf-8").decode("unicode_escape")
            except Exception:
                pass
        # cut broken tail after last complete def agent block - try compile progressively
        for cut in (len(raw), len(raw) // 2, int(len(raw) * 0.7), int(len(raw) * 0.9)):
            cand = raw[:cut]
            # remove unterminated triple quotes at end
            if cand.count('"""') % 2 == 1:
                cand = cand.rsplit('"""', 1)[0] + "\n"
            if cand.count("'''") % 2 == 1:
                cand = cand.rsplit("'''", 1)[0] + "\n"
            if "def agent" not in cand:
                continue
            out.write_text(cand, encoding="utf-8")
            try:
                try_load(out, "andrey_repair")
                print("andrey OK repair cut", cut, out.stat().st_size, flush=True)
                return out
            except Exception as e:
                print("andrey repair fail", cut, e, flush=True)
    print("andrey EXTRACT FAIL", flush=True)
    return None


def series(path, name, opp_path, opp_name, seeds):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = try_load(path, f"c_{tag}")
                o = try_load(opp_path, f"o_{tag}")
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
                print(f"{name} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {name} {opp_name} s={seed} seat0={seat0}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": f"{type(e).__name__}:{e}"[:220]})
    sm = {
        "cand": name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def gate_candidate(src: Path, name: str, payload: dict, smoke_seeds=(1, 2, 3)):
    print(f"\n######## {name} ########", flush=True)
    print("path", src, "size", src.stat().st_size, "sha", sha256(src), flush=True)
    try:
        try_load(src, f"probe_{name}")
        print("LOAD OK", flush=True)
    except Exception as e:
        print("LOAD FAIL", e, flush=True)
        payload["results"].setdefault(name, {})["load_error"] = str(e)[:200]
        return False

    # fingerprint vs known lineages (1 seed smoke)
    for fp_name, fp_path in [
        ("fp_v43", KAITO43),
        ("fp_guru4", GURU4),
        ("fp_pipe16", PIPE16),
    ]:
        if fp_path.exists():
            r, sm = series(src, name, fp_path, fp_name, (1,))
            payload["results"].setdefault(name, {})[fp_name] = sm
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    panel = [
        ("metav4", METAV4, smoke_seeds),
        ("shop_v7", SHOPV7, smoke_seeds),
        ("thomas", THOMAS, (1, 2)),
        ("alperen", ALPEREN, (1,)),
    ]
    res = payload["results"].setdefault(name, {})
    for opp, path, seeds in panel:
        if not path.exists():
            continue
        key = f"vs_{opp}"
        if (res.get(key) or {}).get("n", 0) >= len(seeds) * 2:
            print("cached", key, res[key], flush=True)
            continue
        r, sm = series(src, name, path, opp, seeds)
        res[key] = {**sm, "rows": r}
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    wr_mv = (res.get("vs_metav4") or {}).get("win_rate") or 0
    wr_sp = (res.get("vs_shop_v7") or {}).get("win_rate") or 0
    slot_a = wr_mv >= 0.6 and wr_sp >= 0.5
    collapses = [k for k, v in res.items() if k.startswith("vs_") and (v.get("n") or 0) >= 4 and (v.get("wins") or 0) == 0]
    print(f"SLOT_A {name}: mv={wr_mv}({(res.get('vs_metav4') or {}).get('mean_margin')}) shop={wr_sp}({(res.get('vs_shop_v7') or {}).get('mean_margin')}) pass={slot_a} collapses={collapses}", flush=True)
    res["slot_a"] = slot_a
    res["collapses"] = collapses
    payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if slot_a:
        print("ESCALATE 8-seed holdout", flush=True)
        r2, s2 = series(src, name, METAV4, "metav4_h", (4, 5, 6, 7))
        r3, s3 = series(src, name, SHOPV7, "shop_h", (4, 5, 6, 7))
        res["hold_mv"] = s2
        res["hold_sp"] = s3
        res["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"HOLD {name}: mv={s2.get('win_rate')} shop={s3.get('win_rate')} dual={res['holdout_dual']}", flush=True)
        return bool(res["holdout_dual"])
    return False


def main():
    payload = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": "P92b counsel exact recheck v48 + breaking-the-tie; no submit",
        "results": {},
        "version_pull": "403 Forbidden on historical scriptVersionId; using local public_nb artifacts",
    }
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    # 1) Kaito v48
    if KAITO48.exists():
        print("v48 manifest sha expected dadee25a...", flush=True)
        print("v48 actual", sha256(KAITO48), flush=True)
        gate_candidate(KAITO48, "kaito_v48_fast_routes", payload, smoke_seeds=(1, 2, 3))
    else:
        print("MISSING kaito_v48", flush=True)

    # 2) Breaking the Tie
    andrey = extract_andrey()
    if andrey:
        gate_candidate(andrey, "andrey_breaking_tie", payload, smoke_seeds=(1, 2, 3))
    else:
        print("MISSING andrey extract", flush=True)

    print("\n==== P92b TABLE ====", flush=True)
    for k, v in payload["results"].items():
        if not isinstance(v, dict):
            continue
        print(k, "slot_a", v.get("slot_a"), "collapses", v.get("collapses"),
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              flush=True)


if __name__ == "__main__":
    main()
