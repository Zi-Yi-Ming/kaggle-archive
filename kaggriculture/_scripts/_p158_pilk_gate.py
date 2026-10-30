# -*- coding: utf-8 -*-
"""P158: gate pilk upstream + hamburger candidates."""
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
EX = PROJ / "_external/scan_burst/extracted"
OUTJSON = PROJ / "_research" / "p158_pilk.json"


def series(cand: Path, opp: Path, seeds, label):
    wins = 0
    margins = []
    for seed in seeds:
        try:
            c = p79.load_quiet(cand, f"c_{label}_{seed}")
            o = p79.load_quiet(opp, f"o_{label}_{seed}")
            b0, b1, stt, sec = p79.run(c, o, seed)
            margin = b0 - b1
            win = b0 > b1
            wins += int(win)
            margins.append(margin)
            print(f"  {label} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
        except Exception as e:
            print(f"  FAIL {label} s={seed}: {str(e)[:150]}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    payload = {}
    for tag, path in (
        ("pilk_upstream", EX / "pilk_upstream.py"),
    ):
        if not path.exists():
            print("missing", path, flush=True)
            continue
        print(f"\n==== {tag} ====", flush=True)
        mv = series(path, METAV4, (1, 2, 3), f"{tag}_mv")
        sh = series(path, SHOPV7, (1, 2), f"{tag}_sh")
        payload[tag] = {"mv": mv, "sh": sh}
        print(f"DUAL mv={mv} sh={sh} beats_h3x={(mv.get('mean_margin') or -1e9) > 508}", flush=True)
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
