# -*- coding: utf-8 -*-
"""P119: full gold tape as agent (p97d-safe), just measure ceiling again + compare."""
from __future__ import annotations

import json
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
TAPE = json.loads((PROJ / "_research" / "p104_gold_full_tape.json").read_text(encoding="utf-8"))["tape"]


def make_tape_agent():
    def agent(observation, configuration=None):
        try:
            step = int((observation or {}).get("step", 0))
            farms = (observation or {}).get("farms") or []
            me = int((observation or {}).get("player") if (observation or {}).get("player") is not None else 0)
            farm = farms[me] if me < len(farms) and isinstance(farms[me], dict) else {}
            live_n = len(farm.get("hands") or [])
            t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}
            hands = [list(h) for h in (t.get("h") or [])]
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


# export for p79 style load
agent = make_tape_agent()

if __name__ == "__main__":
    print("tape agent ready, steps", len(TAPE))
