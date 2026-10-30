# -*- coding: utf-8 -*-
"""P120: Farm OS v4 — role-slot binder. Glue gold tape hands to live hand count.

When live hands == tape hands: replay tape hands exactly.
When mismatch: map tape roles to live slots:
  slot0,1 = logistics (from tape h0,h1)
  slot2   = spare (PASS or tape h2)
  slot3+  = field (cycle tape field cmds)
Plus: always keep gold market window (h1 hire/buy, h4-10 fert sell).
Day0 = exact tape.
"""
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
OUTJSON = PROJ / "_research" / "p120_farm_os_v4.json"

CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


def bind_hands(tape_h, live_n):
    """Map tape hand commands onto live_n slots by role."""
    tape_h = [list(h) for h in (tape_h or [])]
    if live_n <= 0:
        return []
    if len(tape_h) == live_n:
        return tape_h
    # roles: logistics = first 2 tape cmds that look like logistics, else tape[0], tape[1]
    logi = []
    field = []
    for h in tape_h:
        op = h[0] if h else "PASS"
        if op in ("PICKUP", "PLACE", "BUILD_PASTURE", "BUILD_COOP", "FEED", "CARE", "DROP", "HARVEST"):
            logi.append(h)
        elif op in ("PLANT", "WATER", "FERTILIZE", "COLLECT_FERTILIZER"):
            field.append(h)
        elif op in ("WEST", "NORTH", "EAST", "SOUTH"):
            field.append(h)
        else:
            field.append(h)
    if not logi and tape_h:
        logi = tape_h[:1]
    if not field:
        field = [["PASS"]]
    out = []
    for i in range(live_n):
        if i < 2 and logi:
            out.append(logi[i % len(logi)])
        elif i == 2:
            out.append(["PASS"])
        else:
            out.append(field[(i - 3) % len(field)])
    return out


def farm_os_v4(tag: str):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            day, hour = step // 24, step % 24
            priv = (obs or {}).get("private") or {}
            shed = dict(priv.get("shed") or {})
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if 0 <= me < len(farms) and isinstance(farms[me], dict) else {}
            money = float(farm.get("money") or 0)
            live_n = len(farm.get("hands") or [])
            t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}

            # physical: gold farmer from tape; hands via role binder
            f = list(t.get("f") or ["PASS"])
            hands = bind_hands(t.get("h"), live_n)

            # market: gold tape + reactive fert/window safety
            m = [list(o) for o in (t.get("m") or [])]
            # reinforce daily hire if hands vanished
            if hour == 1 and live_n < 4:
                need = min(10 - len(m), 8)
                for _ in range(max(0, need)):
                    m.append(["HIRE"])
            # always dump fert in window
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0 and 4 <= hour <= 10:
                if not any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in m):
                    m.append(["SELL", "FERTILIZER", fert])
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
    payload = {"v4": {}}
    rec = payload["v4"]
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2), "shop"),
    ):
        print(f"\n== v4 vs {opp_name} ==", flush=True)
        rec[key] = series(farm_os_v4, opp_path, seeds, f"v4_{opp_name}")
        print("SUM", key, rec[key], flush=True)
    print("RESULT", rec, flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
