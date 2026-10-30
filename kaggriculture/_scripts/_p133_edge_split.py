# -*- coding: utf-8 -*-
"""P133: where is gold's edge? tape market vs tape physical, separately."""
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
TAPE = json.loads((PROJ / "_research" / "p104_gold_full_tape.json").read_text(encoding="utf-8"))["tape"]
OUTJSON = PROJ / "_research" / "p133_edge_split.json"
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


def gold_full(tag):
    def agent(obs, configuration=None):
        step = int((obs or {}).get("step", 0))
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = farms[me] if me < len(farms) else {}
        live_n = len(farm.get("hands") or []) if isinstance(farm, dict) else 0
        t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}
        return {"farmer": list(t.get("f") or ["PASS"]), "hands": pad(t.get("h"), live_n),
                "market": [list(o) for o in (t.get("m") or [])]}
    return agent


def gold_mkt_on_mv(tag, start=642):
    """Metav4 physical + gold tape MARKET + H3x terminal."""
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        step = int((obs or {}).get("step", 0))
        t = TAPE[step] if step < len(TAPE) else {"m": []}
        m = [list(o) for o in (t.get("m") or [])]
        # plus terminal cash
        if step >= start:
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
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
        if isinstance(action, dict):
            return dict(action, market=m)
        return {"farmer": ["PASS"], "hands": [], "market": m}
    return agent


def gold_phys_on_mv(tag, start=642):
    """Metav4 market + gold tape PHYSICAL + H3x terminal on market."""
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        step = int((obs or {}).get("step", 0))
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = farms[me] if me < len(farms) else {}
        live_n = len(farm.get("hands") or []) if isinstance(farm, dict) else 0
        t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": []}
        m = [list(o) for o in ((action.get("market") if isinstance(action, dict) else []) or [])]
        if step >= start:
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
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
        return {"farmer": list(t.get("f") or ["PASS"]), "hands": pad(t.get("h"), live_n), "market": m}
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
    payload = {}
    for name, fn in (
        ("gold_full_tape", gold_full),
        ("gold_mkt_on_mv", gold_mkt_on_mv),
        ("gold_phys_on_mv", gold_phys_on_mv),
    ):
        print(f"\n==== {name} vs metav4 ====", flush=True)
        mv = series(fn, METAV4, (1, 2, 3), name)
        print("MV", name, mv, flush=True)
        payload[name] = mv
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nEDGE SPLIT (cand money vs mv):", payload, flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
