# -*- coding: utf-8 -*-
"""P112: diff gold WIN vs LOSE tapes to find the adaptive edge."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")
GOLD = "吃白饭的大肥鱼"

meta = json.loads((OUT / "gold_meta.json").read_text(encoding="utf-8"))
idx = {}
for row in meta:
    for a in row.get("agents") or []:
        if a.get("teamName") == GOLD:
            idx[row["episode_id"]] = int(a.get("index") or 0)

wins, losses = [], []
for p in sorted((OUT / "gold").glob("episode-*-replay.json")):
    eid = int(p.name.split("-")[1])
    if eid not in idx:
        continue
    ai = idx[eid]
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    scores = data.get("rewards") or [0, 0]
    win = scores[ai] > scores[1 - ai]
    tape = []
    for st in data.get("steps") or []:
        act = st[ai].get("action") or {}
        tape.append({
            "m": [tuple(o) if isinstance(o, list) else o for o in (act.get("market") or [])],
            "f": tuple(act.get("farmer") or []),
        })
    rec = {"file": p.name, "eid": eid, "win": win, "score": scores[ai], "opp": scores[1 - ai], "tape": tape}
    (wins if win else losses).append(rec)
    print(p.name, "win" if win else "LOSE", scores, flush=True)

print(f"\nwins={len(wins)} losses={len(losses)}", flush=True)


def sell_profile(rec):
    per_day = Counter()
    for si, t in enumerate(rec["tape"]):
        for o in t["m"]:
            if o and o[0] == "SELL":
                per_day[si // 24] += int(o[2] if len(o) > 2 else 1)
    return per_day


print("\n=== WIN sell-by-day (mean) ===", flush=True)
if wins:
    days = range(30)
    for d in days:
        vals = [sell_profile(w)[d] for w in wins]
        print(f"  d{d}: {sum(vals)/len(vals):.1f}", flush=True)

print("\n=== LOSE sell-by-day (mean) ===", flush=True)
if losses:
    for d in range(30):
        vals = [sell_profile(w)[d] for w in losses]
        print(f"  d{d}: {sum(vals)/len(vals):.1f}", flush=True)

# find steps where winner and loser diverge in market significantly
if wins and losses:
    print("\n=== first 30 market divergences win vs lose ===", flush=True)
    w, l = wins[0], losses[0]
    n = min(len(w["tape"]), len(l["tape"]))
    shown = 0
    for i in range(n):
        wm = sorted(w["tape"][i]["m"])
        lm = sorted(l["tape"][i]["m"])
        if wm != lm and (wm or lm):
            print(f"  s{i} d{i//24} h{i%24} WIN={wm} LOSE={lm}", flush=True)
            shown += 1
            if shown >= 30:
                break

(RESEARCH / "p112_win_vs_lose.json").write_text(json.dumps({
    "wins": [{"file": w["file"], "score": w["score"]} for w in wins],
    "losses": [{"file": l["file"], "score": l["score"]} for l in losses],
}, indent=2), encoding="utf-8")
print("WROTE p112_win_vs_lose.json", flush=True)
