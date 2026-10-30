# -*- coding: utf-8 -*-
"""P111 Farm OS v2: follow gold's extracted rules table exactly.

Rules from p110:
  h01: HIRE + all market buys
  h04-h10: SELL FERTILIZER + seeds (白饭 window)
  h12-h23: physical only (almost no market)
  crops: melon(d1-5) -> strawberry(d6-16) -> carrot/wheat(d17+)
  coops for geese around d9-12
  fert sells are the #1 cash item (409 in gold samples)
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
OUTJSON = PROJ / "_research" / "p111_farm_os_v2.json"

OPEN_TAPE = {
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
    3: (["PICKUP", "WHEAT", 1], [["PICKUP"], ["PICKUP"], ["PASS"], ["PICKUP"], ["PICKUP"]], []),
    4: (["WEST"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["WEST"]], []),
    5: (["NORTH"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["BUILD_PASTURE"]], []),
    6: (["BUILD_PASTURE"], [["BUILD_PASTURE"], ["BUILD_PASTURE"], ["PASS"], ["BUILD_PASTURE"], ["PLACE", "SHEEP"]], []),
    7: (["PLACE", "COW"], [["PLACE", "SHEEP"], ["PLACE", "SHEEP"], ["PASS"], ["PLACE", "COW"], ["FEED"]], []),
    8: (["FEED"], [["FEED"], ["FEED"], ["PASS"], ["FEED"], ["CARE"]], []),
    9: (["CARE"], [["CARE"], ["CARE"], ["PASS"], ["CARE"], ["DROP"]], []),
    10: (["EAST"], [["EAST"], ["SOUTH"], ["PASS"], ["SOUTH"], ["WEST"]], []),
    11: (["SOUTH"], [["DROP"], ["DROP"], ["PASS"], ["SOUTH"], ["WEST"]], []),
    12: (["DROP"], [["PASS"], ["NORTH"], ["PASS"], ["DROP"], ["WEST"]], []),
}


def pick_crop(day, seeds):
    if day <= 5:
        return "MELON" if seeds.get("MELON", 0) else "WHEAT"
    if day <= 16:
        return "STRAWBERRY" if seeds.get("STRAWBERRY", 0) else ("MELON" if seeds.get("MELON", 0) else "WHEAT")
    return "CARROT" if seeds.get("CARROT", 0) else "WHEAT"


def farm_os_v2(tag: str):
    def pad(cmds, n):
        cmds = [list(c) for c in (cmds or [])]
        if len(cmds) > n:
            return cmds[:n]
        while len(cmds) < n:
            cmds.append(["PASS"])
        return cmds

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

            if step in OPEN_TAPE:
                f, h, m = OPEN_TAPE[step]
                return {"farmer": list(f), "hands": pad(h, max(hands_n, len(h))), "market": [list(o) for o in m]}

            f = ["PASS"]
            hands = []
            mkt = []

            # ===== MARKET WINDOWS (from p110) =====
            if hour == 1:
                # HIRE wave + buys
                n = 5 if day <= 5 else (10 if day == 6 else 9)
                n = min(n, 10)
                for _ in range(n):
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
                # animal/land waves
                if step == 152 or (day in (6, 10) and money > 2500 and hour == 1):
                    mkt.append(["BUY_LAND"])
                if day == 6 and money > 800:
                    mkt.append(["BUY_ANIMAL", "COW", 3])
                if day in (9, 10, 11) and money > 600:
                    mkt.append(["BUY_ANIMAL", "GOOSE", 3])
                if day == 11 and money > 400:
                    mkt.append(["BUY_ANIMAL", "SHEEP", 2])

            elif 4 <= hour <= 10:
                # 白饭 window: sell fert + trickle seeds/products
                fert = int(shed.get("FERTILIZER") or 0)
                if fert > 0:
                    mkt.append(["SELL", "FERTILIZER", fert])
                if hour in (5, 6) and money > 80:
                    mkt.append(["BUY_PRODUCT", "WHEAT", 1])
                    if day >= 2 and money > 120:
                        mkt.append(["BUY_SEED", "STRAWBERRY", 1])
                # early product trickle (day5+ wool/wheat, day8+ milk)
                if day >= 5 and hour in (7, 8):
                    for item, th in (("WOOL", 2), ("WHEAT", 8), ("MILK", 2), ("EGG", 4)):
                        q = int(shed.get(item) or 0)
                        if q >= th:
                            mkt.append(["SELL", item, min(q, 3)])
                # late game broader sells in this window only
                if day >= 12 and hour in (7, 8, 9):
                    for item in ("EGG", "MILK", "STRAWBERRY", "CARROT", "TOMATO", "MELON"):
                        q = int(shed.get(item) or 0)
                        if q >= 3:
                            mkt.append(["SELL", item, min(q, 5 if day < 28 else 15)])

            elif hour == 11 and day >= 8:
                for item in ("MILK", "EGG"):
                    q = int(shed.get(item) or 0)
                    if q >= 2:
                        mkt.append(["SELL", item, min(q, 3)])

            # terminal days: extra dump at h1 (already) + h7
            if day >= 28 and hour in (7, 8):
                for item in ("CARROT", "STRAWBERRY", "WHEAT", "EGG", "MILK", "WOOL", "TOMATO", "MELON"):
                    q = int(shed.get(item) or 0)
                    if q > 0:
                        mkt.append(["SELL", item, q])

            # ===== PHYSICAL (from p110 farmer profile) =====
            crop = pick_crop(day, seeds)
            if hour in (2, 3):
                f = ["WEST"] if hour == 2 else ["NORTH"]
                hands = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]]
            elif hour == 4:
                f = ["COLLECT_FERTILIZER"]
                hands = [["COLLECT_FERTILIZER"] for _ in range(max(hands_n, 1))]
            elif hour in (5, 6):
                f = ["FEED"] if hour == 5 else ["CARE"]
                hands = [["FEED"] if hour == 5 else ["CARE"] for _ in range(max(hands_n, 1))]
            elif hour in (7, 8):
                f = ["CARE"] if hour == 7 else ["DROP"]
                hands = [["CARE"] if hour == 7 else ["DROP"] for _ in range(max(hands_n, 1))]
            elif hour in (9, 10):
                f = ["EAST"] if hour == 9 else ["SOUTH"]
                hands = [["PASS"] for _ in range(max(hands_n, 1))]
            elif hour in (11, 12):
                f = ["DROP"] if hour == 11 else ["PASS"]
                hands = [["DROP"] for _ in range(max(hands_n, 1))]
            elif hour == 13 and day >= 9 and day <= 12:
                # build coop wave for geese
                f = ["BUILD_COOP"]
                hands = [["BUILD_COOP"] for _ in range(min(max(hands_n, 1), 4))]
            else:
                # plant/water/harvest
                if day >= 25 and hour % 3 == 0:
                    f = ["HARVEST"]
                    hands = [["HARVEST"] if i % 2 == 0 else ["WATER"] for i in range(max(hands_n, 1))]
                elif hour % 2 == 1:
                    f = ["PLANT", crop]
                    hands = [["PLANT", crop] if i % 2 == 1 else ["WATER"] for i in range(max(hands_n, 1))]
                else:
                    f = ["WATER"]
                    hands = [["WATER"] if i % 2 == 0 else ["PLANT", crop] for i in range(max(hands_n, 1))]

            return {"farmer": f, "hands": pad(hands, hands_n), "market": mkt}
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
                rows.append({"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
               "mean_margin": (sum(margins) / len(margins)) if margins else None}
    return rows, summary


def gate(name, make, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
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
    name = "farm_os_v2"
    if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
        print("skip", name, flush=True)
    else:
        gate(name, farm_os_v2, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"), rec.get("metav4", {}).get("summary"), rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
