# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import json
import re
import zlib
from pathlib import Path

import importlib.util

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
OUTDIR = PROJ / "_external/scan_p93_reopen/extracted2"
OUTDIR.mkdir(parents=True, exist_ok=True)


def show_and_extract(nb_path: Path, keys=("SOURCE_BLOB", "SOURCE", "PAYLOAD", "EXPECTED", "SUBMISSION")):
    nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    print("====", nb_path.name)
    for i, c in enumerate(nb.get("cells", [])):
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if len(s) < 5000:
            continue
        print(f" cell{i} len={len(s)}")
        print("  head:", repr(s[:300]))
        for k in keys:
            j = s.find(k)
            if j >= 0:
                print(f"  {k} at {j}:", repr(s[j:j+200]))
        # try decode SOURCE_BLOB join with various quote forms
        if "SOURCE_BLOB" in s:
            region = s[s.find("SOURCE_BLOB") : s.find("SOURCE_BLOB") + 500000]
            # stop at next major assign
            m = re.search(r"SOURCE_BLOB\s*=\s*(.+?)(?:\nEXPECTED|\nassert|\nMAIN\s*=|\nsource_bytes|\nsource\s*=)", region, re.S)
            assign = m.group(1) if m else region[:200000]
            print("  assign head", repr(assign[:150]), "len", len(assign))
            parts = re.findall(r"b?[\"']([^\"']{10,})[\"']", assign)
            print("  parts", len(parts), "joined", sum(len(p) for p in parts))
            packed = "".join(parts)
            for name, fn in [
                ("b85z", lambda p: zlib.decompress(base64.b85decode(p))),
                ("a85z", lambda p: zlib.decompress(base64.a85decode(p))),
                ("b64z", lambda p: zlib.decompress(base64.b64decode(p))),
                ("b64g", lambda p: gzip.decompress(base64.b64decode(p))),
                ("b85", lambda p: base64.b85decode(p)),
            ]:
                try:
                    src = fn(packed)
                    print(" ", name, "ok", len(src), b"def agent" in src)
                    if b"def agent" in src:
                        out = OUTDIR / (nb_path.stem[:40] + ".py")
                        out.write_bytes(src)
                        print("  WROTE", out, hashlib.sha256(src).hexdigest())
                        return True
                except Exception as e:
                    print(" ", name, "fail", type(e).__name__)
        # farmer john / idle: SOURCE = '...' after EXPECTED sha
        if "SOURCE" in s and len(s) > 50000:
            m = re.search(r"SOURCE\s*=\s*[\"']([A-Za-z0-9+/=_-]{100,})[\"']", s)
            if m:
                print("  SOURCE str len", len(m.group(1)))
                packed = m.group(1)
                for name, fn in [
                    ("b85z", lambda p: zlib.decompress(base64.b85decode(p))),
                    ("b64z", lambda p: zlib.decompress(base64.b64decode(p))),
                    ("b64g", lambda p: gzip.decompress(base64.b64decode(p))),
                ]:
                    try:
                        src = fn(packed)
                        print(" ", name, len(src), b"def agent" in src)
                        if b"def agent" in src:
                            out = OUTDIR / (nb_path.stem[:40] + ".py")
                            out.write_bytes(src)
                            print("  WROTE", out)
                            return True
                    except Exception as e:
                        print(" ", name, e)
            # multi-quoted after SOURCE =
            idx = s.find("SOURCE")
            if idx > 0:
                region = s[idx : idx + 300000]
                parts = re.findall(r"[\"']([A-Za-z0-9+/=_-]{40,})[\"']", region)
                print("  SOURCE-region parts", len(parts), "len", sum(map(len, parts)))
                packed = "".join(parts)
                for name, fn in [
                    ("b85z", lambda p: zlib.decompress(base64.b85decode(p))),
                    ("b64z", lambda p: zlib.decompress(base64.b64decode(p))),
                    ("b64g", lambda p: gzip.decompress(base64.b64decode(p))),
                ]:
                    try:
                        src = fn(packed)
                        print(" ", name, len(src), b"def agent" in src)
                        if b"def agent" in src:
                            out = OUTDIR / (nb_path.stem[:40] + ".py")
                            out.write_bytes(src)
                            print("  WROTE", out)
                            return True
                    except Exception as e:
                        print(" ", name, type(e).__name__)
        # god-s-mode / idle-workers: just collect all long quoted tokens in largest cell
        if len(s) > 200000:
            parts = re.findall(r"[\"']([A-Za-z0-9+/=_-]{50,})[\"']", s)
            print("  bigcell parts", len(parts), "len", sum(map(len, parts)))
            packed = "".join(parts)
            if packed:
                for name, fn in [
                    ("b85z", lambda p: zlib.decompress(base64.b85decode(p))),
                    ("b64g", lambda p: gzip.decompress(base64.b64decode(p))),
                    ("b64z", lambda p: zlib.decompress(base64.b64decode(p))),
                ]:
                    try:
                        src = fn(packed)
                        print(" ", name, len(src), b"def agent" in src)
                        if b"def agent" in src:
                            out = OUTDIR / (nb_path.stem[:40] + ".py")
                            out.write_bytes(src)
                            print("  WROTE", out)
                            return True
                    except Exception as e:
                        print(" ", name, type(e).__name__, e)
        # farmcraft SUBMISSION_SOURCE
        if "SUBMISSION_SOURCE" in s:
            m = re.search(r"SUBMISSION_SOURCE\s*=\s*(?:r)?[\"']{3}([\s\S]+?)[\"']{3}", s)
            if m:
                src = m.group(1)
                print("  SUBMISSION_SOURCE len", len(src), "def agent", "def agent" in src)
                if "def agent" in src:
                    out = OUTDIR / (nb_path.stem[:40] + ".py")
                    out.write_text(src, encoding="utf-8")
                    print("  WROTE", out)
                    return True
    return False


