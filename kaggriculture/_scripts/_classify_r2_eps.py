# -*- coding: utf-8 -*-
"""Classify R2 live episodes: win/loss and loss-mode structure."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "replays"
spec = importlib.util.spec_from_file_location("ar", str(ROOT / "_analyze_replays.py"))
ar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ar)


def classify(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [0, 0]
    try:
        me = teams.index("ZiYiMing")
    except ValueError:
        me = None
    if me is None:
        return None
    opp = 1 - me
    my_r = float(rewards[me])
    opp_r = float(rewards[opp])
    return {
        "file": path.name,
        "teams": teams,
        "me_seat": me,
        "opp": teams[opp] if opp < len(teams) else "?",
        "my_bank": my_r,
        "opp_bank": opp_r,
        "margin": my_r - opp_r,
        "win": my_r > opp_r,
        "tie": my_r == opp_r,
    }


def main():
    rows = []
    for f in sorted(REP.glob("episode-1080*-replay.json")):
        r = classify(f)
        if r:
            rows.append(r)
            flag = "WIN" if r["win"] else ("TIE" if r["tie"] else "LOSS")
            print(f"{flag:4s} {r['file']} seat={r['me_seat']} vs {r['opp']}: "
                  f"{r['my_bank']:.0f} vs {r['opp_bank']:.0f} m={r['margin']:+.0f}")
    wins = sum(1 for r in rows if r["win"])
    losses = sum(1 for r in rows if not r["win"] and not r["tie"])
    ties = sum(1 for r in rows if r["tie"])
    print(f"\nSUMMARY n={len(rows)} W-L-T={wins}-{losses}-{ties}")
    print("\n=== LOSSES detail ===")
    for r in rows:
        if r["win"] or r["tie"]:
            continue
        print("\n", r["file"], "vs", r["opp"], "margin", r["margin"])
        ar.analyze(REP / r["file"])


if __name__ == "__main__":
    main()
