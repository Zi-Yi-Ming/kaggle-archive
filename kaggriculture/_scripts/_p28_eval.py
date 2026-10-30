# -*- coding: utf-8 -*-
"""P28c: eval extracted policy vs R2 on NEW seeds 6-10, pinned harness."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from p26_harness import load_r2, load_pool, run_game  # noqa: E402


def main():
    finn = load_pool("fallow_finn")
    rows = []
    for seed in (6, 7, 8, 9, 10):
        # R2 reference
        r_r2 = run_game(load_r2(), finn, seed)
        # extracted policy
        import p28_extracted_policy as ext
        ext.reset()
        # ensure B backbone flags
        import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library, p18_selector
        p13_1_melon.set_enabled(False)
        p13_3_water.set_enabled(True)
        p14_1_on.set_enabled(True)
        p14_2_on.set_enabled(False)
        p16_branch.set_branch_mode("off")
        p17_1_library.set_enabled(False)
        p18_selector.set_selector("S0")
        r_ext = run_game(ext.agent, finn, seed)
        ratio = r_ext["bank0"] / r_r2["bank0"] if r_r2["bank0"] else 0
        rec = {
            "seed": seed,
            "r2_bank": r_r2["bank0"],
            "ext_bank": r_ext["bank0"],
            "ratio": ratio,
            "r2_hash": r_r2["hash0"],
            "ext_hash": r_ext["hash0"],
        }
        rows.append(rec)
        print(f"seed{seed}: R2={r_r2['bank0']:.0f} EXT={r_ext['bank0']:.0f} "
              f"ratio={ratio:.2%}", flush=True)

    out = ROOT / "p28_extracted_eval.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    ratios = [r["ratio"] for r in rows]
    print(f"\nmean ratio={sum(ratios)/len(ratios):.2%} "
          f"min={min(ratios):.2%} max={max(ratios):.2%}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
