# -*- coding: utf-8 -*-
"""P152: dual-gate hy2965 NOW. If PASS and better than H3x, package."""
from __future__ import annotations

import importlib.util
import json
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
CAND = PROJ / "_external/scan_final/extracted/hy2965_main.py"
OUTJSON = PROJ / "_research" / "p152_2965.json"


def series(opp_path, seeds, label):
    wins = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = p79.load_quiet(CAND, f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp_path, f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, stt, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, stt, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    rec = {}
    for opp, seeds, key in (
        (METAV4, (1, 2, 3, 4), "metav4"),
        (SHOPV7, (1, 2, 3), "shop"),
        (THOMAS, (1, 2), "thomas"),
    ):
        print(f"\n== 2965 vs {key} ==", flush=True)
        rec[key] = series(opp, seeds, f"2965_{key}")
        print("SUM", key, rec[key], flush=True)
    dual = rec["metav4"].get("win_rate", 0) >= 0.6 and rec["shop"].get("win_rate", 0) >= 0.5
    rec["dual"] = "PASS" if dual else "FAIL"
    print("DUAL", rec["dual"], "H3x=+508", flush=True)
    OUTJSON.write_text(json.dumps(rec, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
