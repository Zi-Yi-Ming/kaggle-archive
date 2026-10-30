# -*- coding: utf-8 -*-
"""P104e debug: run tape clone one game, log money/errors every 24 steps."""
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
TAPE = json.loads((PROJ / "_research" / "p104_gold_tape.json").read_text(encoding="utf-8"))["tape"]


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


LOG = []


def spy_clone(obs, configuration=None):
    step = int((obs or {}).get("step", 0))
    farms = (obs or {}).get("farms") or []
    me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
    farm = farms[me] if me < len(farms) else {}
    money = farm.get("money") if isinstance(farm, dict) else None
    hands_n = len(farm.get("hands") or []) if isinstance(farm, dict) else 0
    priv = (obs or {}).get("private") or {}
    shed = priv.get("shed") or {}
    fert = shed.get("FERTILIZER")

    if step < len(TAPE):
        t = TAPE[step]
        act = {"farmer": list(t["farmer"]), "hands": [list(h) for h in t["hands"]], "market": [list(o) for o in t["market"]]}
    else:
        n = hands_n
        act = {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(n)], "market": []}

    if step % 24 == 0 or step < 10 or step in (28, 30, 72, 73):
        LOG.append({
            "s": step, "money": money, "hands": hands_n, "fert": fert,
            "tape_hands": len(TAPE[step]["hands"]) if step < len(TAPE) else None,
            "mkt_n": len(act["market"]),
        })
    return act


def main():
    o = load_mv("mv")
    # wrap o to log too
    b0, b1, st, sec = p79.run(spy_clone, o, 1)
    print("result", b0, b1, st, sec, flush=True)
    print("LOG:", flush=True)
    for row in LOG:
        print(row, flush=True)


if __name__ == "__main__":
    main()
