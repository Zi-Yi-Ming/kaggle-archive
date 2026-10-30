# -*- coding: utf-8 -*-
"""P2-E2: R2 live games — win vs loss opponent signature clustering."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\replays")


def classify_and_profile(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [0, 0]
    if "ZiYiMing" not in teams:
        return None
    me = teams.index("ZiYiMing")
    opp = 1 - me
    my, op = float(rewards[me]), float(rewards[opp])
    steps = data.get("steps") or []

    def profile(player):
        an = Counter()
        quads = 0
        money_d20 = None
        sells = Counter()
        for idx, snap in enumerate(steps):
            if player >= len(snap):
                continue
            rec = snap[player] or {}
            obs = rec.get("observation") or {}
            act = rec.get("action") or {}
            if not isinstance(obs, dict):
                continue
            step = obs.get("step")
            step = int(step) if step is not None else idx
            farm = (obs.get("farms") or [None, None])[player]
            if isinstance(farm, dict) and step % 24 == 0:
                quads = len(farm.get("unlocked_quadrants") or [])
                if step // 24 == 20:
                    money_d20 = float(farm.get("money") or 0)
                an.clear()
                for row in farm.get("tiles") or []:
                    for t in row or []:
                        if isinstance(t, dict) and t.get("animal"):
                            an[t["animal"]] += 1
            if int(obs.get("player") or player) != player:
                continue
            for o in act.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) > 0:
                    sells[o[1]] += 1
        return {
            "quads": quads,
            "an": dict(an),
            "an_total": sum(an.values()),
            "money_d20": money_d20,
            "sell_events": dict(sells),
        }

    return {
        "file": path.name,
        "opp": teams[opp] if opp < len(teams) else "?",
        "win": my > op,
        "my_bank": my,
        "opp_bank": op,
        "margin": my - op,
        "opp_profile": profile(opp),
        "my_profile": profile(me),
    }


def main():
    rows = []
    for p in sorted(REP.glob("episode-*.json")):
        try:
            r = classify_and_profile(p)
        except Exception as e:
            print("fail", p.name, e)
            continue
        if r:
            rows.append(r)
    print(f"n={len(rows)} W={sum(1 for r in rows if r['win'])} L={sum(1 for r in rows if not r['win'])}")
    print("\n=== by result ===")
    for flag in (True, False):
        sub = [r for r in rows if r["win"] == flag]
        if not sub:
            continue
        print(f"\n{'WIN' if flag else 'LOSS'} n={len(sub)}")
        for r in sub:
            op = r["opp_profile"]
            print(f"  vs {r['opp'][:20]:20s} m={r['margin']:+8.0f} opp_an={op['an_total']} "
                  f"{op['an']} q={op['quads']} d20$={op['money_d20']} "
                  f"sells={dict(list(sorted(op['sell_events'].items(), key=lambda kv: -kv[1])[:5]))}")


if __name__ == "__main__":
    main()
