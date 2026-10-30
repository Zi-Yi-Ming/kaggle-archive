# -*- coding: utf-8 -*-
"""Extract elite sell schedules at key steps vs R2 tape0."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
P = ROOT / "_external" / "public_data" / "ashok_top10" / "replays_2026-08-03.parquet"

# load R2 tape
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("medal", str(ROOT / "_push_medal" / "main.py"))
medal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(medal)
tape0 = medal._INLINE_TAPES[0]

KEY_STEPS = [597, 619, 649, 669, 670, 671, 672, 673, 709, 712, 713, 716, 717]


def sells_at(tape, step):
    if step >= len(tape):
        return []
    return [(o[1], int(o[2] or 0)) for o in (tape[step].get("market") or []) if o and o[0] == "SELL" and len(o) >= 3]


def main():
    print("=== R2 tape0 key-step sells ===")
    for st in KEY_STEPS:
        print(f"  step{st} d{st//24}h{st%24}: {sells_at(tape0, st)}")

    df = pd.read_parquet(P)
    # aggregate winner sell qty by step for elite
    win_qty = defaultdict(Counter)
    lose_qty = defaultdict(Counter)
    n = 0
    for i in range(len(df)):
        try:
            data = json.loads(df.iloc[i]["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            r0, r1 = float(rew[0]), float(rew[1])
        except Exception:
            continue
        if min(r0, r1) < 100000:
            continue
        w = 0 if r0 >= r1 else 1
        l = 1 - w
        steps = data.get("steps") or []
        for step in KEY_STEPS:
            if step >= len(steps):
                continue
            for p, bucket in ((w, win_qty), (l, lose_qty)):
                rec = steps[step][p] if p < len(steps[step]) else {}
                action = rec.get("action") or {}
                for o in action.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3:
                        q = int(o[2] or 0)
                        if q > 0:
                            bucket[step][o[1]] += q
        n += 1
    print(f"\nelite n={n}")
    print("\n=== elite winner vs loser mean sell qty (per game) at key steps ===")
    for st in KEY_STEPS:
        wtot = win_qty[st]
        ltot = lose_qty[st]
        items = set(wtot) | set(ltot)
        if not items:
            continue
        wtop = ", ".join(f"{k}:{wtot[k]/max(1,n):.1f}" for k, _ in wtot.most_common(6))
        ltop = ", ".join(f"{k}:{ltot[k]/max(1,n):.1f}" for k, _ in ltot.most_common(6))
        print(f"  step{st} d{st//24}h{st%24}")
        print(f"    WIN  {wtop}")
        print(f"    LOSE {ltop}")


if __name__ == "__main__":
    main()
