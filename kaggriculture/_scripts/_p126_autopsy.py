# -*- coding: utf-8 -*-
"""P126: H3 live losses autopsy + gold sell triggers vs price path."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")

h3_meta = json.loads((OUT / "h3_meta.json").read_text(encoding="utf-8"))
print("=== H3 LIVE ===", flush=True)
losses = []
for row in h3_meta:
    agents = row.get("agents") or []
    us = next((a for a in agents if a.get("teamName") == "ZiYiMing"), None)
    them = next((a for a in agents if a.get("teamName") != "ZiYiMing"), None)
    if not us or not them:
        continue
    win = float(us.get("reward") or 0) > float(them.get("reward") or 0)
    gap = float(us.get("reward") or 0) - float(them.get("reward") or 0)
    rec = {"win": win, "gap": gap, "opp": them.get("teamName"), "our": us.get("reward"), "their": them.get("reward")}
    if not win:
        losses.append(rec)
    print(f"  {'W' if win else 'L'} {rec['our']}:{rec['their']} gap={gap:.0f} vs {rec['opp']}", flush=True)

losses.sort(key=lambda r: r["gap"])
print("\nWORST:", flush=True)
for r in losses[:6]:
    print(f"  gap={r['gap']:.0f} vs {r['opp']}", flush=True)

GOLD = "吃白饭的大肥鱼"
meta = json.loads((OUT / "gold_meta.json").read_text(encoding="utf-8"))
idx = {}
for row in meta:
    for a in row.get("agents") or []:
        if a.get("teamName") == GOLD:
            idx[row["episode_id"]] = int(a.get("index") or 0)

sell_ctx = []
for p in sorted((OUT / "gold").glob("episode-*-replay.json"))[:5]:
    eid = int(p.name.split("-")[1])
    ai = idx.get(eid, 0)
    data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    day_px = defaultdict(lambda: defaultdict(list))
    for si, st in enumerate(data.get("steps") or []):
        ag = st[ai]
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        px = ((obs.get("market") or {}).get("prices") or {})
        day, hour = si // 24, si % 24
        for item, v in px.items():
            day_px[day][item].append(float(v or 0))
        for o in act.get("market") or []:
            if isinstance(o, (list, tuple)) and o and o[0] == "SELL" and len(o) >= 3:
                item, q = o[1], int(o[2] or 0)
                pnow = float(px.get(item) or 0)
                hist = day_px[day][item]
                pmax = max(hist) if hist else pnow
                pmin = min(hist) if hist else pnow
                sell_ctx.append({
                    "day": day, "hour": hour, "item": item, "q": q, "p": pnow,
                    "rel": (pnow - pmin) / (pmax - pmin + 1e-9),
                })

print(f"\nGOLD SELLS n={len(sell_ctx)}", flush=True)
buckets = Counter()
for s in sell_ctx:
    buckets[round(s["rel"] * 4) / 4] += 1
for b in sorted(buckets):
    print(f"  rel={b:.2f}: {buckets[b]}", flush=True)

by_h = defaultdict(list)
for s in sell_ctx:
    by_h[s["hour"]].append(s["rel"])
print("\nmean rel by hour:", flush=True)
for h in sorted(by_h):
    vals = by_h[h]
    print(f"  h{h:02d}: n={len(vals):3d} mean={sum(vals)/len(vals):.2f}", flush=True)

(RESEARCH / "p126_autopsy_sell_trigger.json").write_text(json.dumps({
    "losses": losses, "n_sells": len(sell_ctx),
    "rel": {str(k): v for k, v in buckets.items()},
}, indent=2, ensure_ascii=False), encoding="utf-8")
print("WROTE", flush=True)
