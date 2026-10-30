# -*- coding: utf-8 -*-
"""Gate guru_master_v4 + extract/gate beat_v48; dual-gate vs Metav4 + shop_v7."""
from __future__ import annotations

import base64
import gzip
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
CLEAN = PROJ / "_external/scan_p88_new/extracted_clean"
OUTJSON = PROJ / "_research/p88e_guru_beat.json"


def extract_beat():
    p2 = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p88_new\beat-v48-100-0-your-herd-is-decided-on-day-6\beat-v48-100-0-your-herd-is-decided-on-day-6.ipynb")
    out = CLEAN / "beat_v48.py"
    if out.exists() and out.stat().st_size > 20000:
        return out
    nb = json.loads(p2.read_text(encoding="utf-8", errors="ignore"))
    for c in nb["cells"]:
        if c.get("cell_type") != "code":
            continue
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if "PAYLOAD" not in s:
            continue
        m = re.search(r"PAYLOAD\s*=\s*\"([^\"]+)\"", s)
        if not m:
            m = re.search(r"PAYLOAD\s*=\s*'([^']+)'", s)
        if not m:
            print("still no PAYLOAD")
            continue
        packed = m.group(1)
        print("PAYLOAD len", len(packed))
        for name, fn in [
            ("b85z", lambda x: zlib.decompress(base64.b85decode(x))),
            ("a85z", lambda x: zlib.decompress(base64.a85decode(x))),
            ("b64g", lambda x: gzip.decompress(base64.b64decode(x))),
        ]:
            try:
                src = fn(packed)
                print(name, "ok", len(src), b"def agent" in src)
                if b"def agent" in src:
                    out.write_bytes(src)
                    print("WROTE", out, len(src))
                    return out
            except Exception as e:
                print(name, "fail", e)
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


def gate(path, name, payload):
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
    return dual


def main():
    payload = {"results": {}, "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    guru = CLEAN / "guru_master_v4.py"
    if guru.exists() and guru.stat().st_size > 20000:
        gate(guru, "guru_master_v4", payload)
    else:
        print("no guru", guru, flush=True)

    beat = extract_beat()
    if beat and beat.exists():
        gate(beat, "beat_v48", payload)
    else:
        print("no beat_v48", flush=True)

    print("\n==== P88e TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "th", (v.get("vs_thomas") or {}).get("win_rate"), "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
