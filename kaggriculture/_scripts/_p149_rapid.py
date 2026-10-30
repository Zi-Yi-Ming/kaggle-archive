# -*- coding: utf-8 -*-
"""P149: rapid terminal grid."""
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
OUTJSON = PROJ / "_research" / "p149_rapid.json"
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


def make(tag, start, cap, min_stock=1, only_high=False):
    parent = load_mv(tag)
    items = ("STRAWBERRY", "MELON", "MILK", "WOOL") if only_high else CASH

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
            for item in items:
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock < min_stock or int(prices.get(item, 0) or 0) < 1:
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(stock, cap)])
                already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def eval_one(name, **kw):
    wins = 0
    margins = []
    for seed in (1, 2, 3, 4):
        for seat0 in (True, False):
            try:
                c = make(f"c_{name}_{seed}_{int(seat0)}", **kw)
                o = p79.load_quiet(METAV4, f"o_{name}_{seed}_{int(seat0)}")
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
                print(f"  {name} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"  FAIL {name} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    grid = [
        ("s636_c60", dict(start=636, cap=60)),
        ("s642_c60", dict(start=642, cap=60)),
        ("s642_c80", dict(start=642, cap=80)),
        ("s630_c60", dict(start=630, cap=60)),
        ("s636_c80_hi", dict(start=636, cap=80, only_high=True)),
        ("s642_c60_s2", dict(start=642, cap=60, min_stock=2)),
    ]
    payload = {}
    best = None
    for name, kw in grid:
        print(f"\n==== {name} ====", flush=True)
        mv = eval_one(name, **kw)
        print("SUM", name, mv, flush=True)
        payload[name] = mv
        if best is None or (mv.get("mean_margin") or -1e9) > (best[1].get("mean_margin") or -1e9):
            best = (name, mv)
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nBEST", best, flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
