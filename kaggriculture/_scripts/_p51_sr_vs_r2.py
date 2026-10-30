# -*- coding: utf-8 -*-
"""state_router vs R2 H2H. Load once. Suppress import smoke. finn never wrapped."""
from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    with redirect_stdout(buf):
        spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        return m.agent
    return m.build_agent({})


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


SR = ROOT / "_external" / "p51_extracted" / "kaggriculture_public_state_router_74_5_win_rate.py"
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3, 11, 12)


def main():
    print("loading state_router...", flush=True)
    sr = load_quiet(SR, "sr_main")
    print("loading R2...", flush=True)
    r2 = load_quiet(R2, "r2_main")
    print("loaded, starting H2H", flush=True)

    w = d = l = 0
    for seed in SEEDS:
        b0, b1 = run(sr, r2, seed)
        c0, c1 = run(r2, sr, seed)
        our = (b0 + c1) / 2
        theirs = (b1 + c0) / 2
        if our > theirs + 1:
            w += 1
            res = "SR"
        elif theirs > our + 1:
            l += 1
            res = "R2"
        else:
            d += 1
            res = "TIE"
        print(f"s{seed}: SR={our:.0f} R2={theirs:.0f} {res}", flush=True)

    print(f"state_router W-T-L vs R2: {w}-{d}-{l} ({w}/{w+d+l})", flush=True)
    print("LOCAL_GATE_HINT_PASS" if w >= 4 else "LOCAL_GATE_FAIL", flush=True)


if __name__ == "__main__":
    main()
