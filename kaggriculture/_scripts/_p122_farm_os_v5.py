# -*- coding: utf-8 -*-
"""P122 Farm OS v5: supervised hand binder from gold (hour, n) -> modal actions."""
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
BINDER = json.loads((PROJ / "_research" / "p121_hand_binder.json").read_text(encoding="utf-8"))["binder"]
OUTJSON = PROJ / "_research" / "p122_farm_os_v5.json"


def hands_for(hour, n, tape_h):
    key = f"{hour}_{n}"
    if key in BINDER:
        cmds = [list(h) for h in BINDER[key]]
        if len(cmds) == n:
            return cmds
        if len(cmds) > n:
            return cmds[:n]
        return cmds + [["PASS"] for _ in range(n - len(cmds))]
    # fallback: tape
    tape_h = [list(h) for h in (tape_h or [])]
    if len(tape_h) == n:
        return tape_h
    if len(tape_h) > n:
        return tape_h[:n]
    return tape_h + [["PASS"] for _ in range(n - len(tape_h))]


def farm_os_v5(tag: str):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            hour = step % 24
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if 0 <= me < len(farms) and isinstance(farms[me], dict) else {}
            live_n = len(farm.get("hands") or [])
            t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}
            f = list(t.get("f") or ["PASS"])
            hands = hands_for(hour, live_n, t.get("h"))
            m = [list(o) for o in (t.get("m") or [])]
            return {"farmer": f, "hands": hands, "market": m}
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

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
    payload = {"v5": {}}
    rec = payload["v5"]
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2), "shop"),
    ):
        print(f"\n== v5 vs {opp_name} ==", flush=True)
        rec[key] = series(farm_os_v5, opp_path, seeds, f"v5_{opp_name}")
        print("SUM", key, rec[key], flush=True)
    # compare to pure tape ~40k
    print("RESULT", rec, "(pure tape ~40k vs metav4)", flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
