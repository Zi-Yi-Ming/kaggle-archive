# -*- coding: utf-8 -*-
"""P144: fert route on idle hands only + always sell fert. H3x base."""
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
OUTJSON = PROJ / "_research" / "p144_fert_route.json"
CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def call(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs, obs and configuration)


def make(tag, start=642):
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            day, hour = step // 24, step % 24
            if not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            farmer = list(action.get("farmer") or ["PASS"])
            hands = [list(h) for h in (action.get("hands") or [])]
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0 and not any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in m):
                m.append(["SELL", "FERTILIZER", fert])
            if day >= 1 and hour in (2, 3, 4):
                for i in range(len(hands)):
                    if hands[i] == ["PASS"]:
                        hands[i] = ["WEST"] if hour == 2 else (["NORTH"] if hour == 3 else ["COLLECT_FERTILIZER"])
            if step >= start:
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                for item in CASH:
                    if item in already:
                        continue
                    stock = int(shed.get(item, 0) or 0)
                    if stock <= 0 or int(prices.get(item, 0) or 0) < 1:
                        continue
                    if len(m) >= 10:
                        break
                    m.append(["SELL", item, min(stock, 60)])
                    already.add(item)
            return dict(action, market=m, farmer=farmer, hands=hands)
        except Exception:
            return action

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
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
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    payload = {"fert_route": {}}
    rec = payload["fert_route"]
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4, 5, 6), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
    ):
        print(f"\n== vs {opp_name} ==", flush=True)
        rec[key] = series(make, opp_path, seeds, f"fr_{opp_name}")
        print("SUM", key, rec[key], flush=True)
    print("VERDICT", rec, "H3x=+508", flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
