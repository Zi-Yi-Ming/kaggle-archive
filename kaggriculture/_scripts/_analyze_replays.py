# -*- coding: utf-8 -*-
"""Analyze live episode replays (handles p1 obs.step=None)."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\replays")


def farm_struct(farm):
    animals = Counter()
    plants = Counter()
    for row in farm.get("tiles") or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            if tile.get("animal"):
                animals[tile["animal"]] += 1
            elif tile.get("kind") == "PLANT" and tile.get("crop"):
                plants[tile["crop"]] += 1
    return {
        "money": float(farm.get("money") or 0),
        "hands": len(farm.get("hands") or []),
        "quads": len(farm.get("unlocked_quadrants") or []),
        "animals": dict(animals),
        "plants": dict(plants),
        "an": sum(animals.values()),
        "pl": sum(plants.values()),
    }


def analyze(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    agents = info.get("Agents") or []
    rewards = data.get("rewards")
    statuses = data.get("statuses")
    steps = data.get("steps") or []

    snaps = {}
    sells = [Counter(), Counter()]
    sell_by_day = [Counter(), Counter()]
    # track own farm only: player p uses farms[p]
    final_banks = [None, None]

    for idx, snap in enumerate(steps):
        for p in (0, 1):
            if p >= len(snap):
                continue
            rec = snap[p] or {}
            obs = rec.get("observation") or {}
            action = rec.get("action") or {}
            if not isinstance(obs, dict):
                continue
            # p1 often has step=None; use frame index
            step = obs.get("step")
            step = int(step) if step is not None else idx
            day = step // 24
            farms = obs.get("farms") or []
            if p < len(farms) and isinstance(farms[p], dict):
                if step % 24 == 0 and day in (10, 15, 20, 25, 29):
                    snaps[(day, p)] = farm_struct(farms[p])
                if step >= 719 or idx >= len(steps) - 1:
                    final_banks[p] = float(farms[p].get("money") or 0)
            for o in action.get("market") or []:
                if o and o[0] == "SELL" and len(o) >= 3:
                    try:
                        qty = int(o[2] or 0)
                    except Exception:
                        qty = 0
                    if qty > 0:
                        sells[p][o[1]] += qty
                        sell_by_day[p][day] += qty

    print("=" * 72)
    print(path.name)
    print("  teams:", teams)
    print("  agents:", [str(a)[:80] for a in agents[:4]])
    print("  rewards:", rewards, "statuses:", statuses)
    print("  final banks:", final_banks)
    if None not in final_banks:
        print(f"  margin p0-p1: {final_banks[0]-final_banks[1]:+.0f}")
        if rewards:
            print(f"  reward margin: {float(rewards[0])-float(rewards[1]):+.0f}")
    for p in (0, 1):
        label = f"p{p}"
        if teams and p < len(teams):
            label = f"p{p}({teams[p]})"
        print(f"  --- {label} top sells ---")
        for item, q in sells[p].most_common(8):
            print(f"    {item:12s} {q}")
        late = " ".join(f"d{d}:{sell_by_day[p][d]}" for d in range(20, 30) if sell_by_day[p][d])
        print(f"    d20-29 volume: {late}")
    for day in (10, 15, 20, 25, 29):
        parts = []
        for p in (0, 1):
            s = snaps.get((day, p))
            if not s:
                parts.append(f"p{p}=?")
            else:
                parts.append(
                    f"p{p}=${s['money']:.0f} q={s['quads']} an={s['an']}{s['animals']} pl={s['pl']}"
                )
        print(f"  day {day:2d}: {parts[0]} | {parts[1]}")
    return {"file": path.name, "teams": teams, "banks": final_banks, "rewards": rewards}


def main():
    files = sorted(REP.glob("episode-*-replay.json"))
    print("found", len(files))
    rows = []
    for f in files:
        try:
            rows.append(analyze(f))
        except Exception as e:
            import traceback
            print("FAIL", f.name, e)
            traceback.print_exc()
    print("\n=== SUMMARY ===")
    for r in rows:
        print(r["file"], "teams=", r["teams"], "rewards=", r["rewards"], "banks=", r["banks"])


if __name__ == "__main__":
    main()
