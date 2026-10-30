# -*- coding: utf-8 -*-
"""P55b: skip step0 opening; per-day divergence profile alperen vs close elites."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
OPPS = {
    "R2": ROOT / "_push_medal" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    "guru_dynamic": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
}


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def record(a_fn, b_fn, seed):
    aa, bb = [], []

    def wa(obs, configuration=None):
        act = a_fn(obs, configuration)
        aa.append(act)
        return act

    def wb(obs, configuration=None):
        act = b_fn(obs, configuration)
        bb.append(act)
        return act

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wa, wb])
    f = env.steps[-1]
    return aa, bb, float(f[0]["observation"]["farms"][0]["money"]), float(f[1]["observation"]["farms"][1]["money"])


def main():
    alp = load_quiet(ALPEREN, "p55b_alp")
    print("=== per-day divergent step count (skip step 0) ===", flush=True)
    rows = []
    for oname, path in OPPS.items():
        opp = load_quiet(path, f"p55b_{oname}")
        aa, bb, ba, bo = record(alp, opp, 1)
        print(f"\n{oname}: alp={ba:.0f} opp={bo:.0f}", flush=True)
        day_counts = []
        first_after0 = None
        for day in range(30):
            n = 0
            for t in range(day * 24, min((day + 1) * 24, len(aa), len(bb))):
                if t == 0:
                    continue
                if akey(aa[t]) != akey(bb[t]):
                    n += 1
                    if first_after0 is None:
                        first_after0 = t
            day_counts.append(n)
            if n:
                print(f"  d{day:02d}: {n}/24", flush=True)
        peak_days = sorted(range(30), key=lambda d: -day_counts[d])[:5]
        print(f"  first_div_after0={first_after0} peak_days={peak_days}", flush=True)
        for day in range(30):
            rows.append({
                "opponent": oname, "day": day,
                "div_steps": day_counts[day],
                "alp_bank": ba, "opp_bank": bo,
            })
        # top landmark windows
        for w in (6, 7, 9, 10, 12, 15, 18):
            print(f"  window d{w}: {day_counts[w]}/24", flush=True)

    with open(ROOT / "p55_gate_day_profile.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p55_gate_day_profile.csv", flush=True)


if __name__ == "__main__":
    main()
