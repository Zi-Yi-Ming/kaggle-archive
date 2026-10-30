# -*- coding: utf-8 -*-
"""P114: more local knobs on H3+ (gold: RL only small). start x cap grid + mid drip."""
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
OUTJSON = PROJ / "_research" / "p114_knobs2.json"
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


def make(tag, start=624, cap=60, mid_drip=False):
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not isinstance(action, dict):
                return action
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            if mid_drip and 240 <= step < start and step % 12 == 0:
                for item, stock in shed.items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), 8)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
            if step >= start:
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
        (612, 60, False), (624, 60, False), (636, 60, False),
        (624, 45, False), (624, 80, False),
        (624, 60, True),
    ]
    best = None
    for start, cap, drip in grid:
        name = f"s{start}_c{cap}_d{int(drip)}"
        print(f"\n==== {name} vs metav4 ====", flush=True)
        mv = series(lambda tag: make(tag, start, cap, drip), METAV4, (1, 2, 3, 4, 5, 6), name)
        print("MV", name, mv, flush=True)
        payload["results"].append({"name": name, "start": start, "cap": cap, "drip": drip, "mv": mv})
        if best is None or (mv.get("mean_margin") or -1e9) > (best[1].get("mean_margin") or -1e9):
            best = (name, mv, start, cap, drip)
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["best"] = {"name": best[0], "mv": best[1], "start": best[2], "cap": best[3], "drip": best[4]} if best else None
    print("\nBEST", payload["best"], flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
