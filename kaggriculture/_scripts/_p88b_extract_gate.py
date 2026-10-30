# -*- coding: utf-8 -*-
"""P88b extract new notebooks + dual-gate priority candidates."""
from __future__ import annotations

import base64
import gzip
import importlib.util
import json
import re
import sys
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
P85 = PROJ / "_external/scan_p85_new_0920"
OUTDIR = PROJ / "_external/scan_p88_new/extracted"
OUTJSON = PROJ / "_research/p88b_new_gates.json"
OUTDIR.mkdir(parents=True, exist_ok=True)


def cells_text(nb_path: Path) -> str:
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    out = []
    for c in nb.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        out.append(s)
    return "\n".join(out)


def extract_one(nb_path: Path) -> Path | None:
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", nb_path.stem)[:50]
    out = OUTDIR / f"{stem}.py"
    if out.exists() and out.stat().st_size > 8000:
        print("cached", out.name, out.stat().st_size)
        return out
    text = cells_text(nb_path)
    # 1) SOURCE_BYTES = b''.join((...))
    m = re.search(r"(SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\))", text)
    if m:
        try:
            ns = {}
            exec(m.group(1), ns)
            src = ns.get("SOURCE_BYTES")
            if src and b"def agent" in src:
                out.write_bytes(src)
                print("OK SOURCE_BYTES", out.name, len(src))
                return out
        except Exception as e:
            print("SOURCE_BYTES fail", nb_path.name, e)
    # 2) SOURCE_BLOB zlib b85
    if "SOURCE_BLOB" in text:
        region = text[text.find("SOURCE_BLOB"):]
        for stop in ("EXPECTED", "source_bytes", "MAIN =", "assert"):
            j = region.find(stop)
            if j > 30:
                region = region[:j]
        parts = re.findall(r"['\"]([A-Za-z0-9+/=]{30,})['\"]", region)
        packed = "".join(parts)
        for fn in (
            lambda p: zlib.decompress(base64.b85decode(p)),
            lambda p: zlib.decompress(base64.a85decode(p)),
            lambda p: gzip.decompress(base64.b64decode(p)),
        ):
            try:
                src = fn(packed)
                if b"def agent" in src:
                    out.write_bytes(src)
                    print("OK SOURCE_BLOB", out.name, len(src))
                    return out
            except Exception:
                continue
    # 3) AGENT_B64 / AGENT_GZ_B64 gzip+b64
    for key in ("AGENT_B64", "AGENT_GZ_B64", "AGENT_SOURCE"):
        if key not in text:
            continue
        idx = text.find(key)
        region = text[idx: idx + 500000]
        parts = re.findall(r"['\"]([A-Za-z0-9+/=]{40,})['\"]", region)
        packed = "".join(parts[:200])
        if len(packed) < 80:
            continue
        for fn in (
            lambda p: gzip.decompress(base64.b64decode(p)),
            lambda p: zlib.decompress(base64.b64decode(p)),
            lambda p: base64.b64decode(p),
        ):
            try:
                src = fn(packed)
                if b"def agent" in src:
                    out.write_bytes(src)
                    print("OK", key, out.name, len(src))
                    return out
            except Exception:
                continue
        # lzma b85
        m2 = re.search(r"b85decode\('([^']{50,})'\)", region)
        if m2 and "lzma" in region:
            try:
                import lzma

                src = lzma.decompress(base64.b85decode(m2.group(1)))
                if b"def agent" in src:
                    out.write_bytes(src)
                    print("OK lzma", out.name, len(src))
                    return out
            except Exception as e:
                print("lzma fail", e)
    # 4) inline def agent in notebook (rare)
    if re.search(r"(?m)^def agent\b", text) and "SOURCE_BYTES" not in text:
        code = text
        code = re.split(r"(?m)^(from kaggle_environments|env\.run\(|Path\([\"']main\.py)", code, maxsplit=1)[0]
        if "def agent" in code and len(code) > 3000:
            out.write_text(code, encoding="utf-8")
            print("OK inline", out.name, len(code))
            return out
    print("FAIL extract", nb_path.name)
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
        "errors": len(rows) - n,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    # extract all new notebooks + v51/v52
    targets = list(NEW.rglob("*.ipynb"))
    targets += list(P85.glob("**/*v51*.ipynb"))
    targets += list(P85.glob("**/*v52*.ipynb"))
    extracted = []
    for nb in targets:
        if "extracted" in str(nb):
            continue
        p = extract_one(nb)
        if p:
            extracted.append((p.stem[:40], p))
    # also already-extracted v51
    v51 = P85 / "extracted/ahmedberatozer__kaggriculture-v51-lean-flock.py"
    if v51.exists():
        # may still be notebook wrapper; try extract SOURCE_BYTES from it
        p = extract_one(v51) if v51.suffix == ".ipynb" else None
        if v51.stat().st_size > 50000 and b"def agent" in v51.read_bytes()[:200000] or (v51.exists() and "SOURCE_BYTES" in v51.read_text(encoding="utf-8", errors="ignore")[:5000]):
            try:
                text = v51.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r"(SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\))", text)
                if m:
                    ns = {}
                    exec(m.group(1), ns)
                    src = ns.get("SOURCE_BYTES")
                    if src:
                        out = OUTDIR / "ahmed_v51.py"
                        out.write_bytes(src)
                        extracted.append(("ahmed_v51", out))
                        print("OK ahmed_v51 from extracted wrapper", len(src))
            except Exception as e:
                print("v51 reextract fail", e)
        if "def agent" in v51.read_text(encoding="utf-8", errors="ignore") and v51.stat().st_size > 100000:
            extracted.append(("ahmed_v51_raw", v51))

    print("\nEXTRACTED:", flush=True)
    for n, p in extracted:
        print(f"  {n}: {p} {p.stat().st_size if p.exists() else 0}", flush=True)

    # priority order
    priority_names = [
        "2965", "2950", "master-engine-v4", "master_engine_v4", "one-more-wheat",
        "a1-t31", "beat-v48", "visible-price", "demand-preserving", "countering",
        "demystifying", "ahmed_v51", "ahmed_v52", "lean-flock",
    ]

    def score(item):
        n, p = item
        for i, key in enumerate(priority_names):
            if key.lower() in n.lower() or key.lower() in p.name.lower():
                return i
        return 99

    extracted = sorted(extracted, key=score)
    payload = {"results": {}, "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    seeds = (1, 2)
    for name, path in extracted:
        if not path.exists() or path.stat().st_size < 5000:
            print("SKIP small", name, flush=True)
            continue
        prev = payload["results"].get(name) or {}
        if (prev.get("vs_metav4") or {}).get("n", 0) >= 4:
            print("SKIP done", name, prev.get("vs_metav4"), flush=True)
            continue
        print(f"\n===== {name} =====", flush=True)
        r_mv, s_mv = series(path, name, METAV4, "metav4", seeds)
        r_sp, s_sp = series(path, name, SHOPV7, "shop_v7", seeds)
        r_th, s_th = series(path, name, THOMAS, "thomas", (1,))
        prev.update({"path": str(path), "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
                     "rows": r_mv + r_sp + r_th})
        payload["results"][name] = prev
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
            prev["hold_mv"] = s2
            prev["hold_sp"] = s3
            prev["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            payload["results"][name] = prev
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"HOLD {name}: mv={s2.get('win_rate')} shop={s3.get('win_rate')} dual={prev['holdout_dual']}", flush=True)

    print("\n==== P88b TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "th", (v.get("vs_thomas") or {}).get("win_rate"), "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
