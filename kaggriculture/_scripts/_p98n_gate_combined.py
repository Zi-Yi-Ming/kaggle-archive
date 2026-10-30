# -*- coding: utf-8 -*-
"""Quick dual-gate for v54leak combined only (smoke shop + metav4)."""
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
CAND = PROJ / "_external/scan_p98_new/extracted/v54leak_combined_main.py"
OUT = PROJ / "_research/p98_v54leak_combined.json"


def series(cand_path, opp_path, seeds=(1, 2, 3, 4)):
    wins = 0
    margins = []
    rows = []
    for seed in seeds:
        c = p79.load_quiet(cand_path, f"c_{seed}")
        o = p79.load_quiet(opp_path, f"o_{seed}")
        b0, b1, st, sec = p79.run(c, o, seed)
        margin = b0 - b1
        win = b0 > b1
        wins += int(win)
        margins.append(margin)
        rows.append({"seed": seed, "cand": b0, "opp": b1, "margin": margin, "win": win, "sec": sec})
        print(f"seed={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
    n = len(rows)
    return rows, {"n": n, "wins": wins, "win_rate": wins / n, "mean_margin": sum(margins) / n}


def main():
    payload = {}
    print("== vs shopv7 (smoke 2 seeds) ==", flush=True)
    rows, sm = series(CAND, SHOPV7, seeds=(1, 2))
    payload["shop_smoke"] = {"rows": rows, "summary": sm}
    print("shop", sm, flush=True)
    if sm["win_rate"] == 0 and sm["mean_margin"] < -5000:
        print("SHOP COLLAPSE — dual gate FAIL, skip expand", flush=True)
        payload["verdict"] = "NO shop collapse"
    else:
        print("== vs metav4 ==", flush=True)
        rows, sm = series(CAND, METAV4, seeds=(1, 2, 3, 4))
        payload["metav4"] = {"rows": rows, "summary": sm}
        print("metav4", sm, flush=True)
        payload["verdict"] = "dual pending"
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUT, "verdict", payload.get("verdict"), flush=True)


if __name__ == "__main__":
    main()
