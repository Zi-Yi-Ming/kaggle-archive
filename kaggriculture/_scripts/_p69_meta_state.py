# -*- coding: utf-8 -*-
"""P69 Meta State Discovery: first-div events + precursors across daily top episodes."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

EP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p69_daily_top")
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def classify(a, b):
    ma = json.dumps(a.get("market"), sort_keys=True, default=str)
    mb = json.dumps(b.get("market"), sort_keys=True, default=str)
    if ma != mb:
        if any(o and o[0] == "SELL" for o in (a.get("market") or []) + (b.get("market") or [])):
            return "SELL"
        return "MARKET"
    return "WORKER"


def eco(obs, player):
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
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
    px = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80,
          "EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40}
    inv_val = sum(int(v or 0) * px.get(k, 1) for k, v in shed.items())
    return {
        "money": money, "plants": plants, "animals": animals,
        "hands": len(farm.get("hands") or []),
        "asset": money + inv_val,
        "n_shops": len((obs.get("town") or {}).get("unlocked_shops") or []),
    }


def main():
    games = []
    for path in sorted(EP.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        rewards = d.get("rewards") or [None, None]
        teams = (d.get("info") or {}).get("TeamNames") or []
        if len(steps) < 720:
            continue
        # first divergence seat0 vs seat1
        fd = None
        fd_type = None
        for t in range(720):
            a0 = steps[t][0].get("action") or {}
            a1 = steps[t][1].get("action") or {}
            if akey(a0) != akey(a1):
                fd = t
                fd_type = classify(a0, a1)
                break
        # eco snapshot just before fd
        def snap(seat, step):
            s = max(0, min(719, step))
            obs = steps[s][seat].get("observation") or {}
            return eco(obs, int(obs.get("player") or seat))

        pre0 = snap(0, (fd - 1) if fd else 0)
        pre1 = snap(1, (fd - 1) if fd else 0)
        mid0 = snap(0, 15 * 24 + 12)
        mid1 = snap(1, 15 * 24 + 12)
        # late outcome = reward gap
        r0, r1 = rewards[0] if rewards else None, rewards[1] if rewards else None
        games.append({
            "file": path.name,
            "team0": teams[0] if teams else "",
            "team1": teams[1] if len(teams) > 1 else "",
            "r0": r0, "r1": r1,
            "winner_seat": 0 if (r0 or 0) > (r1 or 0) else (1 if (r1 or 0) > (r0 or 0) else -1),
            "first_div": fd,
            "first_div_day": (fd // 24) if fd is not None else -1,
            "first_div_type": fd_type,
            "pre0_animals": pre0["animals"], "pre1_animals": pre1["animals"],
            "pre0_plants": pre0["plants"], "pre1_plants": pre1["plants"],
            "pre0_money": pre0["money"], "pre1_money": pre1["money"],
            "pre0_asset": pre0["asset"], "pre1_asset": pre1["asset"],
            "pre0_hands": pre0["hands"], "pre1_hands": pre1["hands"],
            "pre0_shops": pre0["n_shops"], "pre1_shops": pre1["n_shops"],
            "d15_0_animals": mid0["animals"], "d15_1_animals": mid1["animals"],
            "d15_0_asset": mid0["asset"], "d15_1_asset": mid1["asset"],
            "d15_gap": mid0["asset"] - mid1["asset"],
        })

    print(f"games n={len(games)}", flush=True)
    print("\n=== first_div day/type ===", flush=True)
    print("days", Counter(g["first_div_day"] for g in games).most_common(), flush=True)
    print("types", Counter(g["first_div_type"] for g in games).most_common(), flush=True)

    # winner vs loser at first_div precursor
    wins, loses = [], []
    for g in games:
        w = g["winner_seat"]
        if w < 0:
            continue
        weco = {
            "animals": g["pre0_animals"] if w == 0 else g["pre1_animals"],
            "plants": g["pre0_plants"] if w == 0 else g["pre1_plants"],
            "money": g["pre0_money"] if w == 0 else g["pre1_money"],
            "asset": g["pre0_asset"] if w == 0 else g["pre1_asset"],
            "hands": g["pre0_hands"] if w == 0 else g["pre1_hands"],
        }
        leco = {
            "animals": g["pre1_animals"] if w == 0 else g["pre0_animals"],
            "plants": g["pre1_plants"] if w == 0 else g["pre0_plants"],
            "money": g["pre1_money"] if w == 0 else g["pre0_money"],
            "asset": g["pre1_asset"] if w == 0 else g["pre0_asset"],
            "hands": g["pre1_hands"] if w == 0 else g["pre0_hands"],
        }
        wins.append(weco)
        loses.append(leco)

    def mean(xs, k):
        return sum(x[k] for x in xs) / len(xs) if xs else 0

    print("\n=== precursor winner vs loser (at first_div) ===", flush=True)
    for k in ("animals", "plants", "money", "asset", "hands"):
        print(f"  {k:8s} win={mean(wins,k):.1f} lose={mean(loses,k):.1f} "
              f"d={mean(wins,k)-mean(loses,k):+.1f}", flush=True)

    # is precursor consistent direction?
    print("\n=== direction consistency (win>lose per game) ===", flush=True)
    for k in ("animals", "plants", "money", "asset", "hands"):
        cnt = 0
        n = 0
        for w, l in zip(wins, loses):
            n += 1
            if w[k] > l[k]:
                cnt += 1
        print(f"  {k}: winner higher {cnt}/{n}", flush=True)

    # first_div type vs winner eco gap at d15
    print("\n=== d15 winner-asset gap by first_div_day ===", flush=True)
    byday = defaultdict(list)
    for g in games:
        w = g["winner_seat"]
        if w < 0:
            continue
        gap = g["d15_gap"] if w == 0 else -g["d15_gap"]
        byday[g["first_div_day"]].append(gap)
    for d in sorted(byday):
        v = byday[d]
        print(f"  d{d}: n={len(v)} mean_win_lose_asset={sum(v)/len(v):+.0f}", flush=True)

    # lineage clustering: d15 animals winner + first_div_day
    print("\n=== winner d15 animals x first_div_day ===", flush=True)
    cl = Counter()
    for g in games:
        w = g["winner_seat"]
        if w < 0:
            continue
        an = g["d15_0_animals"] if w == 0 else g["d15_1_animals"]
        cl[(an, g["first_div_day"] // 3 * 3)] += 1
    print(cl.most_common(12), flush=True)

    with open(ROOT / "p69_meta_state.csv", "w", newline="", encoding="utf-8") as f:
        fields = list(games[0].keys())
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(games)

    # STOP criteria
    # stable precursor: one eco field where winner>lose in >=70% games AND mean gap significant
    stable = []
    for k in ("animals", "plants", "money", "asset", "hands"):
        cnt = sum(1 for w, l in zip(wins, loses) if w[k] > l[k])
        frac = cnt / max(1, len(wins))
        if frac >= 0.7 and abs(mean(wins, k) - mean(loses, k)) >= 1:
            stable.append(k)
    print("\nstable precursors", stable, flush=True)
    if not stable:
        print("P69_FINAL_STOP NO_STABLE_PRECURSOR", flush=True)
    else:
        print("P69_PRECURSOR_FOUND", flush=True)
    print("wrote p69_meta_state.csv", flush=True)


if __name__ == "__main__":
    main()
