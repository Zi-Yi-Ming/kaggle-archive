# -*- coding: utf-8 -*-
"""P105 Gold Farm OS: daily-hire multi-unit scheduler + fert cash + timed sells.

Fixes vs prior clones:
  - REHIRE every day at hour 1 (hands expire daily)
  - Navigate to fert post then COLLECT_FERTILIZER (白饭 cash)
  - Animal FEED/CARE loop
  - Plant/water with correct action shapes [op, item?]
  - Sells follow gold's day-profile (trickle -> ramp -> late dump), NOT greedy dump
  - Pad hands to live count so engine doesn't reject the turn

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
OUTJSON = PROJ / "_research" / "p105_farm_os.json"

# gold sell-by-day qty profile (from p103 recon, averaged)
SELL_BUDGET = {
    1: 5, 2: 5, 3: 5, 4: 5, 5: 10, 6: 30, 7: 10, 8: 20, 9: 5,
    10: 55, 11: 15, 12: 40, 13: 50, 14: 60, 15: 65, 16: 60,
    17: 75, 18: 70, 19: 80, 20: 85, 21: 70, 22: 95, 23: 70,
    24: 85, 25: 85, 26: 100, 27: 100, 28: 160, 29: 150,
}

CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


def farm_os(tag: str):
    st = {"day": -1, "hired": 0, "sold_today": 0, "pasture_built": 0, "phase": "open"}

    def pad_hands(cmds, n):
        cmds = [list(c) for c in (cmds or [])]
        if len(cmds) > n:
            return cmds[:n]
        while len(cmds) < n:
            cmds.append(["PASS"])
        return cmds

    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            day = step // 24
            hour = step % 24
            if day != st["day"]:
                st["day"] = day
                st["hired"] = 0
                st["sold_today"] = 0

            priv = (obs or {}).get("private") or {}
            shed = dict(priv.get("shed") or {})
            seeds = dict(priv.get("seeds") or {})
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if 0 <= me < len(farms) and isinstance(farms[me], dict) else {}
            money = float(farm.get("money") or 0)
            hands_n = len(farm.get("hands") or [])
            px = ((obs.get("market") or {}).get("prices") or {})

            mkt = []
            f_act = ["PASS"]
            hand_cmds = []

            # ================= MARKET =================
            # --- day0 exact gold open ---
            if step == 1:
                mkt = [
                    ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
                    ["BUY_PRODUCT", "WHEAT", 5],
                    ["BUY_ANIMAL", "COW", 2],
                    ["BUY_SEED", "MELON", 6],
                    ["BUY_ANIMAL", "SHEEP", 3],
                    ["BUY_SEED", "WHEAT", 2],
                ]
                st["hired"] = 5
            elif hour == 1:
                # daily rehire (hands expired)
                n = 6 if day <= 5 else (10 if day == 6 else 9)
                n = min(n, 10)
                for _ in range(n):
                    mkt.append(["HIRE"])
                st["hired"] += n
                if day <= 4 and money > 60:
                    mkt.append(["BUY_PRODUCT", "WHEAT", 2])

            # 白饭: sell free fert continuously
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0:
                mkt.append(["SELL", "FERTILIZER", min(fert, 2 if day < 8 else 4)])

            # seeds keep topped up
            if money > 80:
                if seeds.get("MELON", 0) < 6:
                    mkt.append(["BUY_SEED", "MELON", 1])
                if day >= 2 and seeds.get("STRAWBERRY", 0) < 8 and money > 120:
                    mkt.append(["BUY_SEED", "STRAWBERRY", 1])
                if seeds.get("WHEAT", 0) < 3 and money > 30:
                    mkt.append(["BUY_SEED", "WHEAT", 1])

            # land + animals at gold's steps
            if step == 152:
                mkt.append(["BUY_LAND"])
            if step in (217, 242) and money > 2500:
                mkt.append(["BUY_LAND"])
            if step == 154 and money > 800:
                mkt.append(["BUY_ANIMAL", "COW", 3])
            if step == 217 and money > 600:
                mkt.append(["BUY_ANIMAL", "GOOSE", 2])
                mkt.append(["BUY_ANIMAL", "COW", 1])
            if step == 242 and money > 600:
                mkt.append(["BUY_ANIMAL", "SHEEP", 2])
                mkt.append(["BUY_ANIMAL", "GOOSE", 1])
            if step == 265 and money > 1500:
                mkt.append(["BUY_ANIMAL", "GOOSE", 6])

            # timed product sells (NOT greedy): follow day budget
            budget = SELL_BUDGET.get(day, 40)
            already_q = 0
            already = {}
            for o in mkt:
                if len(o) >= 3 and o[0] == "SELL":
                    already[o[1]] = already.get(o[1], 0) + int(o[2] or 0)
                    already_q += int(o[2] or 0)
            room = max(0, budget - already_q - st["sold_today"])
            if room > 0 and day >= 1:
                # prefer cash goods, skip inputs except fert already handled
                for item in CASH + ("WHEAT",):
                    if room <= 0:
                        break
                    stock = int(shed.get(item) or 0) - already.get(item, 0)
                    if stock <= 0:
                        continue
                    q = min(stock, room, 8 if day < 15 else (20 if day < 28 else 40))
                    if q > 0:
                        mkt.append(["SELL", item, q])
                        room -= q
                        st["sold_today"] += q

            # ================= PHYSICAL =================
            if step <= 23:
                # gold day0 tape (exact shapes)
                OPEN = {
                    0: (["PASS"], []),
                    1: (["PASS"], []),
                    2: (["PICKUP", "COW", 1], [["PICKUP", "SHEEP", 1], ["PICKUP", "SHEEP", 1], ["PASS"], ["PICKUP", "COW", 1], ["PICKUP", "SHEEP", 1]]),
                    3: (["PICKUP", "WHEAT", 1], [["PICKUP"], ["PICKUP"], ["PASS"], ["PICKUP"], ["PICKUP"]]),
                    4: (["WEST"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["WEST"]]),
                    5: (["NORTH"], [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["BUILD_PASTURE"]]),
                    6: (["BUILD_PASTURE"], [["BUILD_PASTURE"], ["BUILD_PASTURE"], ["PASS"], ["BUILD_PASTURE"], ["PLACE", "SHEEP"]]),
                    7: (["PLACE", "COW"], [["PLACE", "SHEEP"], ["PLACE", "SHEEP"], ["PASS"], ["PLACE", "COW"], ["FEED"]]),
                    8: (["FEED"], [["FEED"], ["FEED"], ["PASS"], ["FEED"], ["CARE"]]),
                    9: (["CARE"], [["CARE"], ["CARE"], ["PASS"], ["CARE"], ["DROP"]]),
                    10: (["EAST"], [["EAST"], ["SOUTH"], ["PASS"], ["SOUTH"], ["WEST"]]),
                    11: (["SOUTH"], [["DROP"], ["DROP"], ["PASS"], ["SOUTH"], ["WEST"]]),
                    12: (["DROP"], [["PASS"], ["NORTH"], ["PASS"], ["DROP"], ["WEST"]]),
                }
                if step in OPEN:
                    f_act, hand_cmds = OPEN[step]
                elif 13 <= step <= 23:
                    f_act = ["PLANT", "MELON"] if hour % 2 == 1 else ["WATER"]
                    hand_cmds = []
                    for i in range(5):
                        if i in (3, 4):
                            hand_cmds.append(["PLANT", "MELON"] if (i + hour) % 2 == 1 else ["WATER"])
                        else:
                            hand_cmds.append(["PASS"])
            elif hour == 2:
                f_act = ["WEST"]
                hand_cmds = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]]
            elif hour == 3:
                f_act = ["NORTH"]
                hand_cmds = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]]
            elif hour == 4:
                f_act = ["COLLECT_FERTILIZER"]
                hand_cmds = [["COLLECT_FERTILIZER"] for _ in range(max(hands_n, 1))]
            elif hour in (5, 6):
                f_act = ["EAST"] if hour == 5 else ["SOUTH"]
                hand_cmds = [["FEED"] for _ in range(max(hands_n, 1))]
            elif hour in (7, 8):
                f_act = ["CARE"] if hour == 7 else ["DROP"]
                hand_cmds = [["CARE"] if hour == 7 else ["DROP"] for _ in range(max(hands_n, 1))]
            elif hour in (9, 10):
                f_act = ["EAST"] if hour == 9 else ["SOUTH"]
                hand_cmds = [["PASS"] for _ in range(max(hands_n, 1))]
            elif hour in (11, 12):
                f_act = ["DROP"]
                hand_cmds = [["DROP"] for _ in range(max(hands_n, 1))]
            elif hour >= 13 or hour in (0, 1):
                crop = "STRAWBERRY" if seeds.get("STRAWBERRY", 0) else ("MELON" if seeds.get("MELON", 0) else "WHEAT")
                if hour % 2 == 1:
                    f_act = ["PLANT", crop]
                else:
                    f_act = ["WATER"]
                hand_cmds = []
                for i in range(max(hands_n, 1)):
                    if i % 2 == hour % 2:
                        hand_cmds.append(["PLANT", crop] if hour % 2 == 1 else ["WATER"])
                    else:
                        hand_cmds.append(["PASS"])
            else:
                f_act = ["PASS"]
                hand_cmds = [["PASS"] for _ in range(max(hands_n, 0))]

            return {
                "farmer": f_act,
                "hands": pad_hands(hand_cmds, hands_n),
                "market": mkt,
            }
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
    name = "farm_os"
    if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
        print("skip", name, flush=True)
    else:
        gate(name, farm_os, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"), rec.get("metav4", {}).get("summary"), rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
