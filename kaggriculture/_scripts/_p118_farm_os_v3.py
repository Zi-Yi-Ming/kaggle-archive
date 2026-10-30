# -*- coding: utf-8 -*-
"""P118 Farm OS v3: exact gold choreography (shed home, fert@3,3, role hands).

Key facts from p117:
  - Board starts 5x5, farmer home (4,4), hands spawn at shed tiles
  - Every day h00: units reset home, hands=0; h01: HIRE + shopping
  - Fert post action at (3,3): path = WEST, NORTH, COLLECT_FERTILIZER
  - Hand0/1 = logistics (pickup/build/place/feed/care/drop)
  - Hand3+ = field (plant/water), migrate NW then outward
  - Market almost only at h1 (buys) and h4-10 (fert sells)
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUTJSON = PROJ / "_research" / "p118_farm_os_v3.json"

# Exact day0 from gold (24/24 identical)
DAY0 = {
    0: (["PASS"], [], []),
    1: (["PASS"], [], [
        ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
        ["BUY_PRODUCT", "WHEAT", 5],
        ["BUY_ANIMAL", "COW", 2],
        ["BUY_SEED", "MELON", 6],
        ["BUY_ANIMAL", "SHEEP", 3],
        ["BUY_SEED", "WHEAT", 2],
    ]),
    2: (["PICKUP", "COW", 1],
        [["PICKUP", "SHEEP", 1], ["PICKUP", "SHEEP", 1], ["PASS"], ["PICKUP", "COW", 1], ["PICKUP", "SHEEP", 1]],
        [["BUY_SEED", "WHEAT", 1]]),
    3: (["PICKUP", "WHEAT", 1],
        [["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1], ["PASS"], ["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1]],
        []),
    4: (["WEST"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["WEST"]], []),
    5: (["NORTH"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["BUILD_PASTURE"]], []),
    6: (["BUILD_PASTURE"],
        [["BUILD_PASTURE"], ["BUILD_PASTURE"], ["PASS"], ["BUILD_PASTURE"], ["PLACE", "SHEEP"]], []),
    7: (["PLACE", "COW"],
        [["PLACE", "SHEEP"], ["PLACE", "SHEEP"], ["PASS"], ["PLACE", "COW"], ["FEED"]], []),
    8: (["FEED"], [["FEED"], ["FEED"], ["PASS"], ["FEED"], ["CARE"]], []),
    9: (["CARE"], [["CARE"], ["CARE"], ["PASS"], ["CARE"], ["DROP"]], []),
    10: (["EAST"], [["EAST"], ["SOUTH"], ["PASS"], ["SOUTH"], ["WEST"]], []),
    11: (["SOUTH"], [["DROP"], ["DROP"], ["PASS"], ["SOUTH"], ["WEST"]], []),
    12: (["DROP"], [["PASS"], ["NORTH"], ["PASS"], ["DROP"], ["WEST"]], []),
    # 13-23: plant/water melon in NW; hand3 plants, hand4 waters/alternates
    13: (["PASS"], [["PASS"], ["NORTH"], ["PASS"], ["WEST"], ["PLANT", "MELON"]], []),
    14: (["PASS"], [["PASS"], ["NORTH"], ["PASS"], ["NORTH"], ["WATER"]], []),
    15: (["PASS"], [["PASS"], ["PLANT", "MELON"], ["PASS"], ["NORTH"], ["WEST"]], []),
    16: (["PASS"], [["PASS"], ["WATER"], ["PASS"], ["PLANT", "MELON"], ["NORTH"]], []),
    17: (["PASS"], [["PASS"], ["NORTH"], ["PASS"], ["WATER"], ["NORTH"]], []),
    18: (["PASS"], [["PASS"], ["PLANT", "MELON"], ["PASS"], ["WEST"], ["PLANT", "WHEAT"]], []),
    19: (["PASS"], [["PASS"], ["WATER"], ["PASS"], ["SOUTH"], ["WATER"]], []),
    20: (["PASS"], [["PASS"], ["WEST"], ["PASS"], ["PLANT", "MELON"], ["EAST"]], []),
    21: (["PASS"], [["PASS"], ["WEST"], ["PASS"], ["WATER"], ["NORTH"]], []),
    22: (["PASS"], [["PASS"], ["PLANT", "WHEAT"], ["PASS"], ["SOUTH"], ["PLANT", "WHEAT"]], []),
    23: (["PASS"], [["PASS"], ["WATER"], ["PASS"], ["PLANT", "MELON"], ["WATER"]], []),
}

# Day1+ morning: WEST, NORTH, COLLECT at (3,3)
MORNING = {
    2: (["WEST"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]]),
    3: (["NORTH"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]]),
    4: (["COLLECT_FERTILIZER"],
        [["COLLECT_FERTILIZER"], ["COLLECT_FERTILIZER"], ["PASS"], ["COLLECT_FERTILIZER"], ["DROP"], ["PASS"]]),
    5: (["EAST"], [["EAST"], ["SOUTH"], ["PASS"], ["SOUTH"], ["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1]]),
    6: (["SOUTH"], [["DROP"], ["DROP"], ["PASS"], ["SOUTH"], ["WEST"], ["NORTH"]]),
    7: (["DROP"], [["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1], ["PASS"], ["DROP"], ["NORTH"], ["NORTH"]]),
    8: (["FEED"], [["WEST"], ["NORTH"], ["PASS"], ["WEST"], ["FEED"], ["NORTH"]]),
    9: (["CARE"], [["FEED"], ["FEED"], ["PASS"], ["NORTH"], ["CARE"], ["FEED"]]),
    10: (["CARE"], [["CARE"], ["CARE"], ["PASS"], ["NORTH"], ["EAST"], ["CARE"]]),
    11: (["DROP"], [["EAST"], ["SOUTH"], ["PASS"], ["NORTH"], ["SOUTH"], ["SOUTH"]]),
}


def pad(cmds, n):
    cmds = [list(c) for c in (cmds or [])]
    if len(cmds) > n:
        return cmds[:n]
    while len(cmds) < n:
        cmds.append(["PASS"])
    return cmds


def pick_crop(day, seeds):
    if day <= 5:
        return "MELON" if seeds.get("MELON", 0) else "WHEAT"
    if day <= 16:
        return "STRAWBERRY" if seeds.get("STRAWBERRY", 0) else "WHEAT"
    return "CARROT" if seeds.get("CARROT", 0) else "WHEAT"


def farm_os_v3(tag: str):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            day, hour = step // 24, step % 24
            priv = (obs or {}).get("private") or {}
            shed = dict(priv.get("shed") or {})
            seeds = dict(priv.get("seeds") or {})
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if 0 <= me < len(farms) and isinstance(farms[me], dict) else {}
            money = float(farm.get("money") or 0)
            hands_n = len(farm.get("hands") or [])
            crop = pick_crop(day, seeds)

            # ---- day0 exact ----
            if step <= 23:
                f, h, m = DAY0[step]
                return {"farmer": list(f), "hands": pad(h, max(hands_n, len(h))), "market": [list(o) for o in m]}

            mkt = []
            # h1 shopping window
            if hour == 1:
                n = 6 if day <= 5 else (10 if day == 6 else 9)
                for _ in range(min(n, 10)):
                    mkt.append(["HIRE"])
                if money > 50:
                    mkt.append(["BUY_PRODUCT", "WHEAT", 3])
                if money > 150:
                    if day <= 5:
                        mkt.append(["BUY_SEED", "MELON", 2])
                    elif day <= 16:
                        mkt.append(["BUY_SEED", "STRAWBERRY", 3])
                    else:
                        mkt.append(["BUY_SEED", "CARROT", 3])
                    mkt.append(["BUY_SEED", "WHEAT", 2])
                if day == 6 and money > 2500:
                    mkt.append(["BUY_LAND"])
                if day == 9 and money > 2000:
                    mkt.append(["BUY_LAND"])
                    mkt.append(["BUY_ANIMAL", "GOOSE", 1])
                if day == 6 and money > 800:
                    mkt.append(["BUY_ANIMAL", "COW", 3])
                if day in (10, 11) and money > 800:
                    mkt.append(["BUY_ANIMAL", "GOOSE", 4])
            elif 4 <= hour <= 10:
                fert = int(shed.get("FERTILIZER") or 0)
                if fert > 0:
                    mkt.append(["SELL", "FERTILIZER", fert])
                if hour in (5, 6) and money > 80:
                    mkt.append(["BUY_PRODUCT", "WHEAT", 1])
                if day >= 5 and hour in (7, 8):
                    for item, th in (("WOOL", 2), ("WHEAT", 6), ("MILK", 2), ("EGG", 3)):
                        q = int(shed.get(item) or 0)
                        if q >= th:
                            mkt.append(["SELL", item, min(q, 3)])
                if day >= 12 and hour in (7, 8, 9):
                    for item in ("EGG", "MILK", "STRAWBERRY", "CARROT", "TOMATO", "MELON"):
                        q = int(shed.get(item) or 0)
                        if q >= 3:
                            mkt.append(["SELL", item, min(q, 5 if day < 28 else 15)])
            if day >= 28 and hour in (1, 7):
                for item in ("CARROT", "STRAWBERRY", "WHEAT", "EGG", "MILK", "WOOL", "TOMATO", "MELON"):
                    q = int(shed.get(item) or 0)
                    if q > 0:
                        mkt.append(["SELL", item, q])

            # ---- physical ----
            if hour in MORNING:
                f, h = MORNING[hour]
                # pad/truncate to live
                return {"farmer": list(f), "hands": pad(h, hands_n), "market": mkt}

            # afternoon/evening: field work, roles
            if hour == 12:
                f = ["DROP"]
                h = [["DROP"] for _ in range(hands_n)]
            elif hour == 13 and 9 <= day <= 12:
                f = ["BUILD_COOP"]
                h = [["BUILD_COOP"] for _ in range(min(hands_n, 4))]
            elif day >= 25 and hour % 3 == 0:
                f = ["HARVEST"]
                h = [["HARVEST"] if i % 2 == 0 else ["WATER"] for i in range(hands_n)]
            elif hour % 2 == 1:
                f = ["PLANT", crop]
                # hand0/1 logistics pass, hand2 pass, hand3+ plant/water
                h = []
                for i in range(hands_n):
                    if i <= 2:
                        h.append(["PASS"])
                    elif i % 2 == 1:
                        h.append(["PLANT", crop])
                    else:
                        h.append(["WATER"])
            else:
                f = ["WATER"]
                h = []
                for i in range(hands_n):
                    if i <= 2:
                        h.append(["PASS"])
                    elif i % 2 == 0:
                        h.append(["WATER"])
                    else:
                        h.append(["PLANT", crop])

            return {"farmer": f, "hands": pad(h, hands_n), "market": mkt}
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = make_cand(f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp_path, f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, stt, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, stt, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                rows.append({"seed": seed, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def gate(name, make, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2), "shop"),
    ):
        print(f"\n== {name} vs {opp_name} ==", flush=True)
        rows, summary = series(make, opp_path, seeds, f"{name}_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", name, key, summary, flush=True)
        if key == "shop" and summary.get("win_rate", 0) < 0.5:
            rec["verdict"] = f"NO shop {summary}"
            return rec
    mv = rec["metav4"]["summary"]
    sh = rec["shop"]["summary"]
    if mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5:
        rec["verdict"] = "DUAL PASS"
    else:
        rec["verdict"] = f"NO mv={mv} sh={sh}"
    return rec


def main():
    payload = {}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    name = "farm_os_v3"
    if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
        print("skip", name, flush=True)
    else:
        gate(name, farm_os_v3, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"), rec.get("metav4", {}).get("summary"), rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
