# -*- coding: utf-8 -*-
"""P135: gold tape + forced mid-game fert collection to fund d9-11 investment."""
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
OUTJSON = PROJ / "_research" / "p135_fert_fund.json"


def pad(cmds, n):
    cmds = [list(c) for c in (cmds or [])]
    if len(cmds) > n:
        return cmds[:n]
    while len(cmds) < n:
        cmds.append(["PASS"])
    return cmds


def make(tag, force_fert=True):
    def agent(obs, configuration=None):
        step = int((obs or {}).get("step", 0))
        day, hour = step // 24, step % 24
        farms = (obs.get("farms") or [])
        me = int(obs.get("player") if obs.get("player") is not None else 0)
        farm = {}
        if 0 <= me < len(farms) and isinstance(farms[me], dict):
            farm = farms[me]
        live_n = len(farm.get("hands") or [])
        shed = dict(((obs.get("private") or {}).get("shed") or {}))
        t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}
        f = list(t.get("f") or ["PASS"])
        h = pad(t.get("h"), live_n)
        m = [list(o) for o in (t.get("m") or [])]

        if force_fert:
            # inject collect on spare slots during mid-game
            if 2 <= day <= 8 and hour in (3, 4, 5):
                if f[:1] == ["PASS"] or f[0] in ("PASS", "WEST", "NORTH"):
                    f = ["COLLECT_FERTILIZER"]
                for i in range(len(h)):
                    if h[i][:1] in (["PASS"],):
                        h[i] = ["COLLECT_FERTILIZER"]
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0:
                has = any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in m)
                if not has:
                    m.append(["SELL", "FERTILIZER", fert])
        return {"farmer": f, "hands": h, "market": m}
    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    ends = []
    for seed in seeds:
        c = make_cand(f"c_{label}_{seed}")
        o = p79.load_quiet(opp_path, f"o_{label}_{seed}")
        b0, b1, stt, sec = p79.run(c, o, seed)
        margin = b0 - b1
        win = b0 > b1
        wins += int(win)
        margins.append(margin)
        ends.append(b0)
        print(f"{label} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": wins / n,
            "mean_margin": sum(margins) / n, "mean_cand": sum(ends) / n}


def main():
    payload = {}
    for name, fn in (
        ("tape_plain", lambda tag: make(tag, False)),
        ("tape_fert_fund", lambda tag: make(tag, True)),
    ):
        print(f"\n==== {name} ====", flush=True)
        mv = series(fn, METAV4, (1, 2, 3), name)
        print("MV", name, mv, flush=True)
        payload[name] = mv
        OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\n(cand money is the gold-clone quality metric; target 80k+)", flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
