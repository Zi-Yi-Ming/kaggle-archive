# -*- coding: utf-8 -*-
"""P58: where does live alperen lose? Day profile + opponent + repeat patterns."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
OPPS = {
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    "guru_dynamic": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "finn": ROOT / "reference_agents" / "fallow_finn.py",
}
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def run_pair(a0, a1, seed, keys0=None, keys1=None):
    def w(inner, bag):
        n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
        if n <= 1:
            def agent(obs):
                a = inner(obs)
                if bag is not None:
                    bag.append(akey(a))
                return a
        else:
            def agent(obs, configuration=None):
                a = inner(obs, configuration)
                if bag is not None:
                    bag.append(akey(a))
                return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([w(a0, keys0), w(a1, keys1)])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def day_div_profile(ka, kb):
    n = min(len(ka), len(kb))
    by_day = Counter()
    for t in range(n):
        if ka[t] != kb[t]:
            by_day[t // 24] += 1
    return by_day


def main():
    alp = load_quiet(ALPEREN, "p58_alp")
    rows = []
    loss_days = Counter()
    win_days = Counter()
    # for losses, which days have most divergence
    loss_day_div = Counter()

    print("=== P58 alperen failure audit ===", flush=True)
    for oname, opath in OPPS.items():
        print(f"\n-- {oname} --", flush=True)
        opp_w = opp_l = opp_d = 0
        for seed in SEEDS:
            ka, kb = [], []
            a0, a1 = run_pair(alp, load_quiet(opath, f"p58_{oname}_{seed}a"), seed, ka, kb)
            b0, b1 = run_pair(load_quiet(opath, f"p58_{oname}_{seed}b"), alp, seed, kb, ka)
            our = (a0 + b1) / 2
            theirs = (a1 + b0) / 2
            if our > theirs + 1:
                opp_w += 1
                res = "W"
            elif theirs > our + 1:
                opp_l += 1
                res = "L"
                # record divergent days for this loss
                prof = day_div_profile(ka, kb)
                for d, n in prof.items():
                    if n >= 4:  # substantial
                        loss_day_div[d] += 1
                if prof:
                    peak = max(prof.items(), key=lambda x: x[1])
                    loss_days[peak[0]] += 1
            else:
                opp_d += 1
                res = "D"
            print(f"  s{seed}: {res} our={our:.0f} opp={theirs:.0f}", flush=True)
            rows.append({
                "opponent": oname, "seed": seed, "result": res,
                "our": our, "opp": theirs, "margin": our - theirs,
            })
        print(f"  => {oname}: {opp_w}-{opp_d}-{opp_l}", flush=True)

    print("\n=== loss peak-day histogram ===", flush=True)
    print(loss_days.most_common(10), flush=True)
    print("=== days with ≥4 div steps in any loss ===", flush=True)
    print(loss_day_div.most_common(12), flush=True)

    # who beats alperen?
    print("\n=== W-D-L by opponent ===", flush=True)
    by = defaultdict(Counter)
    for r in rows:
        by[r["opponent"]][r["result"]] += 1
    for o, c in by.items():
        print(f"  {o}: {c.get('W',0)}-{c.get('D',0)}-{c.get('L',0)}", flush=True)

    with open(ROOT / "p58_failure_audit.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p58_failure_audit.csv", flush=True)


if __name__ == "__main__":
    main()
