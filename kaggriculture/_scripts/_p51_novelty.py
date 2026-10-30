# -*- coding: utf-8 -*-
"""Confirm: gate-pass candidates vs finn + similarity vs known elites."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

EXT = ROOT / "_external" / "p51_extracted2"
CANDS = {
    "guru_dynamic": EXT / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "alperen_meta": EXT / "kaggriculture_metacounter_r1_scored_agent.py",
}
ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}
FINN = ROOT / "reference_agents" / "fallow_finn.py"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def run_keys(fn, seed, opponent_path):
    keys = []
    opp = load_quiet(opponent_path, f"opp_{seed}_{id(object())}")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def wrap(obs):
            a = fn(obs)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    else:
        def wrap(obs, configuration=None):
            a = fn(obs, configuration)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap, opp])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    return bank, keys, hashlib.md5("\n".join(keys).encode()).hexdigest()[:16]


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def vs_finn_mean(fn, seeds):
    banks = []
    w = l = 0
    for seed in seeds:
        b0, _, _ = run_keys(fn, seed, FINN)
        # seat 1
        opp = load_quiet(FINN, f"f_{seed}")
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.info = {"seed": int(seed)}
        env.run([opp, fn])
        f = env.steps[-1]
        us_s1 = float(f[1]["observation"]["farms"][1]["money"])
        our = (b0 + us_s1) / 2
        banks.append(our)
        if our > 3000 + 1:
            w += 1
        else:
            l += 1
    return sum(banks) / len(banks), w, l, banks


def main():
    elite_keys = {}
    elite_banks = {}
    print("=== elite refs vs finn seed1 ===", flush=True)
    for name, path in ELITES.items():
        fn = load_quiet(path, f"el_{name}")
        bank, keys, h = run_keys(fn, 1, FINN)
        elite_keys[name] = keys
        elite_banks[name] = bank
        print(f"  {name}: {bank:.0f}", flush=True)

    rows = []
    for name, path in CANDS.items():
        print(f"\n=== {name} ===", flush=True)
        fn = load_quiet(path, f"n_{name}")
        bank, keys, h = run_keys(fn, 1, FINN)
        sims = {n: sim(keys, elite_keys[n]) for n in elite_keys}
        nearest = min(sims, key=sims.get)
        mean, w, l, banks = vs_finn_mean(fn, SEEDS)
        print(f"  vs finn 8-seed mean={mean:.0f} W-L={w}-{l}", flush=True)
        print(f"  sim nearest={nearest}:{sims[nearest]:.3f} all={ {k: round(v,3) for k,v in sims.items()} }", flush=True)
        rows.append({
            "name": name, "bank_s1": bank, "finn_mean8": mean,
            "finn_W": w, "finn_L": l, "nearest": nearest,
            "nearest_sim": sims[nearest], "tape_hash": h,
            **{f"sim_{k}": sims[k] for k in sims},
        })

    with open(ROOT / "p51_novelty.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p51_novelty.csv", flush=True)


if __name__ == "__main__":
    main()
