# -*- coding: utf-8 -*-
"""P96 local dual-gate: dmitrii lb-2700 + goodpjw melon2749 + retry extracts."""
from __future__ import annotations

import importlib.util
import json
import time
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
OUTJSON = PROJ / "_research/p96_local_gates.json"

CANDS = [
    (
        "dmitrii_herd_lb2700",
        PROJ / "_external/scan_p84_vs_metav4/extracted/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700.py",
    ),
    (
        "dmitrii_herd_p77",
        PROJ / "_external/scan_p77/extracted/dmitriigluzdov__kaggriculture-herd-safe-sale-win.py",
    ),
    (
        "goodpjw_melon2749",
        PROJ / "_external/scan_20260919/extracted/goodpjw_melon2749_clean.py",
    ),
    (
        "goodpjw_melon2749_raw",
        PROJ / "_external/scan_20260919/extracted/goodpjw_melon2749.py",
    ),
    (
        "goodpjw_p75",
        PROJ / "_external/scan_p75_mass/extracted/goodpjw2008__kaggriculture-melon-thresho.py",
    ),
]


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
    sm = {"cand": name, "opp": opp_name, "n": n, "wins": wins,
          "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm, rows


def main():
    payload = {"results": {}, "note": "P96 local; no auto-submit", "updated": ""}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    for name, path in CANDS:
        if not path.exists():
            print("MISSING", name, path, flush=True)
            continue
        if (payload["results"].get(name) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            print("cached", name, flush=True)
            continue
        print(f"\n===== {name} {path.stat().st_size} =====", flush=True)
        try:
            p79.load_quiet(path, f"probe_{name}")
            print("LOAD OK", flush=True)
        except Exception as e:
            print("LOAD FAIL", e, flush=True)
            payload["results"][name] = {"path": str(path), "load_error": str(e)[:200]}
            continue
        s_mv, r_mv = series(path, name, METAV4, "metav4", (1, 2))
        s_sp, r_sp = series(path, name, SHOPV7, "shop_v7", (1, 2))
        s_th, r_th = series(path, name, THOMAS, "thomas", (1,))
        dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
        payload["results"][name] = {
            "path": str(path), "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "dual": dual, "rows": r_mv + r_sp + r_th,
        }
        print(f"DUAL {name}: mv={s_mv.get('win_rate')}({s_mv.get('mean_margin')}) shop={s_sp.get('win_rate')}({s_sp.get('mean_margin')}) dual={dual}", flush=True)
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P96 TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "dual", v.get("dual"), flush=True)


if __name__ == "__main__":
    main()
