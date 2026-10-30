# -*- coding: utf-8 -*-
"""P104f: pure open-loop full 720 gold tape, hands-count adaptive."""
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
OUTJSON = PROJ / "_research" / "p104f_full_tape.json"


def full_tape_agent(tag: str):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if me < len(farms) and isinstance(farms[me], dict) else {}
            live_n = len(farm.get("hands") or [])
            t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}
            hands = [list(h) for h in (t.get("h") or [])]
            # pad/truncate to live hand count so engine doesn't INVALID the turn
            if len(hands) > live_n:
                hands = hands[:live_n]
            while len(hands) < live_n:
                hands.append(["PASS"])
            return {
                "farmer": list(t.get("f") or ["PASS"]),
                "hands": hands,
                "market": [list(o) for o in (t.get("m") or [])],
            }
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    rows = []
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
                rows.append({"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
               "mean_margin": (sum(margins) / len(margins)) if margins else None}
    return rows, summary


def main():
    payload = {"variants": {}}
    rec = payload["variants"]["full_tape"] = {}
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2), "shop"),
    ):
        print(f"\n== full_tape vs {opp_name} ==", flush=True)
        rows, summary = series(full_tape_agent, opp_path, seeds, f"ft_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", key, summary, flush=True)
    print("RESULT", rec.get("metav4"), rec.get("shop"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
