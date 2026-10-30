# -*- coding: utf-8 -*-
"""P16: compress R2/B day traces into skeleton milestones (not a tape)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")


def main():
    tl = list(csv.DictReader((ROOT / "p14_r2_production_timeline.csv").open(encoding="utf-8")))
    r2 = [r for r in tl if r["label"] == "R2"]
    # milestone days: 1,5,7,10 (stable across seeds from prior read)
    milestones = []
    for day in (0, 1, 5, 7, 10):
        rows = [r for r in r2 if int(r["day"]) == day]
        if not rows:
            continue
        def m(k):
            v = [float(r[k]) for r in rows if r.get(k) not in ("", None)]
            return sum(v) / len(v) if v else 0
        milestones.append({
            "phase_guess": (
                "SETUP" if day <= 2 else
                "GROW" if day <= 9 else
                "CASH_WINDOW"
            ),
            "day": day,
            "money": m("money"),
            "hands": m("hands"),
            "n_land": m("n_land"),
            "structs": m("structs"),
            "animals": m("animals"),
            "WHEAT": m("WHEAT"),
            "MELON": m("MELON"),
            "STRAWBERRY": m("STRAWBERRY"),
            "empty": m("empty"),
        })
        print(f"d{day}: {milestones[-1]}")

    # compressed skeleton (intent level, not per-step)
    skeleton = [
        ("S0_SETUP", 0, 2, "hire daily; plant short WHEAT + long MELON; buy 2C+2S",
         "money~3000→100; melon_tiles~12; animals~4"),
        ("S1_GROW", 3, 9, "water/care; add STRAW mid-horizon; scale animals; land2",
         "money~200-2000; animals~8-12; straw~12-20"),
        ("S2_CASH_WINDOW", 10, 15, "harvest long crops; sell; continue livestock",
         "money inflection; melon revenue"),
        ("S3_SCALE", 16, 25, "livestock products; more land/crops",
         "milk/wool/fert revenue"),
        ("S4_TERMINAL", 26, 29, "liquidate inventory; stop expansion",
         "final bank"),
    ]
    out = ROOT / "p16_skeletons.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["phase", "day_start", "day_end", "strategic_intent", "expected_state"])
        for row in skeleton:
            w.writerow(list(row))
    print("wrote", out.name)

    out2 = ROOT / "p16_branch_points.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["branch_id", "day", "trigger", "base_continuation", "branch_continuation",
                    "evidence", "priority"])
        w.writerow([
            "B_CASH_WINDOW_FAIL", 10,
            "money < 400 AND field_melon == 0 AND shed_melon == 0",
            "continue GROW/CASH_WINDOW portfolio",
            "FORCE_CONVERT: sell_all products; no new long seeds; prioritize animal/wheat cash",
            "P13: melon death => no d10 cash; P11: hands=0 spiral",
            1,
        ])
        w.writerow([
            "B_CASH_WINDOW_STUCK", 10,
            "money < 1500 AND (field_melon > 0 OR shed_melon > 0)",
            "hold for later premium",
            "FORCE_SELL_MELON: list melon now at market",
            "P13 ledger: d10 melon sale is the cash engine",
            2,
        ])
        w.writerow([
            "B_ANIMAL_STARVED", 12,
            "animals == 0 AND money > 800",
            "crop-only path",
            "buy bootstrap 2C+2S if cash allows",
            "P14.2: livestock EV positive with feed",
            3,
        ])
    print("wrote", out2.name)

    # B vs R2 first divergence already known
    out3 = ROOT / "p16_branch_triggers.csv"
    with open(out3, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["trigger_id", "observable", "threshold", "when", "action"])
        w.writerow(["T_MELON_MISSING", "count tiles crop==MELON", "==0", "day>=10", "FAIL_WINDOW"])
        w.writerow(["T_CASH_LOW", "farm.money", "<400", "day>=10", "FAIL_WINDOW"])
        w.writerow(["T_MELON_STUCK", "shed.MELON + field melon yield", ">0 and money<1500", "day>=10", "FORCE_SELL"])
    print("wrote", out3.name)


if __name__ == "__main__":
    main()
