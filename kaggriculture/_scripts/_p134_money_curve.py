# -*- coding: utf-8 -*-
"""P134: money curve gold tape vs Metav4 — where does gold lose?"""
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
TAPE = json.loads((PROJ / "_research" / "p104_gold_full_tape.json").read_text(encoding="utf-8"))["tape"]
RESEARCH = PROJ / "_research"


def pad(cmds, n):
    cmds = [list(c) for c in (cmds or [])]
    if len(cmds) > n:
        return cmds[:n]
    while len(cmds) < n:
        cmds.append(["PASS"])
    return cmds


LOG_G, LOG_M = [], []


def gold_full(tag):
    def agent(obs, configuration=None):
        step = int((obs or {}).get("step", 0))
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = {}
        if 0 <= me < len(farms) and isinstance(farms[me], dict):
            farm = farms[me]
        live_n = len(farm.get("hands") or [])
        t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}
        if step % 24 == 0:
            LOG_G.append({"step": step, "money": farm.get("money"), "hands": live_n})
        return {"farmer": list(t.get("f") or ["PASS"]), "hands": pad(t.get("h"), live_n),
                "market": [list(o) for o in (t.get("m") or [])]}
    return agent


def mv_spy(tag):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        step = int((obs or {}).get("step", 0))
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = {}
        if 0 <= me < len(farms) and isinstance(farms[me], dict):
            farm = farms[me]
        if step % 24 == 0:
            LOG_M.append({"step": step, "money": farm.get("money")})
        return fn(obs) if n <= 1 else fn(obs, configuration)
    return agent


def main():
    global LOG_G, LOG_M
    LOG_G, LOG_M = [], []
    b0, b1, st, sec = p79.run(gold_full("g"), mv_spy("m"), 1)
    print("result", b0, b1, flush=True)
    print(f"{'step':>6} {'day':>3} {'gold':>10} {'mv':>10} {'gap':>10}", flush=True)
    for g, m in zip(LOG_G, LOG_M):
        gap = (g["money"] or 0) - (m["money"] or 0)
        print(f"{g['step']:6d} {g['step']//24:3d} {g['money'] or 0:10.0f} {m['money'] or 0:10.0f} {gap:10.0f} hands={g['hands']}", flush=True)
    (RESEARCH / "p134_money_curve.json").write_text(json.dumps({"gold": LOG_G, "mv": LOG_M}, indent=2), encoding="utf-8")
    print("WROTE", flush=True)


if __name__ == "__main__":
    main()
