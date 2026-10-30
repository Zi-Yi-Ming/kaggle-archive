# -*- coding: utf-8 -*-
"""P103: reconstruct gold agent policy timeline from live replays."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")
GOLD = "吃白饭的大肥鱼"


def load_meta_index():
    meta = json.loads((OUT / "gold_meta.json").read_text(encoding="utf-8"))
    idx = {}
    for row in meta:
        for a in row.get("agents") or []:
            if a.get("teamName") == GOLD:
                idx[row["episode_id"]] = int(a.get("index") or 0)
    return idx


def recon(path: Path, ai: int):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    timeline = []  # per-day aggregates
    first_120 = []  # step-level actions first 120
    plant_log = []
    hire_log = []
    animal_log = []
    land_log = []
    sell_log = []
    buy_log = []
    farmer_moves = Counter()
    hand_count_path = []
    money_path = []
    shed_path = []
    prices_at_sell = []

    for si, st in enumerate(steps):
        if not isinstance(st, list) or ai >= len(st):
            continue
        ag = st[ai]
        if not isinstance(ag, dict):
            continue
        act = ag.get("action") or {}
        obs = ag.get("observation") or {}
        day = si // 24
        hour = si % 24

        mkt = act.get("market") or []
        farmer = act.get("farmer") or []
        hands = act.get("hands") or []
        hand_count_path.append(len(hands) if isinstance(hands, list) else 0)
        if isinstance(farmer, list) and farmer:
            farmer_moves[str(farmer[0])] += 1

        if si < 120:
            first_120.append({
                "s": si, "d": day, "h": hour,
                "farmer": farmer, "hands_n": len(hands) if isinstance(hands, list) else 0,
                "market": mkt,
            })

        px = ((obs.get("market") or {}).get("prices") or {})
        farm = (obs.get("farms") or [])
        me = obs.get("player") if obs.get("player") is not None else ai
        if isinstance(farm, list) and 0 <= me < len(farm) and isinstance(farm[me], dict):
            money_path.append((si, float(farm[me].get("money") or 0)))
            tiles = farm[me].get("tiles") or []
            plants = []
            for row in tiles:
                if not isinstance(row, list):
                    continue
                for cell in row:
                    if isinstance(cell, dict) and cell.get("kind") == "PLANT":
                        plants.append(cell)
            shed = ((obs.get("private") or {}).get("shed") or {})
            shed_path.append((si, dict(shed)))
            # log plants by planted_day
            for cell in plants:
                plant_log.append((si, day, cell.get("crop"), cell.get("planted_day")))

        for o in mkt:
            if not isinstance(o, (list, tuple)) or not o:
                continue
            op = o[0]
            if op == "HIRE":
                hire_log.append(si)
            elif op == "BUY_ANIMAL" and len(o) >= 3:
                animal_log.append((si, day, o[1], int(o[2] or 0)))
                buy_log.append((si, "BUY_ANIMAL", o[1], int(o[2] or 0), float(px.get(o[1]) or 0)))
            elif op == "BUY_LAND":
                land_log.append((si, day, o[1] if len(o) > 1 else None))
            elif op == "BUY_SEED" and len(o) >= 3:
                buy_log.append((si, "BUY_SEED", o[1], int(o[2] or 0), float(px.get(o[1]) or 0)))
            elif op == "BUY_PRODUCT" and len(o) >= 3:
                buy_log.append((si, "BUY_PRODUCT", o[1], int(o[2] or 0), float(px.get(o[1]) or 0)))
            elif op == "SELL" and len(o) >= 3:
                item, q = o[1], int(o[2] or 0)
                sell_log.append((si, day, item, q, float(px.get(item) or 0)))
                prices_at_sell.append(float(px.get(item) or 0))

    # per-day summary
    sell_by_day = Counter()
    hire_by_day = Counter()
    for si, day, item, q, p in sell_log:
        sell_by_day[day] += q
    for si in hire_log:
        hire_by_day[si // 24] += 1

    crops_planted = Counter(c for _, _, c, _ in plant_log if c)
    return {
        "file": path.name,
        "ai": ai,
        "rewards": data.get("rewards"),
        "first_120": first_120[:40],
        "hire_by_day": dict(sorted(hire_by_day.items())),
        "hire_total": len(hire_log),
        "hire_first20_steps": hire_log[:20],
        "animals": animal_log,
        "lands": land_log,
        "crops_planted": dict(crops_planted),
        "n_plant_tiles_logged": len(plant_log),
        "sell_by_day": dict(sorted(sell_by_day.items())),
        "sell_log_head": sell_log[:15],
        "sell_log_tail": sell_log[-15:],
        "buy_log_head": buy_log[:25],
        "farmer_moves": dict(farmer_moves),
        "hand_count_max": max(hand_count_path) if hand_count_path else 0,
        "hand_count_mean": (sum(hand_count_path) / len(hand_count_path)) if hand_count_path else 0,
        "money_path_sample": money_path[::24][:30],
        "money_end": money_path[-1][1] if money_path else None,
    }


def main():
    idx = load_meta_index()
    recs = []
    files = sorted((OUT / "gold").glob("episode-*-replay.json"))[:8]
    for p in files:
        eid = int(p.name.split("-")[1])
        ai = idx.get(eid, 0)
        r = recon(p, ai)
        recs.append(r)
        print("====", p.name, "ai", ai, "r", r["rewards"], "money_end", r["money_end"], flush=True)
        print("  hires", r["hire_total"], "by_day", r["hire_by_day"], flush=True)
        print("  animals", r["animals"][:8], "lands", r["lands"], flush=True)
        print("  crops", r["crops_planted"], flush=True)
        print("  sell_by_day", r["sell_by_day"], flush=True)
        print("  hands mean/max", round(r["hand_count_mean"], 2), r["hand_count_max"], flush=True)
        print("  farmer_moves", r["farmer_moves"], flush=True)
        print("  buy_head", r["buy_log_head"][:10], flush=True)

    (RESEARCH / "p103_gold_timeline.json").write_text(
        json.dumps(recs, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print("WROTE p103_gold_timeline.json", flush=True)


if __name__ == "__main__":
    main()
