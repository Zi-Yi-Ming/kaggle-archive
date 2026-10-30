# -*- coding: utf-8 -*-
"""P138: best gold tape (129k game) open-loop + time-split to H3x."""
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
BEST = json.loads((PROJ / "_research" / "p137_best_tape.json").read_text(encoding="utf-8"))["tape"]
OLD = json.loads((PROJ / "_research" / "p104_gold_full_tape.json").read_text(encoding="utf-8"))["tape"]
OUTJSON = PROJ / "_research" / "p138_best_tape.json"
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


def pad(cmds, n):
    cmds = [list(c) for c in (cmds or [])]
    if len(cmds) > n:
        return cmds[:n]
    while len(cmds) < n:
        cmds.append(["PASS"])
    return cmds


def tape_agent(tape):
    def agent(obs, configuration=None):
        step = int((obs or {}).get("step", 0))
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = farms[me] if me < len(farms) and isinstance(farms[me], dict) else {}
        live_n = len(farm.get("hands") or [])
        t = tape[step] if step < len(tape) else {"f": ["PASS"], "h": [], "m": []}
        return {"farmer": list(t.get("f") or ["PASS"]), "hands": pad(t.get("h"), live_n),
                "market": [list(o) for o in (t.get("m") or [])]}
    return agent


def split_agent(tape, switch=240, start=642):
    parent = load_mv("mv")

    def agent(obs, configuration=None):
        step = int((obs or {}).get("step", 0))
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = farms[me] if me < len(farms) and isinstance(farms[me], dict) else {}
        live_n = len(farm.get("hands") or [])
        if step < switch:
            t = tape[step] if step < len(tape) else {"f": ["PASS"], "h": [], "m": []}
            return {"farmer": list(t.get("f") or ["PASS"]), "hands": pad(t.get("h"), live_n),
                    "market": [list(o) for o in (t.get("m") or [])]}
        action = call(parent, obs, configuration)
        if not isinstance(action, dict):
            action = {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(live_n)], "market": []}
        if step >= start:
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
            for item in CASH:
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0 or int(prices.get(item, 0) or 0) < 1:
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(stock, 60)])
            action = dict(action, market=m)
        return action
    return agent


def series(fn, seeds):
    ends = []
    for seed in seeds:
        b0, b1, stt, sec = p79.run(fn, p79.load_quiet(METAV4, f"o{seed}"), seed)
        ends.append(b0)
        print(f"  s={seed} cand={b0:.0f} mv={b1:.0f} m={b0-b1:.0f}", flush=True)
    return {"mean_cand": sum(ends) / len(ends), "ends": ends}


def main():
    payload = {}
    print("== OLD tape open ==", flush=True)
    payload["old_open"] = series(tape_agent(OLD), (1, 2, 3))
    print("== BEST tape open ==", flush=True)
    payload["best_open"] = series(tape_agent(BEST), (1, 2, 3))
    print("== BEST->d9->H3x ==", flush=True)
    payload["best_split"] = series(split_agent(BEST, 240), (1, 2, 3))
    print("== OLD->d9->H3x ==", flush=True)
    payload["old_split"] = series(split_agent(OLD, 240), (1, 2, 3))
    print("RESULT", payload, flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
