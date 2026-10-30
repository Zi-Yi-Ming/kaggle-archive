# -*- coding: utf-8 -*-
"""P68b: internal clustering of daily top episodes. Opening signatures."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

EP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p68_daily_top")
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")


def market_sig(market):
    ops = []
    for o in market or []:
        if not o:
            continue
        ops.append(tuple(o[:3] if len(o) >= 3 else o))
    return tuple(sorted(ops))


def main():
    seats = []
    for path in sorted(EP.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        rewards = d.get("rewards") or [None, None]
        info = d.get("info") or {}
        teams = info.get("TeamNames") or []
        for seat in (0, 1):
            a0 = steps[0][seat].get("action") or {}
            # first 6 market days sell/buy pattern
            day_mkt = []
            for day in range(7):
                t = day * 24
                if t >= len(steps):
                    break
                act = steps[t][seat].get("action") or {}
                day_mkt.append(market_sig(act.get("market")))
            # plants/animals at d5 midday
            t5 = min(5 * 24 + 12, len(steps) - 1)
            obs = steps[t5][seat].get("observation") or {}
            player = int(obs.get("player") or seat)
            farms = obs.get("farms") or []
            farm = farms[player] if player < len(farms) else {}
            tiles = farm.get("tiles") or []
            plants = animals = 0
            for row in tiles:
                for t in row:
                    if isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            plants += 1
                        if t.get("animal"):
                            animals += 1
            money = float(farm.get("money") or 0)
            seats.append({
                "file": path.name,
                "seat": seat,
                "team": teams[seat] if seat < len(teams) else "",
                "reward": rewards[seat] if seat < len(rewards) else None,
                "open_sig": str(market_sig(a0.get("market"))),
                "d0_n_orders": len(a0.get("market") or []),
                "d5_plants": plants, "d5_animals": animals, "d5_money": money,
                "d0_d6_sig_hash": hash(tuple(str(x) for x in day_mkt)),
            })

    print("n_seats", len(seats), flush=True)
    print("\n=== opening market signatures (top) ===", flush=True)
    opens = Counter(s["open_sig"][:100] for s in seats)
    for sig, n in opens.most_common(8):
        r = [s["reward"] for s in seats if s["open_sig"][:100] == sig and s["reward"] is not None]
        print(f"  n={n} mean_r={sum(r)/len(r) if r else 0:.0f} {sig[:90]}", flush=True)

    print("\n=== d5 eco clusters ===", flush=True)
    for bucket_name, key in [
        ("animals", lambda s: (s["d5_animals"],)),
        ("plants", lambda s: (s["d5_plants"] // 10 * 10,)),
    ]:
        by = defaultdict(list)
        for s in seats:
            by[key(s)].append(s["reward"] or 0)
        print(bucket_name, flush=True)
        for k, rs in sorted(by.items(), key=lambda x: -sum(x[1])/max(1,len(x[1]))):
            print(f"  {k}: n={len(rs)} mean_r={sum(rs)/len(rs):.0f}", flush=True)

    # winner vs loser d5
    wins = [s for s in seats if s["reward"] and s["reward"] > 120000]
    loses = [s for s in seats if s["reward"] and s["reward"] < 90000]
    print(f"\nhigh>120k n={len(wins)} mean_plants={sum(s['d5_plants'] for s in wins)/max(1,len(wins)):.1f} "
          f"mean_an={sum(s['d5_animals'] for s in wins)/max(1,len(wins)):.1f}", flush=True)
    print(f"low<90k n={len(loses)} mean_plants={sum(s['d5_plants'] for s in loses)/max(1,len(loses)):.1f} "
          f"mean_an={sum(s['d5_animals'] for s in loses)/max(1,len(loses)):.1f}", flush=True)

    # d0-d6 signature diversity
    sigs = Counter(s["d0_d6_sig_hash"] for s in seats)
    print(f"\nunique d0-d6 market-hash: {len(sigs)} / {len(seats)}", flush=True)
    for h, n in sigs.most_common(5):
        r = [s["reward"] for s in seats if s["d0_d6_sig_hash"] == h and s["reward"] is not None]
        print(f"  n={n} mean_r={sum(r)/len(r) if r else 0:.0f}", flush=True)

    with open(ROOT / "p68b_daily_openings.csv", "w", newline="", encoding="utf-8") as f:
        fields = list(seats[0].keys())
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(seats)
    print("wrote p68b_daily_openings.csv", flush=True)


if __name__ == "__main__":
    main()
