# -*- coding: utf-8 -*-
"""P106: modal gold tape (5 games) + winner tape. Open-loop with hand-count adapt."""
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = PROJ / "_research"
GOLD = "吃白饭的大肥鱼"
OUTJSON = RESEARCH / "p106_modal_tape.json"


def load_tapes():
    meta = json.loads((OUT / "gold_meta.json").read_text(encoding="utf-8"))
    idx = {}
    for row in meta:
        for a in row.get("agents") or []:
            if a.get("teamName") == GOLD:
                idx[row["episode_id"]] = (int(a.get("index") or 0), a.get("reward"))
    tapes = []
    winner = None
    for p in sorted((OUT / "gold").glob("episode-*-replay.json")):
        eid = int(p.name.split("-")[1])
        if eid not in idx:
            continue
        ai, reward = idx[eid]
        data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        tape = []
        for st in data.get("steps") or []:
            act = st[ai].get("action") or {}
            tape.append({
                "f": act.get("farmer") or ["PASS"],
                "h": act.get("hands") or [],
                "m": act.get("market") or [],
            })
        tapes.append(tape)
        # winner = higher reward at our index
        scores = data.get("rewards") or [0, 0]
        if scores[ai] == max(scores):
            winner = tape
        if len(tapes) >= 5:
            break
    return tapes, winner


def modal_tape(tapes):
    n = max(len(t) for t in tapes)
    out = []
    for i in range(n):
        fs = [tuple(map(str, t[i]["f"])) for t in tapes if i < len(t)]
        ms = [json.dumps(t[i]["m"], sort_keys=True) for t in tapes if i < len(t)]
        f = list(Counter(fs).most_common(1)[0][0])
        m = json.loads(Counter(ms).most_common(1)[0][0])
        # hands: pick from the tape whose hand-count is modal at this step
        hs = [len(t[i]["h"]) for t in tapes if i < len(t)]
        want = Counter(hs).most_common(1)[0][0]
        src = next(t[i]["h"] for t in tapes if i < len(t) and len(t[i]["h"]) == want)
        out.append({"f": f, "h": [list(x) for x in src], "m": m})
    return out


def make_open_loop(tape):
    def agent(obs, configuration=None):
        try:
            step = int((obs or {}).get("step", 0))
            farms = (obs or {}).get("farms") or []
            me = int((obs or {}).get("player") if (obs or {}).get("player") is not None else 0)
            farm = farms[me] if me < len(farms) and isinstance(farms[me], dict) else {}
            live_n = len(farm.get("hands") or [])
            t = tape[step] if step < len(tape) else {"f": ["PASS"], "h": [], "m": []}
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
    tapes, winner = load_tapes()
    print("tapes", len(tapes), "winner", winner is not None, flush=True)
    modal = modal_tape(tapes)
    print("modal len", len(modal), flush=True)

    payload = {"variants": {}}
    for name, tape in (("modal", modal), ("winner", winner or modal)):
        rec = payload["variants"][name] = {}
        print(f"\n==== {name} ====", flush=True)
        for opp_name, opp_path, seeds, key in (
            ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
            ("shopv7", SHOPV7, (1, 2), "shop"),
        ):
            rows, summary = series(make_open_loop(tape), opp_path, seeds, f"{name}_{opp_name}")
            rec[key] = {"rows": rows, "summary": summary}
            print("SUM", name, key, summary, flush=True)

    best = None
    for name, rec in payload["variants"].items():
        mv = rec.get("metav4", {}).get("summary", {}).get("mean_margin") or -1e9
        print(name, "mv_margin", mv, flush=True)
        if best is None or mv > best[0]:
            best = (mv, name)
    payload["best"] = {"name": best[1], "mv_margin": best[0]} if best else None
    print("BEST", payload["best"], flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
