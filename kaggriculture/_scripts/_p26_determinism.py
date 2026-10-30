# -*- coding: utf-8 -*-
"""P26: R2 baseline determinism audit.

Same seed/seat/opponent/code — measure bank + action-hash stability.
Identifies whether T0 drift is real env nondeterminism or harness state pollution.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2_fresh():
    spec = importlib.util.spec_from_file_location(
        "r2_det_" + hashlib.md5(str(Path(__file__).stat().st_mtime).encode()).hexdigest()[:8]
        + "_" + str(id(object())),
        str(ROOT / "_push_medal" / "main.py"),
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_finn_cached():
    from _pm_pool import load_agent
    return load_agent("fallow_finn")


def load_finn_fresh():
    """Load fallow_finn without pool cache if possible."""
    path = ROOT / "reference_agents" / "fallow_finn.py"
    spec = importlib.util.spec_from_file_location(
        "finn_fresh_" + str(id(object())), str(path)
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_once(seed, seat, opp_loader, r2_loader, tag):
    r2 = r2_loader()
    opp = opp_loader()
    agents = [None, None]
    agents[seat] = r2
    agents[1 - seat] = opp
    actions = []

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            if is_own:
                # hash market+farmer compactly
                mkt = json.dumps(a.get("market") or [], sort_keys=True, default=str)
                farm = json.dumps(a.get("farmer") or [], default=str)
                hands = json.dumps(a.get("hands") or [], default=str)
                actions.append(hashlib.md5((mkt + farm + hands).encode()).hexdigest()[:12])
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    act_hash = hashlib.md5("|".join(actions).encode()).hexdigest()[:16]
    rec = {
        "tag": tag, "seed": seed, "seat": seat,
        "bank": my, "opp": op, "n_actions": len(actions),
        "act_hash": act_hash,
    }
    print(f"  {tag:28s} bank={my:.0f} n_act={len(actions)} hash={act_hash}", flush=True)
    return rec


def main():
    rows = []
    seed, seat = 1, 0

    print("=== A. same process, cached finn, fresh R2 ===")
    for i in range(3):
        rows.append(run_once(seed, seat, load_finn_cached, load_r2_fresh, f"A_cached_finn_rep{i}"))

    print("\n=== B. same process, fresh finn, fresh R2 ===")
    for i in range(3):
        rows.append(run_once(seed, seat, load_finn_fresh, load_r2_fresh, f"B_fresh_finn_rep{i}"))

    print("\n=== C. cached finn vs cached finn (control: does finn itself drift?) ===")
    # run R2 twice with same cached finn object reused? load each time from cache
    for i in range(2):
        rows.append(run_once(seed, seat, load_finn_cached, load_r2_fresh, f"C_cached_again_rep{i}"))

    # compare hashes
    print("\n=== HASH GROUPS ===")
    from collections import defaultdict
    by_hash = defaultdict(list)
    for r in rows:
        by_hash[r["act_hash"]].append(r["tag"])
    for h, tags in by_hash.items():
        print(f"  {h}: {tags}")

    banks = [r["bank"] for r in rows]
    print(f"\nbank min={min(banks):.0f} max={max(banks):.0f} spread={max(banks)-min(banks):.0f}")
    print(f"unique act_hash: {len(by_hash)} / {len(rows)} runs")

    out = ROOT / "p26_determinism_audit.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out.name)


if __name__ == "__main__":
    main()