def main():
    base = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p93_reopen")
    ok = []
    for nb in sorted(base.rglob("*.ipynb")):
        if "extracted" in str(nb):
            continue
        if show_and_extract(nb):
            ok.append(nb.name)
    print("OK", ok)
    # load test + gate V54 first if present
    METAV4 = PROJ / "_push_metav4_v13" / "main.py"
    SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
    THOMAS = PROJ / "_push_thomas_2945" / "main.py"
    OUTJSON = PROJ / "_research/p93_reopen_gates.json"
    payload = {"results": {}, "note": "P93c"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})
    for py in sorted(OUTDIR.glob("*.py")):
        name = py.stem[:40]
        try:
            p79.load_quiet(py, f"probe_{name}")
            print("LOAD OK", name)
        except Exception as e:
            print("LOAD FAIL", name, e)
            continue

        def series(opp_path, opp_name, seeds=(1, 2)):
            wins = n = 0
            margins = []
            for seed in seeds:
                for seat0 in (True, False):
                    tag = f"{name}_{opp_name}_{seed}_{int(seat0)}"
                    try:
                        c = p79.load_quiet(py, f"c_{tag}")
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
                        print(f"FAIL {name} {opp_name} s={seed}: {e}", flush=True)
            sm = {"n": n, "wins": wins, "win_rate": round(wins / n, 3) if n else None,
                  "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
            print("SUM", name, opp_name, sm, flush=True)
            return sm

        if (payload["results"].get(name) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            continue
        s_mv = series(METAV4, "metav4")
        s_sp = series(SHOPV7, "shop_v7")
        s_th = series(THOMAS, "thomas", (1,))
        payload["results"][name] = {"vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th, "path": str(py)}
        dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
        print(f"DUAL {name}: mv={s_mv} shop={s_sp} dual={dual}")
        payload["results"][name]["dual"] = dual
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("TABLE")
    for k, v in payload["results"].items():
        print(k, v.get("vs_metav4"), v.get("vs_shop_v7"), "dual", v.get("dual"))


if __name__ == "__main__":
    main()
