# -*- coding: utf-8 -*-
"""P74 expanded local gate: thomas_2945 vs alperen + R2. finn never wrap. No submit."""
from __future__ import annotations

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
R2 = ROOT / "_push_medal" / "main.py"
CAND = ROOT / "_external" / "scan_20260919" / "extracted" / "thomas_2945_clean.py"
OUT = ROOT / "_research" / "p74_thomas_gate_expanded.json"
SEEDS = (1, 2, 3, 4)


def load_quiet(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            spec.loader.exec_module(m)
    except Exception:
        spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        return m.agent
    if hasattr(m, "build_agent"):
        return m.build_agent({})
    raise RuntimeError(f"no agent in {path}")


def wrap_agent(fn):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def fresh(path: Path, tag: str):
    return wrap_agent(load_quiet(path, tag))


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
    return {"bank0": b0, "bank1": b1, "status": st, "sec": round(dt, 1)}


def series(cand_path: Path, opp_path: Path, opp_name: str) -> list[dict]:
    rows = []
    for seed in SEEDS:
        for cand_seat0 in (True, False):
            tag = f"{opp_name}_{seed}_{int(cand_seat0)}"
            cand = fresh(cand_path, f"c_{tag}")
            opp = fresh(opp_path, f"o_{tag}")
            if cand_seat0:
                r = run_game(cand, opp, seed)
                cand_bank, opp_bank = r["bank0"], r["bank1"]
            else:
                r = run_game(opp, cand, seed)
                cand_bank, opp_bank = r["bank1"], r["bank0"]
            row = {
                "opp": opp_name,
                "seed": seed,
                "cand_seat0": cand_seat0,
                "cand_bank": cand_bank,
                "opp_bank": opp_bank,
                "margin": cand_bank - opp_bank,
                "win": cand_bank > opp_bank,
                "status": r["status"],
                "sec": r["sec"],
            }
            print(
                f"{opp_name} seed={seed} seat0={cand_seat0} "
                f"cand={cand_bank:.0f} opp={opp_bank:.0f} "
                f"margin={row['margin']:.0f} win={row['win']} {row['sec']}s"
            )
            rows.append(row)
    return rows


def main() -> None:
    all_rows: list[dict] = []
    for opp_path, opp_name in ((ALPEREN, "alperen"), (R2, "R2")):
        print(f"=== series vs {opp_name} ===")
        all_rows.extend(series(CAND, opp_path, opp_name))

    summary = {}
    for name in ("alperen", "R2"):
        sub = [r for r in all_rows if r["opp"] == name]
        wins = sum(1 for r in sub if r["win"])
        margins = [r["margin"] for r in sub]
        summary[name] = {
            "wins": wins,
            "n": len(sub),
            "mean_margin": sum(margins) / max(1, len(margins)),
            "seat0_wins": sum(1 for r in sub if r["cand_seat0"] and r["win"]),
            "seat1_wins": sum(1 for r in sub if (not r["cand_seat0"]) and r["win"]),
            "all_done": all(r["status"] == ["DONE", "DONE"] for r in sub),
        }
        print(
            f"SUMMARY vs {name}: {wins}/{len(sub)} "
            f"mean_margin={summary[name]['mean_margin']:.0f} "
            f"seat0W={summary[name]['seat0_wins']} seat1W={summary[name]['seat1_wins']}"
        )

    payload = {
        "cand": str(CAND),
        "seeds": list(SEEDS),
        "rows": all_rows,
        "summary": summary,
        "full_gate_still_needed": [
            "seeds 5-8 if smoke pattern holds",
            "vs additional elite (tetsu/kaito/rayk) if available",
            "fingerprint novelty review",
        ],
        "submit": False,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
