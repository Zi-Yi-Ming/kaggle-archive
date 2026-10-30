# -*- coding: utf-8 -*-
"""Local R2 tape endgame inspector: what does the tape sell on d27-29?"""
from __future__ import annotations

import importlib.util
import os
import sys
from collections import Counter, defaultdict

ROOT = r"D:\桌面\Kaggle\kaggriculture"
sys.path.insert(0, ROOT)

# load medal module without running a game
spec = importlib.util.spec_from_file_location("medal", os.path.join(ROOT, "_push_medal", "main.py"))
medal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(medal)

tapes = medal._INLINE_TAPES
print("n_tapes", len(tapes), "len0", len(tapes[0]) if tapes else None)

# For each tape, summarize market SELLs on last 3 days
for ti, tape in enumerate(tapes):
    by_day = defaultdict(Counter)
    for step in range(672, 719):  # d28-29
        if step >= len(tape):
            continue
        day = step // 24
        for o in tape[step].get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3:
                by_day[day][o[1]] += int(o[2] or 0)
    print(f"\n=== tape {ti} d28-29 sells ===")
    for day in sorted(by_day):
        print(f"  d{day}:", dict(by_day[day]))

# Also count how often FERT/WHEAT appear in advance_sales exclusion
print("\nadvance_sales skips:", "WHEAT, FERTILIZER")
print("LAST_STEP liquidate only at", medal.LAST_STEP)
