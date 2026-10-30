# -*- coding: utf-8 -*-
"""Classify v66 live episodes."""
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
    }


def main():
    # v66 overnight episode ids
    ids = [
        "108042085", "108016182", "108010215", "107987215",
        "107966468", "107965620", "107947265", "107939188",
        "107926208", "107917555",
    ]
    rows = []
    for eid in ids:
        p = REP / f"episode-{eid}-replay.json"
        if not p.exists():
            print("missing", p.name)
            continue
        r = classify(p)
        if not r:
            print("no ZiYiMing", p.name)
            continue
        rows.append(r)
        flag = "WIN" if r["win"] else "LOSS"
        print(f"{flag:4s} {p.name} seat={r['me_seat']} vs {r['opp']}: "
              f"{r['my_bank']:.0f} vs {r['opp_bank']:.0f} m={r['margin']:+.0f}")
    wins = sum(1 for r in rows if r["win"])
    print(f"\nSUMMARY n={len(rows)} W-L={wins}-{len(rows)-wins}")
    for r in rows:
        if r["win"]:
            continue
        print("\n--- LOSS", r["opp"], r["margin"])
        ar.analyze(REP / r["file"])


if __name__ == "__main__":
    main()
