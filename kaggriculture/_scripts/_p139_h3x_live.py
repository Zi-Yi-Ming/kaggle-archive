# -*- coding: utf-8 -*-
"""P139: pull H3x live episodes — who do we lose to?"""
from __future__ import annotations

import json
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p139_h3x_live")
OUT.mkdir(parents=True, exist_ok=True)
H3X_SUB = 56488134


def main():
    api = KaggleApi()
    api.authenticate()
    eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=H3X_SUB)]
    eps = [e for e in eps if (e.get("state") or "").upper() == "COMPLETED"]
    eps.sort(key=lambda e: e.get("createTime") or "", reverse=True)
    print(f"H3x completed: {len(eps)}", flush=True)
    rows = []
    for e in eps[:30]:
        eid = e.get("id")
        agents = e.get("agents") or []
        us = next((a for a in agents if a.get("teamName") == "ZiYiMing"), None)
        them = next((a for a in agents if a.get("teamName") != "ZiYiMing"), None)
        if not us or not them:
            continue
        win = float(us.get("reward") or 0) > float(them.get("reward") or 0)
        gap = float(us.get("reward") or 0) - float(them.get("reward") or 0)
        rows.append({"eid": eid, "win": win, "gap": gap, "opp": them.get("teamName"),
                     "our": us.get("reward"), "their": them.get("reward")})
        print(f"  {'W' if win else 'L'} {us.get('reward')}:{them.get('reward')} gap={gap:.0f} vs {them.get('teamName')}", flush=True)
        if not win and gap < -800:
            dest = OUT / f"episode-{eid}-replay.json"
            if not dest.exists():
                try:
                    api.competition_episode_replay(eid, path=str(OUT), quiet=True)
                    print("    dl", eid, flush=True)
                except Exception as ex:
                    print("    dl fail", ex, flush=True)
                time.sleep(0.3)

    wins = sum(1 for r in rows if r["win"])
    print(f"\nH3x live: {wins}W-{len(rows)-wins}L ({wins/max(len(rows),1):.0%})", flush=True)
    losses = sorted([r for r in rows if not r["win"]], key=lambda r: r["gap"])
    print("WORST:", flush=True)
    for r in losses[:8]:
        print(f"  {r['gap']:.0f} vs {r['opp']}", flush=True)
    (OUT / "meta.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
