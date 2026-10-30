# -*- coding: utf-8 -*-
"""P125 Farm OS v6: gold tape + high-purity position rules for hands."""
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
RULES = json.loads((PROJ / "_research" / "p123_hand_rules.json").read_text(encoding="utf-8"))
LOOKUP = RULES["lookup"]
# only keep high-purity rules
HIGH = {}
for r in RULES["top_rules"]:
    if r["purity"] >= 0.75 and r["n"] >= 40:
        HIGH[r["feat"]] = r["op"]
print("high-purity rules", len(HIGH), flush=True)


def tile_char(cell):
    if cell is None:
        return "emp"
    if cell == "LOCKED":
        return "lock"
    if not isinstance(cell, dict):
        return "?"
    k = cell.get("kind") or "?"
    if k == "PLANT":
        return "pl_" + (cell.get("crop") or "?")
    return str(k).lower()


def feat_of(hpos, tiles, hour, day, fert):
    x, y = int(hpos[0]), int(hpos[1])
    t = "oob"
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        t = tile_char(tiles[y][x])
    return f"t={t}|dx={x-3}|dy={y-3}|h={hour}|d={day//5}|fert={1 if fert else 0}"


def parse_op(op):
    if ":" in op:
        a, b = op.split(":", 1)
        return [a, b]
    return [op]


def farm_os_v6(tag: str):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            hour, day = step % 24, step // 24
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if 0 <= me < len(farms) and isinstance(farms[me], dict) else {}
            hands = farm.get("hands") or []
            live_n = len(hands)
            tiles = farm.get("tiles") or []
            shed = ((obs.get("private") or {}).get("shed") or {})
            fert = int(shed.get("FERTILIZER") or 0)
            t = TAPE[step] if step < len(TAPE) else {"f": ["PASS"], "h": [], "m": []}

            f = list(t.get("f") or ["PASS"])
            m = [list(o) for o in (t.get("m") or [])]
            out_h = []
            tape_h = [list(x) for x in (t.get("h") or [])]
            for i in range(live_n):
                h = hands[i]
                hp = h.get("pos") if isinstance(h, dict) and "pos" in h else h
                cmd = None
                if isinstance(hp, list) and len(hp) == 2:
                    feat = feat_of(hp, tiles, hour, day, fert)
                    if feat in HIGH:
                        cmd = parse_op(HIGH[feat])
                if cmd is None:
                    if i < len(tape_h):
                        cmd = tape_h[i]
                    else:
                        cmd = ["PASS"]
                out_h.append(cmd)
            return {"farmer": f, "hands": out_h, "market": m}
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    for seed in seeds:
        c = make_cand(f"c_{label}_{seed}")
        o = p79.load_quiet(opp_path, f"o_{label}_{seed}")
        b0, b1, stt, sec = p79.run(c, o, seed)
        margin = b0 - b1
        win = b0 > b1
        wins += int(win)
        margins.append(margin)
        print(f"{label} s={seed} {b0:.0f}:{b1:.0f} m={margin:.0f} win={win}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": wins / n, "mean_margin": sum(margins) / n}


def main():
    print("== v6 vs metav4 ==", flush=True)
    mv = series(farm_os_v6, METAV4, (1, 2, 3), "v6_mv")
    print("MV", mv, flush=True)
    print("== v6 vs shop ==", flush=True)
    sh = series(farm_os_v6, SHOPV7, (1, 2), "v6_sh")
    print("SH", sh, flush=True)


if __name__ == "__main__":
    main()
