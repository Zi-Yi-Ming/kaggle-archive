# -*- coding: utf-8 -*-
"""P109: local bandit on H3 terminal cap (gold: RL only on small knobs)."""
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
OUTJSON = PROJ / "_research" / "p109_cap_bandit.json"
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


def make_h3(tag, start=648, cap=60):
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
            for item, stock in shed.items():
                if item in INPUTS or item in already:
                    continue
                q = min(int(stock or 0), cap)
                if q > 0:
                    m.append(["SELL", item, q])
                    already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def eval_cap(cap, start, seeds=(1, 2, 3, 4, 5, 6, 7, 8)):
    wins = 0
    margins = []
    for seed in seeds:
        c = lambda obs, configuration=None, tag=f"c{cap}_{start}_{seed}": make_h3(tag, start, cap)(obs, configuration)
        # rebuild properly
        c = make_h3(f"c_{cap}_{start}_{seed}", start, cap)
        o = p79.load_quiet(METAV4, f"o_{cap}_{start}_{seed}")
        b0, b1, stt, sec = p79.run(c, o, seed)
        margin = b0 - b1
        win = b0 > b1
        wins += int(win)
        margins.append(margin)
        print(f"  cap={cap} start={start} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
    n = len(margins)
    return {
        "cap": cap, "start": start, "n": n, "wins": wins,
        "win_rate": wins / n, "mean_margin": sum(margins) / n,
        "margins": margins,
    }


def main():
    payload = {"results": []}
    # local knob search: cap x start
    grid = [
        (50, 648), (60, 648), (70, 648), (80, 648),
        (60, 624), (60, 672),
    ]
    best = None
    for cap, start in grid:
        print(f"\n==== cap={cap} start={start} ====", flush=True)
        r = eval_cap(cap, start)
        payload["results"].append(r)
        print("SUM", r["win_rate"], r["mean_margin"], flush=True)
        if best is None or r["mean_margin"] > best["mean_margin"]:
            best = r
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["best"] = best
    print("\nBEST", best, flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
