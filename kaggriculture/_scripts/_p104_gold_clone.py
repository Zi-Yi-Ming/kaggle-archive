# -*- coding: utf-8 -*-
"""P104 Gold Clone: reconstruct 吃白饭的大肥鱼 opening + free-fert cash + labor farm.

NOT a Metav4 patch. Fresh chassis:
  - day0 tape: 5 HIRE + animals + seeds, build pasture, place cow, feed/care
  - day1+: 6 HIRE/day early, COLLECT_FERTILIZER -> SELL FERTILIZER (白饭)
  - animal waves + land unlocks at steps 154/217/242/265
  - continuous plant/water/harvest + product sells from day 6
  - final dump day 28-29

Dual-gate only.
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
OUTJSON = PROJ / "_research/p104_gold_clone.json"

MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


def gold_clone(tag: str):
    """Deterministic-ish gold clone based on replay recon."""
    st = {"hires_today": 0, "day": -1, "built_pasture": 0, "built_coop": 0}

    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            day = step // 24
            hour = step % 24
            priv = (obs or {}).get("private") or {}
            shed = dict(priv.get("shed") or {})
            seeds = dict(priv.get("seeds") or {})
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if 0 <= me < len(farms) and isinstance(farms[me], dict) else {}
            money = float(farm.get("money") or 0)
            hands_n = len(farm.get("hands") or [])
            tiles = farm.get("tiles") or []
            farmer = farm.get("farmer") or [4, 4]
            market = (obs or {}).get("market") or {}
            px = market.get("prices") or {}

            if day != st["day"]:
                st["day"] = day
                st["hires_today"] = 0

            mkt = []
            hands = []
            f_act = ["PASS"]

            # ---------- market ----------
            if step == 1:
                # exact gold open
                mkt = [
                    ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
                    ["BUY_PRODUCT", "WHEAT", 5],
                    ["BUY_ANIMAL", "COW", 2],
                    ["BUY_SEED", "MELON", 6],
                    ["BUY_ANIMAL", "SHEEP", 3],
                    ["BUY_SEED", "WHEAT", 2],
                ]
                st["hires_today"] = 5
            elif hour == 1 and 1 <= day <= 29:
                # daily hire wave
                n = 5 if day == 0 else (6 if day <= 5 else (10 if day == 6 else 9))
                n = min(n, 10)
                for _ in range(n):
                    mkt.append(["HIRE"])
                st["hires_today"] += n
                # small wheat feed
                if money > 80 and day <= 5:
                    mkt.append(["BUY_PRODUCT", "WHEAT", 2])
            # 白饭: sell free fertilizer
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0 and step >= 28:
                sell_q = min(fert, 2 if day < 6 else 4)
                if sell_q > 0:
                    mkt.append(["SELL", "FERTILIZER", sell_q])
            # seeds keep coming
            if step == 2 or (hour in (5, 6, 7) and day in (1, 2, 3, 4, 5) and money > 50):
                if seeds.get("MELON", 0) < 8 and money > 200:
                    mkt.append(["BUY_SEED", "MELON", 1])
                if seeds.get("WHEAT", 0) < 6 and money > 40:
                    mkt.append(["BUY_SEED", "WHEAT", 1])
                if day >= 2 and seeds.get("STRAWBERRY", 0) < 6 and money > 150:
                    mkt.append(["BUY_SEED", "STRAWBERRY", 1])
            # land unlocks
            if step == 152:
                mkt.append(["BUY_LAND"])
            if step in (217, 242, 265) and money > 2000:
                mkt.append(["BUY_LAND"])
            # animal waves
            if step == 154 and money > 800:
                mkt.append(["BUY_ANIMAL", "COW", 3])
            if step in (217, 242) and money > 600:
                mkt.append(["BUY_ANIMAL", "GOOSE", 2])
                mkt.append(["BUY_ANIMAL", "COW", 1])
            if step == 265 and money > 1500:
                mkt.append(["BUY_ANIMAL", "GOOSE", 6])
            # product sells from day 6 (keep cash flow) + terminal
            if day >= 6:
                cap = 8 if day < 20 else (20 if day < 28 else 40)
                for item in ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT", "WHEAT"):
                    q = int(shed.get(item) or 0)
                    if q >= 3:
                        mkt.append(["SELL", item, min(q, cap)])

            # ---------- physical: day0 choreography ----------
            # replay day0 is a tight script; approximate
            if step == 2:
                f_act = ["PICKUP", "COW", 1]
                hands = [["PICKUP"], ["PICKUP"], ["PASS"], ["PICKUP"], ["PICKUP"]]
            elif step == 3:
                f_act = ["PICKUP", "WHEAT", 1]
                hands = [["PICKUP"], ["PICKUP"], ["PASS"], ["PICKUP"], ["PICKUP"]]
            elif step == 4:
                f_act = ["WEST"]
                hands = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["WEST"]]
            elif step == 5:
                f_act = ["NORTH"]
                hands = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["BUILD_PASTURE"]]
            elif step == 6:
                f_act = ["BUILD_PASTURE"]
                hands = [["BUILD_PASTURE"], ["BUILD_PASTURE"], ["PASS"], ["BUILD_PASTURE"], ["PLACE"]]
            elif step == 7:
                f_act = ["PLACE", "COW"]
                hands = [["PLACE"], ["PLACE"], ["PASS"], ["PLACE"], ["FEED"]]
            elif step == 8:
                f_act = ["FEED"]
                hands = [["FEED"], ["FEED"], ["PASS"], ["FEED"], ["CARE"]]
            elif step == 9:
                f_act = ["CARE"]
                hands = [["CARE"], ["CARE"], ["PASS"], ["CARE"], ["DROP"]]
            elif step == 10:
                f_act = ["EAST"]
                hands = [["EAST"], ["SOUTH"], ["PASS"], ["SOUTH"], ["WEST"]]
            elif step == 11:
                f_act = ["SOUTH"]
                hands = [["DROP"], ["DROP"], ["PASS"], ["SOUTH"], ["WEST"]]
            elif step == 12:
                f_act = ["DROP"]
                hands = [["PASS"], ["NORTH"], ["PASS"], ["DROP"], ["WEST"]]
            elif 13 <= step <= 23:
                # plant/water melon zone
                seq = ["PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "PASS"]
                if hour % 2 == 1:
                    f_act = ["PLANT", "MELON"]
                else:
                    f_act = ["WATER"]
                # hands alternate plant/water
                hands = []
                for i in range(min(max(hands_n, 5), 6)):
                    if i == 3:
                        hands.append(["PLANT"] if hour % 2 == 1 else ["WATER"])
                    elif i == 4:
                        hands.append(["WATER"] if hour % 2 == 1 else ["PLANT"])
                    else:
                        hands.append(["PASS"])
            else:
                # generic day cycle: go to fert post at h2-4, collect, feed/care, plant/water
                if hour in (2, 3):
                    f_act = ["WEST"] if hour == 2 else ["NORTH"]
                    hands = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]][: max(hands_n, 0)]
                    if hands_n >= 4:
                        hands[3] = ["COLLECT_FERTILIZER"]
                elif hour == 4:
                    f_act = ["COLLECT_FERTILIZER"]
                    hands = [["COLLECT_FERTILIZER"] for _ in range(max(hands_n, 1))]
                elif hour in (5, 6):
                    f_act = ["EAST"] if hour == 5 else ["SOUTH"]
                    hands = [["FEED"] for _ in range(max(hands_n, 1))]
                elif hour in (7, 8):
                    f_act = ["CARE"] if hour == 7 else ["DROP"]
                    hands = [["CARE"] for _ in range(max(hands_n, 1))]
                elif hour in (9, 10):
                    f_act = ["EAST"] if hour == 9 else ["SOUTH"]
                    hands = [["PASS"] for _ in range(max(hands_n, 1))]
                elif hour in (11, 12):
                    f_act = ["DROP"]
                    hands = [["DROP"] for _ in range(max(hands_n, 1))]
                elif hour >= 13:
                    # plant/water
                    crop = "STRAWBERRY" if day >= 2 and seeds.get("STRAWBERRY", 0) > 0 else (
                        "MELON" if seeds.get("MELON", 0) > 0 else "WHEAT"
                    )
                    if hour % 2 == 1:
                        f_act = ["PLANT", crop]
                    else:
                        f_act = ["WATER"]
                    hands = []
                    for i in range(max(hands_n, 0)):
                        if i % 2 == hour % 2:
                            hands.append(["PLANT", crop] if hour % 2 == 1 else ["WATER"])
                        else:
                            hands.append(["PASS"])
                else:
                    f_act = ["PASS"]
                    hands = [["PASS"] for _ in range(max(hands_n, 0))]

            return {"farmer": f_act, "hands": hands, "market": mkt}
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
    name = "gold_clone"
    if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
        print("skip", name, flush=True)
    else:
        gate(name, gold_clone, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"), rec.get("metav4", {}).get("summary"), rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
