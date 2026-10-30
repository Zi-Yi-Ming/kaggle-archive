# -*- coding: utf-8 -*-
"""P63: characterize LB winners on big alperen losses. Read-only."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p61_alperen_replays")
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
SUB = 56244291


def eco_from_obs(obs, player):
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    tiles = farm.get("tiles") or []
    plants = animals = 0
    crops = Counter()
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants += 1
                    crops[t.get("crop")] += 1
                if t.get("animal"):
                    animals += 1
    money = float(farm.get("money") or 0)
    px = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80,
          "EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40}
    inv_val = sum(int(v or 0) * px.get(k, 1) for k, v in shed.items())
    return {
        "money": money, "plants": plants, "animals": animals,
        "hands": len(farm.get("hands") or []),
        "land": len(farm.get("unlocked_quadrants") or []),
        "inv_val": inv_val, "asset": money + inv_val,
        "crops": dict(crops),
        "n_shops": len((obs.get("town") or {}).get("unlocked_shops") or []),
    }


def main():
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    losses = [m for m in meta if m["result"] == "L" and m["margin"] <= -15000]
    print(f"big losses n={len(losses)}", flush=True)

    rows = []
    for m in losses:
        path = Path(m["path"])
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d["steps"]
        seat = int(m.get("our_seat") or 0)
        oseat = 1 - seat
        print(f"\n=== {m['episode_id']} vs {m['opp_team']} margin={m['margin']:.0f} ===", flush=True)
        for day in (5, 10, 15, 20, 25):
            t = day * 24 + 12
            if t >= len(steps):
                continue
            oa = steps[t][seat].get("observation") or {}
            ob = steps[t][oseat].get("observation") or {}
            # player index in each obs
            ea = eco_from_obs(oa, int(oa.get("player") or seat))
            eb = eco_from_obs(ob, int(ob.get("player") or oseat))
            print(f"  d{day:02d} ALP money={ea['money']:7.0f} pl={ea['plants']:3d} an={ea['animals']:2d} "
                  f"hd={ea['hands']:2d} | WIN money={eb['money']:7.0f} pl={eb['plants']:3d} "
                  f"an={eb['animals']:2d} hd={eb['hands']:2d} | d_asset={eb['asset']-ea['asset']:+.0f}", flush=True)
            rows.append({
                "episode_id": m["episode_id"], "opp": m["opp_team"], "day": day,
                "alp_money": ea["money"], "alp_plants": ea["plants"], "alp_animals": ea["animals"],
                "alp_hands": ea["hands"], "alp_asset": ea["asset"],
                "win_money": eb["money"], "win_plants": eb["plants"], "win_animals": eb["animals"],
                "win_hands": eb["hands"], "win_asset": eb["asset"],
                "gap_asset": eb["asset"] - ea["asset"],
                "alp_crops": json.dumps(ea["crops"]), "win_crops": json.dumps(eb["crops"]),
            })

    with open(ROOT / "p63_lb_winners_eco.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)

    # mean gap by day
    print("\n=== mean winner-alperen asset gap by day ===", flush=True)
    by = {}
    for r in rows:
        by.setdefault(r["day"], []).append(r["gap_asset"])
    for day in sorted(by):
        v = by[day]
        print(f"  d{day}: mean={sum(v)/len(v):+.0f} n={len(v)}", flush=True)
    print("wrote p63_lb_winners_eco.csv", flush=True)


if __name__ == "__main__":
    main()
