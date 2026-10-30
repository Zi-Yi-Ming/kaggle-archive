# -*- coding: utf-8 -*-
"""P131: Gold OS v7 — day0 tape + morning fert + evening PASS."""
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
OUTJSON = PROJ / "_research" / "p131_gold_os_v7.json"

DAY0 = {
    0: (["PASS"], [], []),
    1: (["PASS"], [], [["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
        ["BUY_PRODUCT", "WHEAT", 5], ["BUY_ANIMAL", "COW", 2], ["BUY_SEED", "MELON", 6],
        ["BUY_ANIMAL", "SHEEP", 3], ["BUY_SEED", "WHEAT", 2]]),
    2: (["PICKUP", "COW", 1], [["PICKUP", "SHEEP", 1], ["PICKUP", "SHEEP", 1], ["PASS"], ["PICKUP", "COW", 1], ["PICKUP", "SHEEP", 1]], [["BUY_SEED", "WHEAT", 1]]),
    3: (["PICKUP", "WHEAT", 1], [["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1], ["PASS"], ["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1]], []),
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
MORNING = {
    2: (["WEST"], ["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]),
    3: (["NORTH"], ["WEST"], ["NORTH"], ["PASS"], ["NORTH"], ["COLLECT_FERTILIZER"], ["PASS"]),
    4: (["COLLECT_FERTILIZER"], ["COLLECT_FERTILIZER"], ["COLLECT_FERTILIZER"], ["PASS"], ["COLLECT_FERTILIZER"], ["DROP"], ["PASS"]),
    5: (["EAST"], ["EAST"], ["SOUTH"], ["PASS"], ["SOUTH"], ["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1]),
    6: (["SOUTH"], ["DROP"], ["DROP"], ["PASS"], ["SOUTH"], ["WEST"], ["NORTH"]),
    7: (["DROP"], ["PICKUP", "WHEAT", 1], ["PICKUP", "WHEAT", 1], ["PASS"], ["DROP"], ["NORTH"], ["NORTH"]),
    8: (["FEED"], ["WEST"], ["NORTH"], ["PASS"], ["WEST"], ["FEED"], ["NORTH"]),
    9: (["CARE"], ["FEED"], ["FEED"], ["PASS"], ["NORTH"], ["CARE"], ["FEED"]),
    10: (["CARE"], ["CARE"], ["CARE"], ["PASS"], ["NORTH"], ["EAST"], ["CARE"]),
    11: (["DROP"], ["EAST"], ["SOUTH"], ["PASS"], ["NORTH"], ["SOUTH"], ["SOUTH"]),
}


def pad(cmds, n):
    cmds = [list(c) for c in (cmds or [])]
    if len(cmds) > n:
        return cmds[:n]
    while len(cmds) < n:
        cmds.append(["PASS"])
    return cmds


def gold_os_v7(tag: str):
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

            if step <= 23:
                f, h, m = DAY0[step]
                return {"farmer": list(f), "hands": pad(h, max(hands_n, len(h))), "market": [list(o) for o in m]}

            mkt = []
            if hour == 1:
                n = 6 if day <= 5 else (10 if day == 6 else 9)
                for _ in range(min(n, 10)):
                    mkt.append(["HIRE"])
                if money > 50:
                    mkt.append(["BUY_PRODUCT", "WHEAT", 3])
                if money > 150:
                    mkt.append(["BUY_SEED", "MELON" if day <= 5 else ("STRAWBERRY" if day <= 16 else "CARROT"), 2])
                    mkt.append(["BUY_SEED", "WHEAT", 2])
                if day == 6 and money > 2500:
                    mkt.append(["BUY_LAND"])
                if day == 9 and money > 2000:
                    mkt.append(["BUY_LAND"])
                if day == 6 and money > 800:
                    mkt.append(["BUY_ANIMAL", "COW", 3])
            elif 4 <= hour <= 10:
                fert = int(shed.get("FERTILIZER") or 0)
                if fert > 0:
                    mkt.append(["SELL", "FERTILIZER", fert])
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

            if hour in MORNING:
                f, *hs = MORNING[hour]
                return {"farmer": list(f), "hands": pad([list(x) for x in hs], hands_n), "market": mkt}

            if hour >= 14:
                crop = "STRAWBERRY" if day >= 2 and seeds.get("STRAWBERRY", 0) else ("MELON" if seeds.get("MELON", 0) else "WHEAT")
                f = ["PLANT", crop] if hour % 2 == 1 else ["WATER"]
                h = [["PASS"] for _ in range(hands_n)]
                for i in range(3, hands_n):
                    h[i] = ["PLANT", crop] if (i % 2) == (hour % 2) else ["WATER"]
                return {"farmer": f, "hands": pad(h, hands_n), "market": mkt}

            f = ["DROP"] if hour == 12 else ["PASS"]
            h = [[f[0]] for _ in range(hands_n)] if hour == 12 else [["PASS"] for _ in range(hands_n)]
            return {"farmer": f, "hands": pad(h, hands_n), "market": mkt}
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    for seed in seeds:
        c = make_cand(f"c_{label}_{seed}")
        o = p79.load_quiet(opp_path, f"o_{label}_{seed}")
        b0, b1, stt, sec = p79.run(c, o, seed)
        margin = b0 - b1
        win = b0 > b1
        wins += int(win)
        margins.append(margin)
        print(f"{label} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": wins / n, "mean_margin": sum(margins) / n}


def main():
    print("== v7 vs metav4 ==", flush=True)
    mv = series(gold_os_v7, METAV4, (1, 2, 3), "v7")
    print("MV", mv, "(pure tape ~40k)", flush=True)
    OUTJSON.write_text(json.dumps({"mv": mv}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
