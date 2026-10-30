# -*- coding: utf-8 -*-
"""P104c: gold tape prefix (72 steps exact) + reactive tail. Correct action shapes."""
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
TAPE = json.loads((PROJ / "_research" / "p104_gold_tape.json").read_text(encoding="utf-8"))["tape"]
OUTJSON = PROJ / "_research" / "p104c_gold_tape_clone.json"

CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


def gold_tape_clone(tag: str):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            # exact gold tape for first 72 steps (deterministic 24/24)
            if step < len(TAPE):
                t = TAPE[step]
                return {
                    "farmer": list(t["farmer"]),
                    "hands": [list(h) for h in t["hands"]],
                    "market": [list(o) for o in t["market"]],
                }

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
            market = (obs or {}).get("market") or {}
            px = market.get("prices") or {}

            mkt = []
            # daily hire (gold: 6 then 9-13)
            if hour == 1:
                n = 6 if day <= 5 else (10 if day == 6 else 9)
                n = min(n, 10, max(0, (13 - hands_n)))
                for _ in range(max(n, 0)):
                    if money > 20:
                        mkt.append(["HIRE"])
                        money -= 15
            # 白饭 sell fert
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0:
                mkt.append(["SELL", "FERTILIZER", min(fert, 2 if day < 8 else 5)])
            # seeds
            if money > 100:
                if seeds.get("MELON", 0) < 6:
                    mkt.append(["BUY_SEED", "MELON", 1])
                if seeds.get("STRAWBERRY", 0) < 8 and day >= 2:
                    mkt.append(["BUY_SEED", "STRAWBERRY", 1])
                if seeds.get("WHEAT", 0) < 4:
                    mkt.append(["BUY_SEED", "WHEAT", 1])
            # land / animals
            if step == 152:
                mkt.append(["BUY_LAND"])
            if step in (154, 217, 242, 265) and money > 500:
                mkt.append(["BUY_ANIMAL", "COW", 2])
                mkt.append(["BUY_ANIMAL", "GOOSE", 2])
            if step in (217, 242) and money > 2000:
                mkt.append(["BUY_LAND"])
            # product sells
            if day >= 6:
                cap = 6 if day < 18 else (15 if day < 28 else 35)
                for item in CASH + ("WHEAT",):
                    q = int(shed.get(item) or 0)
                    if q >= 2:
                        mkt.append(["SELL", item, min(q, cap)])

            # physical: fert collect / feed / care / plant-water cycle
            hands = []
            if hour in (2, 3):
                f = ["WEST"] if hour == 2 else ["NORTH"]
                hands = [["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]][:hands_n] or [["PASS"] for _ in range(hands_n)]
            elif hour == 4:
                f = ["COLLECT_FERTILIZER"]
                hands = [["COLLECT_FERTILIZER"] for _ in range(hands_n)]
            elif hour in (5, 6):
                f = ["EAST"] if hour == 5 else ["SOUTH"]
                hands = [["FEED"] for _ in range(hands_n)]
            elif hour in (7, 8):
                f = ["CARE"] if hour == 7 else ["DROP"]
                hands = [["CARE"] for _ in range(hands_n)]
            elif hour in (11, 12):
                f = ["DROP"]
                hands = [["DROP"] for _ in range(hands_n)]
            elif hour >= 13 or hour in (9, 10):
                crop = "STRAWBERRY" if seeds.get("STRAWBERRY", 0) else ("MELON" if seeds.get("MELON", 0) else "WHEAT")
                if hour % 2 == 1:
                    f = ["PLANT", crop]
                else:
                    f = ["WATER"]
                hands = []
                for i in range(hands_n):
                    hands.append(["PLANT", crop] if (i % 2) == (hour % 2) else ["WATER"])
            else:
                f = ["PASS"]
                hands = [["PASS"] for _ in range(hands_n)]

            return {"farmer": f, "hands": hands, "market": mkt}
        except Exception:
            n = 0
            try:
                n = len(((obs or {}).get("farms") or [[]])[0].get("hands") or [])
            except Exception:
                n = 0
            return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(n)], "market": []}

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
    name = "tape_clone"
    if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
        print("skip", name, flush=True)
    else:
        gate(name, gold_tape_clone, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"), rec.get("metav4", {}).get("summary"), rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
