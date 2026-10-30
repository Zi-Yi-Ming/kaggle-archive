# -*- coding: utf-8 -*-
"""P74 gate smoke: thomas_2945 vs alperen. finn never wrap. No submit."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_push_alperen" / "main.py"
CAND = ROOT / "_external" / "scan_20260919" / "extracted" / "thomas_2945_clean.py"
OUT = ROOT / "_research" / "p74_thomas_vs_alperen_smoke.json"


def load_quiet(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stdout(buf):
        try:
            spec.loader.exec_module(m)
        except Exception:
            # retry without stdout redirect to see error
            spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        return m.agent
    if hasattr(m, "build_agent"):
        return m.build_agent({})
    raise RuntimeError(f"no agent in {path}")


def wrap_agent(fn):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        if n <= 1:
            return fn(obs)
        return fn(obs, configuration)

    return agent


def run_game(a0, a1, seed: int) -> dict:
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    t0 = time.time()
    env.run([a0, a1])
    dt = time.time() - t0
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    st = [s.get("status") for s in f]
    return {"seed": seed, "bank0": b0, "bank1": b1, "status": st, "sec": round(dt, 1)}


def main() -> None:
    print("load alperen ...")
    alp = wrap_agent(load_quiet(ALPEREN, "p74_alperen"))
    print("load thomas ...")
    th = wrap_agent(load_quiet(CAND, "p74_thomas"))
    print("loaded. start smoke games seeds 1-2 both seats")

    games = []
    for seed in (1, 2):
        for seat_cand in (True, False):
            # fresh instances via reload each game
            alp = wrap_agent(load_quiet(ALPEREN, f"p74_alperen_{seed}_{seat_cand}"))
            th = wrap_agent(load_quiet(CAND, f"p74_thomas_{seed}_{seat_cand}"))
            if seat_cand:
                r = run_game(th, alp, seed)
                r["cand_seat"] = 0
                r["cand_bank"] = r["bank0"]
                r["alp_bank"] = r["bank1"]
            else:
                r = run_game(alp, th, seed)
                r["cand_seat"] = 1
                r["cand_bank"] = r["bank1"]
                r["alp_bank"] = r["bank0"]
            r["cand_win"] = r["cand_bank"] > r["alp_bank"]
            print(
                f"seed={seed} cand_seat={r['cand_seat']} "
                f"cand={r['cand_bank']:.0f} alp={r['alp_bank']:.0f} "
                f"win={r['cand_win']} st={r['status']} {r['sec']}s"
            )
            games.append(r)

    wins = sum(1 for g in games if g["cand_win"])
    summary = {
        "cand": str(CAND),
        "alperen": str(ALPEREN),
        "games": games,
        "cand_wins": wins,
        "n": len(games),
        "gate_note": "smoke only; full gate needs 5/8 vs alperen + 2 elites both seats",
        "submit": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"RESULT cand {wins}/{len(games)} vs alperen (smoke)")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
