# -*- coding: utf-8 -*-
"""P160: gate C05 (58k py) vs Metav4+shop. Target beat H3x +508."""
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
CAND = PROJ / "_external/scan_burst/c05/kaggriculture-c05-mid-herd-10.py"
OUTJSON = PROJ / "_research" / "p160_c05.json"


def series(opp: Path, seeds, label):
    wins = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = p79.load_quiet(CAND, f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp, f"o_{label}_{seed}_{int(seat0)}")
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
                print(f"FAIL {label} s={seed}: {str(e)[:150]}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    rec = {}
    for opp, seeds, key in (
        (METAV4, (1, 2, 3, 4), "metav4"),
        (SHOPV7, (1, 2, 3), "shop"),
    ):
        print(f"\n== C05 vs {key} ==", flush=True)
        rec[key] = series(opp, seeds, f"c05_{key}")
        print("SUM", key, rec[key], flush=True)
    dual = rec["metav4"].get("win_rate", 0) >= 0.6 and rec["shop"].get("win_rate", 0) >= 0.5
    rec["dual"] = "PASS" if dual else "FAIL"
    rec["beats_h3x"] = (rec["metav4"].get("mean_margin") or -1e9) > 508
    print("DUAL", rec["dual"], "beats_h3x", rec["beats_h3x"], flush=True)
    OUTJSON.write_text(json.dumps(rec, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
