# -*- coding: utf-8 -*-
"""P128: fine grid around start=636 (current best +428)."""
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
OUTJSON = PROJ / "_research" / "p128_fine_grid.json"
CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


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


def make(tag, start=636, cap=60, min_px=1, max_orders=10):
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
            for item in CASH:
                if item in already:
                    continue
                stock = int(shed.get(item) or 0)
                if stock <= 0 or int(prices.get(item, 0) or 0) < min_px:
                    continue
                if len(m) >= max_orders:
                    break
                m.append(["SELL", item, min(stock, cap)])
                already.add(item)
            return dict(action, market=m) if m else action
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
    payload = {"results": []}
    grid = [
        (630, 60, 1, 10), (636, 60, 1, 10), (642, 60, 1, 10), (648, 60, 1, 10),
        (636, 100, 1, 10), (636, 60, 2, 10),
    ]
    best = None
    for start, cap, min_px, maxo in grid:
        name = f"s{start}_c{cap}_px{min_px}_m{maxo}"
        print(f"\n==== {name} ====", flush=True)
        mv = series(lambda tag: make(tag, start, cap, min_px, maxo), METAV4, (1, 2, 3, 4, 5, 6), name)
        print("MV", name, mv, flush=True)
        payload["results"].append({"name": name, "mv": mv, "start": start, "cap": cap})
        if best is None or (mv.get("mean_margin") or -1e9) > (best[1].get("mean_margin") or -1e9):
            best = (name, mv)
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["best"] = {"name": best[0], "mv": best[1]} if best else None
    print("\nBEST", payload["best"], "vs 636=+428", flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
